from .help import HelpCommand
from core import DolphinBot
from disnake.ext import commands


class Help(commands.Cog, name="help"):
    def __init__(self, bot: DolphinBot):
        self.bot = bot
        self._original_help_command = bot.help_command
        self.bot.help_command = HelpCommand()
        self.bot.help_command.cog = self


def setup(bot: DolphinBot):
    bot.add_cog(Help(bot))
