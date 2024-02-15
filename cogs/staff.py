import disnake
from disnake.ext import commands

from core import DolphinBot

class Staff(commands.Cog):
    def __init__(self, bot: DolphinBot):
        self.bot = bot
    
    @commands.command(hidden=True)
    async def reload(self):
        pass