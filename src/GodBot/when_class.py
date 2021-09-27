"""Contains the "when" class"""


from dataclasses import dataclass


def list_to_str(lst: list[str]):
    "transform a list into a DB-able string"
    db_string = ""
    for string in lst:
        db_string += string + "|"
    return db_string.removesuffix("|")


@dataclass
class When():
    "Used by the !when command"

    subjects: list[str]
    comparators: list[str]
    cmp_param: str
    actions: list[str]
    action_param: str

    @property
    def tuple(self):
        "return a DB-able list"
        return (list_to_str(self.subjects), list_to_str(self.comparators),
                self.cmp_param, list_to_str(self.actions), self.action_param)
