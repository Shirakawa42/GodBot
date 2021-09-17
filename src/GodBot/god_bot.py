"""
This is the main file to use, create an instance of GodBot()
and call GodBot.start_bot() to start the bot
"""


from discord.ext import commands
from handle_message import HandleMessage


class GodBot(commands.Bot):
    "This class contain everything related to the bot initialisation"
    def __init__(self):
        super().__init__(command_prefix="!")
        self.bot_token = "NzQ1NjA4OTExNDkwMzgzOTQz.Xz0QaQ.uTKHwBlmaLy32fcDQItfRARCK9E"
        self.add_cog(HandleMessage(self))

    def start_bot(self):
        "Start the bot"
        self.run(self.bot_token)


BOT = GodBot()
BOT.start_bot()
