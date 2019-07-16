from ..src import timezones

_tzs: timezones.Timezones = None


def getTimezones():
  global _tzs
  if _tzs == None:
    _tzs = timezones.Timezones()
  return _tzs



