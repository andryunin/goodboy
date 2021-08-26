from contextlib import contextmanager

import pytest

from goodboy.schema import Error, InvalidValueError


@contextmanager
def assert_errors(errors: list[Error]):
    with pytest.raises(InvalidValueError) as e:
        yield

    assert e.value.errors == errors
