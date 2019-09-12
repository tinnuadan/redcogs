from redbot.core import commands
import discord
import typing
from .process_message import MessageProcessor
from .timezones import Timezones
from . import convert
from . import error
from . import utils

class DTConvertCog(commands.Cog):
  """Converts date and time to different timezones"""

  def __init__(self):
    # load all the timezones on init
    self._tzs: Timezones = Timezones()
    self._mp: MessageProcessor = MessageProcessor(self._tzs)
    #todo: load ids from settings
    self._timezoneids = ["UTC","America/Los_Angeles", "America/New_York","Europe/London","Europe/Berlin","Australia/Hobart","Pacific/Auckland"]


  @commands.command()
  async def tz(self, ctx, *, datetime):
    msg = self._tz(ctx, datetime)
    await ctx.send(msg)

  @commands.command()
  async def t(self, ctx, *, datetime):
    msg = self._tz(ctx, datetime)
    await ctx.send(msg)

  def _tz(self, ctx, datetime):
    """Converts date and time to multiple timezones"""
    txt = datetime.strip()
    msg: str = None
    if txt == "help":
      msg = self._help()
    elif txt == "tz":
      msg = self._avtzs()
    else:
      try:
        msg = self._doConversion(txt)
      except error.TimezoneNotFoundError:
        msg = "The timezone identifier was not found. Please have a look at `!tz tz` for valid identifiers."
      except error.ParsingError:
        msg = "Unable to extract date and/or time. Please have a look at `!tz help` for help on formatting."
      except error.DateError as e:
        msg = str(e)
      except error.TimeError as e:
        msg = str(e)
      except error.Error:
        msg = "Uh oh, something went wrong."

    return msg


  def _help(self):
    msg = """Convert a date and time or only a time with:
`!tz [<date>] <time> <timezone>`.
`<date>` can be either `dd.mm.[yy]yy` or `mm/dd/[yy]yy` or omitted totally.
`<time>` can be `hh[:mm] [am/pm]`. If am or pm is not specified, the 24h clock will be used.
`<timezone>` should be the abbreviation like "EDT" or "CEST" or an UTC offset like "+1000" / "+10:00". For possible values please use `!tz tz`.
You can also specifiy everything according to ISO 8601: `!tz yyyy-mm-ddThh:mm:ss+hh:mm`."""
    return msg

  def _avtzs(self):
    av = self._tzs.getAvailableAbbreviations()
    av = ", ".join(av)
    msg = "Available timezone abbreviations:\n`%s`\nSee also <https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations>" % av
    return msg

  def _doConversion(self, msg):
    orig = self._mp.extractDateTime(msg)
    converted = self._mp.convertDateTime(orig, self._timezoneids)
    lines = []
    for conv in converted:
      date = conv.date
      time = conv.time
      line = ""
      if date:
        line = "%4i-%02i-%02i " % (date.year, date.month, date.day)
      ampm = utils.toAmPm(time.hour)
      line = "%s%02i:%02i (%2i:%02i %s) " % (line, time.hour, time.minute, ampm[0], time.minute, ampm[1])
      if not date:
        line = "%s%+i day " % (line, conv.dayShift)
      line = "%s%s " % (line, conv.timezone.abbr)
      lines.append(line)
    return "```HTTP\n%s```" % ("\n".join(lines))
      
