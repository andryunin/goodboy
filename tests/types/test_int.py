import pytest

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.numeric import Int
from tests.types.conftest import assert_errors


def test_accepts_int_type():
    schema = Int()
    good_value = 42

    assert schema(good_value) == good_value


@pytest.mark.parametrize("bad_value", ["42", 42.0])
def test_rejects_non_int_type(bad_value):
    schema = Int()

    with assert_errors([Error("unexpected_type", {"expected_type": type_name("int")})]):
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


def test_accepts_allowed_value():
    schema = Int(allowed=[42, 100])
    assert schema(42) == 42
    assert schema(100) == 100


def test_none_check_precedes_allowed():
    schema = Int(allowed=[42, 100], allow_none=True)
    assert schema(None) is None


def test_rejects_not_allowed_value():
    allowed = [42, 100]
    schema = Int(allowed=allowed)

    with assert_errors([Error("not_allowed", {"allowed": allowed})]):
        schema(150)
