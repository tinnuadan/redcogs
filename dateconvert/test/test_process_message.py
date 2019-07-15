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
    mp._tryUTC("2019-07-14T12:03:11FOO")
    assert False
  except Error:
    assert True
