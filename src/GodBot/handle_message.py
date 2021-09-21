"""This file is used by GodBot() to handle messages and commands from users"""


import json
import os.path
from pathlib import Path

from discord.ext import commands
import parsimonious
from GodBot.check_condition import is_condition_true, execute_action
from GodBot.parser_functions import formated_tree_from_grammar
from GodBot.parser_grammars import GRAMMAR_COMMAND_WHEN


class HandleMessage(commands.Cog):

    """This class is used by GodBot() to handle messages and commands from users"""

    def __init__(self, bot):
        self.bot = bot
        try:
            self.load_json()
        except FileNotFoundError:
            self.whens = []

    def save_in_json(self):
        "save !when in a json"
        with open(os.path.join(Path.home(), "whens.json"), "w",
                  encoding="utf-8") as when_commands_file:
            json.dump(self.whens, when_commands_file)

    def load_json(self):
        "load !when json"
        with open(os.path.join(Path.home(), "whens.json"), "r",
                  encoding="utf-8") as when_commands_file:
            self.whens = json.load(when_commands_file)

    @commands.Cog.listener()
    async def on_message(self, message):
        "Handle any messages sent by users by checking current conditions and apply actions"
        if message.author == self.bot.user:
            return
        for when in self.whens:
            if is_condition_true([when[1], when[2], when[3]], message):
                if len(when[4]) > 1:
                    await execute_action([when[4][:-1:], when[4][-1::]], message)
                else:
                    await execute_action([when[4], when[4]], message)

    @commands.command("reset")
    async def reset(self, ctx):
        "!reset: Delete every rules made with !when command"
        self.whens = []
        self.save_in_json()
        await ctx.message.channel.send("Every !when reseted")

    @commands.command("when")
    async def when(self, ctx):
        """
        !when subject comparator text action text: Create a rule
        example 1: !when message equal "nice" react ":+1:"
        example 2: !when author match "42" send "je t'aime"
        example 3: !when message match "insulte" delete
        """
        try:
            formated_tree = formated_tree_from_grammar(GRAMMAR_COMMAND_WHEN, ctx.message.content)
            self.whens.append(formated_tree)
            self.save_in_json()
        except parsimonious.exceptions.ParseError:
            await ctx.message.channel.send("error, use \"!help when\"")
