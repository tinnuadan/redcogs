from redbot.core import commands
import discord
import typing

class DateConvertCog(commands.Cog):
  """Converts date and time to different timezones"""


  @commands.command()
  async def test(self, ctx, *, txt):
    """Do the conversion"""
    await ctx.send("ping")