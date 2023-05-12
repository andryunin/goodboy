from decimal import Decimal

import pytest

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.numeric import DecimalSchema
from tests.conftest import assert_errors, validate_value_is_42_and_double_it


@pytest.mark.parametrize("good_value", [Decimal("42.0")])
def test_accepts_decimal_type(good_value):
    schema = DecimalSchema()
    assert schema(good_value) == good_value


@pytest.mark.parametrize("good_value", [42.0, 42])
def test_accepts_float_and_int_type(good_value):
    schema = DecimalSchema()
    assert schema(good_value) == good_value


def test_rejects_other_types():
    bad_value = "42.0"
    schema = DecimalSchema()

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("decimal")})]
    ):
        schema(bad_value)


@pytest.mark.parametrize("good_input", ["42.0", "42"])
def test_type_casting_accepts_good_input(good_input):
    schema = DecimalSchema()
    value = Decimal("42.0")

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input():
    schema = DecimalSchema()
    bad_input = "oops"

    with assert_errors([Error("invalid_numeric_format")]):
        schema(bad_input, typecast=True)


def test_accepts_allowed_value():
    schema = DecimalSchema(allowed=[Decimal("42.0"), Decimal("100.0")])
    assert schema(Decimal("42.0")) == Decimal("42.0")
    assert schema(Decimal("100.0")) == Decimal("100.0")


def test_none_check_precedes_allowed():
    schema = DecimalSchema(allowed=[Decimal("42.0"), Decimal("100.0")], allow_none=True)
    assert schema(None) is None


def test_rejects_not_allowed_value():
    allowed = [Decimal("42.0"), Decimal("100.0")]
    schema = DecimalSchema(allowed=allowed)

    with assert_errors([Error("not_allowed", {"allowed": allowed})]):
        schema(Decimal("150.0"))


def test_ignores_rules_when_value_has_unexpected_type():
    schema = DecimalSchema(rules=[validate_value_is_42_and_double_it])

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("decimal")})]
    ):
        schema("42")
