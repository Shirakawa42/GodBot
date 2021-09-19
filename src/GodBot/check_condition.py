"""This file is used by HandleMessage() to check if a condition is true or not"""


import re

from discord.ext import commands


def match(str1, str2):
    "check if str1 match with str2, support regex"
    if str2 in str1:
        return True
    try:
        str2 = re.compile(str2)
        if str2.match(str1) is not None:
            return True
    except re.error:
        print("Regex not valid")
    return False


def msg_text(subject, message):
    "Return which part of the message is used depending on what is the subject"
    if subject == 'author':
        return message.author
    if subject == 'message':
        return message.content
    return message.content


def is_condition_true(condition, message):
    "Check if given condition in true or not when applied to the message"
    for subject in condition[0]:
        msg_content = msg_text(subject, message)
        for cmp_f in condition[1]:
            cmp_func = COMPARE_FUNCS[cmp_f]
            if not cmp_func(str(msg_content), str(condition[2][0])):
                return False
    return True


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


COMPARE_FUNCS = {
        'equal': str.__eq__,
        'match': match,
        'startswith': str.startswith,
        'endswith': str.endswith
}
