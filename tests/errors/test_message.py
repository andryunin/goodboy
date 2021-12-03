from goodboy.messages import Message


def test_known_formats():
    message = Message("Cannot be None", json="Cannot be null")

    assert message.get() == "Cannot be None"
    assert message.get("default") == "Cannot be None"
    assert message.get("json") == "Cannot be null"


def test_unknown_format():
    message = Message("Cannot be None", json="Cannot be null")

    assert message.get("grpc") == "Cannot be None"
