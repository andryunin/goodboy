from __future__ import annotations

from typing import Optional

from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Schema, SchemaError


class List(Schema):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        item: Optional[Schema] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        length: Optional[int] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
        self.item = item
        self.min_length = min_length
        self.max_length = max_length
        self.length = length

    def validate(self, value, typecast):
        if not isinstance(value, list):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("list")})
            ]

        errors = []

        if self.min_length is not None and len(value) < self.min_length:
            errors.append(self.error("too_short", {"value": self.min_length}))

        if self.max_length is not None and len(value) > self.max_length:
            errors.append(self.error("too_long", {"value": self.max_length}))

        if self.length is not None and len(value) != self.length:
            errors.append(self.error("invalid_length", {"value": self.length}))

        if self.item:
            value_errors = {}
            result_value = []

            for item_index, item_value in enumerate(value):
                try:
                    item_value = self.item(item_value, typecast=typecast)
                except SchemaError as e:
                    value_errors[item_index] = e.errors
                else:
                    result_value.append(item_value)

            if value_errors:
                errors.append(self.error("value_errors", nested_errors=value_errors))
        else:
            result_value = value

        return result_value, errors

    def typecast(self, input):
        return input, []
