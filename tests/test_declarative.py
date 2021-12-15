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


def test_builds_invalid_schema_options():
    schema = DeclarativeBuilder().build(
        {"schema": "int", "less_or_equal_to": 100, "greater_or_equal_to": 0}
    )

    assert schema(42) == 42

    with assert_errors([Error("less_than", {"value": 0})]):
        schema(-1)

    with assert_errors([Error("greater_than", {"value": 100})]):
        schema(200)
