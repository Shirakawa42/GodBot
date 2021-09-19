""" Bot Command Parser """


import re

from parsimonious.grammar import Grammar


def node_explorer(node, child_list):
    "Recursive function to get text from most distant nodes"
    for child in node.children:
        ret = node_explorer(child, child_list)
        if isinstance(ret, str):
            child_list.append(ret)
    if len(node.children) >= 1:
        return child_list
    return node.text


def tree_reader(tree):
    """read the tree obtained from the parsimonious parser and return a
    list of list of strings containing only relevant nodes"""
    tree_list = []
    for node in tree:
        read_node = node_explorer(node, [])
        if isinstance(read_node, list):
            tree_list.append(read_node)
        else:
            tree_list.append([read_node])
    return tree_list


def format_tree_list(tree_list):
    "remove useless texts from the tree_list returned by tree_reader"
    match_tuple = (r"^s*\(s*$", r"^s*\)s*$", r"^s*&s*$")
    compiled_list = []
    for regex_str in match_tuple:
        compiled_list.append(re.compile(regex_str))
    for i, instruction_list in enumerate(tree_list):
        for instruction in instruction_list:
            for regex in compiled_list:
                if regex.match(instruction):
                    instruction_list.remove(instruction)
        for j, _ in enumerate(instruction_list):
            instruction_list[j] = instruction_list[j].strip()
            if instruction_list[j].startswith('"') and instruction_list[j].endswith('"'):
                instruction_list[j] = instruction_list[j].removeprefix('"').removesuffix('"')
        tree_list[i] = list(dict.fromkeys(instruction_list))
    return tree_list


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
    args: string - "any" - "number" - [...] - "or" [[], []] - "multi" []
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

def formated_tree_from_grammar(grammar: Grammar, input_str: str):
    "Return a formated tree of a grammar with the input"
    return format_tree_list(tree_reader(grammar.parse(input_str)))
