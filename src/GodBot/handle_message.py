"""This file is used by GodBot() to handle messages and commands from users"""


from discord.ext import commands
from discord.message import Message

from GodBot.check_condition import is_condition_true, execute_action
from GodBot.parser_functions import parse_grammar
from GodBot.parser_grammars import GRAMMAR_COMMAND_WHEN


def to_list(item: str):
    "Transform a string into a list, if it's something else, return it"
    if isinstance(item, str):
        return [item]
    return item


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
            if is_condition_true(when["subject"], when["comparator"], when["cmp_param"], message):
                await execute_action(when["actions"], when["action_param"], message)

    @commands.command("reset")
    async def reset(self, ctx: commands.Context):
        "!reset: Delete every rules made with !when command"
        self.whens = []
        self.save_in_db()
        await ctx.message.channel.send("Every !when reseted")

    @commands.command("when")
    @parse_grammar(GRAMMAR_COMMAND_WHEN)
    async def when(
        self, ctx: commands.Context, subject: str, comparator: str, cmp_param: str, action: str):
        """
        !when subject comparator text action text: Create a rule
        example 1: !when message equal "nice" react ":+1:"
        example 2: !when author match "42" send "je t'aime"
        example 3: !when message match "insulte" delete
        """
        del ctx
        action = to_list(action)
        if len(action) == 1:
            action.append("")
        self.whens.append({
            "subject": to_list(subject),
            "comparator": to_list(comparator),
            "cmp_param": cmp_param,
            "actions": action[:-1],
            "action_param": action[-1]
        })
