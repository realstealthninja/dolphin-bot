from disnake.ext import commands
from .modals import event_modal
from .objects import Base


from sqlalchemy.ext.asyncio import async_sessionmaker


class Seasonal(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.session = async_sessionmaker(
            self.bot.seasonal, expire_on_commit=False
        )

    async def cog_load(self):
        async with self.bot.seasonal.begin() as connection:
            await connection.run_sync(Base.metadata.createall)
    

    @commands.slash_command()
    async def event(self, inter) -> None:
        await inter.response.send_modal(modal=event_modal(self.session))


def setup(bot) -> None:
    bot.add_cog(Seasonal(bot))
