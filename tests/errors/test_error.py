from goodboy.errors import Error
from goodboy.messages import Message, MessageCollection


def test_equality():
    assert Error("oops", {"arg": "val"}) == Error("oops", {"arg": "val"})


def test_message():
    messages = MessageCollection({"oops": Message("Oops!", json="JSON oops!")})

    error = Error("oops", messages=messages)

    assert error.get_message() == "Oops!"
    assert error.get_message("json") == "JSON oops!"
