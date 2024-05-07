import disnake
from disnake.enums import TextInputStyle
from disnake.ui import Modal

from datetime import datetime
from disnake.ext import commands

from .utils import add_event, fetch_config


class event_modal(Modal):
    def __init__(self, cog):
        self.cog: commands.Cog = cog
        components = [
            disnake.ui.TextInput(
                label="Title",
                placeholder="Beats to beat 1",
                custom_id="title",
                style=TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Description",
                placeholder="lorem ipsum dore amen",
                custom_id="description",
                style=TextInputStyle.paragraph,
            ),
            disnake.ui.TextInput(
                label="Date",
                placeholder="14/03/2007",
                custom_id="date",
                style=TextInputStyle.short,
            ),
        ]

        super().__init__(
            title="Create an Event",
            components=components,
            timeout=300,
        )

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        embed = disnake.Embed(title="Creating Event")
        for key, value in interaction.text_values.items():
            embed.add_field(name=key.capitalize(), value=value, inline=False)
        await interaction.response.send_message(embed=embed)

        channel = await fetch_config(self.cog, interaction.guild_id)

        if not channel:
            await interaction.followup.send(
                embed=disnake.Embed(
                    title="Your server hasn't setup events yet! :x:",
                    color=disnake.Color.red(),
                )
            )
        else:
            embed = disnake.Embed(
                title=interaction.text_values.get("title"),
                description=interaction.text_values.get("description"),
            ).set_footer(text=f"until {interaction.text_values.get('date')}")

            msg = await self.cog.bot.get_channel(channel.channel).send(embed=embed)

            await add_event(
                self.cog,
                datetime.strptime(
                    interaction.text_values.get("date"), "%d/%m/%Y"
                ).timestamp(),
                interaction.guild_id,
                msg.id,
            )
