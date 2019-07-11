import csv
from typing import List, Dict
import sqlite3
import os

class Timezone:
  def __init__(self):
    self.id: int = 0
    self.country_code: str = None
    self.zone_name: str = None
    self.abbr: str = None
    self.gmt_offset: int = 0
    self.dst: bool = False

class Timezones:
  _mconn: sqlite3.Connection = None

  def __init__(self, file: str = None):
    if Timezones._mconn == None:
      self._initDB()

  def getUTCOffset(self, abbreviation: str, unixtime: int):
    cur = self._conn().cursor()
    cur.execute("SELECT tz.gmt_offset FROM `timezone` tz WHERE tz.abbreviation=? AND tz.time_start <= ? ORDER BY tz.time_start DESC LIMIT 1;", [abbreviation])
    return int(cur.fetchone()[0])

  def getTimezone(self, name: str, unixtime: int):
    cur = self._conn().cursor()
    cur.execute("""SELECT z.zone_id, z.country_code, z.zone_name, tz.abbreviation, tz.gmt_offset, tz.dst
      FROM `timezone` tz JOIN `zone` z
      ON tz.zone_id=z.zone_id
      WHERE tz.time_start <= ? AND z.zone_name=?
      ORDER BY tz.time_start DESC LIMIT 1;""", [unixtime, name])
    row = cur.fetchone()
    tz: Timezone = Timezone()
    tz.id = int(row[0])
    tz.country_code = row[1]
    tz.zone_name = row[2]
    tz.abbr = row[3]
    tz.gmt_offset = int(row[4])
    tz.dst = int(row[5])==1
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
      
