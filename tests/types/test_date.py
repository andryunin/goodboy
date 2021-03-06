from datetime import date

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.dates import Date
from tests.conftest import assert_errors, validate_value_has_odd_year


def test_accepts_date_type():
    schema = Date()
    good_value = date(2000, 1, 1)

    assert schema(good_value) == good_value


def test_rejects_non_date_type():
    schema = Date()
    bad_value = "1985-10-26"

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("date")})]
    ):
        schema(bad_value)


def test_type_casting_accepts_good_input_with_default_format():
    schema = Date()
    good_input = "1985-10-26"
    value = date(1985, 10, 26)

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input_with_default_format():
    schema = Date()
    bad_input = "1985/10/26"

    with assert_errors([Error("invalid_date_format")]):
        schema(bad_input, typecast=True)


def test_type_casting_accepts_good_input_with_custom_format():
    schema = Date(format="%Y/%m/%d")
    good_input = "1985/10/26"
    value = date(1985, 10, 26)

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input_with_custom_format():
    schema = Date(format="%Y/%m/%d")
    bad_input = "1985-10-26"

    with assert_errors([Error("invalid_date_format")]):
        schema(bad_input, typecast=True)


def test_type_casting_accepts_good_input_with_custom_format_from_context():
    schema = Date(format="should_not_be_used")
    good_input = "1985/10/26"
    value = date(1985, 10, 26)
    context = {"date_format": "%Y/%m/%d"}

    assert schema(good_input, typecast=True, context=context) == value


def test_type_casting_rejects_bad_input_with_custom_format_from_context():
    schema = Date(format="should_not_be_used")
    bad_input = "1985-10-26"
    context = {"date_format": "%Y/%m/%d"}

    with assert_errors([Error("invalid_date_format")]):
        schema(bad_input, typecast=True, context=context)


def test_type_casting_accepts_date_values():
    schema = Date()
    good_input = date(1985, 10, 26)

    assert schema(good_input, typecast=True) == good_input


def test_type_casting_rejects_non_string_values():
    schema = Date()
    bad_input = 42

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("date")})]
    ):
        schema(bad_input, typecast=True)


def test_accepts_allowed_value():
    schema = Date(allowed=[date(1985, 10, 26), date(2015, 10, 21)])
    assert schema(date(1985, 10, 26)) == date(1985, 10, 26)
    assert schema(date(2015, 10, 21)) == date(2015, 10, 21)


def test_none_check_precedes_allowed():
    schema = Date(allowed=[date(1985, 10, 26), date(2015, 10, 21)], allow_none=True)
    assert schema(None) is None


def test_rejects_not_allowed_value():
    allowed = [date(1985, 10, 26), date(2015, 10, 21)]
    schema = Date(allowed=allowed)

    with assert_errors([Error("not_allowed", {"allowed": allowed})]):
        schema(date(2000, 1, 1))


def test_ignores_rules_when_value_has_unexpected_type():
    schema = Date(rules=[validate_value_has_odd_year])

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("date")})]
    ):
        schema("oops")


def test_options_type_casting():
    option_val = date(2000, 1, 1)
    option_str = "2000-01-01"

    schema_val = Date(
        earlier_than=option_val,
        earlier_or_equal_to=option_val,
        later_than=option_val,
        later_or_equal_to=option_val,
        allowed=[option_val],
    )

    schema_str = Date(
        earlier_than=option_str,
        earlier_or_equal_to=option_str,
        later_than=option_str,
        later_or_equal_to=option_str,
        allowed=[option_str],
    )

    assert schema_val == schema_str
