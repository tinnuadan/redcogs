from redbot.core import Config, commands
import typing
import datetime
from .process_message import MessageProcessor
from .timezones import Timezones, Timezone
from .utils import toUnixTime
from . import convert


async def get_user_tzid(ctx: commands.Context, cfg: Config):
  """ tries to find's the users timezone id, returns None if none is set """
  id = await cfg.user(ctx.message.author).usertz()
  return id

async def get_user_tz(ctx: commands.Context, cfg: Config, tzs: Timezones):
  """ tries to find's the users timezone and displays it to the user """
  id = await get_user_tzid(ctx, cfg)
  if id:
    tz: Timezone = tzs.getTimezoneByID(id, 0)
    return f"Your timezone is **{tz.zone_name}**."
  else:
    return f"Your don't have a timezone set."

async def set_user_tz(ctx: commands.Context, cfg: Config, tzs: Timezones, name: str):
  """ tries to set's the users timezone, sends an error if the identifer is not found """
  if name.lower() == "clear":
    await cfg.user(ctx.message.author).usertz.set(None)
    return f"Successfully cleared your timezone."

  id = tzs.getTzID(name)
  if not id:
    return "Unrecognized timezone. Try `tz set Continent/City`: see <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>"
  else:
    tz: Timezone = tzs.getTimezoneByID(id, 0)
    await cfg.user(ctx.message.author).usertz.set(id)
    return f"Successfully set your timezone to **{tz.zone_name}**."



