""" Bot Command Parser """


import re


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
            instruction_list[j] = instruction_list[j].lstrip().rstrip()
            if instruction_list[j].startswith('"') and instruction_list[j].endswith('"'):
                instruction_list[j] = instruction_list[j].removeprefix('"').removesuffix('"')
        tree_list[i] = list(dict.fromkeys(instruction_list))
    return tree_list
