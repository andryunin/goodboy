from datetime import date

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.dates import Date
from tests.types.conftest import assert_errors


def test_accepts_date_type():
    schema = Date()
    good_value = date(2000, 1, 1)

    assert schema(good_value) == good_value


def test_rejects_non_date_type():
    schema = Date()
    bad_value = "2000-01-01"

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("date")})]
    ):
        schema(bad_value)


def test_type_casting_accepts_good_input_with_default_format():
    schema = Date()
    good_input = "2000-01-01"
    value = date(2000, 1, 1)

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input_with_default_format():
    schema = Date()
    bad_input = "2000/01/01"

    with assert_errors([Error("invalid_date_format")]):
        schema(bad_input, typecast=True)


def test_type_casting_accepts_good_input_with_custom_format():
    schema = Date(format="%Y/%m/%d")
    good_input = "2000/01/01"
    value = date(2000, 1, 1)

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input_with_custom_format():
    schema = Date(format="%Y/%m/%d")
    bad_input = "2000-01-01"

    with assert_errors([Error("invalid_date_format")]):
        schema(bad_input, typecast=True)


def test_type_casting_accepts_date_values():
    schema = Date()
    good_input = date(2000, 1, 1)

    assert schema(good_input, typecast=True) == good_input


def test_type_casting_rejects_non_string_values():
    schema = Date()
    bad_input = 42

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("date")})]
    ):
        schema(bad_input, typecast=True)
