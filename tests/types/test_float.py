import pytest

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.numeric import Float
from tests.conftest import assert_errors, validate_value_is_42_and_double_it


@pytest.mark.parametrize("good_value", [42.0, 42])
def test_accepts_float_and_int_type(good_value):
    schema = Float()
    assert schema(good_value) == good_value


def test_rejects_non_float_and_non_int_type():
    bad_value = "42.0"
    schema = Float()

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("float")})]
    ):
        schema(bad_value)


@pytest.mark.parametrize("good_input", ["42.0", "42"])
def test_type_casting_accepts_good_input(good_input):
    schema = Float()
    value = 42.0

    assert schema(good_input, typecast=True) == value


def test_type_casting_rejects_bad_input():
    schema = Float()
    bad_input = "oops"

    with assert_errors([Error("invalid_numeric_format")]):
        schema(bad_input, typecast=True)


def test_accepts_allowed_value():
    schema = Float(allowed=[42.0, 100.0])
    assert schema(42.0) == 42.0
    assert schema(100.0) == 100.0


def test_none_check_precedes_allowed():
    schema = Float(allowed=[42.0, 100.0], allow_none=True)
    assert schema(None) is None


def test_rejects_not_allowed_value():
    allowed = [42.0, 100.0]
    schema = Float(allowed=allowed)

    with assert_errors([Error("not_allowed", {"allowed": allowed})]):
        schema(150.0)


def test_ignores_rules_when_value_has_unexpected_type():
    schema = Float(rules=[validate_value_is_42_and_double_it])

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("float")})]
    ):
        schema("42")
