from .error import Error, DateError, TimeError
import enum
from typing import List, Dict
import datetime

_daysPerMonth = { 1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


class _DateNotation(enum.Enum):
  ISO = 0
  US = 1
  European = 2

class DateObj:
  def __init__(self, year: int, month: int, day: int):
    self.year: int = year
    self.month: int = month
    self.day: int = day

class TimeObj:
  def __init__(self, hour: int, minute: int, second: int):
    self.hour: int = hour
    self.minute: int = minute
    self.second: int = second

def _isLeapYear(year: int):
  return (year % 4 == 0) and (year % 100 != 0 or year % 400 == 0)

def _inRange(a, min, max):
  return a >= min and a <= max

def getToday():
  td = datetime.date.today()
  return DateObj(td.year, td.month, td.day)

def getMidnight():
  return TimeObj(0, 0, 0)

def getDate(fullmatch: str, data: List):
  #us or european notation?
  notation: _DateNotation = None
  if len(fullmatch.split(".")) == 3:
    notation = _DateNotation.European
  elif len(fullmatch.split("/")) == 3:
    notation = _DateNotation.US
  elif len(fullmatch.split("-")) == 3:
    notation = _DateNotation.ISO
  
  if notation == None:
    raise DateError("No valid date notation found for %s. Please use either dd.mm.yy(yy) or mm/dd/yy(yy)" % fullmatch)

  if notation == _DateNotation.ISO:
    year = data[0]
    month = data[1]
    day = data[2]
  else:
    year = data[2]
    month = data[1] if notation == _DateNotation.European else data[0]
    day = data[0] if notation == _DateNotation.European else data[1]

  if year < 100:
    year += 2000
  
  if not _inRange(month, 1, 12):
    raise DateError("Month %02i not valid" % month)
  
  dim = _daysPerMonth[month]
  if month == 2 and _isLeapYear(year):
    dim += 1
  if not _inRange(day, 1, dim):
    raise DateError("Day %02i not valid for month %02i" % (day,month))
  
  return DateObj(year, month, day)

def getTime(data: List, ampm: str):
  hour = data[0]
  minute = data[1] if len(data) > 1 else 0
  second = data[2] if len(data) > 2 else 0

  if ampm != None and not _inRange(hour, 1, 12):
    raise TimeError("Hour %02i not valid if am/pm is provided" % hour)
  elif not _inRange(hour, 0, 23):
    raise TimeError("Hour %02i not valid" % hour)
  
  if not _inRange(minute, 0, 59):
    raise TimeError("Minute %02i not valid" % minute)

  if not _inRange(second, 0, 59):
    raise TimeError("Second %02i not valid" % second)

  if ampm != None:
    if ampm == "am" and hour == 12: #midnight
      hour = 0
    elif ampm == "pm" and hour < 12: #after noon
      hour += 12

  return TimeObj(hour, minute, second)