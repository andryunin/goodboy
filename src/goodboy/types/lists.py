from __future__ import annotations

from typing import Optional

from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Rule, Schema, SchemaError


class List(Schema):
    """
    Accept ``list`` value.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    :param item: Schema for list item.
    :param min_length: Minimal allowed list length.
    :param max_length: Maximum allowed list length.
    :param length: Exact allowed list length.
    """

    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
        item: Optional[Schema] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        length: Optional[int] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self._item = item
        self._min_length = min_length
        self._max_length = max_length
        self._length = length

    def _validate(self, value, typecast: bool, context: dict = {}):
        if not isinstance(value, list):
            return None, [
                self._error("unexpected_type", {"expected_type": type_name("list")})
            ]

        errors = []

        if self._min_length is not None and len(value) < self._min_length:
            errors.append(self._error("too_short", {"value": self._min_length}))

        if self._max_length is not None and len(value) > self._max_length:
            errors.append(self._error("too_long", {"value": self._max_length}))

        if self._length is not None and len(value) != self._length:
            errors.append(self._error("invalid_length", {"value": self._length}))

        if self._item:
            value_errors = {}
            result_value = []

            for item_index, item_value in enumerate(value):
                try:
                    item_value = self._item(item_value, typecast=typecast)
                except SchemaError as e:
                    value_errors[item_index] = e.errors
                else:
                    result_value.append(item_value)

            if value_errors:
                errors.append(self._error("value_errors", nested_errors=value_errors))
        else:
            result_value = value

        result_value, rule_errors = self._call_rules(result_value, typecast, context)

        return result_value, errors + rule_errors

    def _typecast(self, input, context: dict = {}):
        return input, []
