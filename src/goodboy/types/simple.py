from __future__ import annotations

import re
from typing import Optional, Pattern, Union

from goodboy.errors import DEFAULT_MESSAGES, MessageCollection
from goodboy.schema import Schema


class AnyType(Schema):
    def validate(self, value, typecast):
        return value, []

    def typecast(self, value):
        return value, []


class Str(Schema):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollection = DEFAULT_MESSAGES,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        length: Optional[int] = None,
        pattern: Union[str, Pattern[str], None] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
        self.min_length = min_length
        self.max_length = max_length
        self.length = length

        self.pattern: Optional[Pattern[str]]

        if isinstance(pattern, str):
            self.pattern = re.compile(pattern)
        else:
            self.pattern = pattern

    def validate(self, value, typecast):
        if not isinstance(value, str):
            return None, [self.error("unexpected_type", {"expected_type": "string"})]

        errors = []

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
            return None, [self.error("unexpected_type", {"expected_type": "string"})]
