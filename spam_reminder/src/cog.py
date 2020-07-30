from redbot.core import Config, commands
import discord
import typing
import datetime
from . import message_counter

class SpamReminderCog(commands.Cog):
  """Reminds people to switch to another channel if too many messages are posted in a channel which is not meant for discussions"""

  def __init__(self):
    self.counter_mgr = message_counter.MessageCounterMgr()
    return

  @commands.Cog.listener()
  async def on_message(self, message: discord.Message):
    if message.author.bot:
      return
    await self.count_messages(message)

  async def count_messages(self, message):
    res = self.counter_mgr.new_msg(message)
    if res == message_counter.MessageCounterResult.OverThreshold:
      counter = self.counter_mgr.get_counter(message.channel)
      repl = f"It seems to be an unsually high activity in this channel. You may consider moving the conversation to #{counter.channel.name}"
      counter.clear()
      await message.channel.send(repl)



    