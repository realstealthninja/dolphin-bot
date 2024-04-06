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
    
    async def _gen_gif(self, image: str, avatar: BytesIO, location: tuple[int, int]):
        gif = Image.open(f"./assets/gifs/{image}")
        avatar = Image.open(avatar)
        
        new = []
        for i in range(gif.n_frames):
            gif.seek(i)
            frame = Image.new('RGBA', gif.size)
            frame.paste(avatar, location)
            new.append(frame)
        
        if len(gif.n_frames) > 1:
            new[0].save(image, format="GIF", save_all=True, append_images=new[1:], loop=0, delay=0)
        else:
            new[0].save(image, format="PNG")

    async def _gen_gwab(self, ctx: commands.Context | disnake.ApplicationCommandInteraction, user):
        await self._gen_gif("gwwab.png", await user.avatar.with_size(64).read(), (57, 37))
        if isinstance(ctx, commands.Context):
            await ctx.reply(file=disnake.File(fp="gwwab.png"))
        else:
            await ctx.followup.send(file=disnake.File(fp="gwwab.png"))

    async def _gen_bonk(self, ctx: commands.Context | disnake.ApplicationCommandInteraction, user):
        await self._gen_gif("bonk.gif", await user.avatar.with_size(256).read(), (400, 180))
        if isinstance(ctx, commands.Context):
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

    @commands.command(description="glitches the bot")
    @commands.cooldown(1, 5, commands.BucketType.user)
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
        await inter.followup.send(message)
        for i in range(10):
            await inter.edit_original_message(content=message + "m"*i)
            await asyncio.sleep(0.1)
        for i in range(4):
            await inter.edit_original_message(content="rebooting" + "."*i)
            await asyncio.sleep(0.5)
        await inter.delete_original_message()
    
    @commands.command(description="bonks a givent user")
    async def bonk(self, ctx: commands.Context, reciver: disnake.Member = None):
        """Bonks a given user"""
        await ctx.trigger_typing()
        if not reciver:
            await self._gen_bonk(ctx, ctx.author)
            return
        if reciver.id == self.bot.user.id:
            if(random.choice([True, False])):
                await ctx.reply("I won't bonk myself")
            else:
                await self._gen_bonk(ctx, self.bot.user)
                await ctx.send("Ow~ that hurts, y'know?")
        else:
            await self._gen_bonk(ctx, reciver)
    
    @commands.slash_command(name="bonk", description="bonks a given user")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bonk_slash(self, inter: disnake.ApplicationCommandInteraction, reciver: disnake.Member = None):
        await inter.response.defer()
        if not reciver:
            await self._gen_bonk(inter, inter.author)
            return
        if reciver.id == self.bot.user.id:
            if(random.choice([True, False])):
                await inter.response.send_message("I won't bonk myself")
            else:
                await self._gen_bonk(inter, self.bot.user)
                await inter.followup.send("Ow~ that hurts, y'know?")
        else:
            await self._gen_bonk(inter, reciver)

    @commands.slash_command(name="gwwab", description="grabs a given user")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def grab_slash(self, inter: disnake.ApplicationCommandInteraction, gwwabee: disnake.Member = None):
        await inter.response.defer()
        if not gwwabee:
            await self._gen_grab(inter, inter.author)
            return
        if gwwabee.id == self.bot.user.id:
            if(random.choice([True, False])):
                await inter.response.send_message("I won't gwwab myself 😡")
            else:
                await self._gen_grab(inter, self.bot.user)
                await inter.followup.send("Stop gwwabing me 😡")
        else:
            await self._gen_grab(inter, gwwabee)

    @commands.commadn(name="gwwab", description="grabs a given user")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def grab_text(self, inter: disnake.ApplicationCommandInteraction, gwwabee: disnake.Member = None):
        await inter.response.defer()
        if not gwwabee:
            await self._gen_grab(inter, inter.author)
            return
        if gwwabee.id == self.bot.user.id:
            if(random.choice([True, False])):
                await inter.response.send_message("I won't gwwab myself 😡")
            else:
                await self._gen_grab(inter, self.bot.user)
                await inter.followup.send("Stop gwwabing me 😡")
        else:
            await self._gen_grab(inter, gwwabee)


def setup(bot: DolphinBot):
    bot.add_cog(Misc(bot))
