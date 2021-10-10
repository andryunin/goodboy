from contextlib import contextmanager

import pytest

from goodboy.schema import Error, SchemaError


@contextmanager
def assert_errors(errors: list[Error]):
    with pytest.raises(SchemaError) as e:
        yield

    assert e.value.errors == errors
