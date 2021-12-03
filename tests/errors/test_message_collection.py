import pytest

from goodboy.messages import Message, MessageCollection


@pytest.fixture
def collection():
    return MessageCollection(
        {
            "oops": Message("Oops!"),
            "ouch": Message("Ouch!"),
        }
    )


def test_known_message(collection: MessageCollection):
    assert collection.get_message("oops").get() == "Oops!"


def test_unknown_message(collection: MessageCollection):
    assert collection.get_message("argh").get() == "argh"


def test_inheritance_message(collection: MessageCollection):
    child_collection = MessageCollection(
        {
            "oops": Message("Overriden Oops!"),
            "argh": Message("Argh!"),
        },
        collection,
    )

    assert child_collection.get_message("oops").get() == "Overriden Oops!"
    assert child_collection.get_message("ouch").get() == "Ouch!"
    assert child_collection.get_message("argh").get() == "Argh!"
