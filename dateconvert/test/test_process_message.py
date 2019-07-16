from ..src import process_message
from ..src import convert
from ..src.error import Error

_mp = process_message.MessageProcessor()

def test_getISO():
  global _mp
  mp: process_message.MessageProcessor = _mp

  res: convert.ConvertFrom = mp._tryUTC("2019-07-14T12:03:11CEST")
  assert res.date.year == 2019
  assert res.date.month == 7
  assert res.date.day == 14
  assert res.time.hour == 12
  assert res.time.minute == 3
  assert res.time.second == 11
  assert res.tzinfo.utcoffset(None).total_seconds() == 7200 # CEST
  assert res.tzinfo._has_dst == True # CEST

  try:
    mp._tryUTC("2019-07-14T12:03:11Foo") #invalid timezone
    assert False
  except Error:
    assert True

  assert mp._tryUTC("2019-07-14X12:03:11EDT") == None# no iso

  res: convert.ConvertFrom = mp._tryUTC("2019-07-14T12:03:11-0200")
  assert res.date.year == 2019
  assert res.date.month == 7
  assert res.date.day == 14
  assert res.time.hour == 12
  assert res.time.minute == 3
  assert res.time.second == 11
  assert res.tzinfo.utcoffset(None).total_seconds() == -7200 # UTC offset
  assert res.tzinfo._has_dst == False # plain offset


def test_getDateTime():
  global _mp
  mp: process_message.MessageProcessor = _mp
  
  res: convert.ConvertFrom = mp._getDateTime("2019-07-14T12:03:11CEST") #iso
  assert res.date.year == 2019
  assert res.date.month == 7
  assert res.date.day == 14
  assert res.time.hour == 12
  assert res.time.minute == 3
  assert res.time.second == 11
  assert res.tzinfo.utcoffset(None).total_seconds() == 7200 # CEST
  assert res.tzinfo._has_dst == True # CEST

  res: convert.ConvertFrom = mp._getDateTime("14.07.19 12:03:11 CEST") #non iso
  assert res.date.year == 2019
  assert res.date.month == 7
  assert res.date.day == 14
  assert res.time.hour == 12
  assert res.time.minute == 3
  assert res.time.second == 11
  assert res.tzinfo.utcoffset(None).total_seconds() == 7200 # CEST
  assert res.tzinfo._has_dst == True # CEST
  
  res: convert.ConvertFrom = mp._getDateTime("14.07.19 12:03 EDT") # hh:m
  assert res.date.year == 2019
  assert res.date.month == 7
  assert res.date.day == 14
  assert res.time.hour == 12
  assert res.time.minute == 3
  assert res.time.second == 0
  assert res.tzinfo.utcoffset(None).total_seconds() == -14400 # EDT
  assert res.tzinfo._has_dst == True # EDT
  
  res: convert.ConvertFrom = mp._getDateTime("14.07.19 12 EDT") # only h
  assert res.date.year == 2019
  assert res.date.month == 7
  assert res.date.day == 14
  assert res.time.hour == 12
  assert res.time.minute == 0
  assert res.time.second == 0
  assert res.tzinfo.utcoffset(None).total_seconds() == -14400 # EDT
  assert res.tzinfo._has_dst == True # EDT
  
  res: convert.ConvertFrom = mp._getDateTime("07/14/2019 9 pm EDT") # only h
  assert res.date.year == 2019
  assert res.date.month == 7
  assert res.date.day == 14
  assert res.time.hour == 21
  assert res.time.minute == 0
  assert res.time.second == 0
  assert res.tzinfo.utcoffset(None).total_seconds() == -14400 # EDT
  assert res.tzinfo._has_dst == True # EDT
  
  res: convert.ConvertFrom = mp._getDateTime("07/14/2019 9 p.m EDT") # only h
  assert res.date.year == 2019
  assert res.date.month == 7
  assert res.date.day == 14
  assert res.time.hour == 21
  assert res.time.minute == 0
  assert res.time.second == 0
  assert res.tzinfo.utcoffset(None).total_seconds() == -14400 # EDT
  assert res.tzinfo._has_dst == True # EDT
  
  res: convert.ConvertFrom = mp._getDateTime("07/14/2019 9 a.m. EDT") # only h
  assert res.date.year == 2019
  assert res.date.month == 7
  assert res.date.day == 14
  assert res.time.hour == 9
  assert res.time.minute == 0
  assert res.time.second == 0
  assert res.tzinfo.utcoffset(None).total_seconds() == -14400 # EDT
  assert res.tzinfo._has_dst == True # EDT
  
  res: convert.ConvertFrom = mp._getDateTime("07/14/2019 9 am EDT") # only h
  assert res.date.year == 2019
  assert res.date.month == 7
  assert res.date.day == 14
  assert res.time.hour == 9
  assert res.time.minute == 0
  assert res.time.second == 0
  assert res.tzinfo.utcoffset(None).total_seconds() == -14400 # EDT
  assert res.tzinfo._has_dst == True # EDT
  
  res: convert.ConvertFrom = mp._getDateTime("9 am EDT") # only time
  assert res.date == None
  assert res.time.hour == 9
  assert res.time.minute == 0
  assert res.time.second == 0
  assert res.tzinfo.utcoffset(None).total_seconds() == -14400 # EDT
  assert res.tzinfo._has_dst == True # EDT
  
  res: convert.ConvertFrom = mp._getDateTime("12:10 am +01:00") # only time
  assert res.date == None
  assert res.time.hour == 0
  assert res.time.minute == 10
  assert res.time.second == 0
  assert res.tzinfo.utcoffset(None).total_seconds() == 3600
  assert res.tzinfo._has_dst == False


def test_getDateTimeFailures():
  global _mp
  mp: process_message.MessageProcessor = _mp
  
  try:
    mp._getDateTime("07/14.2019 9am EDT")
    assert False
  except Error:
    assert True
    
  try:
    mp._getDateTime("07/14/2019 9am +012")
    assert False
  except Error:
    assert True
    
  try:
    mp._getDateTime("9am EDT")
    assert False
  except Error:
    assert True

def test_api():
  global _mp
  mp: process_message.MessageProcessor = _mp
  orig = mp.extractDateTime("07/14/2019 09:00:00 EDT")
  conv = mp.convertDateTime(orig, ["America/Los_Angeles", "Europe/Berlin"])
  assert len(conv) == 2
  assert conv[0].time.hour == 6
  assert conv[0].timezone.abbr == "PDT"
  assert conv[1].time.hour == 15
  assert conv[1].timezone.abbr == "CEST"
  
  #make sure 'orig' is not altered
  orig = mp.extractDateTime("09 am EDT")
  conv = mp.convertDateTime(orig, ["America/Los_Angeles", "Europe/Berlin"])
  assert len(conv) == 2
  assert conv[0].date == None
  assert conv[1].date == None

