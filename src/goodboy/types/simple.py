from __future__ import annotations

import re
from typing import Any, Optional, Pattern, Union

from goodboy.messages import DEFAULT_MESSAGES, MessageCollection, type_name
from goodboy.schema import Schema


# TODO: rename to AnyValue for consistency
class AnyType(Schema):
    """
    Accept any values, taking into account ``allow_none`` and ``allowed`` options.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param allowed: Allow only certain values.
    """

    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollection = DEFAULT_MESSAGES,
        allowed: Optional[list[Any]] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
        self.allowed = allowed

    def validate(self, value, typecast):
        if self.allowed is not None and value not in self.allowed:
            return None, [self.error("not_allowed")]

        return value, []

    def typecast(self, value):
        return value, []


class NoneValue(Schema):
    """
    Accept ``None`` values. Type casting is not performed.

    :param messages: Override error messages.
    """

    def __init__(
        self,
        *,
        messages: MessageCollection = DEFAULT_MESSAGES,
    ):
        super().__init__(allow_none=True, messages=messages)

    def validate(self, value, typecast):
        if value is not None:
            return None, [self.error("must_be_none")]

        return value, []

    def typecast(self, value):
        return value, []


class Str(Schema):
    """
    Accept ``str`` values.

    When blank string found, only ``allow_blank`` validation applied.

    Since any python object can be casted to string (even complex types like ``dict`` or
    ``list``), it's too dangerous to automatically cast input value.
    Therefore, **strings are not type casted**.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
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
        messages: MessageCollection = DEFAULT_MESSAGES,
        allow_blank: bool = False,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        length: Optional[int] = None,
        pattern: Union[str, Pattern[str], None] = None,
        allowed: Optional[list[str]] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
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

    def validate(self, value, typecast):
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

        return value, errors

    def typecast(self, input):
        # Any python object usually can be casted to string, so casting any value to
        # string is too dangerous
        if isinstance(input, str):
            return input, []
        else:
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("str")})
            ]
