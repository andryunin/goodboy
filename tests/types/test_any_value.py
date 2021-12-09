import pytest

from goodboy.errors import Error
from goodboy.messages import Message, MessageCollection
from goodboy.schema import SchemaError
from goodboy.types.simple import AnyValue
from tests.types.conftest import assert_errors


def test_none():
    with assert_errors([Error("cannot_be_none", {})]):
        AnyValue()(None)

    assert AnyValue(allow_none=True)(None) is None


def test_value():
    assert AnyValue()("ok") == "ok"
    assert AnyValue()(42) == 42


def test_allow_none():
    assert AnyValue(allow_none=True)(None) is None

    with assert_errors([Error("cannot_be_none")]):
        AnyValue()(None)


def test_accepts_allowed_value():
    schema = AnyValue(allowed=["foo", 42])
    assert schema("foo") == "foo"
    assert schema(42) == 42


def test_none_check_precedes_allowed():
    schema = AnyValue(allowed=["foo", 42], allow_none=True)
    assert schema(None) is None


def test_rejects_not_allowed_value():
    schema = AnyValue(allowed=["foo", 42])

    with assert_errors([Error("not_allowed")]):
        schema(100)


@pytest.mark.parametrize(
    "messages",
    [
        MessageCollection({"cannot_be_none": Message("no None here please")}),
        {"cannot_be_none": Message("no None here please")},
        {"cannot_be_none": "no None here please"},
    ],
)
def test_messages_override(messages):
    try:
        AnyValue(messages=messages)(None)
    except SchemaError as e:
        assert e.errors[0].get_message() == "no None here please"
    else:
        pytest.fail("exception was not raised")
