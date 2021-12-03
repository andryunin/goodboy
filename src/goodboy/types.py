from __future__ import annotations

import re
from datetime import datetime
from typing import Optional, Pattern, Union

from goodboy.errors import DEFAULT_MESSAGES, Error, MessageCollection
from goodboy.schema import Schema, SchemaError


class AnyType(Schema):
    def validate(self, value, typecast):
        return value, []

    def typecast(self, value):
        return value, []


class DateTime(Schema):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollection = DEFAULT_MESSAGES,
        earlier_than: Optional[datetime] = None,
        earlier_or_equal_to: Optional[datetime] = None,
        later_than: Optional[datetime] = None,
        later_or_equal_to: Optional[datetime] = None,
        format: str = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
        self.earlier_than = earlier_than
        self.earlier_or_equal_to = earlier_or_equal_to
        self.later_than = later_than
        self.later_or_equal_to = later_or_equal_to
        self.format = format

    def validate(self, value, typecast):
        if not isinstance(value, datetime):
            return None, [self.error("unexpected_type", {"expected_type": "datetime"})]

        errors = []

        if self.earlier_than and value >= self.earlier_than:
            errors.append(self.error("later_or_equal_to", {"value": self.earlier_than}))

        if self.earlier_or_equal_to and value > self.earlier_or_equal_to:
            errors.append(self.error("later_than", {"value": self.earlier_or_equal_to}))

        if self.later_than and value <= self.later_than:
            errors.append(self.error("earlier_or_equal_to", {"value": self.later_than}))

        if self.later_or_equal_to and value < self.later_or_equal_to:
            errors.append(self.error("earlier_than", {"value": self.later_or_equal_to}))

        return value, errors

    def typecast(self, input):
        if isinstance(input, datetime):
            return input, []

        if not isinstance(input, str):
            return None, [self.error("unexpected_type", {"expected_type": "datetime"})]

        try:
            if self.format:
                return datetime.strptime(input, self.format), []
            else:
                return datetime.fromisoformat(input), []

        except ValueError:
            return None, [self.error("invalid_datetime_format")]


class Int(Schema):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollection = DEFAULT_MESSAGES,
        less_than: Optional[int] = None,
        less_or_equal_to: Optional[int] = None,
        greater_than: Optional[int] = None,
        greater_or_equal_to: Optional[int] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
        self.less_than = less_than
        self.less_or_equal_to = less_or_equal_to
        self.greater_than = greater_than
        self.greater_or_equal_to = greater_or_equal_to

    def validate(self, value, typecast):
        if not isinstance(value, int):
            return None, [self.error("unexpected_type", {"expected_type": "integer"})]

        errors = []

        if self.less_than is not None and value >= self.less_than:
            errors.append(self.error("greater_or_equal_to", {"value": self.less_than}))

        if self.less_or_equal_to is not None and value > self.less_or_equal_to:
            errors.append(self.error("greater_than", {"value": self.less_or_equal_to}))

        if self.greater_than is not None and value <= self.greater_than:
            errors.append(self.error("less_or_equal_to", {"value": self.greater_than}))

        if self.greater_or_equal_to is not None and value < self.greater_or_equal_to:
            errors.append(self.error("less_than", {"value": self.greater_or_equal_to}))

        return value, errors

    def typecast(self, input):
        if isinstance(input, int):
            return input, []

        if not isinstance(input, str):
            return None, [self.error("unexpected_type", {"expected_type": "integer"})]

        try:
            return int(input), []
        except ValueError:
            return None, [self.error("invalid_integer_format")]


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
            return None, [Error("invalid_type", {"expected_type": "str"})]

        errors = []

        if self.min_length is not None and len(value) < self.min_length:
            errors.append(Error("str.too_short", {"min_length": self.min_length}))

        if self.max_length is not None and len(value) > self.max_length:
            errors.append(Error("str.too_long", {"max_length": self.max_length}))

        if self.length is not None and len(value) != self.length:
            errors.append(Error("str.unexpected_length", {"length": self.length}))

        if self.pattern and not self.pattern.match(value):
            errors.append(Error("str.pattern"))

        return value, errors

    def typecast(self, value):
        if isinstance(value, str):
            return value, []

        try:
            return str(value), []
        except ValueError:
            return None, [Error("str.cast_error")]


class Key:
    def __init__(self, name, schema: Optional[Schema] = None, required: bool = True):
        self.name = name
        self.schema = schema
        self.required = required

    def validate(self, value, typecast):
        return self.schema(value, typecast=typecast)


# TODO: key_schema and key_value params for dynamic keys
# TODO: conditional validation
class Dict(Schema):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollection = DEFAULT_MESSAGES,
        keys: Optional[list[Key]] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
        self.keys = keys

    def validate(self, value, typecast):
        if not isinstance(value, dict):
            return None, [Error("invalid_type", {"expected_type": "dict"})]

        key_errors = {}
        key_values = {}

        if self.keys:
            value_keys = list(value.keys())

            for key in self.keys:
                if key.name in value_keys:
                    value_keys.remove(key.name)

                    try:
                        key_value = key.validate(value[key.name], typecast)
                    except SchemaError as e:
                        key_errors[key.name] = e.errors
                    else:
                        key_values[key.name] = key_value
                elif key.required:
                    key_errors[key.name] = [Error("dict.required_key")]

            for key in value_keys:
                key_errors[key] = [Error("dict.unknown_key")]

        if key_errors:
            return None, [Error("dict.keys_error", key_errors)]

        return key_values, []

    def typecast(self, value):
        return value, []
