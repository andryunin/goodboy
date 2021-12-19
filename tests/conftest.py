from __future__ import annotations

from contextlib import contextmanager

import pytest

from goodboy.declarative import DeclarationError
from goodboy.errors import Error
from goodboy.schema import SchemaError


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
