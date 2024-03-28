import disnake
from disnake.ext import commands
import random
import asyncio
from core import DolphinBot
from PIL import Image
from io import BytesIO

class Misc(commands.Cog):
    def __init__(self, bot: DolphinBot):
        self.bot = bot

    async def _gen_gif(self, ctx: commands.Context | disnake.ApplicationCommandInteraction, user):
        gif = Image.open("./assets/gifs/bonk.gif")
        avatar: BytesIO = BytesIO(await user.avatar.with_size(256).read())
        avatar = Image.open(avatar)
        new: list[Image.Image] = []
        for i in range(gif.n_frames):
            gif.seek(i)
            frame = Image.new('RGBA', gif.size)
            frame.paste(gif)
            frame.paste(avatar, (400, 180))
            new.append(frame)
        new[0].save("bonk.gif", format="GIF", save_all=True, append_images=new[1:], loop=0, delay=0.1)
        if ctx is commands.Context:
            await ctx.reply(file=disnake.File(fp="bonk.gif"))
        else:
            await ctx.followup.send(file=disnake.File(fp="bonk.gif"))

    @commands.command(description="returns the ping of the bot")
    async def ping(self, ctx: commands.Context):
        """returns the ping of the bot"""
        return await ctx.reply(
            embed=disnake.Embed(
                title="Pong! :ping_pong:", description=f"{round(self.bot.latency * 1000)} ms",
                color=disnake.Color.blurple()
            )
        )

    @commands.slash_command(name="ping", description="shows ping of the bot")
    async def ping_slash(self, inter: disnake.ApplicationCommandInteraction) -> None:
        return await inter.response.send_message(
            embed=disnake.Embed(
                title="Pong! :ping_pong:", description=f"{round(self.bot.latency * 1000)} ms",
                color=disnake.Color.blurple()
            )
        )

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.content.find("db/") != -1:
            return
        if message.author.id == 922001668437061712 and message.content == "ded chat":
            await message.reply("You know saying dead chat doesnt do anything right?")
        elif len(message.stickers) > 0 and message.stickers[0].name == "Grab":
            msgs = ["you know they don't like getting grabbed.", "please stop grabbing people without consent!", "That poor cat"]
            await message.reply(random.choice(msgs))
        elif self.bot.user.mentioned_in(message):
            msgs = [
                "Hi how can i help you? try db/help!",
                "Hello!",
                f":3 \nugh {self.bot.get_user(922001668437061712).mention} why do you make me do this?",
                "Did someone ping me?",
                "Need something?",
                "You should stream Aejisei's music while you look at my commands\n [link](https://open.spotify.com/artist/4J45U4EhxTBWKNe28ASAaD)"
            ]
            await message.reply(random.choice(msgs))

    @commands.command(description="glitches the bot")
    async def glitch(self, ctx: commands.Context):
        """Glitches out the bot do not use"""
        message = "Hey dont do that co"
        await ctx.trigger_typing()
        m  = await ctx.reply("Hey dont do that co")
        for i in range(10):
            await m.edit(content=message + "m"*i)
            await asyncio.sleep(0.1)
        for i in range(4):
            await m.edit(content="rebooting" + "."*i)
            await asyncio.sleep(0.5)
        await m.delete()
    
    @commands.slash_command(name="glitch", description="glitches the bot please do not use this command")
    async def glitch_slash(self, inter: disnake.ApplicationCommandInteraction):
        message = "Hey dont do that co"
        await inter.response.defer()
        await inter.response.send_message("Hey dont do that co")
        for i in range(10):
            await inter.response.edit_message(content=message + "m"*i)
            await asyncio.sleep(0.1)
        for i in range(4):
            await inter.response.edit_message(content="rebooting" + "."*i)
            await asyncio.sleep(0.5)
        await inter.delete_original_message()
    
    @commands.command(description="bonks a givent user")
    async def bonk(self, ctx: commands.Context, reciver: disnake.Member = None):
        """Bonks a given user"""
        await ctx.trigger_typing()
        if not reciver:
            await self._gen_gif(ctx, ctx.author)
            return
        if reciver.id == self.bot.user.id:
            if(random.choice([True, False])):
                await ctx.reply("I won't bonk myself")
            else:
                await self._gen_gif(ctx, self.bot.user)
                await ctx.send("Ow~ that hurts, y'know?")
        else:
            await self._gen_gif(ctx, reciver)
    
    @commands.slash_command(name="bonk", description="bonks a given user")
    async def bonk_slash(self, inter: disnake.ApplicationCommandInteraction, reciver: disnake.Member = None):
        await inter.response.defer()
        if not reciver:
            await self._gen_gif(inter, inter.author)
            return
        if reciver.id == self.bot.user.id:
            if(random.choice([True, False])):
                await inter.response.send_message("I won't bonk myself")
            else:
                await self._gen_gif(inter, self.bot.user)
                await inter.followup.send("Ow~ that hurts, y'know?")
        else:
            await self._gen_gif(inter, reciver)


def setup(bot: DolphinBot):
    bot.add_cog(Misc(bot))
