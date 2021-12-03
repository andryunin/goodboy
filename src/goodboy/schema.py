from abc import ABC, abstractmethod
from typing import Any

from goodboy.errors import DEFAULT_MESSAGES, Error, MessageCollection


class SchemaError(Exception):
    def __init__(self, errors: list[Error]):
        self.errors = errors


class Schema(ABC):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollection = DEFAULT_MESSAGES,
    ):
        self.allow_none = allow_none
        self.messages = messages

    def __call__(self, value, *, typecast=False):
        if value is None:
            if not self.allow_none:
                raise SchemaError([self.error("cannot_be_none")])

            return None

        if typecast:
            value, errors = self.typecast(value)

            if errors:
                raise SchemaError(errors)

        value, errors = self.validate(value, typecast)

        if errors:
            raise SchemaError(errors)

        return value

    @abstractmethod
    def validate(self, value: Any, typecast: bool) -> list[Error]:
        ...

    @abstractmethod
    def typecast(self, value: Any) -> tuple[Any, list[Error]]:
        ...

    def error(self, code: str, args: dict = {}):
        return Error(code, args, self.messages)
