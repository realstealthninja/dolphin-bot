import disnake
from disnake.ext import commands

from core.bot import DolphinBot
from .modals import event_modal
from .objects import Base
from .views import ChannelSelectView


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
    

    async def if_admin(ctx: commands.Context) -> bool:
        return ctx.author.guild_permissions.administrator
    
    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def event(self, inter) -> None:
        await inter.response.send_modal(modal=event_modal(self))

    @commands.command()
    @commands.check(if_admin)
    async def config(self, ctx: commands.Context) -> None:
        view = ChannelSelectView(self, ctx)
        print(view)
        await ctx.send(embed=disnake.Embed(title="Configuring events in this server..", description="serber admin only pls dont touchy", color=disnake.Color.orange()), view=view)


def setup(bot) -> None:
    bot.add_cog(Seasonal(bot))
