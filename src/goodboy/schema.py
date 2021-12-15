from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from goodboy.errors import DEFAULT_MESSAGES, Error
from goodboy.messages import MessageCollection, MessageCollectionType


class SchemaError(Exception):
    def __init__(self, errors: list[Error]):
        self.errors = errors


class Schema(ABC):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
    ):
        self.allow_none = allow_none

        if isinstance(messages, MessageCollection):
            self.messages = messages
        else:
            self.messages = MessageCollection(messages, parent=DEFAULT_MESSAGES)

    def __call__(self, value, *, typecast=False, context: dict = {}):
        if value is None:
            if not self.allow_none:
                raise SchemaError([self.error("cannot_be_none")])

            return None

        if typecast:
            value, errors = self.typecast(value, context)

            if errors:
                raise SchemaError(errors)

        value, errors = self.validate(value, typecast, context)

        if errors:
            raise SchemaError(errors)

        return value

    @abstractmethod
    def validate(
        self, value: Any, typecast: bool, context: dict = {}
    ) -> tuple[Any, list[Error]]:
        ...

    @abstractmethod
    def typecast(self, input: Any, context: dict = {}) -> tuple[Any, list[Error]]:
        ...

    def error(self, code: str, args: dict = {}, nested_errors: dict = {}):
        return Error(code, args, nested_errors, self.messages)
