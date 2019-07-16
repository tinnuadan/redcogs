#from ..src.dthandling import getDate, getMidnight, getTime, getToday, _
from ..src import dthandling
from ..src.error import Error
import datetime

def test_helper():
  mid = dthandling.getMidnight()
  assert mid.hour == 0
  assert mid.minute == 0
  assert mid.second == 0

  td_gt = datetime.date.today()
  td = dthandling.getToday()
  assert td.year == td_gt.year
  assert td.month == td_gt.month
  assert td.day == td_gt.day

  assert not dthandling._inRange(0, 1, 20)
  assert dthandling._inRange(1, 1, 20)
  assert dthandling._inRange(20, 1, 20)
  assert not dthandling._inRange(21, 1, 20)

  assert dthandling._isLeapYear(1996)
  assert not dthandling._isLeapYear(1900)
  assert dthandling._isLeapYear(2000)

def test_date():
  #good cases:
  date: dthandling.DateObj = None
  date = dthandling.getDate("05/06/2019", [5,6,2019])
  assert date.year == 2019
  assert date.month == 5
  assert date.day == 6

  date = dthandling.getDate("05.06.2019", [5,6,2019])
  assert date.year == 2019
  assert date.month == 6
  assert date.day == 5

  date = dthandling.getDate("05/06/19", [5,6,19])
  assert date.year == 2019
  assert date.month == 5
  assert date.day == 6

  date = dthandling.getDate("05.06.19", [5,6,19])
  assert date.year == 2019
  assert date.month == 6
  assert date.day == 5

  # bad cases:
  try:
    date = dthandling.getDate("31.06.19", [31,6,19])
  except Error:
    assert True

  try:
    date = dthandling.getDate("00.06.19", [0,6,19])
    assert False #should not be reached
  except Error:
    assert True

  try:
    date = dthandling.getDate("28.02.19", [28,2,19])
    assert date.day == 28
  except Error:
    assert False

  try:
    date = dthandling.getDate("29.02.19", [29,2,19])
    assert False #should not be reached
  except Error:
    assert True

  try:
    date = dthandling.getDate("29.02.19", [29,2,20])
    assert date.day == 29
  except Error:
    assert False

  try:
    date = dthandling.getDate("01.00.19", [1,13,19])
    assert False #should not be reached
  except Error:
    assert True
  try:
    date = dthandling.getDate("01.13.19", [1,13,19])
    assert False #should not be reached
  except Error:
    assert True

def test_time():
  time: dthandling.TimeObj = None

  #good cases
  time = dthandling.getTime([13,34,26], None)
  assert time.hour == 13
  assert time.minute == 34
  assert time.second == 26

  time = dthandling.getTime([13], None)
  assert time.hour == 13
  assert time.minute == 0
  assert time.second == 0
  time = dthandling.getTime([13, 45], None)

  assert time.hour == 13
  assert time.minute == 45
  assert time.second == 0

  time = dthandling.getTime([11,34,26], "am")
  assert time.hour == 11
  assert time.minute == 34
  assert time.second == 26

  time = dthandling.getTime([12], "am")
  assert time.hour == 0

  time = dthandling.getTime([12], "pm")
  assert time.hour == 12

  time = dthandling.getTime([1], "pm")
  assert time.hour == 13

  #bad cases
  try:
    dthandling.getTime([13], "pm")
    assert False #should never be reached
  except Error:
    assert True

  try:
    dthandling.getTime([-1], None)
    assert False #should never be reached
  except Error:
    assert True

  try:
    dthandling.getTime([24], None)
    assert False #should never be reached
  except Error:
    assert True

  try:
    dthandling.getTime([10, -1], None)
    assert False #should never be reached
  except Error:
    assert True

  try:
    dthandling.getTime([10, 60], None)
    assert False #should never be reached
  except Error:
    assert True

  try:
    dthandling.getTime([10, 0, -1], None)
    assert False #should never be reached
  except Error:
    assert True

  try:
    dthandling.getTime([10, 0, 60], None)
    assert False #should never be reached
  except Error:
    assert True