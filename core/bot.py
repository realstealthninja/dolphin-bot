#sys
import os
import asyncio
from datetime import datetime


# constants
from .constants import BOT_TOKEN

from .constants import SPOTIFY_TOKEN
from .constants import SPOTIFY_ID

# spotify
import spotify
from spotify import Track


# db
from sqlalchemy.ext.asyncio import create_async_engine

# disnake
from disnake.ext.commands import Bot
from disnake.ext import commands
from disnake.ext.tasks import loop
from disnake import Intents, Activity, ActivityType

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

class DolphinBot(Bot):
    def __init__(self):
        super().__init__(
            command_prefix="db/",
            intents=Intents.all(),
            case_insensitive=True,
            help_command=None,
            command_sync_flags=command_sync_flags,
            owner_ids=[521226389559443461, 298043305927639041],
        )
        self.COGS: list = list()
        self.seasonal = None
        self.loop.create_task(self.connect_engines())

        for file in os.listdir("./cogs/"):
            if not file.startswith("_"):
                self.COGS.append(f"cogs.{file}")

    def setup(self) -> None:
        print("-----cogs-----")
        print(", ".join(self.COGS))
        for file in self.COGS:
            if file.endswith("py"):
                self.load_extension(f"{file[:-3]}")
            else:
                self.load_extension(file)
        self.load_extension("jishaku")

    @loop(seconds=600)
    async def update_presence(self) -> None:
        async with spotify.Client(SPOTIFY_ID, SPOTIFY_TOKEN) as r:
            aeji = await r.get_artist("4J45U4EhxTBWKNe28ASAaD")
            tracks: list[Track] = await aeji.top_tracks()
            for track in tracks:
                await self.change_presence(activity=Activity(
                    name = track.name,
                    type = ActivityType.listening,
                    ))
                await asyncio.sleep(120)
                await self.change_presence(activity=Activity(
                    name="db/help for help",
                    type=ActivityType.watching
                ))
    
    # check if someone is not using slash commands
    async def bot_check(self, ctx: commands.Context) -> bool:
        if ctx.author.id == 672824404702527509:
            return False
        

    async def connect_engines(self):
        self.seasonal = create_async_engine(
            "sqlite+aiosqlite:///db/seasonal.db", echo=True
        )
        print("connected engine")

    async def on_ready(self) -> None:
        self.update_presence.start()

    def run(self) -> None:
        self.setup()
        super().run(BOT_TOKEN, reconnect=True)
