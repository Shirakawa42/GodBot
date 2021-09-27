"""
This is the main file to use, create an instance of GodBot()
and call GodBot.start_bot() to start the bot
"""

import os

from discord.ext import commands
from dotenv import load_dotenv
from GodBot.handle_rpg_commands import RpgCommands
from GodBot.handle_message import HandleMessage
from GodBot.exceptions import NoEnvException


class GodBot(commands.Bot):
    "This class contain everything related to the bot initialisation"
    def __init__(self):
        super().__init__(command_prefix="!")
        load_dotenv()
        self.bot_token = os.getenv("DISCORD_TOKEN")
        if self.bot_token is None:
            raise NoEnvException("DISCORD_TOKEN")
        self.add_cog(HandleMessage(self))
        self.add_cog(RpgCommands(self))

    def start_bot(self):
        "Start the bot"
        self.run(self.bot_token)
