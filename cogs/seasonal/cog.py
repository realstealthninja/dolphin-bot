import disnake
from disnake.ext import commands
from sqlalchemy import Select, Update, Insert
from core.bot import DolphinBot

from .objects import Base, Seasons, events
from .views import ChannelSelectView

# db
from sqlalchemy.ext.asyncio import async_sessionmaker

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class Seasonal(commands.Cog):
    def __init__(self, bot: DolphinBot):
        self.bot = bot
        self.session = async_sessionmaker(self.bot.seasonal, expire_on_commit=False)
        self.check_time.start()
    
    async def cog_load(self):
        async with self.bot.seasonal.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    def if_admin(ctx: commands.Context):
        return ctx.message.author.guild_permissions.manage_guild
    
    @tasks.loop(hours=24)
    async def check_time(self):
        async 

    
    @commands.check(if_admin)
    @commands.command()
    async def config(self, ctx: commands.Context):
        await ctx.send(embed=disnake.Embed(
            title = "Configure Beats to beat",
            description = """
**announcement channel** - where events will be announced
**submissions  channel** - where users can submit songs
            """,
            color = disnake.Color.from_rgb(0x00, 0x00, 0x00)
        ).set_thumbnail(
            url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/%C5%BB%C3%B3%C5%82ta_nuta.png/640px-%C5%BB%C3%B3%C5%82ta_nuta.png"
        ), view=ChannelSelectView(ctx, self.session))
    
    @commands.check(if_admin)
    @commands.command()
    async def event(self, ctx: commands.Context, *, txt: str):
        
        embed = disnake.Embed(
            title="preparing event",
            description = f"Creating event for {txt[0,50]}"
        )

        msg = await ctx.reply(embed=embed)

        async with self.session() as conn:
            query = Select(Seasons).where(Seasons.guild_id == ctx.guild.id)
            seasons = await conn.execute(query)
            row: Seasons | None = seasons.fetchone()
            if row:
                query = Update(events).where(events.id == ctx.guild.id).values(text=txt, time=datetime.combine((date.today() + relativedelta(months=1)), datetime.now().time()).timestamp())
            else:
                query = Insert(events).values(text=txt, time=datetime.combine((date.today() + relativedelta(months=1)), datetime.now().time().timestamp()))
            await conn.execute(query)
                
            #TODO: Message the announcement chat 
        embed = disnake.Embed(
                title="sucessfully created event")
        await msg.reply(embed=emebd)



def setup(bot: DolphinBot):
    bot.add_cog(Seasonal(bot))
