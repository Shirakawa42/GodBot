"""This file contains the commands grammar used by the parser"""


from parsimonious.grammar import Grammar

from GodBot.parser_functions import str_to_regex


GRAMMAR_BASIC_RULE = {
    "any": """(~'\\s*".*?"' / ~"\\s*[A-Za-z0-9]+")""",
    "nb": '''~"\\s+[0-9]+"''',
    "multiple": """(any / (~"\\s*\\(" any (~"\\s*&" any)* ")"))"""
    }

GRAMMAR_COMMAND_WHEN = Grammar(f"""
    validator = "!when" when_subjects when_comparators any when_actions any?
    any = {GRAMMAR_BASIC_RULE["any"]}
    when_subjects = {GRAMMAR_BASIC_RULE["multiple"]}
    when_comparators = {GRAMMAR_BASIC_RULE["multiple"]}
    when_actions = {GRAMMAR_BASIC_RULE["multiple"]}
""")

GRAMMAR_COMMAND_INITPLAYER = Grammar(f"""
    validator = "!initPlayer" any
    any = {GRAMMAR_BASIC_RULE["any"]}
""")

GRAMMAR_COMMAND_ATTACK = Grammar(f"""
    validator = "!attack" any
    any = {GRAMMAR_BASIC_RULE["any"]}
""")

GRAMMAR_COMMAND_BUILDSHIP = Grammar(f"""
    validator = "!buildShip" any nb nb nb
    any = {GRAMMAR_BASIC_RULE["any"]}
    nb = {GRAMMAR_BASIC_RULE["nb"]}
""")

GRAMMAR_COMMAND_SEND = Grammar(f"""
    validator = "!send" any ((money nb) / (ship any))
    any = {GRAMMAR_BASIC_RULE["any"]}
    nb = {GRAMMAR_BASIC_RULE["nb"]}
    money = {str_to_regex("money")}
    ship = {str_to_regex("ship")}
""")
