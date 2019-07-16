
class Error(Exception):
  pass

class TimezoneNotFoundError(Error):
  pass

class TimezoneAbbreviationNotFoundError(Error):
  pass

class ParsingError(Error):
  pass