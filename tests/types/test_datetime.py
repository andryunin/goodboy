from datetime import datetime

import pytest

from goodboy.errors import Error
from goodboy.types import DateTime
from tests.types.conftest import assert_errors


def test_accepts_none_when_none_allowed():
    schema = DateTime(allow_none=True)
    assert schema(None) is None


def test_rejects_none_when_none_denied():
    schema = DateTime()

    with assert_errors([Error("cannot_be_none")]):
        schema(None)


def test_accepts_datetime_type():
    schema = DateTime()
    good_value = datetime(2000, 1, 1, 0, 0, 0)

    assert schema(good_value) == good_value


def test_rejects_non_datetime_type():
    schema = DateTime()
    bad_value = "2000-01-01T00:00:00"

    with assert_errors([Error("unexpected_type", {"expected_type": "datetime"})]):
        schema(bad_value)


def test_type_casting_accepts_good_input_with_default_format():
    schema = DateTime()
    good_input = "2000-01-01T00:00:00"
    value = datetime(2000, 1, 1, 0, 0, 0)

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input_with_default_format():
    schema = DateTime()
    bad_input = "2000/01/01 00:00:00"

    with assert_errors([Error("invalid_datetime_format")]):
        schema(bad_input, typecast=True)


def test_type_casting_accepts_good_input_with_custom_format():
    schema = DateTime(format="%Y/%m/%d %H:%M:%S")
    good_input = "2000/01/01 00:00:00"
    value = datetime(2000, 1, 1, 0, 0, 0)

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input_with_custom_format():
    schema = DateTime(format="%Y/%m/%d %H:%M:%S")
    bad_input = "2000-01-01T00:00:00"

    with assert_errors([Error("invalid_datetime_format")]):
        schema(bad_input, typecast=True)


def test_earlier_than_option_accepts_good_value():
    schema = DateTime(earlier_than=datetime(1970, 1, 1, 0, 0, 0))
    good_value = datetime(1900, 1, 1, 0, 0, 0)

    assert schema(good_value) == good_value


@pytest.mark.parametrize(
    "bad_value",
    [
        datetime(1970, 1, 1, 0, 0, 0),
        datetime(2000, 1, 1, 0, 0, 0),
    ],
)
def test_earlier_than_option_rejects_bad_values(bad_value):
    earlier_than_value = datetime(1970, 1, 1, 0, 0, 0)
    schema = DateTime(earlier_than=earlier_than_value)

    with assert_errors([Error("later_or_equal_to", {"value": earlier_than_value})]):
        schema(bad_value)


@pytest.mark.parametrize(
    "good_value",
    [
        datetime(1900, 1, 1, 0, 0, 0),
        datetime(1970, 1, 1, 0, 0, 0),
    ],
)
def test_earlier_or_equal_to_option_accepts_good_values(good_value):
    schema = DateTime(earlier_or_equal_to=datetime(1970, 1, 1, 0, 0, 0))
    assert schema(good_value) == good_value


def test_earlier_or_equal_to_option_rejects_bad_value():
    earlier_or_equal_to_value = datetime(1970, 1, 1, 0, 0, 0)
    schema = DateTime(earlier_or_equal_to=earlier_or_equal_to_value)
    bad_value = datetime(1970, 1, 1, 0, 0, 1)

    with assert_errors([Error("later_than", {"value": earlier_or_equal_to_value})]):
        schema(bad_value)


def test_later_than_option_accepts_good_value():
    schema = DateTime(later_than=datetime(1970, 1, 1, 0, 0, 0))
    good_value = datetime(2000, 1, 1, 0, 0, 0)

    assert schema(good_value) == good_value


@pytest.mark.parametrize(
    "bad_value",
    [
        datetime(1970, 1, 1, 0, 0, 0),
        datetime(1900, 1, 1, 0, 0, 0),
    ],
)
def test_later_than_option_rejects_bad_values(bad_value):
    later_than_value = datetime(1970, 1, 1, 0, 0, 0)
    schema = DateTime(later_than=later_than_value)

    with assert_errors([Error("earlier_or_equal_to", {"value": later_than_value})]):
        schema(bad_value)


@pytest.mark.parametrize(
    "good_value",
    [
        datetime(2000, 1, 1, 0, 0, 0),
        datetime(1970, 1, 1, 0, 0, 0),
    ],
)
def test_later_or_equal_to_option_accepts_good_values(good_value):
    schema = DateTime(later_or_equal_to=datetime(1970, 1, 1, 0, 0, 0))
    assert schema(good_value) == good_value


def test_later_or_equal_to_option_rejects_bad_value():
    later_or_equal_to_value = datetime(1970, 1, 1, 0, 0, 0)
    schema = DateTime(later_or_equal_to=later_or_equal_to_value)
    bad_value = datetime(1900, 1, 1, 0, 0, 1)

    with assert_errors([Error("earlier_than", {"value": later_or_equal_to_value})]):
        schema(bad_value)
