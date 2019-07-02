from redbot.core import commands
from .process_message import MessageProcessor, ConversionResult
from .convert_units.converter import loadConversionsData

class UnitCog(commands.Cog):
  """Searches for units in a message and tries to convert them from metric to imperial and vice versa"""

  def __init__(self):
    # load data
    loadConversionsData()
    _ = MessageProcessor()

  @commands.command()
  async def convert(self, ctx, *, txt):
    """Do the conversion"""
    mp: MessageProcessor = MessageProcessor()
    try:
      result = mp.processMessage(txt)
    except Exception as e:
      print("Exception was thrown while trying to process the message: %s" % e)
    if len(result) > 0:
      tmp = []
      for t in result:
        cr: ConversionResult = t
        tmp = "%s = %s" % (cr.orig, cr.conv)
      answer = "Fyi: %s" % ", ".join(tmp)
      await ctx.send(answer)
    else:
      print("No convertable units found in %s" % txt)