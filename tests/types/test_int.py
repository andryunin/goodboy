from goodboy.errors import Error
from goodboy.types import Int
from tests.types.conftest import assert_errors


def test_min():
    minimum = 0
    schema = Int(min=minimum)

    assert schema(minimum) == minimum
    assert schema(minimum + 1) == minimum + 1

    with assert_errors([Error("int.less_then", {"min": minimum})]):
        schema(minimum - 1)


def test_max():
    maximum = 0
    schema = Int(max=0)

    assert schema(maximum - 1) == maximum - 1

    with assert_errors([Error("int.more_or_equal_then", {"max": maximum})]):
        schema(maximum + 1)

    with assert_errors([Error("int.more_or_equal_then", {"max": maximum})]):
        schema(maximum)


def test_typecheck():
    schema = Int()

    assert schema(42) == 42

    with assert_errors([Error("invalid_type", {"expected_type": "int"})]):
        schema("42")


def test_typecast():
    assert Int()("42", typecast=True) == 42

    with assert_errors([Error("int.invalid_format")]):
        Int()("oops", typecast=True)


def test_allow_none():
    assert Int(allow_none=True)(None) is None

    with assert_errors([Error("cannot_be_none")]):
        Int()(None)
