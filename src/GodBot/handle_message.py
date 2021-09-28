"""This file is used by GodBot() to handle messages and commands from users"""


from discord.ext import commands
from discord.message import Message

from GodBot.check_condition import is_condition_true, execute_action
from GodBot.exceptions import WrongInput
from GodBot.parser_functions import parse_grammar
from GodBot.parser_grammars import GRAMMAR_COMMAND_WHEN
from GodBot.postgresql import db_command
from GodBot.when_class import When


class HandleMessage(commands.Cog):

    """This class is used by GodBot() to handle messages and commands from users"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.whens = []
        db_whens = db_command("select * from whens")
        for db_when in db_whens:
            db_when["subjects"] = db_when["subjects"].split("|")
            db_when["comparators"] = db_when["comparators"].split("|")
            db_when["actions"] = db_when["actions"].split("|")
            self.whens.append(When(*db_when))

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        "Handle any messages sent by users by checking current conditions and apply actions"
        if message.author == self.bot.user:
            return
        for when in self.whens:
            if is_condition_true(when.subjects, when.comparators, when.cmp_param, message):
                await execute_action(when.actions, when.action_param, message)

    @commands.command("reset")
    async def reset(self, ctx: commands.Context):
        "!reset: Delete every rules made with !when command"
        self.whens = []
        db_command("delete from whens")
        await ctx.message.channel.send("Every !when reseted")

    @commands.command("when")
    @parse_grammar(GRAMMAR_COMMAND_WHEN)
    async def when(self, ctx: commands.Context, subjects: list[str], comparators: list[str],
                   cmp_param: str, actions: list[str], actions_param):
        """
        !when subject comparator text action text: Create a rule
        example 1: !when message equal "nice" react ":+1:"
        example 2: !when author match "42" send "je t'aime"
        example 3: !when message match "insulte" delete
        """
        del ctx
        for action in actions:
            if action != "delete" and actions_param == "":
                raise WrongInput(f"{action} needs a parameter")
        when = When(subjects, comparators, cmp_param, actions, actions_param)
        self.whens.append(when)
        db_command("insert into whens values (%s, %s, %s, %s, %s)", when.tuple)

    @commands.command("whens")
    async def whens_cmd(self, ctx):
        "Show all !when"
        whens_str = "```"
        for when in self.whens:
            whens_str += ' - '.join(when.tuple) + "\n"
        whens_str += "```"
        if len(self.whens) > 0:
            await ctx.message.channel.send(whens_str)
        else:
            await ctx.message.channel.send("```No whens```")
            