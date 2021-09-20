"""This file contains the commands grammar used by the parser"""


from parsimonious.grammar import Grammar
from GodBot.parser_functions import grammar_maker


WHEN_SUBJECTS = ["message", "author"]
WHEN_ACTIONS = ["send", "delete", "react"]
WHEN_ACTIONS_NO_TEXT = ["delete"]
WHEN_CMPS = ["equal", "startswith", "endswith", "match"]
GRAMMAR_COMMAND_WHEN = Grammar(grammar_maker(
    "!when", "multi", [WHEN_SUBJECTS], "multi", [WHEN_CMPS], "any", "or",
    [["multi", [WHEN_ACTIONS], "any"], [WHEN_ACTIONS_NO_TEXT]]))

GRAMMAR_COMMAND_INITPLAYER = Grammar(grammar_maker("!initPlayer", "any"))

GRAMMAR_COMMAND_ATTACK = Grammar(grammar_maker("!attack", "any"))

GRAMMAR_COMMAND_BUILDSHIP = Grammar(grammar_maker("!buildShip", "any", "nb", "nb", "nb"))
