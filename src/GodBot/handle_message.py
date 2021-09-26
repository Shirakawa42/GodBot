"""This file is used by GodBot() to handle messages and commands from users"""


from discord.ext import commands
from discord.message import Message

from GodBot.check_condition import is_condition_true, execute_action
from GodBot.parser_functions import parse_grammar
from GodBot.parser_grammars import GRAMMAR_COMMAND_WHEN


class HandleMessage(commands.Cog):

    """This class is used by GodBot() to handle messages and commands from users"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.whens = []
        #load whens

    def save_in_db(self):
        "save !when in the RDS db"

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        "Handle any messages sent by users by checking current conditions and apply actions"
        if message.author == self.bot.user:
            return
        for when in self.whens:
            if is_condition_true(when["subjects"], when["comparators"], when["cmp_param"], message):
                await execute_action(when["actions"], when["actions_param"], message)

    @commands.command("reset")
    async def reset(self, ctx: commands.Context):
        "!reset: Delete every rules made with !when command"
        self.whens = []
        self.save_in_db()
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
        self.whens.append({
            "subjects": subjects,
            "comparators": comparators,
            "cmp_param": cmp_param,
            "actions": actions,
            "actions_param": actions_param
        })
