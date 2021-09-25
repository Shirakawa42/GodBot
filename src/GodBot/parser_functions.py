""" Bot Command Parser """


from typing import Union
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor, Node
from parsimonious.exceptions import ParseError


class TreeVisitor(NodeVisitor):
    """Format the tree obtained by grammar.parse()"""
    @staticmethod
    def visit_validator(node: Node, visited_children: list[Union[Node, int]]):
        """ Returns the overall output. """
        del node
        output = []
        for child in visited_children:
            if isinstance(child, int):
                output.append(child)
            else:
                child = node_visitor(child)
                child = node_words_formatter(child)
                if isinstance(child, str):
                    child = child.strip()
                    child = format_treevisitor_str(child)
                output.append(child)
        return output[1:]

    @staticmethod
    def visit_nb(node: Node, visited_children: list[Union[Node, int]]):
        """ Return an int when it's a number node """
        del visited_children
        return int(node.text)

    @staticmethod
    def generic_visit(node: Node, visited_children: list[Union[Node, int]]):
        """ The generic visit method. """
        del visited_children
        return node


def format_treevisitor_str(treevisitor_str: str):
    """
    Transform a string like "(message & author)" into ["message", "author"]
    or "(message)" into "message"
    """
    treevisitor_str = treevisitor_str.removeprefix("(").removesuffix(")")
    if "&" in treevisitor_str:
        word_list = treevisitor_str.split("&")
        for i , _ in enumerate(word_list):
            word_list[i] = word_list[i].strip('" ')
        return word_list
    return treevisitor_str.strip().removeprefix('"').removesuffix('"')


def node_visitor(node: Node):
    "Visit nodes to find each words instead of an entire rule"
    end_nodes = []
    for child in node.children:
        end_nodes += node_visitor(child)
    if len(node.children) == 0:
        return [node.text.strip().removeprefix('"').removesuffix('"')]
    return end_nodes


def node_words_formatter(node_words: list[str]):
    """Format the list returned by node_visitor()"""
    if len(node_words) == 1:
        return node_words[0]
    node_words = list(filter(lambda word: word not in ["(", ")", "", "&"], node_words))
    return node_words


def formated_tree_from_grammar(grammar: Grammar, input_str: str):
    "Return a formated tree of a grammar with the input"
    tree = grammar.parse(input_str)
    tree_visitor = TreeVisitor()
    return tree_visitor.visit(tree)


def parse_grammar(grammar: Grammar):
    """Decorator that check if grammar is valid or not with the input,
        if not, function is not called and print error"""
    def parse_grammar_dec(function):
        async def new_function(self, ctx):
            try:
                formated_tree = formated_tree_from_grammar(grammar, ctx.message.content)
                await function(self, ctx, *formated_tree)
            except ParseError:
                await ctx.message.channel.send(
                    "Command not well formated, use !help \"command name\"")
        new_function.__doc__ = function.__doc__
        return new_function
    return parse_grammar_dec
