import re

import pytest

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.simple import Str
from tests.types.conftest import assert_errors


def test_accepts_none_when_none_allowed():
    schema = Str(allow_none=True)
    assert schema(None) is None


def test_rejects_none_when_none_denied():
    schema = Str()

    with assert_errors([Error("cannot_be_none")]):
        schema(None)


def test_type_casting_accepts_good_input():
    schema = Str()
    good_input = "42"

    assert schema(good_input, typecast=True) == good_input


def test_type_casting_rejects_bad_input():
    schema = Str()
    bad_input = 42

    with assert_errors([Error("unexpected_type", {"expected_type": type_name("str")})]):
        schema(bad_input, typecast=True)


def test_accepts_str_type():
    schema = Str()
    good_value = "42"

    assert schema(good_value) == good_value


def test_rejects_non_str_type():
    schema = Str()
    bad_value = 42

    with assert_errors([Error("unexpected_type", {"expected_type": type_name("str")})]):
        schema(bad_value)


def test_accepts_blank_string_when_enabled():
    schema = Str(allow_blank=True, min_length=10, pattern=r"^\d+$")
    good_value = ""

    assert schema(good_value) == good_value


def test_accepts_blank_string_when_disabled():
    schema = Str(min_length=10, pattern=r"^\d+$")
    bad_value = ""

    with assert_errors([Error("cannot_be_blank")]):
        schema(bad_value)


def test_min_length_option_accepts_good_value():
    schema = Str(min_length=5)
    good_value = "hello"

    assert schema(good_value) == good_value


def test_min_length_option_rejects_bad_value():
    min_length_value = 5
    schema = Str(min_length=min_length_value)
    bad_value = "oops"

    with assert_errors([Error("string_too_short", {"value": min_length_value})]):
        schema(bad_value)


def test_max_length_option_accepts_good_value():
    schema = Str(max_length=5)
    good_value = "hello"

    assert schema(good_value) == good_value


def test_max_length_option_rejects_bad_value():
    max_length_value = 5
    schema = Str(max_length=max_length_value)
    bad_value = "hello world"

    with assert_errors([Error("string_too_long", {"value": max_length_value})]):
        schema(bad_value)


def test_length_option_accepts_good_value():
    schema = Str(length=5)
    good_value = "hello"

    assert schema(good_value) == good_value


def test_length_option_rejects_good_value():
    length_value = 5
    schema = Str(length=length_value)
    bad_value = "hello world"

    with assert_errors([Error("invalid_string_length", {"value": length_value})]):
        schema(bad_value)


@pytest.mark.parametrize("pattern", (r"^\d+$", re.compile(r"^\d+$")))
def test_pattern_option_accepts_good_string(pattern):
    schema = Str(pattern=pattern)
    good_string = "42"

    assert schema(good_string) == good_string


@pytest.mark.parametrize("pattern", (r"^\d+$", re.compile(r"^\d+$")))
def test_pattern_option_rejects_bad_string(pattern):
    schema = Str(pattern=pattern)
    bad_string = "oops"

    with assert_errors([Error("invalid_string_format")]):
        schema(bad_string)
