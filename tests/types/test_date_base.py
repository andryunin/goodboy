from datetime import date, datetime, timedelta

import pytest

from goodboy.errors import Error
from goodboy.types.dates import Date, DateTime
from tests.conftest import assert_errors, validate_value_has_odd_year


@pytest.mark.parametrize(
    "schema_class,value",
    [
        (Date, date(1970, 1, 1)),
        (DateTime, datetime(1970, 1, 1, 0, 0, 0)),
    ],
)
class TestDateBase:
    def test_accepts_none_when_none_allowed(self, schema_class, value):
        schema = schema_class(allow_none=True)
        assert schema(None) is None

    def test_rejects_none_when_none_denied(self, schema_class, value):
        schema = schema_class()

        with assert_errors([Error("cannot_be_none")]):
            schema(None)

    def test_earlier_than_option_accepts_good_value(self, schema_class, value):
        schema = schema_class(earlier_than=value)
        assert schema(value - timedelta(days=1)) == value - timedelta(days=1)

    def test_earlier_than_option_rejects_bad_values(self, schema_class, value):
        schema = schema_class(earlier_than=value)

        with assert_errors([Error("later_or_equal_to", {"value": value})]):
            schema(value)

        with assert_errors([Error("later_or_equal_to", {"value": value})]):
            schema(value + timedelta(days=1))

    def test_earlier_or_equal_to_option_accepts_good_values(self, schema_class, value):
        schema = schema_class(earlier_or_equal_to=value)

        assert schema(value) == value
        assert schema(value - timedelta(days=1)) == value - timedelta(days=1)

    def test_earlier_or_equal_to_option_rejects_bad_value(self, schema_class, value):
        schema = schema_class(earlier_or_equal_to=value)

        with assert_errors([Error("later_than", {"value": value})]):
            schema(value + timedelta(days=1))

    def test_later_than_option_accepts_good_value(self, schema_class, value):
        schema = schema_class(later_than=value)
        assert schema(value + timedelta(days=1)) == value + timedelta(days=1)

    def test_later_than_option_rejects_bad_values(self, schema_class, value):
        schema = schema_class(later_than=value)

        with assert_errors([Error("earlier_or_equal_to", {"value": value})]):
            schema(value)

        with assert_errors([Error("earlier_or_equal_to", {"value": value})]):
            schema(value - timedelta(days=1))

    def test_later_or_equal_to_option_accepts_good_values(self, schema_class, value):
        schema = schema_class(later_or_equal_to=value)

        assert schema(value) == value
        assert schema(value + timedelta(days=1)) == value + timedelta(days=1)

    def test_later_or_equal_to_option_rejects_bad_value(self, schema_class, value):
        schema = schema_class(later_or_equal_to=value)

        with assert_errors([Error("earlier_than", {"value": value})]):
            schema(value - timedelta(days=1))

    def test_applies_rules_when_value_not_none_and_has_expected_type(
        self, schema_class, value
    ):
        schema = schema_class(rules=[validate_value_has_odd_year])

        with assert_errors([Error("not_an_odd_year")]):
            schema(value)

        odd_year_value = value.replace(year=value.year + 1)
        assert schema(odd_year_value) == odd_year_value

    def test_ignores_rules_when_value_is_none_and_denied(self, schema_class, value):
        schema = schema_class(rules=[validate_value_has_odd_year])

        with assert_errors([Error("cannot_be_none")]):
            schema(None)

    def test_ignores_rules_when_value_is_none_and_allowed(self, schema_class, value):
        schema = schema_class(allow_none=True, rules=[validate_value_has_odd_year])
        assert schema(None) is None
