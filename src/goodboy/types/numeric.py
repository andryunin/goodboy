from __future__ import annotations

from abc import abstractmethod
from typing import Optional

from goodboy.errors import DEFAULT_MESSAGES, Error, MessageCollection
from goodboy.schema import Schema


class NumericBase(Schema):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollection = DEFAULT_MESSAGES,
        less_than: Optional[float] = None,
        less_or_equal_to: Optional[float] = None,
        greater_than: Optional[float] = None,
        greater_or_equal_to: Optional[float] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
        self.less_than = less_than
        self.less_or_equal_to = less_or_equal_to
        self.greater_than = greater_than
        self.greater_or_equal_to = greater_or_equal_to

    def validate(self, value, typecast):
        value, type_errors = self.validate_numeric_type(value)

        if type_errors:
            return None, type_errors

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

    @abstractmethod
    def validate_numeric_type(self, value) -> Optional[list[Error]]:
        ...


class Float(NumericBase):
    def validate_numeric_type(self, value):
        if isinstance(value, float):
            return value, []
        elif isinstance(value, int):
            return float(value), []
        else:
            return None, [self.error("unexpected_type", {"expected_type": "numeric"})]

    def typecast(self, input):
        if isinstance(input, float):
            return input, []

        if isinstance(input, int):
            return float(input), []

        if not isinstance(input, str):
            return None, [self.error("unexpected_type", {"expected_type": "numeric"})]

        try:
            return float(input), []
        except ValueError:
            return None, [self.error("invalid_numeric_format")]


class Int(NumericBase):
    def validate_numeric_type(self, value):
        if not isinstance(value, int):
            return None, [self.error("unexpected_type", {"expected_type": "integer"})]
        else:
            return value, []

    def typecast(self, input):
        if isinstance(input, int):
            return input, []

        if not isinstance(input, str):
            return None, [self.error("unexpected_type", {"expected_type": "integer"})]

        try:
            return int(input), []
        except ValueError:
            return None, [self.error("invalid_integer_format")]
