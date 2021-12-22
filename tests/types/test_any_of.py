import pytest

from goodboy.errors import Error
from goodboy.types.simple import Str
from goodboy.types.variants import AnyOf
from tests.conftest import assert_errors

schemas = [Str(allowed=["foo"]), Str(allowed=["bar"])]


def test_accept_value_valid_by_any_schema():
    assert AnyOf(schemas)("foo") == "foo"
    assert AnyOf(schemas)("bar") == "bar"


expected_schema_errors = {
    0: [Error("not_allowed", {"allowed": ["foo"]})],
    1: [Error("not_allowed", {"allowed": ["bar"]})],
}

expected_anyof_error = Error("no_variant_found", {"errors": expected_schema_errors})


def test_rejects_value_invalid_by_all_schemas():
    schema = AnyOf(schemas)

    with assert_errors([expected_anyof_error]):
        schema("oops")


expected_rule_error = Error("rule_error")


def rule(self: Str, value, typecast: bool, context: dict):
    return value, [expected_rule_error]


def test_applies_rules_when_value_not_is_invalid():
    schema = AnyOf(schemas, rules=[rule])

    with assert_errors([expected_anyof_error, expected_rule_error]):
        schema("oops")
