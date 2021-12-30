from __future__ import annotations

from contextlib import contextmanager

import pytest

from goodboy.declarative import DeclarationError
from goodboy.errors import Error
from goodboy.schema import SchemaError


class TranslationsMock:
    def __init__(self, translations):
        self._translations = translations

    def gettext(self, message):
        return self._translations[message]


@contextmanager
def assert_declarative_errors(value_errors: dict[str, list[Error]]):
    with pytest.raises(DeclarationError) as e:
        yield

    assert e.value.errors == [Error("value_errors", nested_errors=value_errors)]


@contextmanager
def assert_errors(errors: list[Error]):
    with pytest.raises(SchemaError) as e:
        yield

    assert e.value.errors == errors


@contextmanager
def assert_dict_key_errors(key_errors: dict[str, list[Error]]):
    with assert_errors([Error("key_errors", nested_errors=key_errors)]):
        yield


@contextmanager
def assert_dict_value_errors(value_errors: dict[str, list[Error]]):
    with assert_errors([Error("value_errors", nested_errors=value_errors)]):
        yield


@contextmanager
def assert_list_value_errors(value_errors: dict[str, list[Error]]):
    with assert_errors([Error("value_errors", nested_errors=value_errors)]):
        yield


def validate_value_is_42_and_double_it(self, value, typecast: bool, context: dict):
    if value == 42:
        return value * 2, []
    else:
        return 42, [self._error("not_a_42")]


def validate_value_has_odd_year(self, value, typecast: bool, context: dict):
    if value.year % 2 == 1:
        return value, []
    else:
        return value, [self._error("not_an_odd_year")]


def dummy_rule(value, typecast: bool, context: dict):
    return value, []


def dummy_key_predicate(value):
    return True
