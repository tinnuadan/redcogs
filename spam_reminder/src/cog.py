from redbot.core import Config, commands
import discord
import typing
import datetime

class SpamReminderCog(commands.Cog):
  """Reminds people to switch to another channel if too many messages are posted in a channel which is not meant for discussions"""

  def __init__(self):
    return

  @commands.Cog.listener()
  async def on_message(self, message: discord.Message):
    if message.author.bot:
      return
    channel: discord.TextChannel = message.channel
    await channel.send(f"Message sent in {channel.name}")
        