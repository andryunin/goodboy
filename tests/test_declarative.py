from goodboy.declarative import DEFAULT_DECLARATIVE_SCHEMA_FABRICS, DeclarativeBuilder
from goodboy.errors import Error

from .conftest import assert_declarative_errors, assert_errors

ALLOWED_SCHEMA_NAMES = list(DEFAULT_DECLARATIVE_SCHEMA_FABRICS.keys())


def test_allows_only_exist_schemas():
    builder = DeclarativeBuilder()

    with assert_declarative_errors(
        {"schema": Error("not_allowed", {"allowed": ALLOWED_SCHEMA_NAMES})}
    ):
        builder.build({"schema": "spaceship"})


def test_rejects_invalid_schema_options():
    builder = DeclarativeBuilder()

    with assert_declarative_errors({"max_length": Error("less_than", {"value": 0})}):
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
