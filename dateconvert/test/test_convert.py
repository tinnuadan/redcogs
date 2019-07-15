from ..src import dthandling
from ..src import convert
from ..src import utils
from ..src.timezones import Timezones, Timezone, TzInfo
import datetime
from .helpers import getTimezones



def test_convert():
  tzs = getTimezones()
  time = dthandling.TimeObj(12,0,0)
  date = dthandling.DateObj(2019,7,14)

  tzinfo = tzs.getTzInfo("CEST")
  convert_from = convert.ConvertFrom(date, time, tzinfo)

  dest_tz = tzs.getTimezone("America/New_York", utils.toUnixTime(convert_from.toDateTime()))

  convert_res = convert.convert(convert_from, dest_tz)

  assert convert_res.date.year == 2019
  assert convert_res.date.month == 7
  assert convert_res.date.day == 14
  assert convert_res.time.hour == 6
  assert convert_res.time.minute == 0
  assert convert_res.time.second == 0

  time = dthandling.TimeObj(4,0,0)
  convert_res = convert.convert(convert.ConvertFrom(None, time, tzinfo), dest_tz)
  assert convert_res.date == None
  assert convert_res.time.hour == 22
  assert convert_res.time.minute == 0
  assert convert_res.time.second == 0
  assert convert_res.dayShift == -1

  dest_tz = tzs.getTimezone("Australia/Brisbane", utils.toUnixTime(convert_from.toDateTime()))

  time = dthandling.TimeObj(18,0,0)
  convert_res = convert.convert(convert.ConvertFrom(None, time, tzinfo), dest_tz)
  assert convert_res.date == None
  assert convert_res.time.hour == 2
  assert convert_res.time.minute == 0
  assert convert_res.time.second == 0
  assert convert_res.dayShift == 1
