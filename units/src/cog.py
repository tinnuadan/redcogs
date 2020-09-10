from redbot.core import commands, VersionInfo, version_info
import discord
import traceback
from .process_message import MessageProcessor, ConversionResult
from .convert_units.converter import loadConversionsData
from .error import Error

class UnitCog(commands.Cog):
  """Searches for units in a message and tries to convert them from metric to imperial and vice versa"""

  def __init__(self, bot):
    # load data
    loadConversionsData()
    self.bot = bot
    _ = MessageProcessor()

  @commands.command()
  async def convert(self, ctx, *, txt):
    """Do the conversion"""
    msg = await self._convert(txt, None)
    if msg:
      await ctx.send(msg)
   

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
    """Request a conversion by reaction"""
    if version_info >= VersionInfo.from_str("3.2.0"):
      await self.bot.wait_until_red_ready()
    else:
      await self.bot.wait_until_ready()
    channel = self.bot.get_channel(id=payload.channel_id)
    if not channel:
      return
    try:
      guild = channel.guild
    except AttributeError:
      return
    if guild is None:
      return
    reacted_user = guild.get_member(payload.user_id)
    if reacted_user.bot:
        return
    try:
      message: discord.Message = await channel.fetch_message(id=payload.message_id)
    except (discord.errors.NotFound, discord.Forbidden):
      return

    if str(payload.emoji) != "⚙️":
      print(str(payload.emoji))
      return

    msg = await self._convert(message.content, reacted_user)
    if msg:
      await channel.send(msg)

  async def _convert(self, txt: str, user: discord.Member = None):
    mp: MessageProcessor = MessageProcessor()
    try:
      result = mp.processMessage(txt)      
      if isinstance(result, str):
        return result
      elif len(result) > 0:
        tmp = []
        for t in result:
          cr: ConversionResult = t
          tmp.append("%s = %s" % (cr.orig, cr.conv))
        answer = "%s" % ", ".join(tmp)
        if user:
          answer = f"{answer}\nRequested by {user.display_name}"
        return answer
      else:
        print("No convertable units found in %s" % txt)
    except Error as e:      
      answer = "Error: %s" % e
      return answer
    except Exception as e:
      print("Exception was thrown while trying to process the message: %s" % e)
      traceback.print_exc()
    return None

