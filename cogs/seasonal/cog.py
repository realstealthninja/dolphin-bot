import disnake

from datetime import datetime
from disnake.ext import commands
from disnake.ext import tasks

from core.bot import DolphinBot

from .modals import event_modal
from .objects import Base, Points, Submission
from .views import ChannelSelectView

from .utils import (
    add_points,
    add_reaction,
    add_submssion,
    delete_event,
    fetch_config,
    fetch_event,
    fetch_points,
    fetch_season,
    fetch_submissions,
    remove_reaction,
    make_leaderboard
)


from sqlalchemy.ext.asyncio import async_sessionmaker


class Seasonal(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: DolphinBot = bot
        self.session = async_sessionmaker(
            bind=self.bot.seasonal, expire_on_commit=False
        )
        self.session.configure(bind=self.bot.seasonal)
        self.event_end.start()

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
    async def leaderboard(self, ctx: commands.Context) -> None:
        points: list[Points] = await fetch_points(self, ctx.guild.id)
        users: list[disnake.User] = []
        if not points:
            return await ctx.send("no one has any points yet")
        for point in points:
            user = self.bot.get_user(point.userid)
            users.append(user)
        await make_leaderboard(users, points)
        await ctx.send(file=disnake.File("board.png"))


    @commands.slash_command(name="leaderboard", description="Shows the seasonal leaderboard")
    async def _leaderboard(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        points: list[Points] = await fetch_points(self, ctx.guild.id)
        users: list[disnake.User] = []
        for point in points:
            user = self.bot.get_user(point.userId)
            users.append(user)
        await make_leaderboard(users, points)
        await ctx.response.send_message(file=disnake.File("board.png"))

    @commands.command()
    @commands.check(if_admin)
    async def config(self, ctx: commands.Context) -> None:
        view = ChannelSelectView(self, ctx)
        await ctx.send(
            embed=disnake.Embed(
                title="Configuring events in this server..",
                description="serber admin only pls dont touchy",
                color=disnake.Color.orange(),
            ),
            view=view,
        )
    
    @commands.command()
    async def event_leaderboard(self, ctx: commands.Context):
        event = await fetch_event(self, ctx.guild.id)
        if not event:
            await ctx.reply("No event going on right now sorry!")
            return

        submissions: list[Submission] = await fetch_submissions(self, ctx.guild.id)
        ret_val = ""
        await ctx.send(submissions)
        for submission in submissions:
            ret_val += f"1. [{self.bot.get_user(submission.userId)}]({self.bot.get_message(submission.messageId).jump_url}) ->  ({submission.reactions}) \n"
        await ctx.reply(ret_val)
    
    @commands.slash_command(name="event_leaderboard", description="shows the event leaderboard")
    async def event_leaderboard_slash(self, inter: disnake.ApplicationCommandInteraction):
        event = await fetch_event(self, inter.guild.id)
        if not event:
            await inter.response.send_message("No event going on right now sorry!")
            return
        
        submissions: list[Submission] = await fetch_submissions(self, inter.guild_id)
        ret_val = ""
        for submission in submissions:
            ret_val += f"1. [{self.bot.get_user(submission.userId)}]({self.bot.get_message(submission.messageId.jump_url)}) ->  ({submission.reactions}) \n"
        await inter.response.send_message(ret_val)



    @tasks.loop(minutes=3)
    async def event_end(self):
        for server in self.bot.guilds:
            event = await fetch_event(self, server.id)

            if event and datetime.now().timestamp() > event.duration:
                msg = self.bot.get_message(event.messageId)
                submissions = await fetch_submissions(self, event.id)
                season = await fetch_season(self, event.id)
                reactions = {}

                await msg.channel.send(
                    embed=disnake.Embed(
                        title=f"{msg.embeds[0].title} has ended!",
                        description="All submissions have stopped and the winner will be announced shortly!",
                        color=disnake.Color.dark_orange(),
                    )
                )

                if not (submissions and season):
                    await delete_event(self, server.id)
                    return await msg.channel.send("no participants sorry!")

                for submission in submissions:
                    await add_points(
                        self,
                        submission.id,
                        submission.userId,
                        season.month,
                        submission.reactions,
                    )
                    reactions[submission.userId] = submission.reactions

                reactions = sorted(reactions, reverse=True)

                await msg.channel.send(
                    content=f"||{self.bot.get_user(reactions[0]).mention}||",
                    embed=disnake.Embed(
                        title=f"The winner is ||{self.bot.get_user(reactions[0]).name}||",
                        description=f"thank you all for participating. see you next time!\
                        rankings will be shared soon, congrats {self.bot.get_user(reactions[0]).mention}",
                    ),
                )

                await delete_event(self, server.id)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        config = await fetch_config(self, message.guild.id)
        event = await fetch_event(self, message.guild.id)

        if not config or not event or message.channel.id != config.channel:
            return

        if len(message.attachments) == 0:
            return

        await message.add_reaction("🔥")
        await add_submssion(self, message.guild.id, message.id, message.author.id)

    @commands.Cog.listener()
    async def on_reaction_add(
        self, reaction: disnake.Reaction, user: disnake.Member | disnake.User
    ):
        if user.id == self.bot.user.id or reaction.emoji != "🔥":
            return

        config = await fetch_config(self, user.guild.id)
        event = await fetch_event(self, user.guild.id)
        submissions = await fetch_submissions(self, user.guild.id)

        if not config or not event or config.channel != reaction.message.channel.id:
            return

        for submission in submissions:
            msg = self.bot.get_message(submission.messageId)

            # check if the reaction was to a submission
            if submission.messageId == reaction.message.id:
                # check if the reactor was the creator
                if submission.userId == user.id:
                    return
                
                for ereaction in msg.reactions:
                    if ereaction == reaction:
                        #  if  we find the reaction add it to the db
                        await add_reaction(self, msg.id)
                        return

            # check  for the other messages to see if the reactor has already reacted 
            for reaction in msg.reactions:
                if ereaction.emoji == "🔥":
                    try:
                        await ereaction.remove(user.id)
                    except disnake.NotFound:
                        break

    @commands.Cog.listener()
    async def on_reaction_remove(
        self, reaction: disnake.Reaction, user: disnake.User | disnake.Member
    ) -> None:
        if user.id == self.bot.user.id or reaction.emoji != "🔥":
            return

        config = await fetch_config(self, user.guild.id)
        submissions = await fetch_submissions(self, user.guild.id)
        event = await fetch_event(self, user.guild.id)

        if not config or not event or config.channel != reaction.message.channel.id:
            return

        for submission in submissions:
            if submission.messageId == reaction.message.id:
                if submission.userId == user.id:
                    return
                await remove_reaction(self, submission.messageId)


def setup(bot) -> None:
    bot.add_cog(Seasonal(bot))
