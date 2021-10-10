from datetime import datetime, timedelta

from goodboy.schema import Error
from goodboy.types import DateTime

from tests.types.conftest import assert_errors


def test_min():
    minimum = datetime(1970, 1, 1, 0, 0, 0)
    schema = DateTime(min=minimum)

    with assert_errors([Error("datetime.less_then", {"min": minimum})]):
        schema(datetime(1900, 1, 1, 0, 0, 0))

    assert schema(minimum) == minimum


def test_max():
    maximum = datetime(1970, 1, 1, 0, 0, 0)
    schema = DateTime(max=maximum)

    with assert_errors([Error("datetime.more_or_equal_then", {"max": maximum})]):
        schema(maximum)

    assert schema(maximum - timedelta(seconds=1)) == maximum - timedelta(seconds=1)


def test_typecheck():
    good_value = datetime(2000, 1, 1, 0, 0, 0)
    bad_value = "2000-01-01T00:00:00"

    schema = DateTime()

    assert schema(good_value) == good_value

    with assert_errors([Error("invalid_type", {"expected_type": "datetime"})]):
        schema(bad_value)


def test_default_typecast():
    value = datetime(2000, 1, 1, 0, 0, 0)

    good_string = "2000-01-01T00:00:00"
    bad_string = "2000/01/01 00:00:00"

    schema = DateTime()

    assert schema(good_string, typecast=True) == value

    with assert_errors([Error("datetime.invalid_format")]):
        schema(bad_string, typecast=True)


def test_format_typecast():
    value = datetime(2000, 1, 1, 0, 0, 0)

    good_string = "2000/01/01 00:00:00"
    bad_string = "2000-01-01T00:00:00"

    schema = DateTime(format="%Y/%m/%d %H:%M:%S")

    assert schema(good_string, typecast=True) == value

    with assert_errors([Error("datetime.invalid_format")]):
        schema(bad_string, typecast=True)


def test_allow_none():
    assert DateTime(allow_none=True)(None) is None

    with assert_errors([Error("cannot_be_none")]):
        DateTime()(None)
