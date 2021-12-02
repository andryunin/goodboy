from goodboy.errors import Error
from goodboy.types import AnyType
from tests.types.conftest import assert_errors


def test_none():
    with assert_errors([Error("cannot_be_none", {})]):
        print(AnyType()(None))

    assert AnyType(allow_none=True)(None) is None


def test_value():
    assert AnyType()("ok") == "ok"
    assert AnyType()(42) == 42


def test_allow_none():
    assert AnyType(allow_none=True)(None) is None

    with assert_errors([Error("cannot_be_none")]):
        AnyType()(None)
