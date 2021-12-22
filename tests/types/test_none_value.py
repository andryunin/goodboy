from goodboy.errors import Error
from goodboy.types.simple import NoneValue
from tests.conftest import assert_errors


def test_accepts_none():
    assert NoneValue()(None) is None


def test_accepts_none_with_typecast():
    assert NoneValue()(None, typecast=True) is None


def test_rejects_not_none():
    with assert_errors([Error("must_be_none")]):
        NoneValue()(42)


def test_rejects_not_none_with_typecast():
    with assert_errors([Error("must_be_none")]):
        NoneValue()(42, typecast=True)
