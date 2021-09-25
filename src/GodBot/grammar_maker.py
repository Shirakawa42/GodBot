"""Contains the grammar_maker function that allows to generate simple grammars easily"""


from typing import Union


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


GRAMMAR_BASIC_RULE = {
    "any": """(~'\\s*".*?"' / ~"\\s*\\S+")""",
    "nb": '''~"\\s+[0-9]+"'''
    }


def grammar_maker_or(rule: list[list[str]], depth: int, i: list[int], counter: Counter=None):
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


def grammar_maker_multi(rule: list[str], depth: int, i: list[int], counter: Counter=None):
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


def format_rule_list(command_data: list[str], validator: bool=False):
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


def grammar_validator_rules_linker(grammar_validator: str, grammar_rules: dict):
    "Format grammar_maker() variables to be useable with Grammar()"
    for rule_name, rule in grammar_rules.items():
        grammar_validator += f"\n{rule_name} = {rule}"
    return grammar_validator


def space_to_underscore(string: str):
    "replace whitespaces by underscore in a string"
    return string.replace(" ", "_")


GRAMMAR_MAKER_COMMANDS = {
    "or": grammar_maker_or,
    "multi": grammar_maker_multi
}


def grammar_maker(
    *rules: Union[str, list[str], list[list[str]]], depth: int=0, counter: Counter=None):
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
