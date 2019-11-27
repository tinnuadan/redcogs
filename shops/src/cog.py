from redbot.core import commands
import discord
import typing

from .actions import Action, ActionType
from .shopmanager import ShopManager
from .backend import sqlitebackend
from .process_message import parse_message
from .process_actions import process_action


class ShopsCog(commands.Cog):
  """Store and finds shops"""

  def __init__(self):
    super().__init__()
    self._mgr = ShopManager(sqlitebackend.SqliteBackend(":memory:"))

  @commands.command()
  async def shop(self, ctx, *, msg):
    action = parse_message(msg)
    if action.isHelp:
      await ctx.send(f"```{action.payload}```")
    else:
      reply = process_action(self._mgr, action, False)
      if reply.embed != None:
        await ctx.send(embed = reply.embed)
      else:
        await ctx.send(reply.message)
