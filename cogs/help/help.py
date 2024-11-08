from datetime import datetime
from typing import Mapping

import disnake
from disnake.ext import commands


class HelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping: Mapping):
        groups = "***:notes: GROUPS :notes:***\n```md\n# Misc\n# Help\n# Staff\n# Seasonal```"
        await self.context.trigger_typing()
        embed = (
            disnake.Embed(
                title="** Help command **",
                description="```toml\n[do db/help <extension> to learn more about <extension>]```",
                timestamp=datetime.now()
            )
            .set_author(name="helping is nice")
            .set_footer(
                text=self.context.author.display_name,
                icon_url=self.context.author.display_avatar.url,
            )
            .add_field(name=" ", value=groups, inline=False)
        )

        await self.context.send(embed=embed)

    async def send_command_help(self, command):
        if not command.description:
            command.description = "``"
        embed = (
            disnake.Embed(timestamp=datetime.now())
            .set_author(name="Help", icon_url=self.context.author.avatar)
            .add_field(
                name="> Name <",
                value=f"`{command.qualified_name}`",
                inline=False,
            )
        )
        if command.aliases:
            command.aliases = ", ".join(command.aliases)
            embed.add_field(
                name="\\> Aliases <", value=f"`{command.aliases}`", inline=False
            )
            embed.add_field(
                name="\\> usage <",
                value=f"`db/{command.name + command.signature}\\`"
                if command.signature
                else f"`db/{command.name}\\`",
                inline=False,
            )
        embed.add_field(
            name="\\> Description <",
            value=f"{command.description}",
            inline=False,
        )
        embed.set_footer(text="<argument> required │ [argument] optional")
        await self.context.send(embed=embed)
    
    async def send_cog_help(self, cog: commands.Cog):
        embed= disnake.Embed(
            title=cog.qualified_name,
            description=cog.description,
            timestamp=datetime.now(),
        )

        value = "```md\n# COMMANDS\n\n"
        for command in cog.get_commands():
            if command.hidden:
                continue
            value += f"- {command.name}: {command.description} \n"
        embed.add_field(name=" ", value=value+"```", inline=False)
        return await self.context.send(embed=embed)
