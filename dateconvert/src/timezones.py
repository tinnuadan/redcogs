from typing import List, Dict
import sqlite3
import os

class Timezones:
  _conn: sqlite3.Connection = None

  def __init__(self):
    if Timezones._conn == None:
      self._initDB()

  def _initDB(self):
    Timezones._conn = sqlite3.connect(":memory:")
    conn = self._cursor()
    
    base_path = os.path.split(os.path.realpath(__file__))[0]
    timezone = os.path.join(base_path,"tzdata","timezone.csv")
    zone = os.path.join(base_path,"tzdata","zone.csv")

    conn.execute("""CREATE TABLE `timezone` (
    `zone_id` INTEGER NOT NULL,
    `abbreviation` TEXT NOT NULL,
    `time_start` INTEGER NOT NULL,
    `gmt_offset` INTEGER NOT NULL,
    `dst` INTEGER NOT NULL
    )""")
    conn.execute("CREATE INDEX `idx_zone_id` ON `timezone` (`zone_id`)")
    conn.execute("CREATE INDEX `idx_time_start` ON `timezone` (`time_start`)")
    #conn.execute("LOAD DATA LOCAL INFILE ? INTO TABLE `timezone` FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n';", timezone)
      
    conn.execute("""CREATE TABLE `zone` (
    `zone_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `country_code` TEXT NOT NULL,
    `zone_name` TEXT NOT NULL
    )""")
    conn.execute("CREATE INDEX `idx_zone_name` ON `zone` (`zone_name`)")
    #conn.execute("LOAD DATA LOCAL INFILE ? INTO TABLE `zone` FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n';", zone)

    conn.commit()

  def _cursor(self):
    return Timezones._conn