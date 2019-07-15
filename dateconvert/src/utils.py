import datetime
from .timezones import TzInfo


def toUnixTime(dt: datetime.datetime):
  utc = TzInfo.Construct(0, False)
  return int((dt - datetime.datetime(1970,1,1, tzinfo = utc)).total_seconds())
