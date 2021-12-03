import pytest

from goodboy.errors import Error
from goodboy.types import Float, Int
from tests.types.conftest import assert_errors


@pytest.mark.parametrize("type_class", [Int, Float])
class TestNumeric:
    def test_accepts_none_when_none_allowed(self, type_class):
        schema = type_class(allow_none=True)
        assert schema(None) is None

    def test_rejects_none_when_none_denied(self, type_class):
        schema = type_class()

        with assert_errors([Error("cannot_be_none")]):
            schema(None)

    def test_less_than_option_accepts_good_value(self, type_class):
        schema = type_class(less_than=0)
        good_value = -1

        assert schema(good_value) == good_value

    @pytest.mark.parametrize("bad_value", [0, 1])
    def test_less_than_option_rejects_bad_values(self, type_class, bad_value):
        print("=============================")
        print(type_class, bad_value)
        print("=============================")
        less_than_value = 0
        schema = type_class(less_than=less_than_value)

        with assert_errors([Error("greater_or_equal_to", {"value": less_than_value})]):
            schema(bad_value)

    @pytest.mark.parametrize("good_value", [0, -1])
    def test_less_or_equal_to_option_accepts_good_values(self, type_class, good_value):
        schema = type_class(less_or_equal_to=0)
        assert schema(good_value) == good_value

    def test_less_or_equal_to_option_rejects_bad_value(self, type_class):
        less_or_equal_to_value = 0
        schema = type_class(less_or_equal_to=less_or_equal_to_value)
        bad_value = 1

        with assert_errors([Error("greater_than", {"value": less_or_equal_to_value})]):
            schema(bad_value)

    def test_greater_than_option_accepts_good_value(self, type_class):
        schema = type_class(greater_than=0)
        good_value = 1

        assert schema(good_value) == good_value

    @pytest.mark.parametrize("bad_value", [0, -1])
    def test_greater_than_option_rejects_bad_values(self, type_class, bad_value):
        greater_than_value = 0
        schema = type_class(greater_than=greater_than_value)

        with assert_errors([Error("less_or_equal_to", {"value": greater_than_value})]):
            schema(bad_value)

    @pytest.mark.parametrize("good_value", [0, 1])
    def test_greater_or_equal_to_option_accepts_good_values(
        self, type_class, good_value
    ):
        schema = type_class(greater_or_equal_to=0)
        assert schema(good_value) == good_value

    def test_greater_or_equal_to_option_rejects_bad_value(self, type_class):
        greater_or_equal_to_value = 0
        schema = type_class(greater_or_equal_to=0)
        bad_value = -1

        with assert_errors([Error("less_than", {"value": greater_or_equal_to_value})]):
            schema(bad_value)
