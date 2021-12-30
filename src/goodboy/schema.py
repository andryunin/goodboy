from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Tuple

from goodboy.errors import DEFAULT_MESSAGES, Error
from goodboy.messages import MessageCollection, MessageCollectionType


class SchemaError(Exception):
    def __init__(self, errors: list[Error]):
        self.errors = errors


Rule = Callable[["Schema", Any, bool, dict], Tuple[Any, List[Error]]]


class Schema(ABC):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
    ):
        self._allow_none = allow_none

        if isinstance(messages, MessageCollection):
            self._messages = messages
        else:
            self._messages = MessageCollection(messages, parent=DEFAULT_MESSAGES)

        self._rules = rules

    def __call__(self, value, *, typecast=False, context: dict = {}):
        if value is None:
            if not self._allow_none:
                raise SchemaError([self._error("cannot_be_none")])

            return None

        if typecast:
            value, errors = self._typecast(value, context)

            if errors:
                raise SchemaError(errors)

        value, errors = self._validate(value, typecast, context)

        if errors:
            raise SchemaError(errors)

        return value

    @abstractmethod
    def _validate(
        self, value: Any, typecast: bool, context: dict = {}
    ) -> tuple[Any, list[Error]]:
        ...

    @abstractmethod
    def _typecast(self, input: Any, context: dict = {}) -> tuple[Any, list[Error]]:
        ...

    def _error(self, code: str, args: dict = {}, nested_errors: dict = {}):
        return Error(code, args, nested_errors, self._messages.get_message(code))

    def _call_rules(
        self, value: Any, typecast=False, context: dict = {}
    ) -> tuple[Any, list[Error]]:
        result_errors = []

        for rule in self._rules:
            value, errors = rule(self, value, typecast, context)
            result_errors += errors

        return value, result_errors

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return super().__eq__(other)
