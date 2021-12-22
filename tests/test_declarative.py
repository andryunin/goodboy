from goodboy.declarative import DEFAULT_DECLARATIVE_SCHEMA_FABRICS, DeclarativeBuilder
from goodboy.errors import Error
from goodboy.messages import type_name

from .conftest import (
    assert_declarative_errors,
    assert_dict_value_errors,
    assert_errors,
    assert_list_value_errors,
)

ALLOWED_SCHEMA_NAMES = list(DEFAULT_DECLARATIVE_SCHEMA_FABRICS.keys())


def test_allows_only_exist_schemas():
    builder = DeclarativeBuilder()

    with assert_declarative_errors(
        {"schema": [Error("not_allowed", {"allowed": ALLOWED_SCHEMA_NAMES})]}
    ):
        builder.build({"schema": "spaceship"})


def test_rejects_invalid_schema_options():
    builder = DeclarativeBuilder()

    with assert_declarative_errors({"max_length": [Error("less_than", {"value": 0})]}):
        builder.build({"schema": "str", "max_length": -1})


def test_builds_valid_schema_options():
    def validate_is_even(self, value, typecast: bool, context: dict):
        if value % 2 == 0:
            return value, []
        else:
            return value, [self.error("not_an_event_value")]

    schema = DeclarativeBuilder().build(
        {
            "schema": "int",
            "less_or_equal_to": 100,
            "greater_or_equal_to": 0,
            "rules": [validate_is_even],
        }
    )

    assert schema(42) == 42

    with assert_errors([Error("less_than", {"value": 0})]):
        schema(-50)

    with assert_errors([Error("greater_than", {"value": 100})]):
        schema(200)

    with assert_errors([Error("not_an_event_value")]):
        schema(1)


def test_bool_building():
    schema = DeclarativeBuilder().build({"schema": "bool"})

    assert schema(True) is True
    assert schema(False) is False

    with assert_errors(
        [Error("unexpected_type", {"expected_type": type_name("bool")})]
    ):
        schema("oops", typecast=True)


def test_dict_building():
    schema = DeclarativeBuilder().build(
        {
            "schema": "dict",
            "keys": [
                {
                    "name": "title",
                    "schema": {"schema": "str"},
                },
                {
                    "name": "flags",
                    "schema": {
                        "schema": "dict",
                        "key_schema": {"schema": "str"},
                        "value_schema": {"schema": "bool"},
                    },
                },
            ],
        }
    )

    good_value = {"title": "Good title", "flags": {"foo": True, "bar": False}}

    assert schema(good_value) == good_value

    bad_value = {"title": "Good title", "flags": {"foo": 42, "bar": "false"}}

    with assert_dict_value_errors(
        {
            "flags": [
                Error(
                    "value_errors",
                    nested_errors={
                        "foo": [
                            Error(
                                "unexpected_type", {"expected_type": type_name("bool")}
                            )
                        ]
                    },
                )
            ]
        }
    ):
        schema(bad_value, typecast=True)


def test_list_building():
    schema = DeclarativeBuilder().build(
        {
            "schema": "list",
            "item": {"schema": "str"},
        }
    )

    good_value = ["foo", "bar"]

    assert schema(good_value) == good_value

    bad_value = ["foo", 42]

    with assert_list_value_errors(
        {1: [Error("unexpected_type", {"expected_type": type_name("str")})]}
    ):
        schema(bad_value, typecast=True)
