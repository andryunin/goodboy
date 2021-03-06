from datetime import datetime

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.dates import DateTime
from tests.conftest import assert_errors, validate_value_has_odd_year


def test_accepts_datetime_type():
    schema = DateTime()
    good_value = datetime(1985, 10, 26, 9, 0, 0)

    assert schema(good_value) == good_value


def test_rejects_non_datetime_type():
    schema = DateTime()
    bad_value = "1985-10-26T09:00:00"

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("datetime")})]
    ):
        schema(bad_value)


def test_type_casting_accepts_good_input_with_default_format():
    schema = DateTime()
    good_input = "1985-10-26T09:00:00"
    value = datetime(1985, 10, 26, 9, 0, 0)

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input_with_default_format():
    schema = DateTime()
    bad_input = "1985/10/26 09:00:00"

    with assert_errors([Error("invalid_datetime_format")]):
        schema(bad_input, typecast=True)


def test_type_casting_accepts_good_input_with_custom_format():
    schema = DateTime(format="%Y/%m/%d %H:%M:%S")
    good_input = "1985/10/26 09:00:00"
    value = datetime(1985, 10, 26, 9, 0, 0)

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input_with_custom_format():
    schema = DateTime(format="%Y/%m/%d %H:%M:%S")
    bad_input = "1985-10-26T09:00:00"

    with assert_errors([Error("invalid_datetime_format")]):
        schema(bad_input, typecast=True)


def test_type_casting_accepts_good_input_with_custom_format_from_context():
    schema = DateTime(format="should_not_be_used")
    good_input = "1985/10/26 09:00:00"
    value = datetime(1985, 10, 26, 9, 0, 0)
    context = {"date_format": "%Y/%m/%d %H:%M:%S"}

    assert schema(good_input, typecast=True, context=context) == value


def test_type_casting_rejects_bad_input_with_custom_format_from_context():
    schema = DateTime(format="should_not_be_used")
    bad_input = "1985-10-26T09:00:00"
    context = {"date_format": "%Y/%m/%d %H:%M:%S"}

    with assert_errors([Error("invalid_datetime_format")]):
        schema(bad_input, typecast=True, context=context)


def test_type_casting_accepts_date_values():
    schema = DateTime()
    good_input = datetime(1985, 10, 26, 9, 0, 0)

    assert schema(good_input, typecast=True) == good_input


def test_type_casting_rejects_non_string_values():
    schema = DateTime()
    bad_input = 42

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("datetime")})]
    ):
        schema(bad_input, typecast=True)


def test_accepts_allowed_value():
    schema = DateTime(
        allowed=[datetime(1985, 10, 26, 9, 0, 0), datetime(2015, 10, 21, 7, 28, 0)]
    )
    assert schema(datetime(1985, 10, 26, 9, 0, 0)) == datetime(1985, 10, 26, 9, 0, 0)
    assert schema(datetime(2015, 10, 21, 7, 28, 0)) == datetime(2015, 10, 21, 7, 28, 0)


def test_none_check_precedes_allowed():
    schema = DateTime(
        allowed=[datetime(1985, 10, 26, 9, 0, 0), datetime(2015, 10, 21, 7, 28, 0)],
        allow_none=True,
    )
    assert schema(None) is None


def test_rejects_not_allowed_value():
    allowed = [datetime(1985, 10, 26, 9, 0, 0), datetime(2015, 10, 21, 7, 28, 0)]
    schema = DateTime(allowed=allowed)

    with assert_errors([Error("not_allowed", {"allowed": allowed})]):
        schema(datetime(1955, 11, 12, 6, 38, 00))


def test_ignores_rules_when_value_has_unexpected_type():
    schema = DateTime(rules=[validate_value_has_odd_year])

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("datetime")})]
    ):
        schema("oops")


def test_options_type_casting():
    option_val = datetime(2000, 1, 1, 0, 0, 0)
    option_str = "2000-01-01T00:00:00"

    schema_val = DateTime(
        earlier_than=option_val,
        earlier_or_equal_to=option_val,
        later_than=option_val,
        later_or_equal_to=option_val,
        allowed=[option_val],
    )

    schema_str = DateTime(
        earlier_than=option_str,
        earlier_or_equal_to=option_str,
        later_than=option_str,
        later_or_equal_to=option_str,
        allowed=[option_str],
    )

    assert schema_val == schema_str
