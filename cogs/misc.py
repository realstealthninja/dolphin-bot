import disnake
from disnake.ext import commands

from core import DolphinBot


class Misc(commands.Cog):
    def __init__(self, bot: DolphinBot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        return await ctx.reply(
            embed=disnake.Embed(
                title=f"�{round(self.bot.latency * 1000)} ms", description=""
            )
        )


def setup(bot: DolphinBot):
    bot.add_cog(Misc(bot))
