"""
This is the main file to use, create an instance of GodBot()
and call GodBot.start_bot() to start the bot
"""

import os

from discord.ext import commands
from dotenv import load_dotenv
from handle_rpg_commands import RpgCommands
from handle_message import HandleMessage


class NoEnvException(Exception):
    "Exception raised when .env file not found or no DISCORD_TOKEN found"


class GodBot(commands.Bot):
    "This class contain everything related to the bot initialisation"
    def __init__(self):
        super().__init__(command_prefix="!")
        load_dotenv()
        self.bot_token = os.getenv("DISCORD_TOKEN")
        if self.bot_token is None:
            raise NoEnvException(".env file not found or DISCORD_TOKEN not inside the file")
        self.add_cog(HandleMessage(self))
        self.add_cog(RpgCommands(self))

    def start_bot(self):
        "Start the bot"
        self.run(self.bot_token)


BOT = GodBot()
BOT.start_bot()
