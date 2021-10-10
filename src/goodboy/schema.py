from typing import Any

from abc import ABC, abstractmethod


class Error:
    def __init__(self, code: str, args: dict = {}):
        self.code = code
        self.args = args

    def __str__(self):
        return self.code

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.code} {repr(self.args)}>"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.code == other.code and self.args == other.args

        return super().__eq__(other)


class SchemaError(Exception):
    def __init__(self, errors: list[Error]):
        self.errors = errors


class Schema(ABC):
    def __init__(self, *, allow_none: bool = False):
        self.allow_none = allow_none

    def __call__(self, value, *, typecast=False):
        if value is None:
            if not self.allow_none:
                raise SchemaError([Error("cannot_be_none")])

            return None

        if typecast:
            value, errors = self.typecast(value)

            if errors:
                raise SchemaError(errors)

        errors = self.validate(value, typecast)

        if errors:
            raise SchemaError(errors)

        return value

    @abstractmethod
    def validate(self, value: Any, typecast: bool) -> list[Error]:
        ...

    @abstractmethod
    def typecast(self, value: Any) -> tuple[Any, list[Error]]:
        ...
