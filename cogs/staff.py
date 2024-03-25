import datetime
import disnake
from disnake.ext import commands

from core import DolphinBot


class Staff(commands.Cog):
    def __init__(self, bot: DolphinBot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True, description="loads an extension")
    async def load(self, ctx: commands.Context, name: str):
        embed: disnake.Embed = disnake.Embed(title=f"loading extension {name}")
        m = await ctx.reply(embed=embed)
        self.bot.load_extension(f"cogs.{name}")
        embed.title = "loaded extension {name} successfully"
        embed.color = disnake.Color.green()
        await m.edit(embed=embed)

    @commands.command(hidden=True)
    async def reload(self, ctx: commands.Context):
        embed: disnake.Embed = disnake.Embed(
            title="reloading extensions",
            description="reloaded:\n",
            timestamp=datetime.datetime.now(),
        )
        embed.set_footer(
            text=ctx.author.display_name,
            icon_url=ctx.author.display_avatar.url,
        )

        message = await ctx.reply(embed=embed)
        await ctx.trigger_typing()
        for cog in tuple(self.bot.extensions):
            self.bot.reload_extension(cog)
            if cog != "jishaku":
                embed.description += f"- {cog[5:]}\n"
            await message.edit(embed=embed)
        embed.set_default_colour(disnake.Color.green())
        embed.title = "reloaded all extensions!"
        await message.edit(embed=embed)
        await message.channel.send("all cogs successfully reloaded")


def setup(bot: DolphinBot):
    bot.add_cog(Staff(bot))
