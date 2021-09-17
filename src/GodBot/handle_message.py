"""This file is used by GodBot() to handle messages and commands from users"""


import json
from pathlib import Path

from discord.ext import commands
import parsimonious
from check_condition import is_condition_true
from parser_functions import format_tree_list, tree_reader
from parser_grammars import grammar_command_when


class HandleMessage(commands.Cog):

    """This class is used by GodBot() to handle messages and commands from users"""

    def __init__(self, bot):
        self.bot = bot
        try:
            with open(str(Path.home())+"/whens.json", "r", encoding="utf-8") as when_commands_file:
                whens_command_data = json.load(when_commands_file)
                self.whens = whens_command_data
        except FileNotFoundError:
            self.whens = []

    @staticmethod
    async def execute_action(action_list, message):
        "Execute all actions in the action_list on the message / message channel"
        for action in action_list[0]:
            try:
                if action == 'send':
                    await message.channel.send(action_list[1][0])
                elif action == 'delete':
                    await message.delete()
                elif action == 'react':
                    await message.add_reaction(action_list[1][0])
            except commands.MessageNotFound:
                print("Message does not exist or have already been deleted")

    @commands.Cog.listener()
    async def on_message(self, message):
        "Handle any messages sent by users by checking current conditions and apply actions"
        if message.author == self.bot.user:
            return
        for when in self.whens:
            if is_condition_true([when[1], when[2], when[3]], message):
                await HandleMessage.execute_action([when[4][:-1:], when[4][-1::]], message)

    @commands.command("reset")
    async def reset(self, ctx):
        "Handle the '!reset' command"
        with open(str(Path.home())+"/whens.json", "w", encoding="utf-8") as when_commands_file:
            json.dump([], when_commands_file)
        self.whens = []
        await ctx.message.channel.send("Every !when reseted")

    @commands.command("when")
    async def when(self, ctx):
        "Handle the '!when' command"
        try:
            parser = grammar_command_when.parse(ctx.message.content)
            tree_list = tree_reader(parser)
            formated_tree = format_tree_list(tree_list)
            self.whens.append(formated_tree)
            with open(str(Path.home())+"/whens.json", "w", encoding="utf-8") as when_commands_file:
                json.dump(self.whens, when_commands_file)
        except parsimonious.exceptions.ParseError as error:
            await ctx.message.channel.send(error)
