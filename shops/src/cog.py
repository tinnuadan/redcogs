from redbot.core import commands
import discord

class ShopsCog(commands.Cog):
  """Store and finds shops"""

  def __init__(self):
    super().__init__()

  @commands.command()
  async def shop(self, ctx):
    msg = discord.Embed(color=0xEE2222, title="Test", description="test desc")
    await ctx.send(embed=msg)