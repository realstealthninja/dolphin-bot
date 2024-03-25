import disnake
from disnake.enums import TextInputStyle
from disnake.ui import Modal


class event_modal(Modal):
    def __init__(self, session):
        self.session = session
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
        ]

        super().__init__(
            title="Create an Event",
            custom_tag="create_event",
            components=components,
        )

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        embed = disnake.Embed(title="Creating Event")
        for key, value in interaction.text_values.items():
            embed.add_field(name=key.capitalize(), value=value, inline=False)
        await interaction.response.send_message(embed=embed)
