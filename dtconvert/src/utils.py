import datetime
from .timezones import TzInfo


def toUnixTime(dt: datetime.datetime):
  utc = TzInfo.Construct(0, False)
  return int((dt - datetime.datetime(1970,1,1, tzinfo = utc)).total_seconds())

def toAmPm(hour: int):
  ampm: str = "am"
  h: int = hour
  if hour > 12:
    h -= 12
    ampm = "pm"
  elif hour == 12:
    ampm = "pm"
  elif hour == 0:
    h = 12
  return (h, ampm)
