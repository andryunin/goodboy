from goodboy.declarative import (
    _DEFAULT_DECLARATIVE_SCHEMA_FABRICS,
    DeclarativeBuilder,
    build,
)
from goodboy.errors import Error
from goodboy.types.dates import Date, DateTime
from goodboy.types.dicts import Dict, Key
from goodboy.types.lists import List
from goodboy.types.numeric import Float, Int
from goodboy.types.simple import AnyValue, Bool, NoneValue, Str
from goodboy.types.variants import AnyOf

from .conftest import assert_declarative_errors, dummy_key_predicate, dummy_rule

ALLOWED_SCHEMA_NAMES = list(_DEFAULT_DECLARATIVE_SCHEMA_FABRICS.keys())


def test_allows_only_known_schemas():
    builder = DeclarativeBuilder()

    with assert_declarative_errors(
        {"type": [Error("not_allowed", {"allowed": ALLOWED_SCHEMA_NAMES})]}
    ):
        builder.build({"type": "spaceship"})


def test_rejects_invalid_schema_options():
    builder = DeclarativeBuilder()

    with assert_declarative_errors({"max_length": [Error("less_than", {"value": 0})]}):
        builder.build({"type": "str", "max_length": -1})


def test_declarative_build_any():
    options = {
        "allow_none": True,
        "messages": {"oops": "Oops!"},
        "rules": [dummy_rule],
        "allowed": ["hello", 123],
    }

    assert build({"type": "any", **options}) == AnyValue(**options)


def test_declarative_build_none():
    options = {
        "messages": {"oops": "Oops!"},
        "rules": [dummy_rule],
    }

    assert build({"type": "none", **options}) == NoneValue(**options)


def test_declarative_build_str():
    options = {
        "allow_none": True,
        "messages": {"cannot_be_none": "No None here"},
        "rules": [dummy_rule],
        "allow_blank": False,
        "min_length": 2,
        "max_length": 5,
        "length": 50,
        "pattern": r"^\d+$",
        "is_regex": False,
        "allowed": ["123", "456"],
    }

    assert build({"type": "str", **options}) == Str(**options)


def test_declarative_build_bool():
    options = {
        "allow_none": True,
        "messages": {"cannot_be_none": "No None here"},
        "rules": [dummy_rule],
        "only_false": True,
        "only_true": True,
        "cast_anything": True,
    }

    assert build({"type": "bool", **options}) == Bool(**options)


def test_declarative_build_int():
    options = {
        "allow_none": True,
        "messages": {"cannot_be_none": "No None here"},
        "rules": [dummy_rule],
        "less_than": 10,
        "less_or_equal_to": 9,
        "greater_than": 0,
        "greater_or_equal_to": 1,
        "allowed": [123, 456],
    }

    assert build({"type": "int", **options}) == Int(**options)


def test_declarative_build_float():
    options = {
        "allow_none": True,
        "messages": {"cannot_be_none": "No None here"},
        "rules": [dummy_rule],
        "less_than": 10.0,
        "less_or_equal_to": 9.0,
        "greater_than": 0.0,
        "greater_or_equal_to": 1.0,
        "allowed": [123.0, 456.0],
    }

    assert build({"type": "float", **options}) == Float(**options)


def test_declarative_build_date():
    options = {
        "allow_none": True,
        "messages": {"cannot_be_none": "No None here"},
        "rules": [dummy_rule],
        "earlier_than": "2010-01-01",
        "earlier_or_equal_to": "2009-12-31",
        "later_than": "1999-12-31",
        "later_or_equal_to": "2000-01-01",
        "allowed": ["2000-01-01", "2009-12-31"],
    }

    assert build({"type": "date", **options}) == Date(**options)


def test_declarative_build_datetime():
    options = {
        "allow_none": True,
        "messages": {"cannot_be_none": "No None here"},
        "rules": [dummy_rule],
        "earlier_than": "2010-01-01T00:00:00",
        "earlier_or_equal_to": "2009-12-31T00:00:00",
        "later_than": "1999-12-31T00:00:00",
        "later_or_equal_to": "2000-01-01T00:00:00",
        "allowed": ["2000-01-01T00:00:00", "2009-12-31T00:00:00"],
    }

    assert build({"type": "datetime", **options}) == DateTime(**options)


def test_declarative_build_dict():
    options = {
        "allow_none": True,
        "messages": {"cannot_be_none": "No None here"},
        "rules": [dummy_rule],
        "keys": [
            {
                "name": "foo",
                "schema": {"type": "str", "allow_none": True},
                "required": True,
            },
            {
                "name": "bar",
                "schema": {"type": "int"},
                "predicate": ["$foo", "==", "bar"],
            },
        ],
        "key_schema": {"type": "str", "length": 3},
        "value_schema": {"type": "str", "length": 3},
        "keys_required_by_default": False,
    }

    schema = Dict(
        allow_none=True,
        messages={"cannot_be_none": "No None here"},
        rules=[dummy_rule],
        keys=[
            Key("foo", Str(allow_none=True), required=True),
            Key("bar", Int(), predicate=("$foo", "==", "bar")),
        ],
        key_schema=Str(length=3),
        value_schema=Str(length=3),
        keys_required_by_default=False,
    )

    assert build({"type": "dict", **options}) == schema


def test_declarative_build_list():
    options = {
        "allow_none": True,
        "messages": {"cannot_be_none": "No None here"},
        "rules": [dummy_rule],
        "item": {"type": "str", "length": 3},
        "min_length": 5,
        "max_length": 10,
        "length": 7,
    }

    schema = List(
        allow_none=True,
        messages={"cannot_be_none": "No None here"},
        rules=[dummy_rule],
        item=Str(length=3),
        min_length=5,
        max_length=10,
        length=7,
    )

    assert build({"type": "list", **options}) == schema


def test_declarative_build_any_of():
    options = {
        "schemas": [
            {"type": "str"},
            {"type": "int"},
        ],
        "messages": {"cannot_be_none": "No None here"},
        "rules": [dummy_rule],
    }

    schema = AnyOf(
        [Str(), Int()],
        messages={"cannot_be_none": "No None here"},
        rules=[dummy_rule],
    )

    assert build({"type": "any_of", **options}) == schema
