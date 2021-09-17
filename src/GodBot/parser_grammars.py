"""This file contains the commands grammar used by the parser"""


from parsimonious.grammar import Grammar


grammar_command_when = Grammar(
    """
    when_validator      = "!when" subject_or_subjects cmp_or_cmps text ((action_or_actions text) / action_no_text)
    subject_or_subjects = (subject / (~"\s*\(" subject (~"\s*&" subject)* ")"))
    subject             = (~"\s*message" / ~"\s*author")
    cmp_or_cmps         = (cmp / (~"\s*\(" cmp (~"\s*&" cmp)* ")"))
    cmp                 = (~"\s*equal" / ~"\s*startswith" / ~"\s*endswith" / ~"\s*match")
    action_or_actions   = (action / (~"\s*\(" action (~"\s*&" action)* ")"))
    action              = (~"\s*send" / ~"\s*delete" / ~"\s*react")
    action_no_text      = ~"\s*delete"
    text                = (~'\s*".*?"' / ~"\s*\S+")
    """)
