from disnake.ext import commands

from core.bot import DolphinBot


class Seasonal(commands.Cog):
    pass

def setup(bot: DolphinBot):
    bot.add_cog(Seasonal(bot))
