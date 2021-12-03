from datetime import datetime

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.dates import DateTime
from tests.types.conftest import assert_errors


def test_accepts_datetime_type():
    schema = DateTime()
    good_value = datetime(2000, 1, 1, 0, 0, 0)

    assert schema(good_value) == good_value


def test_rejects_non_datetime_type():
    schema = DateTime()
    bad_value = "2000-01-01T00:00:00"

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("datetime")})]
    ):
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


def test_type_casting_accepts_date_values():
    schema = DateTime()
    good_input = datetime(2000, 1, 1, 0, 0, 0)

    assert schema(good_input, typecast=True) == good_input


def test_type_casting_rejects_non_string_values():
    schema = DateTime()
    bad_input = 42

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("datetime")})]
    ):
        schema(bad_input, typecast=True)
