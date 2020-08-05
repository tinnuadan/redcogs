from redbot.core import Config, commands, checks
import discord
import typing
import datetime
import json
from . import message_counter

class SpamReminderCog(commands.Cog):
  """Reminds people to switch to another channel if too many messages are posted in a channel which is not meant for discussions"""

  def __init__(self):
    # self.counter_mgr = message_counter.MessageCounterMgr()
    self._config = Config.get_conf(self, 15961704848357, force_registration=True)
    default_user = {"usersr": None}
    self._config.register_user(**default_user)
    default_guild = {
      "msg": "There seems to be an unsually high activity in this channel. You may consider moving the conversation to <alternative>.",
      "counters": []
    }
    self._config.register_guild(**default_guild)
    self._counters = dict()
    self._config_loaded = False
    

  @commands.Cog.listener()
  async def on_message(self, message: discord.Message):
    if message.author.bot:
      return
    if message.content[0] == '!':
      return
    await self.count_messages(message)

  async def count_messages(self, message: discord.Message):
    await self.auto_load_config(message.guild)
    counter = self.get_counter(message.guild, message.channel)
    if not counter:
      return
    res = counter.new_msg()
    if res == message_counter.MessageCounterResult.OverThreshold:
      co: discord.TextChannel = counter.channel_out
      repl = await self.get_message(message.guild, f"{co.mention}")
      counter.clear()
      await message.channel.send(repl)

  @commands.group(name="spamreminder", aliases=["sr"])
  @commands.guild_only()
  @checks.mod_or_permissions(manage_messages=True)
  async def spamreminder(self, ctx: commands.Context) -> None:
    """
        Monitors channels and friendly reminds people to move the conversation to another channel if there are too many mesages.
    """
    pass

  @spamreminder.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def add(self, ctx, watched_channel, alternative_channel, message_threshold, timespan):
    """
        New Monitor for a channel
    """
    await self.auto_load_config(ctx.guild)

    try:
      message_threshold = int(message_threshold)
    except ValueError:
      await ctx.send(f"Unable to convert \"{message_threshold}\" to a number")
      return

    try:
      timespan = self.convert_timespan(timespan)
    except ValueError:
      await ctx.send(f"Unable to convert \"{timespan}\" to a number")
      return
    
    wc = self.get_channel(ctx.guild, watched_channel)
    ac = self.get_channel(ctx.guild, alternative_channel)
    
    if not wc:
      await ctx.send(f"No channel found for \"{watched_channel}\"")
      return
    
    if not ac:
      await ctx.send(f"No channel found for \"{alternative_channel}\"")
      return

    if self.get_counter(ctx.guild, wc):
      await ctx.send(f"Monitor for {wc.mention} already exist.")
      return

    counters = await self._config.guild(ctx.guild).counters()
    cntr = message_counter.MessageCounter(wc, ac, message_threshold, timespan)
    counters.append( cntr.toJson() )
    self._counters[wc.id] =  cntr
    await self._config.guild(ctx.guild).counters.set(counters)
    await ctx.send(f"Monitor for {wc.mention} created.")

  @spamreminder.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def list(self, ctx):
    """
        Lists all monitors
    """
    await self.auto_load_config(ctx.guild)
    counters = self._counters
    repl = []
    for _, cntr in counters.items():
      timespan = self.timespan_to_str(cntr.timespan)
      repl.append(f"{cntr.watched_channel.mention}: Redirect to {cntr.channel_out.mention} if there are more than {cntr.msg_threshold} messages within {timespan}")
    if len(repl) == 0:
      await ctx.send("No monitors set up")
      return
    await ctx.send("\n".join(repl))


  @spamreminder.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def edit(self, ctx, watched_channel, to_edit, value):
    """
        Edit monitor of a channel.
        'to_edit' must be on of the following: 'alternative_channel', 'msg_threshold', 'timespan'
    """
    await self.auto_load_config(ctx.guild)
    to_edits = ['alternative_channel', 'msg_threshold', 'timespan']
    if to_edit not in to_edits:
      to_edits = ",".join(to_edits)
      await ctx.send(f"'to_edit' must be one of the following: {to_edits}")
      return

    wc = self.get_channel(ctx.guild, watched_channel)
    if not wc:
      await ctx.send(f"Channel {watched_channel} not found")
      return

    cntr = self.get_counter(ctx.guild, wc)
    if not cntr:
      await ctx.send(f"There is no monitor set for {wc.mention}")
      return

    if to_edit == 'alternative_channel':
      ac = self.get_channel(value)
      if not ac:
        await ctx.send(f"No channel found for \"{alternative_channel}\"")
        return
      cntr.channel_out = ac
    
    if to_edit == 'msg_threshold':
      try:
        value = int(value)
      except ValueError:
        await ctx.send(f"Unable to convert \"{value}\" to a number")
        return
      cntr.msg_threshold = value
    
    if to_edit == 'timespan':
      try:
        value = self.convert_timespan(value)
      except ValueError:
        await ctx.send(f"Unable to convert \"{value}\" to a number")
        return
      cntr.timespan = value

    counters = await self._config.guild(ctx.guild).counters()
    for i in range(0, len(counters)):
      c = json.loads(counters[i])
      if c['watched_channel'] == cntr.watched_channel.id:
        counters[i] = cntr.toJson()
        break
    self._counters[wc.id] =  cntr
    await self._config.guild(ctx.guild).counters.set(counters)
    await ctx.send(f"Monitor for {wc.mention} updated.")


  @spamreminder.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def remove(self, ctx, watched_channel):
    """
        Removes monitoring from a channel
    """
    await self.auto_load_config(ctx.guild)
    wc = self.get_channel(ctx.guild, watched_channel)
    if not wc:
      await ctx.send(f"Channel {watched_channel} not found")
      return

    cntr = self.get_counter(ctx.guild, wc)
    if not cntr:
      await ctx.send(f"There is no monitor set for {wc.mention}")
      return

    counters = await self._config.guild(ctx.guild).counters()
    for i in range(0, len(counters)):
      c = json.loads(counters[i])
      if c['watched_channel'] == cntr.watched_channel.id:
        del counters[i]
        break
    del self._counters[wc.id]
    await self._config.guild(ctx.guild).counters.set(counters)
    await self.send(f"Monitor for {wc.mention} removed")

  @spamreminder.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def message(self, ctx):
    """
        The message which is displayed when there are too many messages. <alternative> will be replaced with the name of the alternative channel.
    """
    msg = await self.get_message(ctx.guild)
    await ctx.send(f"Current message:\n{msg}")

  @spamreminder.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def setmessage(self, ctx, message):
    """
        The message which is displayed when there are too many messages. <alternative> will be replaced with the name of the alternative channel.
    """
    await self._config.guild(ctx.guild).msg.set(message)
    msg = await self.get_message(ctx.guild)
    await ctx.send(f"Message changed to:\n{msg}")

  async def auto_load_config(self, guild):
    if self._config_loaded:
      return    
    counters = await self._config.guild(guild).counters()
    for cnt in counters:
      data = json.loads(cnt)
      wc = self.get_channel(guild, data['watched_channel'])
      ac = self.get_channel(guild, data['channel_out'])
      counter = message_counter.MessageCounter(wc, ac, int(data['msg_threshold']), int(data['timespan']))
      self._counters[counter.watched_channel.id] = counter
    self._config_loaded = True

  async def get_message(self, guild, channel_name = None) -> str:
    msg = await self._config.guild(guild).msg()
    if channel_name:
      msg = msg.replace("<alternative>", channel_name)
    return msg

  def get_channel(self, guild, channel_name_id):
    if str(channel_name_id)[0] == "<":
      channel_name_id = channel_name_id[2:-1]
    for channel in guild.text_channels:
      channel: discord.TextChannel = channel
      if str(channel.id) == str(channel_name_id):
        return channel
    return None

  def get_counter(self, guild, channel):
    if not isinstance(channel, discord.TextChannel):
      channel = get_channel(guild, channel)
    if not channel:
      return None
    if channel.id in self._counters:
      return self._counters[channel.id]
    return None

  def convert_timespan(self, timespan):
    try:
      i = int(timespan)
      return i
    except:
      pass
    units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 86400*7}
    timespan = str(timespan)
    if len(timespan) == 0:
      raise ValueError
    unit = timespan[-1]
    if unit not in units.keys():
      raise ValueError
    factor = units[unit]
    value = 0
    value = float(timespan[0:-1])
    return value*factor

  def timespan_to_str(self, timespan):
    units = {'sec': 1, 'min': 60, 'hours': 3600, 'days': 86400, 'weeks': 86400*7}
    unit = None
    val = 0
    for i in range(0, len(units)-1):
      k1 = list(units.keys())[i]
      k2 = list(units.keys())[i+1]
      if timespan >= units[k1] and timespan < units[k2]:
        val = self.round(timespan/units[k1])
        unit = k1
        break
    if unit == None:
      unit = 'w'
      val = self.round(timespan/units['w'])
    return f"{val} {unit}"
  
  def round(self,a):
    return round(10*a)/10







    