from datetime import date

import pytest

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.dates import Date
from goodboy.types.dicts import Dict, Key
from goodboy.types.simple import AnyValue, Str
from tests.types.conftest import (
    assert_dict_key_errors,
    assert_dict_value_errors,
    assert_errors,
)


def test_accepts_none_when_none_allowed():
    assert Dict(allow_none=True)(None) is None


def test_rejects_none_when_none_denied():
    with assert_errors([Error("cannot_be_none")]):
        Dict()(None)


def test_type_casting_accepts_good_input():
    assert Dict()({}, typecast=True) == {}


def test_type_casting_rejects_bad_input():
    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("dict")})]
    ):
        Dict()(42, typecast=True)


def test_accepts_dict_type():
    assert Dict()({}) == {}


def test_rejects_non_dict_type():
    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("dict")})]
    ):
        Dict()(42)


def test_accepts_with_optional_key():
    schema = Dict(keys=[Key("minor_key", required=False)])
    good_value = {"minor_key": None}

    assert schema(good_value) == good_value


def test_accepts_without_optional_key():
    schema = Dict(keys=[Key("minor_key", required=False)])
    assert schema({}) == {}


def test_accepts_with_required_key():
    schema = Dict(keys=[Key("major_key", required=True)])
    good_value = {"major_key": None}

    assert schema(good_value) == good_value


def test_rejects_without_required_key():
    schema = Dict(keys=[Key("major_key", required=True)])

    with assert_dict_key_errors({"major_key": [Error("required_key")]}):
        schema({})


def test_keys_are_required_by_default():
    schema = Dict(keys=[Key("major_key")])

    with assert_dict_key_errors({"major_key": [Error("required_key")]}):
        schema({})


def test_keys_are_not_required_by_default_if_option_set():
    schema = Dict(keys=[Key("minor_key")], keys_required_by_default=False)
    assert schema({}) == {}


def test_rejects_unknown_key():
    schema = Dict(keys=[])

    with assert_dict_key_errors({"oops": [Error("unknown_key")]}):
        schema({"oops": True})


def test_accepts_any_key_when_no_keys_specified():
    schema = Dict()
    good_value = {"hello": "world", "the_answer": 42}

    assert schema(good_value) == good_value


def test_accepts_valid_values():
    schema = Dict(keys=[Key("minor", AnyValue(allow_none=True))])
    good_value = {"minor": None}

    assert schema(good_value) == good_value


def test_rejects_invalid_values():
    schema = Dict(keys=[Key("major", AnyValue())])
    bad_value = {"major": None}

    with assert_dict_value_errors({"major": [Error("cannot_be_none")]}):
        schema(bad_value)


def test_passes_typecast_flag_to_key_schemas():
    schema = Dict(keys=[Key("d", Date())])

    assert schema({"d": "1970-01-01"}, typecast=True) == {"d": date(1970, 1, 1)}

    with assert_dict_value_errors(
        {"d": [Error("unexpected_type", {"expected_type": type_name("date")})]}
    ):
        schema({"d": "1970-01-01"})


def test_rejects_values_with_typecasting_errors():
    schema = Dict(keys=[Key("d", Date())])

    with assert_dict_value_errors({"d": [Error("invalid_date_format")]}):
        schema({"d": "1970/01/01"}, typecast=True)


@pytest.mark.parametrize(
    "good_value",
    [
        {"field": "name", "value": "Marty"},
        {"field": "birthday", "value": date(1968, 6, 12)},
    ],
)
def test_accepts_values_when_conditional_validation_succeed(good_value):
    schema = Dict(
        keys=[
            Key("field", Str()),
            Key("value", Str(), predicate=lambda d: d.get("field") == "name"),
            Key("value", Date(), predicate=lambda d: d.get("field") == "birthday"),
        ]
    )

    assert schema(good_value) == good_value


@pytest.mark.parametrize(
    "bad_value,type_name",
    [
        ({"field": "name", "value": date(1968, 6, 12)}, type_name("str")),
        ({"field": "birthday", "value": "Marty"}, type_name("date")),
    ],
)
def test_rejects_values_when_conditional_validation_failed(bad_value, type_name):
    schema = Dict(
        keys=[
            Key("field", Str()),
            Key("value", Str(), predicate=lambda d: d.get("field") == "name"),
            Key("value", Date(), predicate=lambda d: d.get("field") == "birthday"),
        ]
    )

    with assert_dict_value_errors(
        {"value": [Error("unexpected_type", {"expected_type": type_name})]}
    ):
        schema(bad_value)


def test_applies_rules_when_value_not_none_and_has_expected_type():
    schema = Dict(rules=[validate_keys_count_is_odd_and_add_bar_dict_key])

    with assert_errors([Error("key_count_is_not_odd")]):
        schema({})

    assert schema({"foo": 0}) == {"foo": 0, "bar": 1}


def test_ignores_rules_when_value_is_none_and_denied():
    schema = Dict(rules=[validate_keys_count_is_odd_and_add_bar_dict_key])

    with assert_errors([Error("cannot_be_none")]):
        schema(None)


def test_ignores_rules_when_value_is_none_and_allowed():
    schema = Dict(
        allow_none=True, rules=[validate_keys_count_is_odd_and_add_bar_dict_key]
    )
    assert schema(None) is None


def test_ignores_rules_when_value_has_unexpected_type():
    schema = Dict(rules=[validate_keys_count_is_odd_and_add_bar_dict_key])

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("dict")})]
    ):
        schema(42)


def validate_keys_count_is_odd_and_add_bar_dict_key(
    self: Dict, value, typecast: bool, context: dict
):
    if len(value.keys()) % 2 == 1:
        return {**value, "bar": 1}, []
    else:
        return value, [self.error("key_count_is_not_odd")]
