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
    make_leaderboard,
    to_zero
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


    @commands.command(hidden=True)
    @commands.is_owner()
    async def recalculate_reactions(self, ctx: commands.Context) -> None:
        config = await fetch_config(self, ctx.guild.id)
        event = await fetch_event(self, ctx.guild.id)
        submissions = await fetch_submissions(self, ctx.guild.id)

        if not event or not config or not submissions:
            return

        channel = self.bot.get_channel(config.channel)

        sub_messages: list[disnake.Message] = []
        event_message = await channel.fetch_message(event.messageId)
        reactors: dict[disnake.Message, list[disnake.User]] = {}

        embed = disnake.Embed(title="recalculating reactions...")

        sent_message = await ctx.send(embed=embed)

        #         : reactors
        # message : userid, userid, userid

        async for message in channel.history(after=event_message):
            sub_messages.append(message)

        for message in sub_messages:
            for reaction in message.reactions:
                if reaction.emoji != "🔥":
                    continue

                for user in reaction.users():
                    if user.bot:
                        continue

                    reactors[message] += user

        embed.add_field(name="users who've already reacted!", value=" ")
        await sent_message.edit(embed=embed)
        users_reacted = []       
        user_str = []
        for message, users in reactors.items():
            for user in users:
                if user in users_reacted:
                    for reaction in message.reactions:
                        if reaction.emoji != "🔥":
                            continue
                        reaction.remove(user) 
                    remove_reaction(self, message.id)
                    
                    embed.set_field_at(0, "users who've already reacted!", value="\n".join(user_str))
                    await sent_message.edit(embed=embed)
                else:
                    users_reacted.append(user)
                    user_str.append(user.name)

        submissions = await fetch_submissions(self, ctx.guild.id)
        for submission in submissions:
            if submission.reactions < 0:
                await ctx.send("negative reactions found clearing all reactions and reseting reactions back to zero!")
                await to_zero(self, submission.messageId)
                for message in reactors.keys():
                    for reaction in  message.reactions:
                        if reaction.emoji != "🔥":
                            continue

                        for user in reaction.users():
                            if not user.bot:
                                await reaction.remove(user)
                        

        await ctx.send("For the information of these users, Your respective reactions have been removed if you've already reacted\
        \n if you'd like feel free to re add your reaction to your favorite submission! \n any and all negative points have been reverted back to zero!")
        


    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload_submission(self, ctx: commands.Context, channel: disnake.TextChannel) -> None:
        config = await fetch_config(self, ctx.guild.id)
        event = await fetch_event(self, ctx.guild.id)
        submissions = await fetch_submissions(self, ctx.guild.id)

        msg = await  ctx.send("Reloading submissions:")
        

        async for message in channel.history(after=self.bot.get_message(event.messageId)):
            if message.author.bot:
                continue

            if not config or not event or message.channel.id != config.channel:
                continue

            if len(message.attachments) == 0:
                continue

            for submission in submissions:
                if message.id  == submission.messageId:
                    continue

            await message.add_reaction("🔥")

            await add_submssion(self, message.guild.id, message.id, message.author.id)
            msg = await msg.edit(msg.content + f"\nadded: {message.author.name}")
            
        await msg.edit(msg.content + "\n added submissions sucessfully")


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


        submissions = sorted(submissions, key=lambda x: x.reactions, reverse=True)
        ret_val = "```"
        for index, submission in enumerate(submissions):
            ret_val += f"#{index + 1} {self.bot.get_user(submission.userId)} with {submission.reactions} points \n"
        ret_val += "\n```"
        await ctx.reply(ret_val)
    
    @commands.slash_command(name="event_leaderboard", description="shows the event leaderboard")
    async def event_leaderboard_slash(self, inter: disnake.ApplicationCommandInteraction):
        event = await fetch_event(self, inter.guild.id)
        if not event:
            await inter.response.send_message("No event going on right now sorry!")
            return
 
        submissions: list[Submission] = await fetch_submissions(self, inter.guild.id)

        submissions = sorted(submissions, key=lambda x: x.reactions, reverse=True)
        ret_val = "```"
        for index, submission in enumerate(submissions):
            ret_val += f"#{index + 1} {self.bot.get_user(submission.userId)} with {submission.reactions} points \n"
        ret_val += "\n```"       
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
                        break

            # check  for the other messages to see if the reactor has already reacted 
            for ereaction in msg.reactions:
                if ereaction.emoji == "🔥" and msg != reaction.message:
                    try:
                        await ereaction.remove(user)
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
