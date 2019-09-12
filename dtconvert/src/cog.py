from redbot.core import Config, commands
import discord
import typing
import datetime
from .process_message import MessageProcessor
from .timezones import Timezones
from . import convert
from . import error
from . import utils
from . import usercfg

class DTConvertCog(commands.Cog):
  """Converts date and time to different timezones"""

  def __init__(self):
    # load all the timezones on init
    self._tzs: Timezones = Timezones()
    self._mp: MessageProcessor = MessageProcessor(self._tzs)
    #todo: load ids from settings
    self._timezoneids = ["UTC","America/Los_Angeles", "America/New_York","Europe/London","Europe/Berlin","Australia/Hobart","Pacific/Auckland"]
    self._config = Config.get_conf(self, 83576746, force_registration=True)
    default_user = {"usertz": None}
    self._config.register_user(**default_user)


  @commands.command()
  async def tz(self, ctx, *, datetime):
    msg = await self._tz(ctx, datetime)
    await ctx.send(msg)

  @commands.command()
  async def t(self, ctx, *, datetime):
    msg = await self._tz(ctx, datetime) 
    await ctx.send(msg)

  async def _tz(self, ctx, datetime):
    """Converts date and time to multiple timezones"""
    txt = datetime.strip()
    msg: str = None
    if txt == "help":
      msg = self._help()
    elif txt == "tz":
      msg = self._avtzs()
    elif txt[0:2] == "me":
      tmp = txt.split(" ")
      if len(tmp) == 1:
        msg = await usercfg.get_user_tz(ctx, self._config, self._tzs)
      elif len(tmp) == 2:
        msg = await usercfg.set_user_tz(ctx, self._config, self._tzs, tmp[1])
      else:
        msg = "Error in syntax. Try `!tz me [timezone]` to view or set your timezone"
    else:
      try:
        tzid = await usercfg.get_user_tzid(ctx, self._config)
        msg = self._doConversion(txt, tzid)
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

  def _doConversion(self, msg, tzid: int):
    orig: convert.ConvertFrom = self._mp.extractDateTime(msg, tzid)
    tzids = list(self._timezoneids)
    if tzid and not orig.tz_set_explictly:
      tzinfo = self._tzs.getTimezoneByID(tzid, 0)
      print(tzinfo.zone_name)
      if tzinfo:
        tzids.insert(0, tzinfo.zone_name)
    elif tzid and orig.tz_set_explictly:
      tzinfo = self._tzs.getTimezoneByID(tzid, 0)
      print(tzinfo.zone_name)
      if tzinfo:
        tzids.append(tzinfo.zone_name)
    
    converted = self._mp.convertDateTime(orig, tzids)
    
    dnow = datetime.datetime.now()
    convutc = converted[0]
    converted = sorted(converted[1:], key = lambda x: x.tzinfo.utcoffset(dnow))
    converted.insert(0, convutc)

    lines = []
    line0 = None
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
      if not line0:
        line0 = line
        lines.append(line)
        if not orig.tz_set_explictly:
          lines.append("---")
      if line not in lines:
        lines.append(line)
    return "```HTTP\n%s```" % ("\n".join(lines))
      
