from redbot.core import commands
from redbot.core.utils.menus import menu
import contextlib
import discord
import typing
import logging

from .actions import Action, ActionType
from .config import Config
from .shopmanager import ShopManager
from .backend import sqlitebackend
from .process_message import parse_message
from .process_actions import process_action
from .reply import Reply, MessageType
from .logging import setupLogging


class ShopsCog(commands.Cog):
  """Store and finds shops"""

  def __init__(self):
    super().__init__()
    self._config = Config()
    logSettings = self._config.logging
    setupLogging(logSettings['level'],logSettings['output_folder'],logSettings['prefix'],logSettings['max_files'])
    self._mgr = ShopManager(sqlitebackend.SqliteBackend(self._config.databaseuri))
    self._lastAction = None
    logging.getLogger(__name__).info(f"Shops Cog started")

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
      if not isinstance(reply, list):
        reply = [reply]
      for r in reply:
        if r.embed != None:
          await ctx.send(embed = r.embed)
        else:
          await ctx.send(r.message)

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
