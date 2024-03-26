import disnake
from disnake.ext import commands

from core.bot import DolphinBot
from .modals import event_modal
from .objects import Base


from sqlalchemy.ext.asyncio import async_sessionmaker


class Seasonal(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: DolphinBot = bot
        self.session = async_sessionmaker(
            self.bot.seasonal, expire_on_commit=False
        )

    async def cog_load(self):
        async with self.bot.seasonal.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    

    @commands.slash_command()
    async def event(self, inter) -> None:
        await inter.response.send_modal(modal=event_modal(self))

    @commands.command()
    async def config(self, ctx: commands.Context) -> None:
        await ctx.send(embed=disnake.Embed)


def setup(bot) -> None:
    bot.add_cog(Seasonal(bot))
