from redbot.core import commands
from redbot.core.utils.menus import menu
import contextlib
import discord
import typing
import logging

from .actions import Action, ActionType
from .shopmanager import ShopManager
from .backend import sqlitebackend
from .process_message import parse_message
from .process_actions import process_action
from .reply import Reply, MessageType


class ShopsCog(commands.Cog):
  """Store and finds shops"""

  def __init__(self):
    super().__init__()
    logging.getLogger(__name__).setLevel(logging.INFO)
    self._mgr = ShopManager(sqlitebackend.SqliteBackend(":memory:"))
    self._lastAction = None

  @commands.command()
  async def shop(self, ctx, *, msg):
    action = parse_message(msg)
    if action.isHelp:
      await ctx.send(f"```{action.payload}```")
    elif action.confirmationNeeded:
      self._lastAction = action
      reply = process_action(self._mgr, action, False)
      if reply.type == MessageType.Error:
        await ctx.send(embed = reply.embed)
        return
      controls = {"✅": self._confirm_action, "❌": self._discard_action}
      await menu(ctx, [reply.embed], controls)
    else:
      reply = process_action(self._mgr, action, False)
      if reply.embed != None:
        await ctx.send(embed = reply.embed)
      else:
        await ctx.send(reply.message)

  async def _confirm_action(self, ctx, pages, controls, message, page, timeout, emoji):
    await self._remove_reactions(ctx, pages, controls, message, page, timeout, emoji)
    reply = process_action(self._mgr, self._lastAction, True)
    if reply.embed != None:
      await ctx.send(embed = reply.embed)
    else:
      await ctx.send(reply.message)

  async def _discard_action(self, ctx, pages, controls, message, page, timeout, emoji):
    await self._remove_reactions(ctx, pages, controls, message, page, timeout, emoji)

  async def _remove_reactions(self, ctx, pages, controls, message, page, timeout, emoji):    
    with contextlib.suppress(discord.NotFound):
        await message.delete()
