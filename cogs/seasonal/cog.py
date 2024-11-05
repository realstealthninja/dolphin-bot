from disnake import Embed, ApplicationCommandInteraction
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from disnake.ext import commands
from disnake.interactions import AppCommandInteraction 

from core.bot import DolphinBot
from .objects import Base, Season, Event 

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select


class Seasonal(commands.Cog):
    def __init__(self, bot: DolphinBot) -> None:
        self.bot: DolphinBot = bot
        self.session = async_sessionmaker(
            bind=self.bot.seasonal, expire_on_commit=False
        )
        self.session.configure(bind=self.bot.seasonal)

    async def cog_load(self):
        async with self.bot.seasonal.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)


    @commands.slash_command()
    async def season(
            self,
            ctx: ApplicationCommandInteraction,
            start_date: str = date.today().strftime("%m/%d/%y"),
            end_date: str = (date.today() + relativedelta(months=3)).strftime("%m/%d/%y")
        ) -> None:
        """Creates a season. the date is specified in mm/dd/yy format"""
        async with self.session() as session:
            season = (await session.execute(
                    select(Season).filter(date.today() < Season.end_date)
            )).scalar_one_or_none()

            start = datetime.strptime(start_date, "%m/%d/%y")
            end = datetime.strptime(end_date, "%m/%d/%y")
            
            if not season:
                season = Season(start_date = start, end_date = end)
            else:
                season.end_date = end

            session.add(season)
            await session.commit()
        await ctx.send(
            embed = Embed(
                title = "Season has been made",
            ).add_field(
                name = "starts on",
                value = start_date
            ).add_field(
                name = "ends on",
                value = end_date
            )
        )

    @commands.slash_command()
    async def event(
            self,
            ctx: AppCommandInteraction, 
            name: str = "Sample competition",
            start_date: str = date.today().strftime("%m/%d/%y"),
            end_date: str = (date.today() + relativedelta(weeks=1)).strftime("%m/%d/%y"),
        ) -> None: 
        """
        Creates an event for the current season\n
        dates are specified in mm/dd/yy format\n
        """
        async with self.session() as session:
            
            season = (await session.execute(
                    select(Season).filter(date.today() < Season.end_date)
            )).scalar_one_or_none()

            if not season:
                await ctx.send(
                        "You aren't in a season please create one"
                )
                return None

            event = (
                await session.execute(
                    select(Event).filter_by(season = season)
                )
            ).scalar_one_or_none()

            if not event:
                event = Event(
                    season_id = season.id,
                    start_date = datetime.strptime(start_date, "%m/%d/%y"), 
                    end_date = datetime.strptime(end_date, "%m/%d/%y"),
                    season = season
                )
                session.add(event)
            else:
                event.start_date = datetime.strptime(start_date, "%m/%d/%y")
                event.end_date = datetime.strptime(end_date, "%m/%d/%y")


            await session.commit()

        await ctx.send(
            embed = Embed(
                title = name,
            ).add_field(
                name = "starts on",
                value = start_date
            ).add_field(
                name = "ends on",
                value = end_date
            )
        )

def setup(bot) -> None:
    bot.add_cog(Seasonal(bot))
