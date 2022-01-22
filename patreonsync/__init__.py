from .src.cog import PatreonSyncCog

def setup(bot):
  bot.add_cog(PatreonSyncCog(bot))