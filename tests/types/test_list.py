from datetime import date

import pytest

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.dates import Date
from goodboy.types.lists import List
from goodboy.types.simple import AnyValue, Str
from tests.conftest import assert_errors, assert_list_value_errors


def test_accepts_none_when_none_allowed():
    assert List(allow_none=True)(None) is None


def test_rejects_none_when_none_denied():
    with assert_errors([Error("cannot_be_none")]):
        List()(None)


def test_type_casting_accepts_good_input():
    assert List()([], typecast=True) == []


def test_type_casting_rejects_bad_input():
    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("list")})]
    ):
        List()(42, typecast=True)


def test_accepts_list_type():
    assert List()([]) == []


def test_rejects_non_list_type():
    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("list")})]
    ):
        List()(42)


@pytest.mark.parametrize("good_value", [[1, 2, 3], [1, 2, 3, 4]])
def test_min_length_option_accepts_good_value(good_value):
    schema = List(min_length=3)
    assert schema(good_value) == good_value


def test_min_length_option_rejects_bad_value():
    min_length_value = 3
    schema = List(min_length=min_length_value)
    bad_value = [1]

    with assert_errors([Error("too_short", {"value": min_length_value})]):
        schema(bad_value)


@pytest.mark.parametrize("good_value", [[1, 2], [1, 2, 3]])
def test_max_length_option_accepts_good_value(good_value):
    schema = List(max_length=3)
    assert schema(good_value) == good_value


def test_max_length_option_rejects_bad_value():
    max_length_value = 3
    schema = List(max_length=max_length_value)
    bad_value = [1, 2, 3, 4]

    with assert_errors([Error("too_long", {"value": max_length_value})]):
        schema(bad_value)


def test_length_option_accepts_good_value():
    schema = List(length=3)
    good_value = [1, 2, 3]

    assert schema(good_value) == good_value


@pytest.mark.parametrize("bad_value", [[1, 2], [1, 2, 3, 4]])
def test_length_option_rejects_good_value(bad_value):
    length_value = 3
    schema = List(length=length_value)

    with assert_errors([Error("invalid_length", {"value": length_value})]):
        schema(bad_value)


def test_accepts_valid_values():
    schema = List(item=AnyValue(allow_none=True))
    good_value = [None, None]

    assert schema(good_value) == good_value


def test_rejects_invalid_values():
    schema = List(item=AnyValue())
    bad_value = [None, None]

    with assert_list_value_errors(
        {0: [Error("cannot_be_none")], 1: [Error("cannot_be_none")]}
    ):
        schema(bad_value)


def test_passes_typecast_flag_to_key_schemas():
    schema = List(item=Date())

    assert schema(["1970-01-01"], typecast=True) == [date(1970, 1, 1)]

    with assert_list_value_errors(
        {0: [Error("unexpected_type", {"expected_type": type_name("date")})]}
    ):
        schema(["1970-01-01"])


def test_rejects_values_with_typecasting_errors():
    schema = List(item=Date())

    with assert_list_value_errors({0: [Error("invalid_date_format")]}):
        schema(["1970/01/01"], typecast=True)


def test_applies_rules_when_value_not_none_and_has_expected_type():
    schema = List(rules=[validate_value_length_is_odd_and_add_bar_list_item])

    with assert_errors([Error("length_is_not_odd")]):
        schema([])

    assert schema(["foo"]) == ["foo", "bar"]


def test_ignores_rules_when_value_is_none_and_denied():
    schema = List(rules=[validate_value_length_is_odd_and_add_bar_list_item])

    with assert_errors([Error("cannot_be_none")]):
        schema(None)


def test_ignores_rules_when_value_is_none_and_allowed():
    schema = List(
        allow_none=True, rules=[validate_value_length_is_odd_and_add_bar_list_item]
    )
    assert schema(None) is None


def test_ignores_rules_when_value_has_unexpected_type():
    schema = List(rules=[validate_value_length_is_odd_and_add_bar_list_item])

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("list")})]
    ):
        schema(42)


def test_merges_value_errors_from_rule_errors():
    schema = List(
        rules=[rule_with_value_errors],
        item=Str(length=3),
    )

    with assert_errors(
        [
            Error(
                "value_errors",
                nested_errors={
                    0: [
                        Error("invalid_string_length", {"value": 3}),
                        Error("value_error_from_rule"),
                    ],
                    1: [
                        Error("invalid_string_length", {"value": 3}),
                    ],
                },
            )
        ]
    ):
        schema(["oops", "oops"])


def validate_value_length_is_odd_and_add_bar_list_item(
    self: List, value, typecast: bool, context: dict
):
    if len(value) % 2 == 1:
        return value + ["bar"], []
    else:
        return value, [self._error("length_is_not_odd")]


def rule_with_value_errors(self: List, value, typecast: bool, context: dict):
    return value, [
        self._error(
            "value_errors",
            nested_errors={0: [self._error("value_error_from_rule")]},
        ),
    ]
