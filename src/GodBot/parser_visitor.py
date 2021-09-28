"""Contains the Visitor used by parsimonous"""


from typing import Union
from parsimonious.nodes import NodeVisitor, Node

from GodBot.exceptions import WrongInput


WHEN_SUBJECTS = ["message", "author"]
WHEN_ACTIONS = ["send", "delete", "react"]
WHEN_CMPS = ["equal", "startswith", "endswith", "match"]
SEND_WORDS = ["ship", "money"]


def format_treevisitor_str(treevisitor_str: str):
    """
    Transform a string like "(message & author)" into ["message", "author"]
    or "(message)" into ["message"]
    """
    if not treevisitor_str.startswith("("):
        return [treevisitor_str]
    treevisitor_str = treevisitor_str.removeprefix("(").removesuffix(")")
    if "&" in treevisitor_str:
        word_list = treevisitor_str.split("&")
        for i, _ in enumerate(word_list):
            word_list[i] = word_list[i].strip('" ')
        return word_list
    return [treevisitor_str.strip().removeprefix('"').removesuffix('"')]


class TreeVisitor(NodeVisitor):
    """Format the tree obtained by grammar.parse()"""
    @staticmethod
    def visit_validator(node: Node, visited_children: list[Union[Node, int]]):
        """ Returns the overall output. """
        del node
        output = []
        for child in visited_children:
            output.append(child)
        output.pop(0)
        return output

    @staticmethod
    def visit_nb(node: Node, visited_children: list[Union[Node, int]]):
        """ Return an int when it's a number node """
        del visited_children
        return int(node.text)

    @staticmethod
    def visit_when_actions(node: Node, visited_children: list[Union[Node, int]]):
        """ Check if action is valid """
        del visited_children
        actions = format_treevisitor_str(node.text.strip())
        for action in actions:
            if action not in WHEN_ACTIONS:
                raise WrongInput(f"action '{action}' is not inside WHEN_ACTIONS")
        return actions

    @staticmethod
    def visit_when_comparators(node: Node, visited_children: list[Union[Node, int]]):
        """ Check if comparator is valid """
        del visited_children
        comparators = format_treevisitor_str(node.text.strip())
        for comparator in comparators:
            if comparator not in WHEN_CMPS:
                raise WrongInput(f"comparator '{comparator}' is not inside WHEN_CMPS")
        return comparators

    @staticmethod
    def visit_when_subjects(node: Node, visited_children: list[Union[Node, int]]):
        """ Check if subject is valid """
        del visited_children
        subjects = format_treevisitor_str(node.text.strip())
        for subject in subjects:
            if subject not in WHEN_SUBJECTS:
                raise WrongInput(f"subject '{subject}' is not inside WHEN_SUBJECTS")
        return subjects

    @staticmethod
    def visit_send_word(node: Node, visited_children: list[Union[Node, int]]):
        """ Check if subject is valid """
        del visited_children
        send_word = node.text.strip().removeprefix('"').removesuffix('"')
        if send_word not in SEND_WORDS:
            raise WrongInput(f"Word '{send_word}' is not inside SEND_WORDS")
        return send_word

    @staticmethod
    def generic_visit(node: Node, visited_children: list[Union[Node, int]]):
        """ The generic visit method. """
        del visited_children
        return node.text.strip().removeprefix('"').removesuffix('"')
