from redbot.core import commands

class UnitCog(commands.Cog):
  """My custom cog"""

  @commands.command()
  async def convert(self, ctx, *, txt):
    """This does stuff!"""
    # Your code will go here
    await ctx.send("Will convert the text %s" % txt)