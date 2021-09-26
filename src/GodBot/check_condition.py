"""This file is used by HandleMessage() to check if a condition is true or not"""


import re

from discord.ext import commands
from discord.message import Message


def match(str1: str, str2: str):
    "check if str1 match with str2 using regex"
    try:
        str2_reg = re.compile(str2)
        if str2_reg.match(str1) is not None:
            return True
    except re.error as err_msg:
        print(err_msg)
    return False


def msg_text(subject: str, message: Message):
    "Return which part of the message is used depending on what is the subject"
    if subject == 'author':
        return message.author
    if subject == 'message':
        return message.content
    return message.content


def is_condition_true(
    subjects: list[str], comparators: list[str], cmp_param: str, message: Message):
    "Check if given condition in true or not when applied to the message"
    for subject in subjects:
        msg_content = msg_text(subject, message)
        for cmp_f in comparators:
            cmp_func = COMPARE_FUNCS[cmp_f]
            if not cmp_func(str(msg_content), str(cmp_param)):
                return False
    return True


async def execute_action(actions: list[str], action_param: str, message: Message):
    "Execute all actions in the action_list on the message / message channel"
    for action in actions:
        try:
            if action == 'send':
                await message.channel.send(action_param)
            elif action == 'delete':
                await message.delete()
            elif action == 'react':
                await message.add_reaction(action_param)
        except commands.MessageNotFound as err_msg:
            print(err_msg)


COMPARE_FUNCS = {
        'equal': str.__eq__,
        'match': match,
        'startswith': str.startswith,
        'endswith': str.endswith
}
