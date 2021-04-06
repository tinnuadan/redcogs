import csv
from datetime import tzinfo, timedelta, datetime
from typing import List, Dict
import sqlite3
import os
import time

class TzInfo(tzinfo):
  def __init(self):
    self.gmt_offset: int = None
    self.has_dst: bool = False

  @staticmethod
  def Construct(utcoffset: int, has_dst: bool = False):
    tz = TzInfo()
    tz._gmt_offset = utcoffset
    tz._has_dst = has_dst
    if has_dst:
      tz._gmt_offset -= 3600
    return tz

  def utcoffset(self, dt):
    if self._gmt_offset == None:
      return None
    return timedelta(seconds=self._gmt_offset) + self.dst(dt)

  def dst(self, dt):
    if self._gmt_offset == None:
      return None
    return timedelta(hours = 1) if self._has_dst else timedelta(0)

  def __str__(self):
    if not self._gmt_offset:
      return "Empty tzinfo"
    return "%i+%ih" % (self._gmt_offset/3600, self.dst(None).seconds/3600)

class Timezone(TzInfo):
  def __init__(self):
    self.id: int = 0
    self.country_code: str = None
    self.zone_name: str = None
    self.abbr: str = None

  @staticmethod
  def Construct(utcoffset: int, has_dst: bool = False):
    tz = Timezone()
    tz._gmt_offset = utcoffset
    tz._has_dst = has_dst
    if has_dst:
      tz._gmt_offset -= 3600
    return tz

class Timezones:
  _mconn: sqlite3.Connection = None

  def __init__(self, file: str = None):
    if Timezones._mconn == None:
      self._initDB(file)

  def getAvailableAbbreviations(self):
    cur = self._conn().cursor()
    zones = []
    for row in cur.execute("""SELECT tz.abbreviation as abbreviation FROM `timezone` tz 
    WHERE tz.abbreviation NOT LIKE '+%' AND tz.abbreviation NOT LIKE '-%' 
    GROUP BY tz.abbreviation 
    UNION SELECT 'UTC' as abbreviation
    UNION SELECT 'Z' as abbreviation
    ORDER BY tz.abbreviation ASC;"""):
      zones.append(row[0])
    return zones

  def getTzID(self, name):
    cur = self._conn().cursor()
    cur.execute("""SELECT z.zone_id, z.country_code, z.zone_name
      FROM `zone` z
      WHERE z.zone_name=? COLLATE NOCASE""", [name])
    row = cur.fetchone()
    if not row:
      return None
    return int(row[0])

  def getTzInfo(self, abbreviation: str):
    if len(abbreviation) == 5 and (abbreviation[0]=="+" or abbreviation[0]=="-"):
      return self._getRawTzOffset(abbreviation)
    if abbreviation in ["UTC", "Z"]:
      return self._getRawTzOffset("+0000")
    cur = self._conn().cursor()
    cur.execute("""SELECT tz.gmt_offset, tz.dst FROM `timezone` tz 
    WHERE tz.abbreviation=? AND tz.time_start <= ? 
    ORDER BY tz.time_start DESC LIMIT 1;""", [abbreviation, int(time.time())])
    row = cur.fetchone()
    if not row:
      return None
    return TzInfo.Construct(int(row[0]), int(row[1])==1)

  def _getRawTzOffset(self, offset: str):
    sign = int("%s1" % offset[0])
    hours = int(offset[1:3])
    minutes = int(offset[3:])
    return TzInfo.Construct(sign * (hours*3600+minutes*60), False)

  def getTimezone(self, name: str, unixtime: int):
    if name == "UTC":
      tz: Timezone = Timezone.Construct(0, False)
      tz.id = -1
      tz.country_code = ""
      tz.zone_name = "UTC"
      tz.abbr = "UTC"
      return tz
      
    cur = self._conn().cursor()
    cur.execute("""SELECT z.zone_id, z.country_code, z.zone_name, tz.abbreviation, tz.gmt_offset, tz.dst
      FROM `timezone` tz JOIN `zone` z
      ON tz.zone_id=z.zone_id
      WHERE tz.time_start <= ? AND z.zone_name=?
      COLLATE NOCASE
      ORDER BY tz.time_start DESC LIMIT 1;""", [unixtime, name])
    row = cur.fetchone()
    if not row:
      return None
    tz: Timezone = Timezone.Construct(int(row[4]), int(row[5])==1)
    tz.id = int(row[0])
    tz.country_code = row[1]
    tz.zone_name = row[2]
    tz.abbr = row[3]
    return tz

  def getTimezoneByID(self, id: int, unixtime: int):
    if id == 0:
      tz: Timezone = Timezone.Construct(0, False)
      tz.id = -1
      tz.country_code = ""
      tz.zone_name = "UTC"
      tz.abbr = "UTC"
      return tz
      
    cur = self._conn().cursor()
    cur.execute("""SELECT z.zone_id, z.country_code, z.zone_name, tz.abbreviation, tz.gmt_offset, tz.dst
      FROM `timezone` tz JOIN `zone` z
      ON tz.zone_id=z.zone_id
      WHERE tz.time_start <= ? AND z.zone_id=?
      ORDER BY tz.time_start DESC LIMIT 1;""", [unixtime, id])
    row = cur.fetchone()
    if not row:
      return None
    tz: Timezone = Timezone.Construct(int(row[4]), int(row[5])==1)
    tz.id = int(row[0])
    tz.country_code = row[1]
    tz.zone_name = row[2]
    tz.abbr = row[3]
    return tz

  def _initDB(self, file: str = None):
    if file == None:
      file = ":memory:"
    Timezones._mconn = sqlite3.connect(file)
    conn = self._conn()
    
    base_path = os.path.split(os.path.realpath(__file__))[0]
    timezone = os.path.join(base_path,"tzdata","timezone.csv")
    zone = os.path.join(base_path,"tzdata","zone.csv")

    conn.execute("DROP TABLE IF EXISTS `timezone`")
    conn.execute("""CREATE TABLE `timezone` (
    `zone_id` INTEGER NOT NULL,
    `abbreviation` TEXT NOT NULL,
    `time_start` INTEGER NOT NULL,
    `gmt_offset` INTEGER NOT NULL,
    `dst` INTEGER NOT NULL
    )""")
    conn.execute("CREATE INDEX `idx_zone_id` ON `timezone` (`zone_id`)")
    conn.execute("CREATE INDEX `idx_time_start` ON `timezone` (`time_start`)")
    self._loadCSV("timezone", timezone)
      
    conn.execute("DROP TABLE IF EXISTS `zone`")
    conn.execute("""CREATE TABLE `zone` (
    `zone_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `country_code` TEXT NOT NULL,
    `zone_name` TEXT NOT NULL
    )""")
    conn.execute("CREATE INDEX `idx_zone_name` ON `zone` (`zone_name`)")
    self._loadCSV("zone", zone)

    conn.commit()

  def _conn(self):
    return Timezones._mconn

  def _loadCSV(self, tablename: str, filepath: str):
    conn = self._conn()
    with open(filepath, newline='') as csvfile:
      reader = csv.reader(csvfile, delimiter=',', quotechar='"')
      rows = []
      for row in reader:
        rows.append(row)
      values = ",".join(["?"] * len(rows[0]))
      cmd = "INSERT INTO `%s` VALUES (%s)" % (tablename, values)
      conn.executemany(cmd, rows)
      
