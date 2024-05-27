import datetime
import asyncio
import disnake
from disnake.ext import commands

from core import DolphinBot


class Staff(commands.Cog):
    def __init__(self, bot: DolphinBot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        if (await self.bot.is_owner(ctx.author)):
            return True
        else:
            await ctx.send("be owner next time lol")
            return False

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


    @commands.command(hidden=True)
    async def pull(self, ctx: commands.Context):
        embed = disnake.Embed(title="Git pull.", description="")
        git_commands = [["git", "stash"], ["git", "pull", "--ff-only"]]

        for git_command in git_commands:
            process = await asyncio.create_subprocess_exec(
                git_command[0],
                *git_command[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            (output, error) = await process.communicate()
            embed.description += f'[{" ".join(git_command)!r} exited with return code {process.returncode}\n'

            if output:
                embed.description += f"**[stdout]**\n{output.decode()}\n"
            if error:
                embed.description += f"**[stderr]**\n{error.decode()}\n"
        await ctx.reply(embed=embed)


    @commands.command(aliases=["e"], hidden=True)
    async def eval(self, ctx: commands.Context, *, code: str = None) -> None:
        if not code:
            return await ctx.send("...")

        local_variables = {
            "disnake": disnake,
            "commands": commands,
            "bot": ctx.bot,
            "client": ctx.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
        }

        code = clean_code(code)
        stdout = io.StringIO()

        pref = await self.bot.get_prefix(ctx.message)
        message = clean_code(ctx.message.content[len(pref) - 1 :])

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}",
                    local_variables,
                )
                obj = await local_variables["func"]()

                result = f"{stdout.getvalue()}{obj}\n"
        except Exception as e:
            result = "".join(traceback.format_exception(e, e, e.__traceback__))

        result = result.replace("`", "")
        message = message.replace("`", "")
        if result.replace("\n", "").endswith("None") and result != "None":
            result = result[:-5]

        if len(result) < 2000:
            return await ctx.send(f"```py\nIn[0]: {message}\nOut[0]: {result}\n```")

        pager = Paginator(
            timeout=100,
            entries=[result[i : i + 2000] for i in range(0, len(result), 2000)],
            length=1,
            prefix="```py\n",
            suffix="```",
        )
        await pager.start(ctx)

def setup(bot: DolphinBot):
    bot.add_cog(Staff(bot))
