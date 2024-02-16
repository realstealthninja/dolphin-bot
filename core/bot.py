# sys
import os
import asyncio

# constants
from .constants import (
        BOT_TOKEN
)

# db
from sqlalchemy import Column

# disnake
from disnake.ext.commands import Bot
from disnake.ext.tasks import loop
from disnake import (
     Intents,
     Activity,
     ActivityType
)


class DolphinBot(Bot):
    def __init__(self):
        super().__init__(
            command_prefix="db/",
            intents=Intents.all(),
            case_insensitive=True,
            help_command=None,
            owner_ids=[521226389559443461, 298043305927639041],
        )
        self.COGS: list = list()
        self.seasonal = None

        for file in os.listdir("./cogs/"):
            if not file.startswith("_"):
                self.COGS.append(f"cogs.{file}")

    def setup(self) -> None:
        print("-----cogs-----")
        print(", ".join(self.COGS))
        for file in self.COGS:
            if file.endswith("py"):
                self.load_extension(f"{file[:-3]}")
        self.load_extension("jishaku")

    @loop(seconds=540)
    async def update_presence(self) -> None:
        await self.change_presence(
                activity=Activity(
                    type=ActivityType.listening,
                    name="JustADolphin",
                )
        )
        await asyncio.sleep(180)
        await self.change_presence(
            activity=Activity(
                type=ActivityType.watching,
                name="for db/"
            )
        )

    async def on_ready(self) -> None:
        self.update_presence.start()

    def run(self) -> None:
        self.setup()
        super().run(BOT_TOKEN, reconnect=True)


