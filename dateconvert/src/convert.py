from typing import List, Dict
from . import dthandling
from . import timezones
import datetime

class ConvertBase():
  def __init__(self, date: dthandling.DateObj, time: dthandling.TimeObj, tzinfo: timezones.TzInfo):
    self.date: dthandling.DateObj = date
    self.time: dthandling.TimeObj = time
    self.tzinfo: timezones.TzInfo = tzinfo

  def canConvertToDateTime(self):
    return self.date != None

  def toDateTime(self):
    if not self.date:
      return None
    return datetime.datetime(self.date.year, self.date.month, self.date.day, self.time.hour, self.time.minute, self.time.second, 0, self.tzinfo)

  def _utcStr(self):
    utcoff = self.tzinfo.utcoffset(None).total_seconds()
    tzhours = int(utcoff/3600)
    tzminutes = abs(int((utcoff%3600)/60))
    return "%+03i:%02i" % (tzhours, tzminutes)

class ConvertFrom(ConvertBase):
  def __init__(self, date: dthandling.DateObj, time: dthandling.TimeObj, tzinfo: timezones.TzInfo):
    ConvertBase.__init__(self, date, time, tzinfo)

  def __str__(self):
    dateStr = ""
    date = self.date
    time = self.time
    if date:
      dateStr = "%4i-%02i-%02i " % (date.year, date.month, date.day)
    return "%s%02i:%02i:%02i%s" % (dateStr, time.hour, time.minute, time.second, self._utcStr())

class ConvertTo(ConvertBase):
  def __init__(self, date: dthandling.DateObj, time: dthandling.TimeObj, tzinfo: timezones.TzInfo):
    ConvertBase.__init__(self, date, time, tzinfo)
    self.dayShift = 0

  @staticmethod
  def fromDatetime(dt: datetime.datetime, tzinfo: timezones.Timezone):
    date = dthandling.DateObj(dt.year, dt.month, dt.day)
    time = dthandling.TimeObj(dt.hour, dt.minute, dt.second)
    return ConvertTo(date, time, tzinfo)

  def __str__(self):
    date = self.date
    time = self.time
    if date != None:
      return "%4i-%02i-%02i %02i:%02i:%02i%s" % (date.year, date.month, date.day, time.hour, time.minute, time.second, self._utcStr())
    else:
      return "%02i:%02i:%02i%+s %+i day" % (time.hour, time.minute, time.second, self._utcStr(), self.dayShift)

def convert(cfrom: ConvertFrom, desttz: timezones.Timezone):
  #easy, we have time & date:
  if cfrom.canConvertToDateTime():
    dfrom: datetime.datetime  = cfrom.toDateTime()
    dto = dfrom.astimezone(desttz)
    return ConvertTo.fromDatetime(dto, desttz)

  #otherwise, we just would like to have a possible day shift
  cfrom.date = dthandling.getToday()
  dfrom: datetime.datetime  = cfrom.toDateTime()
  dto = dfrom.astimezone(desttz)
  res = ConvertTo.fromDatetime(dto, desttz)
  res.date = None
  #get day shift
  if dto.day != dfrom.day:
    dfromInDest = ConvertFrom(cfrom.date, cfrom.time, desttz).toDateTime() # treat the original date as it would be in the same tz as the destination
    direction = (dto - dfromInDest).total_seconds()
    res.dayShift = 1 if direction > 0 else -1
  
  return res