from ..src import dthandling
from ..src import convert
from ..src.timezones import Timezones, Timezone, TzInfo
import datetime

_tzs = Timezones()

def testToUTC():
  global _tzs
  tzinfo = _tzs.getTzInfo("CEST")
  dt = datetime.datetime(2019, 7, 14, 12, 0,0, 0, tzinfo)
  assert convert._toUnixTime(dt) == 1563098400

def test_convert():
  global _tzs
  time = dthandling.TimeObj(12,0,0)
  date = dthandling.DateObj(2019,7,14)
  tzinfo = _tzs.getTzInfo("CEST")
  dfrom = datetime.datetime(date.year, date.month, date.day, time.hour, time.minute, time.second, 0, tzinfo)
  desttz = _tzs.getTimezone("America/New_York", convert._toUnixTime(dfrom))
  res = convert.convert(convert.ConvertFrom(date, time, tzinfo), desttz)
  print(res)
  print(convert.ConvertFrom(date, time, tzinfo))

  time = dthandling.TimeObj(4,0,0)
  date = dthandling.DateObj(2019,7,14)
  res = convert.convert(convert.ConvertFrom(None, time, tzinfo), desttz)
  print(res)
  print(convert.ConvertFrom(None, time, tzinfo))