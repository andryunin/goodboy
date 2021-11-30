import re

import pytest

from goodboy.schema import Error
from goodboy.types import Str

from tests.types.conftest import assert_errors


def test_min_length():
    min_length = 5
    schema = Str(min_length=min_length)

    assert schema("hello") == "hello"
    assert schema("hello world") == "hello world"

    with assert_errors([Error("str.too_short", {"min_length": min_length})]):
        schema("oops")


def test_max_length():
    max_length = 5
    schema = Str(max_length=max_length)

    assert schema("hello") == "hello"
    assert schema("yep") == "yep"

    with assert_errors([Error("str.too_long", {"max_length": max_length})]):
        schema("oops too long")


def test_length():
    length = 5
    schema = Str(length=length)

    assert schema("hello") == "hello"

    with assert_errors([Error("str.unexpected_length", {"length": length})]):
        schema("oops too long")

    with assert_errors([Error("str.unexpected_length", {"length": length})]):
        schema("oops")


@pytest.mark.parametrize("pattern", (r"^\d+$", re.compile(r"^\d+$")))
def test_pattern(pattern):
    print(pattern)
    schema = Str(pattern=pattern)

    assert schema("42") == "42"

    with assert_errors([Error("str.pattern")]):
        schema("oops")


def test_typecheck():
    assert Str()("hello") == "hello"

    with assert_errors([Error("invalid_type", {"expected_type": "str"})]):
        Str()(42)


def test_typecast():
    class BuggyObject:
        def __str__(self):
            raise ValueError("buggy object can't be casted to string")

    assert Str()(42, typecast=True) == "42"

    with assert_errors([Error("str.cast_error")]):
        Str()(BuggyObject(), typecast=True)


def test_allow_none():
    assert Str(allow_none=True)(None) is None

    with assert_errors([Error("cannot_be_none")]):
        Str()(None)
