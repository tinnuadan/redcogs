from redbot.core import commands, checks, Config, VersionInfo, version_info
from redbot import core as rbcore
import discord
import traceback
from typing import Optional, Dict
from .mcuuid import MCUUID, UUIDResult
from .sync import Sync, SyncResult
from .reply import Reply

class PatreonSyncCog(commands.Cog):
  """Links as discord to a minecraft account"""

  def __init__(self, bot):
    # load data
    self.bot = bot
    self.config = Config.get_conf(self, 0x18055989fd0a4b0491ddb63ada2eed8c, force_registration=True)
    default_guild = { 'server' : "localhost", "user": None, "password": None }
    self.config.register_guild(**default_guild)
    self.cache = { 'server' : None, "user": None, "password": None  }
    self.mcuuid = MCUUID()
    self.dbsync = Sync()

  @commands.command()
  async def link(self, ctx, *, txt):
    """Link discord to minecraft """
    self.dbsync.server = await self._getConfig(ctx.guild, "server")
    self.dbsync.user = await self._getConfig(ctx.guild, "user")
    self.dbsync.password = await self._getConfig(ctx.guild, "password")
    msg = await self._linkunlink(txt, ctx.author, doLink = True)
    if msg:
      await ctx.send(embed = msg.embed)

  @commands.command()
  async def unlink(self, ctx, *, txt):
    """Link discord to minecraft """
    self.dbsync.server = await self._getConfig(ctx.guild, "server")
    self.dbsync.user = await self._getConfig(ctx.guild, "user")
    self.dbsync.password = await self._getConfig(ctx.guild, "password")
    msg = await self._linkunlink(txt, ctx.author, doLink = False)
    if msg:
      await ctx.send(embed = msg.embed)

  async def _linkunlink(self, username, user: discord.User, doLink):
    mcUser: Dict = self.mcuuid.getUUID(username)
    if mcUser["result"] == UUIDResult.NotValid:
      return Reply.CreateError(f"Minecraft account \"{username}\" not valid.")
    if mcUser["result"] == UUIDResult.NotFound:
      return Reply.CreateError(f"Minecraft account \"{username}\" not found.")
    if mcUser["result"] == UUIDResult.NetworkError:
      return Reply.CreateError("Unable to query Mojang API servers. Please try again later.")
    
    if doLink:
      linkRes = self.dbsync.link(user.id, mcUser["id"])
    else:
      linkRes = self.dbsync.unlink(user.id, mcUser["id"])
    if linkRes == SyncResult.DBNotSetup:
      return Reply.CreateError("Database connection not setup.")
    if linkRes == SyncResult.NoDBConnection:
      return Reply.CreateError("Database connection could not be established.")
    if linkRes == SyncResult.DBError:
      return Reply.CreateError("General database error.")
    
    if doLink:
      return Reply.CreateSuccess(f"IGN {mcUser['name']} linked to discord user {user.name}.")   
    else:
      return Reply.CreateSuccess(f"IGN {mcUser['name']} unlinked from discord user {user.name}.")   
  
  @commands.group(name="patreonsync")
  @commands.guild_only()
  @checks.mod_or_permissions(manage_messages=True)
  async def patreonsync(self, ctx: commands.Context) -> None:
    """
        Settings for patreonsync
    """
    pass

  @patreonsync.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def server(self, ctx, server: Optional[str] = None,):
    """
        Gets or sets the mysql/mariadb server
    """
    if not server:
      val = await self._getConfig(ctx.guild, "server")
      repl = Reply.CreateEmbed(f"Used sql server: {val}", "Config")
      await ctx.send(embed = repl.embed)
    else:
      val = str(server)
      await self.config.guild(ctx.guild).server.set(val)
      self.cache['server'] = None
      repl = Reply.CreateEmbed(f"Used sql server set", "Config")
      await ctx.send(embed = repl.embed)

  @patreonsync.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def user(self, ctx, user: Optional[str] = None,):
    """
        Gets or sets the mysql/mariadb user
    """
    if not user:
      val = await self._getConfig(ctx.guild, "user")
      repl = Reply.CreateEmbed(f"Used sql user: {val}", "Config")
      await ctx.send(embed = repl.embed)
    else:
      val = str(user)
      await self.config.guild(ctx.guild).user.set(val)
      self.cache['user'] = None
      repl = Reply.CreateEmbed(f"Used sql user set", "Config")
      await ctx.send(embed = repl.embed)
  
  @patreonsync.command()
  @checks.mod_or_permissions(manage_messages=True)
  async def password(self, ctx, pwd: Optional[str] = None,):
    """
        Sets the mysql/mariadb user
    """
    if not pwd:
      val = await self._getConfig(ctx.guild, "password")
      repl = Reply.CreateEmbed(f"Used sql password: {val}", "Config")
      await ctx.send(embed = repl.embed)
    else:
      val = str(pwd)
      await self.config.guild(ctx.guild).password.set(val)
      self.cache['password'] = None
      repl = Reply.CreateEmbed(f"Used sql password set", "Config")
      await ctx.send(embed = repl.embed)

  async def _getConfig(self, guild, key: str):
    if not self.cache[key]:
      self.cache[key] = await getattr(self.config.guild(guild), key)()    
    return self.cache[key]
    

