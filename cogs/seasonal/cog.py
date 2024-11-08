from disnake import (
    Embed,
    Message,
    NotFound,
    Attachment,
    TextChannel,
    ApplicationCommandInteraction
)
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from disnake.ext import commands
from disnake.interactions import AppCommandInteraction 

from core.bot import DolphinBot
from .objects import Base, Season, Event, Submission, Producer, Sample

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select


class Seasonal(commands.Cog):
    def __init__(self, bot: DolphinBot) -> None:
        self.bot: DolphinBot = bot
        self.session = async_sessionmaker(
            bind=self.bot.seasonal, expire_on_commit=False
        )
        self.session.configure(bind=self.bot.seasonal)

        self.submission_channel: TextChannel = self.bot.get_channel(1244043463306117270)
        self.announcement_channel: TextChannel = self.bot.get_channel(1244047303615053884)

    async def cog_load(self):
        async with self.bot.seasonal.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def get_current_season(
            self,
            session: AsyncSession
    ) -> Season | None:
        return (await session.execute(
                select(Season).filter(date.today() < Season.end_date)
         )).scalar_one_or_none()

    async def get_current_event(
            self,
            session: AsyncSession,
            season: Season,
            ) -> Event | None:
        return (
                await session.execute(
                    select(Event).filter(
                        Event.season ==  season and
                        date.today() < Event.end_date 
                    )
                )
            ).scalar_one_or_none()


    @commands.slash_command()
    async def season(
            self,
            ctx: ApplicationCommandInteraction,
            start_date: str = date.today().strftime("%m/%d/%y"),
            end_date: str = (date.today() + relativedelta(months=3)).strftime("%m/%d/%y")
        ) -> None:
        """Creates a season. the date is specified in mm/dd/yy format"""
        async with self.session() as session:
            season = await self.get_current_season(session)
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
            sample: Attachment | None = None
        ) -> None: 
        """
        Creates an event for the current season\n
        dates are specified in mm/dd/yy format\n
        """
        async with self.session() as session:
            
            season = await self.get_current_season(session) 

            if not season:
                await ctx.send(
                        "You aren't in a season please create one"
                )
                return None

            event: Event | None = await self.get_current_event(session, season)
            start = datetime.strptime(start_date, "%m/%d/%y")
            end = datetime.strptime(end_date, "%m/%d/%y")

            if not event:
                event = Event(
                    season_id = season.id,
                    name = name,
                    start_date = start, 
                    end_date = end,
                    season = season
                )
                session.add(event)
            else:
                event.name = name
                event.start_date = start
                event.end_date = end 

            if sample and sample.content_type.startswith("audio/"):
                file: bytes = await sample.read()  
                db_sample = Sample(name=sample.filename, file=file, event=event)
                session.add(db_sample)

            embed = Embed(
                    title = name,
                ).add_field(
                    name = "starts on",
                    value = f"<t:{round(start.timestamp())}:D>"
                ).add_field(
                    name = "ends on",
                    value = f"<t:{round(end.timestamp())}:D>"
                )

            try:
                msg = await self.announcement_channel.fetch_message(event.id if event.id else 0) 
                msg = await msg.edit(
                    embed = embed,
                    file = ((await sample.to_file(spoiler=True)) if sample else None)
                )
            except NotFound:
                msg = await self.announcement_channel.send(
                    embed = embed,
                    file = ((await sample.to_file(spoiler=True)) if sample else None)
                )

            event.id = msg.id

            await session.commit()
        await ctx.send("created event!")

    @commands.Cog.listener("on_message")
    async def on_submission(self, msg: Message) -> None:
        if msg.channel != self.submission_channel:
            return

        if msg.author.bot and msg.author != self.bot.user:
            await msg.delete()
            return

        if len(msg.attachments) < 0: 
            await msg.author.send("Please use <#1244043434281402582> for chatting")           
            return
        
        async with self.session() as session:
            season = await self.get_current_season(session)

            if not season:
                await msg.delete()
                return

            producer = (await session.execute(
                select(Producer).filter_by(id = msg.author.id)
            )).scalar_one_or_none()

            if not producer:
                producer = Producer(id = msg.author.id)
                session.add(producer)

            submission = (await session.execute(
                select(Submission).filter_by(producer = producer)
            )).scalar_one_or_none()

            event = await self.get_current_event(session, season)

            if not event:
                await msg.delete()
                return

            if not submission:
                msg = await self.submission_channel.send("")
                submission = Submission(id = msg.id, producer = producer, event = event)



def setup(bot) -> None:
    bot.add_cog(Seasonal(bot))
