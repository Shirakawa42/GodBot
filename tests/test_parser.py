""" Parser unit tests """


from GodBot.parser_grammars import GRAMMAR_COMMAND_BUILDSHIP, GRAMMAR_COMMAND_SEND, GRAMMAR_COMMAND_WHEN
from GodBot.parser_visitor import format_treevisitor_str
from GodBot.parser_functions import formated_tree_from_grammar


def test_formated_tree_from_grammar():
    "formated_tree_from_grammar() tests"
    assert formated_tree_from_grammar(GRAMMAR_COMMAND_BUILDSHIP,
    '!buildShip "test ship" 3 2 65') == ['test ship', 3, 2, 65]
    assert formated_tree_from_grammar(GRAMMAR_COMMAND_SEND,
    '!send "player name" money 244') == ['player name', 'money', '244']
    assert formated_tree_from_grammar(GRAMMAR_COMMAND_WHEN,
    '!when message equal "test test" react ":+1:"') == [['message'],
    ['equal'], 'test test', ['react'], ':+1:']


def test_format_treevisitor_str():
    "format_treevisitor_str() tests"
    assert format_treevisitor_str(
        "(message & author & truc & machin)") == ["message", "author", "truc", "machin"]
    assert format_treevisitor_str("(message & author)") == ["message", "author"]
    assert format_treevisitor_str("(message)") == ["message"]
    assert format_treevisitor_str("message") == ["message"]
