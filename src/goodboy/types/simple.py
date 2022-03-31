from __future__ import annotations

import re
from typing import Any, Optional, Pattern, Union

from goodboy.errors import Error
from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Rule, SchemaWithUtils


class AnyValue(SchemaWithUtils):
    """
    Accept any values, taking into account ``allow_none`` and ``allowed`` options.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    :param allowed: Allow only certain values.
    """

    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
        allowed: Optional[list[Any]] = None,
    ) -> None:
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self._allowed = allowed

    def _validate(
        self, value: Any, typecast: bool, context: dict[str, Any] = {}
    ) -> tuple[Any, list[Error]]:
        if self._allowed is not None and value not in self._allowed:
            return None, [self._error("not_allowed")]

        value, rule_errors = self._call_rules(value, typecast, context)

        return value, rule_errors

    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[Any, list[Error]]:
        return input, []


class NoneValue(SchemaWithUtils):
    """
    Accept ``None`` values. Type casting is not performed.

    :param messages: Override error messages.
    :param rules: Custom validation rules.
    """

    def __init__(
        self,
        *,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
    ) -> None:
        super().__init__(allow_none=True, messages=messages, rules=rules)

    def _validate(
        self, value: Any, typecast: bool, context: dict[str, Any] = {}
    ) -> tuple[None, list[Error]]:
        if value is not None:
            return None, [self._error("must_be_none")]

        value, rule_errors = self._call_rules(value, typecast, context)

        return value, rule_errors

    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[None, list[Error]]:
        return input, []


class Str(SchemaWithUtils):
    """
    Accept ``str`` values.

    When blank string found, only ``allow_blank`` validation applied.

    Since any python object can be casted to string (even complex types like ``dict`` or
    ``list``), it's too dangerous to automatically cast input value.
    Therefore, **strings are not type casted**.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    :param allow_blank: If true, value is allowed to be empty string. Defaults to false.
    :param min_length: Minimal allowed string length.
    :param max_length: Maximum allowed string length.
    :param length: Exact allowed string length.
    :param pattern: Regex to match string value.
    :param is_regex: Value itself should be valid regex.
    :param allowed: Allow only certain values.
    """

    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
        allow_blank: bool = False,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        length: Optional[int] = None,
        pattern: Union[str, Pattern[str], None] = None,
        is_regex: bool = False,
        allowed: Optional[list[str]] = None,
    ) -> None:
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self._allow_blank = allow_blank
        self._min_length = min_length
        self._max_length = max_length
        self._length = length

        self._pattern: Optional[Pattern[str]]

        if isinstance(pattern, str):
            self._pattern = re.compile(pattern)
        else:
            self._pattern = pattern

        self._is_regex = is_regex
        self._allowed = allowed

    def _validate(
        self, value: Any, typecast: bool, context: dict[str, Any] = {}
    ) -> tuple[Optional[str], list[Error]]:
        if not isinstance(value, str):
            return None, [
                self._error("unexpected_type", {"expected_type": type_name("str")})
            ]

        if not value:
            if self._allow_blank:
                return value, []
            else:
                return None, [self._error("cannot_be_blank")]

        errors = []

        if self._allowed is not None and value not in self._allowed:
            errors.append(self._error("not_allowed", {"allowed": self._allowed}))

        if self._min_length is not None and len(value) < self._min_length:
            errors.append(self._error("string_too_short", {"value": self._min_length}))

        if self._max_length is not None and len(value) > self._max_length:
            errors.append(self._error("string_too_long", {"value": self._max_length}))

        if self._length is not None and len(value) != self._length:
            errors.append(self._error("invalid_string_length", {"value": self._length}))

        if self._pattern and not self._pattern.match(value):
            errors.append(self._error("invalid_string_format"))

        if self._is_regex:
            try:
                re.compile(value)
            except re.error:
                errors.append(self._error("invalid_regex"))

        value, rule_errors = self._call_rules(value, typecast, context)

        return value, errors + rule_errors

    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[Optional[str], list[Error]]:
        # Any python object usually can be casted to string, so casting any value to
        # string is too dangerous
        if isinstance(input, str):
            return input, []
        else:
            return None, [
                self._error("unexpected_type", {"expected_type": type_name("str")})
            ]


class Bool(SchemaWithUtils):
    """
    Accept ``bool`` values.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    :param only_false: Allow only ``False`` values.
    :param only_true: Allow only ``True`` values.
    """

    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
        only_false: bool = False,
        only_true: bool = False,
        cast_anything: bool = False,
    ) -> None:
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self._only_false = only_false
        self._only_true = only_true
        # TODO: override cast_anything in validation context
        self._cast_anything = cast_anything

    def _validate(
        self, value: Any, typecast: bool, context: dict[str, Any] = {}
    ) -> tuple[Optional[bool], list[Error]]:
        if not isinstance(value, bool):
            return None, [
                self._error("unexpected_type", {"expected_type": type_name("bool")})
            ]

        errors = []

        if self._only_false and value:
            errors.append(self._error("not_allowed", {"allowed": [False]}))

        if self._only_true and not value:
            errors.append(self._error("not_allowed", {"allowed": [True]}))

        value, rule_errors = self._call_rules(value, typecast, context)

        return value, errors + rule_errors

    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[Optional[bool], list[Error]]:
        if isinstance(input, bool):
            return input, []

        if self._cast_anything:
            return bool(input), []

        if isinstance(input, str):
            if input.lower() == "true":
                return True, []

            if input.lower() == "false":
                return False, []

        return None, [
            self._error("unexpected_type", {"expected_type": type_name("bool")})
        ]
