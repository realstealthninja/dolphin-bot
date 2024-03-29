import disnake
from disnake.ext import commands
from disnake.ui import View, ChannelSelect

from .utils import add_config

class ChannelSelectView(View):
    def __init__(self, cog: commands.Cog, ctx: commands.context):
        self.cog = cog
        self.ctx = ctx
        super().__init__()

        @disnake.ui.channel_select(
            placeholder="text annoucement/submission channel",
            channel_types=[disnake.ChannelType.text]
        )
        async def callback(
            self,
            select: ChannelSelect,
            inter: disnake.MessageInteraction
        ) -> None:
            await add_config(cog, inter.guild_id, select.values[0].id)
            await inter.repsone.send_message(embed=disnake.Embed(
                title="Configured sucessfully!",
                description="Have fun in the competitions",
                color=disnake.Color.green()
            ))
        
        async def interaction_check(self, inter: disnake.MessageInteraction) -> bool:
            return inter.author == self.ctx.author
