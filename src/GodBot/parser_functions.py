""" Bot Command Parser """


from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from parsimonious.exceptions import ParseError


def format_rule_list(command_data, validator=False):
    "format a list to be useable in a grammar"
    formated_data = ""
    for data in command_data:
        if formated_data != "":
            formated_data += " / "
        if not validator:
            formated_data += f"""(~"\\s*{data}" / ~'\\s*"{data}"')"""
        else:
            formated_data += f"""{data}"""
    return formated_data


def grammar_validator_rules_linker(grammar_validator, grammar_rules):
    "Format grammar_maker() variables to be useable with Grammar()"
    for rule_name, rule in grammar_rules.items():
        grammar_validator += f"\n{rule_name} = {rule}"
    return grammar_validator


GRAMMAR_BASIC_RULE = {
    "any": """(~'\\s*".*?"' / ~"\\s*\\S+")""",
    "nb": '''~"\\s+[0-9]+"'''
    }


class Counter():
    "Use .count to get 0, then +1 each call"

    def __init__(self):
        self.counter = -1

    @property
    def count(self):
        "return +1 at each call"
        self.counter += 1
        return self.counter

    def reset_counter(self):
        "reset the counter"
        self.counter = -1


def grammar_maker_or(rule, depth, i, counter=None):
    "The 'or' parameter from grammar_maker"
    grammar_rules = {}
    grammar_validator = " ("
    for j, rule_list in enumerate(rule):
        grammar_validator += "("
        rules_recurs = grammar_maker(*rule_list, depth=depth+1, counter=counter)
        grammar_validator += rules_recurs[0].removeprefix(" ")
        if j < len(rule)-1:
            grammar_validator += ") / "
        else:
            grammar_validator += ")"
        for rules_recurs_key, rule_recurs in rules_recurs[1].items():
            grammar_rules[f"{rules_recurs_key}"] = rule_recurs
    grammar_validator += ")"
    i[0] += 1
    return [grammar_validator, grammar_rules]


def grammar_maker_multi(rule, depth, i, counter=None):
    "The 'multi' parameter from grammar_maker"
    grammar_rules = {}
    rules_recurs = grammar_maker(*rule, depth=depth+1, counter=counter)
    rules_recurs[0] = rules_recurs[0].removeprefix(" ")
    grammar_rules.update(rules_recurs[1])
    grammar_validator = f" _multi_{i[0]}_{depth}"
    grammar_rules[f"_multi_{i[0]}_{depth}"] = f'(({rules_recurs[0]}) / (~"\\s*\\(" \
        ({rules_recurs[0]}) (~"\\s*&" ({rules_recurs[0]}))* ")"))'
    i[0] += 1
    return [grammar_validator, grammar_rules]


def space_to_underscore(string):
    "replace whitespaces by underscore in a string"
    return string.replace(" ", "_")


GRAMMAR_MAKER_COMMANDS = {
    "or": grammar_maker_or,
    "multi": grammar_maker_multi
}


def grammar_maker(*rules, depth=0, counter=None):
    """
    Return a Grammar() of the input from easy to use arguments
    args: word - "any" - "nb" - "or" [[], []] - "multi" []
    first argument is always the command
    """
    if depth == 0:
        grammar_validator = 'validator = "' + rules[0] + '"'
        grammar_rules = GRAMMAR_BASIC_RULE
        counter = Counter()
        i = [1]
    else:
        grammar_validator = ""
        grammar_rules = {}
        i = [0]
    while i[0] < len(rules):
        if isinstance(rules[i[0]], list):
            count = counter.count
            grammar_rules[f"_{count}_list{i[0]}_{depth}"] = f"({format_rule_list(rules[i[0]])})"
            grammar_validator += f" _{count}_list{i[0]}_{depth}"
        elif rules[i[0]] in GRAMMAR_BASIC_RULE:
            grammar_validator += f" {rules[i[0]]}"
        elif rules[i[0]] in GRAMMAR_MAKER_COMMANDS:
            rule_ret = GRAMMAR_MAKER_COMMANDS[rules[i[0]]](rules[i[0]+1], depth, i, counter)
            grammar_validator += rule_ret[0]
            grammar_rules.update(rule_ret[1])
        else:
            grammar_rules[f"{space_to_underscore(rules[i[0]])}_{i[0]}_{depth}"] = \
                f"{format_rule_list([rules[i[0]]])}"
            grammar_validator += f" {space_to_underscore(rules[i[0]])}_{i[0]}_{depth}"
        i[0] += 1
    if depth == 0:
        return grammar_validator_rules_linker(grammar_validator, grammar_rules)
    return [grammar_validator, grammar_rules]


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


def node_visitor(node):
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
    print(node_words)
    node_words = list(filter(lambda word: word not in ["(", ")", "", "&"], node_words))
    return node_words


class TreeVisitor(NodeVisitor):
    """Format the tree obtained by grammar.parse()"""
    # pylint: disable=unused-argument
    def visit_validator(self, node, visited_children):
        """ Returns the overall output. """
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

    # pylint: disable=unused-argument
    def visit_nb(self, node, visited_children):
        """ Return an int when it's a number node """
        return int(node.text)

    def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        return node


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
