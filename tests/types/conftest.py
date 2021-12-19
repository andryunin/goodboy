from __future__ import annotations

from contextlib import contextmanager

import pytest

from goodboy.errors import Error
from goodboy.schema import SchemaError


@contextmanager
def assert_errors(errors: list[Error]):
    with pytest.raises(SchemaError) as e:
        yield

    assert e.value.errors == errors


@contextmanager
def assert_dict_key_errors(key_errors: dict[str, list[Error]]):
    with pytest.raises(SchemaError) as e:
        yield

    assert e.value.errors == [Error("key_errors", nested_errors=key_errors)]


@contextmanager
def assert_dict_value_errors(value_errors: dict[str, list[Error]]):
    with pytest.raises(SchemaError) as e:
        yield

    assert e.value.errors == [Error("value_errors", nested_errors=value_errors)]


@contextmanager
def assert_list_value_errors(value_errors: dict[str, list[Error]]):
    with pytest.raises(SchemaError) as e:
        yield

    assert e.value.errors == [Error("value_errors", nested_errors=value_errors)]


def validate_value_is_42_and_double_it(self, value, typecast: bool, context: dict):
    if value == 42:
        return value * 2, []
    else:
        return 42, [self.error("not_a_42")]


def validate_value_has_odd_year(self, value, typecast: bool, context: dict):
    if value.year % 2 == 1:
        return value, []
    else:
        return value, [self.error("not_an_odd_year")]
