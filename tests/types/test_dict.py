from datetime import datetime

from goodboy.errors import Error
from goodboy.messages import type_name
from goodboy.types.dates import DateTime
from goodboy.types.dicts import Dict, Key
from goodboy.types.numeric import Int
from goodboy.types.simple import AnyType
from tests.types.conftest import assert_errors


def test_key_required():
    schema = Dict(
        keys=[
            Key("key_0", AnyType()),
            Key("key_1", AnyType(), required=False),
        ]
    )

    good_value = {"key_0": 0, "key_1": 1}
    assert schema({"key_0": 0, "key_1": 1}) == good_value

    bad_value = good_value = {"key_1": 1}

    bad_value_errors = [
        Error(
            "keys_error",
            args={
                "key_0": [Error("required_key")],
            },
        )
    ]

    with assert_errors(bad_value_errors):
        schema(bad_value)


def test_value_validation():
    schema = Dict(
        keys=[
            Key("timestamp", DateTime()),
            Key("value", Int(allow_none=True)),
        ]
    )

    good_value = {"timestamp": datetime(2021, 10, 10, 21, 30, 00), "value": None}
    assert schema(good_value) == good_value

    bad_value = {
        "timestamp": None,
        "value": None,
    }

    bad_value_errors = [
        Error(
            "keys_error",
            args={
                "timestamp": [Error("cannot_be_none")],
            },
        )
    ]

    with assert_errors(bad_value_errors):
        schema(bad_value)


def test_value_typecasting():
    schema = Dict(
        keys=[
            Key("timestamp", DateTime()),
            Key("value", Int()),
        ]
    )

    value = {"timestamp": datetime(2021, 10, 10, 21, 30, 00), "value": 42}

    good_value = {"timestamp": "2021-10-10T21:30:00", "value": "42"}
    assert schema(good_value, typecast=True) == value

    bad_value = {
        "timestamp": "oops",
        "value": "oops",
    }

    bad_value_errors = [
        Error(
            "keys_error",
            args={
                "timestamp": [Error("invalid_datetime_format")],
                "value": [Error("invalid_integer_format")],
            },
        )
    ]

    with assert_errors(bad_value_errors):
        schema(bad_value, typecast=True)


def test_typecast():
    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("dict")})]
    ):
        Dict()("oops", typecast=True)


def test_typecheck():
    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("dict")})]
    ):
        Dict()("oops")


def test_allow_none():
    assert Dict(allow_none=True)(None) is None

    with assert_errors([Error("cannot_be_none")]):
        Dict()(None)
