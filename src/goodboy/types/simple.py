from __future__ import annotations

import re
from typing import Any, Optional, Pattern, Union

from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Rule, Schema


class AnyValue(Schema):
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
    ):
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self.allowed = allowed

    def validate(self, value, typecast: bool, context: dict = {}):
        if self.allowed is not None and value not in self.allowed:
            return None, [self.error("not_allowed")]

        value, rule_errors = self.call_rules(value, typecast, context)

        return value, rule_errors

    def typecast(self, input, context: dict = {}):
        return input, []


class NoneValue(Schema):
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
    ):
        super().__init__(allow_none=True, messages=messages, rules=rules)

    def validate(self, value, typecast: bool, context: dict = {}):
        if value is not None:
            return None, [self.error("must_be_none")]

        value, rule_errors = self.call_rules(value, typecast, context)

        return value, rule_errors

    def typecast(self, input, context: dict = {}):
        return input, []


class Str(Schema):
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
    :param pattern: Regexp to match string value.
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
        allowed: Optional[list[str]] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self.allow_blank = allow_blank
        self.min_length = min_length
        self.max_length = max_length
        self.length = length

        self.pattern: Optional[Pattern[str]]

        if isinstance(pattern, str):
            self.pattern = re.compile(pattern)
        else:
            self.pattern = pattern

        self.allowed = allowed

    def validate(self, value, typecast: bool, context: dict = {}):
        if not isinstance(value, str):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("str")})
            ]

        if not value:
            if self.allow_blank:
                return value, []
            else:
                return None, [self.error("cannot_be_blank")]

        errors = []

        if self.allowed is not None and value not in self.allowed:
            errors.append(self.error("not_allowed", {"allowed": self.allowed}))

        if self.min_length is not None and len(value) < self.min_length:
            errors.append(self.error("string_too_short", {"value": self.min_length}))

        if self.max_length is not None and len(value) > self.max_length:
            errors.append(self.error("string_too_long", {"value": self.max_length}))

        if self.length is not None and len(value) != self.length:
            errors.append(self.error("invalid_string_length", {"value": self.length}))

        if self.pattern and not self.pattern.match(value):
            errors.append(self.error("invalid_string_format"))

        value, rule_errors = self.call_rules(value, typecast, context)

        return value, errors + rule_errors

    def typecast(self, input, context: dict = {}):
        # Any python object usually can be casted to string, so casting any value to
        # string is too dangerous
        if isinstance(input, str):
            return input, []
        else:
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("str")})
            ]
