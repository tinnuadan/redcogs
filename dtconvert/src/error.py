
class Error(Exception):
  pass

class TimezoneNotFoundError(Error):
  pass

class TimezoneAbbreviationNotFoundError(Error):
  pass

class ParsingError(Error):
  pass

class DateError(Error):
  pass

class TimeError(Error):
  pass