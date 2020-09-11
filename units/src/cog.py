from redbot.core import commands, checks, Config, VersionInfo, version_info
import discord
import traceback
from typing import Optional
from .process_message import MessageProcessor, ConversionResult
from .convert_units.converter import loadConversionsData
from .error import Error
from .reply import Reply

class UnitCog(commands.Cog):
  """Searches for units in a message and tries to convert them from metric to imperial and vice versa"""

  def __init__(self, bot):
    # load data
    loadConversionsData()
    _ = MessageProcessor()
    self.bot = bot
    self.config = Config.get_conf(self, 0xdd227e37d7df40f780bcb9981ac91e26, force_registration=True)
    default_guild = { 'emoji' : "⚙️" }
    self.config.register_guild(**default_guild)
    self.cache = { 'emoji' : None }

  
  @commands.group(name="units")
  @commands.guild_only()
  @checks.mod_or_permissions(manage_messages=True)
  async def units(self, ctx: commands.Context) -> None:
    """
        Settings for unit conversions
    """
    pass

  @units.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def emoji(self, ctx, emoji: Optional[str] = None,):
    """
        Gets or sets the emoji used for reaction-triggered conversion
    """
    if not emoji:
      val = await self._getConfig(ctx.guild, "emoji")
      repl = Reply.CreateEmbed(f"Emoji used for reaction-triggered conversion: {val}", "Config")
      await ctx.send(embed = repl.embed)
    else:
      val = str(emoji)
      await self.config.guild(ctx.guild).emoji(val)
      self.cache['emoji'] =  val
      repl = Reply.CreateEmbed(f"Emoji used for reaction-triggered conversion set", "Config")
      await ctx.send(embed = repl.embed)


  @commands.command()
  async def convert(self, ctx, *, txt):
    """Do the conversion"""
    msg = await self._convert(txt, None)
    if msg:
      await ctx.send(embed = msg.embed)
   

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

    if str(payload.emoji) != await self._getConfig(guild, 'emoji'):
      return

    msg = await self._convert(message.content, reacted_user)
    if msg:
      await channel.send(embed = msg.embed)

  async def _convert(self, txt: str, user: discord.Member = None):
    mp: MessageProcessor = MessageProcessor()
    try:
      result = mp.processMessage(txt)      
      if isinstance(result, str):
        return Reply.CreateEmbed(result, "Value conversion")
      elif len(result) > 0:
        tmp = []
        for t in result:
          cr: ConversionResult = t
          tmp.append("%s = %s" % (cr.orig, cr.conv))
        answer = "%s" % "\n".join(tmp)
        repl = Reply.CreateEmbed(answer, "Value conversion")
        if user:
          repl.embed.set_footer(text = f"Requested by {user.display_name}")
        return repl
      else:
        print("No convertable units found in %s" % txt)
    except Error as e:
      return Reply.CreateError(e)
    except Exception as e:
      print("Exception was thrown while trying to process the message: %s" % e)
      traceback.print_exc()
    return None
    

  async def _getConfig(self, guild, key: str):
    if not self.cache[key]:
      self.cache[key] = await getattr(self.config.guild(guild), key)()    
    return self.cache[key]
    

