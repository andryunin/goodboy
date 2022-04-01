from __future__ import annotations

from abc import abstractmethod
from typing import Any, Callable, Generic, List, Optional, Tuple, TypeVar, Union

from goodboy.errors import Error
from goodboy.messages import DEFAULT_MESSAGES, MessageCollection, MessageCollectionType


class SchemaError(Exception):
    def __init__(self, errors: list[Error]):
        self.errors = errors


T = TypeVar("T")


class Schema(Generic[T]):
    @abstractmethod
    def __call__(
        self, value: Any, *, typecast: bool = False, context: dict[str, Any] = {}
    ) -> Optional[T]:
        ...


class SchemaErrorMixin:
    _messages: MessageCollection

    def _error(
        self,
        code: str,
        args: dict[str, Any] = {},
        nested_errors: dict[Union[str, int], list[Error]] = {},
    ) -> Error:
        return Error(code, args, nested_errors, self._messages.get_message(code))


Rule = Callable[["SchemaRulesMixin", Any, bool, dict], Tuple[Any, List[Error]]]


class SchemaRulesMixin:
    _rules: list[Rule]

    def _call_rules(
        self, value: Any, typecast: bool = False, context: dict[str, Any] = {}
    ) -> tuple[Any, list[Error]]:
        result_errors = []

        for rule in self._rules:
            value, errors = rule(self, value, typecast, context)
            result_errors += errors

        return value, result_errors


class SchemaWithUtils(Schema[T], SchemaErrorMixin, SchemaRulesMixin):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
    ) -> None:
        self._allow_none = allow_none

        if isinstance(messages, MessageCollection):
            self._messages = messages
        else:
            self._messages = MessageCollection(messages, parent=DEFAULT_MESSAGES)

        self._rules = rules

    def __call__(
        self, value: Any, *, typecast: bool = False, context: dict[str, Any] = {}
    ) -> Optional[T]:
        if value is None:
            if not self._allow_none:
                raise SchemaError([self._error("cannot_be_none")])

            return None

        if typecast:
            value, errors = self._typecast(value, context)

            if errors:
                raise SchemaError(errors)

        result_value, errors = self._validate(value, typecast, context)

        if errors:
            raise SchemaError(errors)

        return result_value

    @abstractmethod
    def _validate(
        self, value: Any, typecast: bool, context: dict[str, Any] = {}
    ) -> tuple[Optional[T], list[Error]]:
        ...

    @abstractmethod
    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[Any, list[Error]]:
        ...

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return super().__eq__(other)
