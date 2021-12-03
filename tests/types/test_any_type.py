import pytest

from goodboy.errors import Error, Message, MessageCollection
from goodboy.schema import SchemaError
from goodboy.types.simple import AnyType
from tests.types.conftest import assert_errors


def test_none():
    with assert_errors([Error("cannot_be_none", {})]):
        print(AnyType()(None))

    assert AnyType(allow_none=True)(None) is None


def test_value():
    assert AnyType()("ok") == "ok"
    assert AnyType()(42) == 42


def test_allow_none():
    assert AnyType(allow_none=True)(None) is None

    with assert_errors([Error("cannot_be_none")]):
        AnyType()(None)


def test_messages_override():
    messages = MessageCollection({"cannot_be_none": Message("no None here please")})

    try:
        AnyType(messages=messages)(None)
    except SchemaError as e:
        assert e.errors[0].get_message() == "no None here please"
    else:
        pytest.fail("exception was not raised")
