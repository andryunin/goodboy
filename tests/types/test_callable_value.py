from goodboy.errors import Error
from goodboy.types.simple import CallableValue
from tests.types.conftest import assert_errors


def test_accepts_none_when_none_allowed():
    assert CallableValue(allow_none=True)(None) is None


def test_rejects_none_when_none_denied():
    with assert_errors([Error("cannot_be_none")]):
        CallableValue()(None)


def test_accepts_callable_value():
    def func():
        pass

    assert CallableValue()(func) == func


def test_rejects_not_callable_value():
    with assert_errors([Error("not_callable")]):
        CallableValue()(42)
