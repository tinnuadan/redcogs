import datetime
import re
from typing import List, Dict


class MessageProcessor:
  _reDate: re.Pattern = re.compile(r'^([0-3]?[0-9])(\/|\.)([0-3]?[0-9])(\/|\.)(\d{2}|\d{4})$')
  _reTime: re.Pattern = re.compile(r'^([0-2]\d)(?::([0-5]\d))?(?::([0-5]\d))?$')
  _reUTC: re.Pattern = re.compile(r'^(\d{4})-([0-1]\d)-([0-3]\d)T([0-2]\d):([0-5]\d):([0-5]\d)([A-Z]+|(?:(?:\+|-)[0-1]\d{1}:?\d{2}))$')


  def processMessage(self, msg):
    msg = msg.strip()
    #try for utc first
    

  def _tryUTC(self, msg):
    result: datetime.datetime = None
    match = MessageProcessor._reUTC.match(msg)
    if match:
      tz = match.group(6) # todo: get timezone
      data: List [ match.group(0), match.group(1), match.group(2), match.group(3), match.group(4), match.group(5)]
      data = list(map(lambda x: int(x)))
      result = datetime.datetime(data[0], data[1], data[2], data[3], data[4], data[5], 0, tz)
    return result




    


