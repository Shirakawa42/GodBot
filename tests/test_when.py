""" Parser unit tests """


from GodBot.when_class import When, list_to_str


def test_when():
    "When class functions tests"
    when = When(["author", "message"], ["equal"], "test param", ["send"], "test action param")
    assert when.tuple == ('author|message', 'equal', 'test param', 'send', 'test action param')
    assert list_to_str(["test1", "test2", "test3"]) == "test1|test2|test3"
    assert list_to_str(["test1"]) == "test1"
