import pytest

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.simple import Bool
from tests.conftest import assert_errors


def test_accepts_none_when_none_allowed():
    assert Bool(allow_none=True)(None) is None


def test_rejects_none_when_none_denied():
    with assert_errors([Error("cannot_be_none")]):
        Bool()(None)


@pytest.mark.parametrize(
    "good_input,result",
    [
        ("true", True),
        ("false", False),
    ],
)
def test_type_casting_accepts_good_input(good_input, result):
    assert Bool()(good_input, typecast=True) is result


def test_type_casting_rejects_bad_input():
    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("bool")})]
    ):
        Bool()("oops", typecast=True)


def test_type_casting_accepts_any_value_when_cast_anything_enabled():
    Bool(cast_anything=True)({}, typecast=True) is False
    Bool(cast_anything=True)({"hello": "world"}, typecast=True) is True


def test_accepts_bool_type():
    assert Bool()(True) is True
    assert Bool()(False) is False


def test_rejects_non_str_type():
    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("bool")})]
    ):
        Bool()("true")


def test_only_true_option_accepts_true_value():
    assert Bool(only_true=True)(True) is True


def test_only_true_option_rejects_false_value():
    with assert_errors([Error("not_allowed", {"allowed": [True]})]):
        assert Bool(only_true=True)(False)


def test_only_false_option_accepts_false_value():
    assert Bool(only_false=True)(False) is False


def test_only_false_option_rejects_true_value():
    with assert_errors([Error("not_allowed", {"allowed": [False]})]):
        assert Bool(only_false=True)(True)


def test_applies_rules_when_value_not_none_and_has_expected_type():
    assert Bool(rules=[invert_value])(False) is True


def test_ignores_rules_when_value_is_none_and_denied():
    with assert_errors([Error("cannot_be_none")]):
        Bool(rules=[invert_value])(None)


def test_ignores_rules_when_value_is_none_and_allowed():
    assert Bool(allow_none=True, rules=[invert_value])(None) is None


def test_ignores_rules_when_value_has_unexpected_type():
    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("bool")})]
    ):
        Bool(rules=[invert_value])(42)


def invert_value(self: Bool, value: Bool, typecast: bool, context: dict):
    return not value, []
