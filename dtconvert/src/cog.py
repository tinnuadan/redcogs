from time import timezone
from redbot.core import Config, commands, checks
import discord
from typing import Optional
import datetime
from .process_message import MessageProcessor
from .timezones import Timezones, Timezone, TzInfo
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
    self._timezoneids = []
    self._config = Config.get_conf(self, 83576746, force_registration=True)
    default_user = {"usertz": None}
    default_guild = {"timezones": ["America/Los_Angeles", "America/New_York","Europe/London","Europe/Berlin","Australia/Hobart","Pacific/Auckland"], "usertimezones": False, "showutc": True}
    self._config.register_user(**default_user)
    self._config.register_guild(**default_guild)


  @commands.command()
  async def tz(self, ctx, *, datetime):
    msg = await self._tz(ctx, datetime)
    msg = msg.replace("[p]", ctx.clean_prefix)
    await ctx.send(msg)

  @commands.command()
  async def t(self, ctx, *, datetime):
    msg = await self._tz(ctx, datetime)
    msg = msg.replace("[p]", ctx.clean_prefix)
    await ctx.send(msg)


  @commands.group(name="dtconvert")
  @commands.guild_only()
  @checks.mod_or_permissions(manage_messages=True)
  async def dtconvert(self, ctx: commands.Context) -> None:
    """
        Settings for dtconvert
    """
    pass

  @dtconvert.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def showutc(self, ctx, enable: Optional[bool] = None):
    """
        Show UTC in the results
    """
    if enable != None:
      await self._config.guild(ctx.guild).showutc.set(enable)
      await ctx.send(f"Show UTC in the results was set to: {enable}")
    else:
      enable = await self._config.guild(ctx.guild).showutc()
      await ctx.send(f"Show UTC in the results is set to: {enable}")

  @dtconvert.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def usertimezones(self, ctx, enable: Optional[bool] = None):
    """
        Allow users to set their timezone
    """
    if enable != None:
      await self._config.guild(ctx.guild).usertimezones.set(enable)
      await ctx.send(f"Allow users to set their timezone was set to: {enable}")
    else:
      enable = await self._config.guild(ctx.guild).usertimezones()
      await ctx.send(f"Allow users to set their timezone is set to: {enable}")

  @dtconvert.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def list(self, ctx):
    """
        List timezones to convert to
    """
    timezones = await self._config.guild(ctx.guild).timezones()
    msg = []
    for i in range(0, len(timezones)):
      msg.append(f"{i:2d}: {timezones[i]}")
    await ctx.send("\n".join(msg))


  @dtconvert.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def remove(self, ctx, id: int):
    """
        Removes a timezone from the list
    """
    timezones = await self._config.guild(ctx.guild).timezones()
    if id < 0 or id >= len(timezones):
      await ctx.send(f"ID {id} out of range")
      return
    to_delete = timezones[id]
    del timezones[id]
    await self._config.guild(ctx.guild).timezones.set(timezones)
    self._timezoneids.clear()
    await ctx.send(f"Timezone \"{to_delete}\" was removed")

  @dtconvert.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def add(self, ctx, timezone):
    """
        Add timezone to the list
    """
    timezones = await self._config.guild(ctx.guild).timezones()
    tz: Timezone = self._tzs.getTimezone(timezone.replace(" ","_"), 0)
    if not tz:
      await ctx.send(f"{timezone} not found")
      return
    if tz.zone_name in timezones:
      await ctx.send(f"{tz.zone_name} already included")
      return
    timezones.append(tz.zone_name)
    timezones = self._order_timezones(timezones)
    await self._config.guild(ctx.guild).timezones.set(timezones)
    self._timezoneids.clear()
    await ctx.send(f"{tz.zone_name} added")

  def _order_timezones(self, timezones):
    to_order = dict()
    result = []
    for tz_name in timezones:
      print(tz_name)
      tz:Timezone = self._tzs.getTimezone(tz_name, 0)
      to_order[tz.zone_name] = tz.utcoffset(False)
    #sort by utc offset
    to_order = sorted(to_order, key=to_order.__getitem__)
    for tz in to_order:
      result.append(tz)
    return result



  async def _tz(self, ctx, datetime):
    """Converts date and time to multiple timezones"""
    usertimezones = await self._config.guild(ctx.guild).usertimezones()
    if len(self._timezoneids) == 0:
      showutc = await self._config.guild(ctx.guild).showutc()
      self._timezoneids = await self._config.guild(ctx.guild).timezones()
      if showutc:
        self._timezoneids.insert(0, "UTC")
    txt = datetime.strip()
    msg: str = None
    if txt == "help":
      msg = self._help()
    elif txt == "tz":
      msg = self._avtzs()
    elif txt[0:2] == "me":
      if not usertimezones:
        return "Personal timezones are not enabled"
      tmp = txt.split(" ")
      if len(tmp) == 1:
        msg = await usercfg.get_user_tz(ctx, self._config, self._tzs)
      elif len(tmp) == 2:
        msg = await usercfg.set_user_tz(ctx, self._config, self._tzs, tmp[1])
      else:
        msg = "Error in syntax. Try `[p]tz me <timezone>` to view or set your timezone"
    else:
      try:
        tzid = await usercfg.get_user_tzid(ctx, self._config)
        msg = self._doConversion(txt, tzid)
      except error.TimezoneNotFoundError:
        msg = "The timezone identifier was not found. Please have a look at `[p]tz tz` for valid identifiers."
      except error.ParsingError:
        msg = "Unable to extract date and/or time. Please have a look at `[p]tz help` for help on formatting."
      except error.DateError as e:
        msg = str(e)
      except error.TimeError as e:
        msg = str(e)
      except error.Error:
        msg = "Uh oh, something went wrong."

    return msg


  def _help(self):
    msg = """Convert a date and time or only a time with:
`[p]tz [<date>] <time> <timezone>`.
`<date>` can be either `dd.mm.[yy]yy` or `mm/dd/[yy]yy` or omitted totally.
`<time>` can be `hh[:mm] [am/pm]`. If am or pm is not specified, the 24h clock will be used.
`<timezone>` should be the abbreviation like "EDT" or "CEST", an identifier such as America/New York, or an UTC offset like "+1000" / "+10:00". For possible values please use `[p]tz tz`.
You can also specifiy everything according to ISO 8601: `[p]tz yyyy-mm-ddThh:mm:ss+hh:mm`."""
    return msg

  def _avtzs(self):
    av = self._tzs.getAvailableAbbreviations()
    av = ", ".join(av)
    msg = "Available timezone abbreviations:\n`%s`\nSee also <https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations> and <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>" % av
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
      
