import disnake
from disnake.ext import commands

from .objects import Config

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from sqlalchemy.dialects.sqlite import insert


class dropdown(disnake.ui.ChannelSelect):
    def __init__(
        self,
        ctx: commands.Context,
        channel: str,
        session: async_sessionmaker[AsyncSession],
    ):
        self.ctx = ctx
        self.session = session
        self.channel = channel

        super().__init__(
            placeholder=f"select {self.channel} channel",
            channel_types=[disnake.ChannelType.text],
            max_values=1,
            min_values=1,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        async with self.session() as conn:
            if self.channel == "announcement":
                res = (
                    insert(Config)
                    .values(
                        guild_id=interaction.guild_id,
                        announcement_channel=interaction.resolved_values[0].id,
                    )
                    .on_conflict_do_update(
                        index_elements=[Config.guild_id],
                        set_=dict(
                            announcement_channel=interaction.resolved_values[
                                0
                            ].id
                        ),
                    )
                )
            else:
                res = (
                    insert(Config)
                    .values(
                        guild_id=interaction.guild_id,
                        sub_channel=interaction.resolved_values[0].id,
                    )
                    .on_conflict_do_update(
                        index_elements=[Config.guild_id],
                        set_=dict(
                            sub_channel=interaction.resolved_values[0].id
                        ),
                    )
                )
            await conn.execute(res)
            await conn.commit()

        await interaction.response.send_message(
            f"set {self.channel} channel to be \
                {interaction.resolved_values[0].mention}"
        )


class ChannelSelectView(disnake.ui.View):
    def __init__(
        self, ctx: commands.Context, session: async_sessionmaker[AsyncSession]
    ):
        self.ctx = ctx
        super().__init__(timeout=None)
        self.add_item(dropdown(ctx, "announcement", session))
        self.add_item(dropdown(ctx, "submission", session))

    async def interaction_check(
        self, interaction: disnake.MessageInteraction
    ) -> bool:
        return interaction.author == self.ctx.author
