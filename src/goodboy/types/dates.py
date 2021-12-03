from __future__ import annotations

from datetime import datetime
from typing import Optional

from goodboy.errors import DEFAULT_MESSAGES, MessageCollection
from goodboy.schema import Schema


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
