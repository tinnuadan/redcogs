import copy
import datetime
import enum
import re
from typing import List, Dict
from .timezones import Timezone, Timezones, TzInfo
from .error import Error, ParsingError, TimezoneNotFoundError
from .utils import toUnixTime
from . import dthandling
from . import convert


class MessageProcessor:
  _reDate: re.Pattern = re.compile(r'^([0-3]?[0-9])(?:\/|\.)([0-3]?[0-9])(?:\/|\.)(\d{2}|\d{4})$')
  _reTime: re.Pattern = re.compile(r'^([0-2]?\d)(?::([0-5]\d))?(?::([0-5]\d))?$')
  _reUTC: re.Pattern = re.compile(r'^(\d{4})-([0-1]\d)-([0-3]\d)T([0-2]\d):([0-5]\d):([0-5]\d)([A-Z]+|(?:(?:\+|-)[0-1]\d{1}:?\d{2}))$')
  _re_ampm_missingSpace: re.Pattern = re.compile(r'[^ ]([aA]\.?[mM]|[pP]\.?[mM])')

  def __init__(self, tzs: Timezones = None):
    if tzs:
      self.tzs = tzs
    else:
      self.tzs = Timezones()

  def extractDateTime(self, msg: str, usertzid: int = None):
    msg = msg.strip()
    orig = self._getDateTime(msg, usertzid)
    if not orig:
      raise ParsingError("Unable to extract date and/or time.")
    return orig

  def convertDateTime(self, orig: convert.ConvertFrom, totimezoneIDs: List):
    result = []
    unixorig = toUnixTime(orig.toDateTime())
    for tzid in totimezoneIDs:
      tz = self.tzs.getTimezone(tzid, unixorig)
      if not tz:
        raise TimezoneNotFoundError("Timezone %s not found" % tzid)
      res = convert.convert(orig, tz)
      #print(res)
      result.append(res)
    return result

  def _getDateTime(self, msg, usertzid: int):
    #is maybe the current time requested?
    if msg == "now":
      return self._getNow()
    #try for utc first
    res: convert.ConvertFrom = self._tryUTC(msg)
    if res:
      return res
    #go down the more elaborate route...
    msg = copy.deepcopy(msg)
    match = MessageProcessor._re_ampm_missingSpace.match(msg)
    if match: #am/pm with without space in front
      fnd = match.group(1)
      msg = msg.replace(fnd, " %s" % fnd)

    parts = msg.split(' ') # split on spaces

    match = MessageProcessor._reDate.match(parts[0])
    date = None
    if match:
      #we have a date
      data = list(map(lambda x: int(x), match.groups()))
      date = dthandling.getDate(match.group(0), data)
      del parts[0]
    
    match = MessageProcessor._reTime.match(parts[0])
    time = None
    if match:
      #we have a time
      data = list(map(lambda x: int(x), match.groups('0')))
      ampm: str = None if len(parts) == 1 else parts[1]
      if ampm != None:
        ampm = ampm.lower().replace(".","")
        if ampm not in ["am","pm"]:
          ampm = None
      time = dthandling.getTime(data, ampm)

    if not time and not date:
      raise ParsingError("Unable to extract date and/or time.")
    if not time:
      time = dthandling.getMidnight()

    tz = self._getTzInfo(parts[-1].upper())
    tz_set = tz!=None
    if tz == None and usertzid != None:
      tdate: datetime.date = date if date else dthandling.getToday()
      tz = self.tzs.getTimezoneByID(usertzid, toUnixTime( datetime.datetime(tdate.year, tdate.month, tdate.day, tzinfo = TzInfo.Construct(0, False))))
    if not tz:
      print("No timezone for %s found and now timezone was set" % parts[-1].upper())
      raise TimezoneNotFoundError("No timezone for %s found and now timezone was set" % parts[-1].upper())

    return convert.ConvertFrom(date, time, tz, tz_set)


  def _getTzInfo(self, identifier: str):
    tz_str = identifier.replace(":","")
    
    tz = self.tzs.getTzInfo(tz_str)
    return tz


  def _tryUTC(self, msg: str):
    result: convert.ConvertFrom = None
    msg = msg.upper()
    match = MessageProcessor._reUTC.match(msg)
    if match:
      tz = self._getTzInfo(match.group(7))
      if tz == None:
        raise TimezoneNotFoundError("No valid timezone found")
      data = list(map(lambda x: int(x), match.group(1, 2, 3, 4, 5, 6)))
      
      date = dthandling.getDate("%04i-%02i-%02i" % tuple(data[0:3]), data[0:3])
      time = dthandling.getTime(data[3:6], None)

      result = convert.ConvertFrom(date, time, tz, True)
    return result

  def _getNow(self) -> convert.ConvertFrom:
    tz = self._getTzInfo("UTC")
    now = datetime.datetime.now(tz)
    date = dthandling.DateObj(now.year, now.month, now.day)
    time = dthandling.TimeObj(now.hour, now.minute, now.second)
    return convert.ConvertFrom(date, time, tz, True)






