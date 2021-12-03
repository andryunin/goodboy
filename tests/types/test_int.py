import pytest

from goodboy.errors import Error
from goodboy.types import Int
from tests.types.conftest import assert_errors


def test_accepts_none_when_none_allowed():
    schema = Int(allow_none=True)
    assert schema(None) is None


def test_rejects_none_when_none_denied():
    schema = Int()

    with assert_errors([Error("cannot_be_none")]):
        schema(None)


def test_accepts_datetime_type():
    schema = Int()
    good_value = 42

    assert schema(good_value) == good_value


def test_rejects_non_datetime_type():
    schema = Int()
    bad_value = "42"

    with assert_errors([Error("unexpected_type", {"expected_type": "integer"})]):
        schema(bad_value)


def test_type_casting_accepts_good_input():
    schema = Int()
    good_input = "42"
    value = 42

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input():
    schema = Int()
    bad_input = "42.0"

    with assert_errors([Error("invalid_integer_format")]):
        schema(bad_input, typecast=True)


def test_less_than_option_accepts_good_value():
    schema = Int(less_than=0)
    good_value = -1

    assert schema(good_value) == good_value


@pytest.mark.parametrize("bad_value", [0, 1])
def test_less_than_option_rejects_bad_values(bad_value):
    less_than_value = 0
    schema = Int(less_than=less_than_value)

    with assert_errors([Error("greater_or_equal_to", {"value": less_than_value})]):
        schema(bad_value)


@pytest.mark.parametrize("good_value", [0, -1])
def test_less_or_equal_to_option_accepts_good_values(good_value):
    schema = Int(less_or_equal_to=0)
    assert schema(good_value) == good_value


def test_less_or_equal_to_option_rejects_bad_value():
    less_or_equal_to_value = 0
    schema = Int(less_or_equal_to=less_or_equal_to_value)
    bad_value = 1

    with assert_errors([Error("greater_than", {"value": less_or_equal_to_value})]):
        schema(bad_value)


def test_greater_than_option_accepts_good_value():
    schema = Int(greater_than=0)
    good_value = 1

    assert schema(good_value) == good_value


@pytest.mark.parametrize("bad_value", [0, -1])
def test_greater_than_option_rejects_bad_values(bad_value):
    greater_than_value = 0
    schema = Int(greater_than=greater_than_value)

    with assert_errors([Error("less_or_equal_to", {"value": greater_than_value})]):
        schema(bad_value)


@pytest.mark.parametrize("good_value", [0, 1])
def test_greater_or_equal_to_option_accepts_good_values(good_value):
    schema = Int(greater_or_equal_to=0)
    assert schema(good_value) == good_value


def test_greater_or_equal_to_option_rejects_bad_value():
    greater_or_equal_to_value = 0
    schema = Int(greater_or_equal_to=0)
    bad_value = -1

    with assert_errors([Error("less_than", {"value": greater_or_equal_to_value})]):
        schema(bad_value)
