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
                title="Pong! :ping_pong:", description=f"{round(self.bot.latency * 1000)} ms",
                color=disnake.Color.blurple()
            )
        )


def setup(bot: DolphinBot):
    bot.add_cog(Misc(bot))
