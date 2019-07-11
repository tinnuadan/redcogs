import json
import sqlite3
from ..src.timezones import Timezones, Timezone


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
  assert tz.gmt_offset == +7200
  assert tz.dst == True

