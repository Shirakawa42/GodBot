""" Bot Command Parser """


from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError

from GodBot.parser_visitor import TreeVisitor


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


def str_to_regex(string: str):
    "Modify a string useable in a grammar rule"
    return f'''(~"\\s*{string}" / ~'\\s*"{string}"')'''
