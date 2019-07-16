import json
import sqlite3
import datetime
from ..src.timezones import Timezones, Timezone, TzInfo


def test_loading():
  tzs = Timezones()
  conn: sqlite3.Connection = tzs._conn()
  assert conn != None

  cur: sqlite3.Cursor = conn.cursor()
  cur.execute("SELECT COUNT(`zone_id`) AS rowcount FROM `zone`")
  assert cur.fetchone()[0] == 425
  cur.execute("SELECT COUNT(`zone_id`) AS rowcount FROM `timezone`")
  assert cur.fetchone()[0] == 163009

  tz: Timezone = tzs.getTimezone("Europe/Berlin", 1562853025)
  assert tz.zone_name == "Europe/Berlin"
  assert tz.id == 135
  assert tz.abbr == "CEST"
  assert tz._gmt_offset == +3600
  assert tz._has_dst == True
  assert tz.utcoffset(None).seconds == 7200

  tz_info: TzInfo = tzs.getTzInfo("CET")
  assert tz_info.utcoffset(datetime.datetime.now()) == datetime.timedelta(hours = 1)
  assert tz_info.dst(datetime.datetime.now()) == datetime.timedelta(0)

  tz_info = tzs.getTzInfo("CEST")
  assert tz_info.utcoffset(datetime.datetime.now()) == datetime.timedelta(hours = 2)
  assert tz_info.dst(datetime.datetime.now()) == datetime.timedelta(hours = 1)

  assert tzs.getTimezone("Europe/bsa", 1562853025) == None
  assert tzs.getTzInfo("GNT") == None


  assert tzs._getRawTzOffset("+1000").utcoffset(None).total_seconds() == 10*3600
  assert tzs._getRawTzOffset("-1000").utcoffset(None).total_seconds() == -10*3600
  assert tzs._getRawTzOffset("+0145").utcoffset(None).total_seconds() == 3600+45*60
  assert tzs._getRawTzOffset("-0145").utcoffset(None).total_seconds() == -3600-45*60