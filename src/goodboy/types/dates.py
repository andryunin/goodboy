from __future__ import annotations

from abc import abstractmethod
from datetime import date, datetime
from typing import Generic, Optional, TypeVar

from goodboy.errors import Error
from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Schema

D = TypeVar("D")


class DateBase(Generic[D], Schema):
    """
    Abstract base class for Date/DateTime schemas, should not be used directly. Use
    :class:`Date` or :class:`DateTime` instead.
    """

    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        earlier_than: Optional[D] = None,
        earlier_or_equal_to: Optional[D] = None,
        later_than: Optional[D] = None,
        later_or_equal_to: Optional[D] = None,
        format: str = None,
        allowed: Optional[list[D]] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
        self.earlier_than = earlier_than
        self.earlier_or_equal_to = earlier_or_equal_to
        self.later_than = later_than
        self.later_or_equal_to = later_or_equal_to
        self.format = format
        self.allowed = allowed

    def validate(self, value, typecast):
        type_errors = self.validate_exact_type(value)

        if type_errors:
            return value, type_errors

        errors = []

        if self.allowed is not None and value not in self.allowed:
            errors.append(self.error("not_allowed", {"allowed": self.allowed}))

        if self.earlier_than and value >= self.earlier_than:
            errors.append(self.error("later_or_equal_to", {"value": self.earlier_than}))

        if self.earlier_or_equal_to and value > self.earlier_or_equal_to:
            errors.append(self.error("later_than", {"value": self.earlier_or_equal_to}))

        if self.later_than and value <= self.later_than:
            errors.append(self.error("earlier_or_equal_to", {"value": self.later_than}))

        if self.later_or_equal_to and value < self.later_or_equal_to:
            errors.append(self.error("earlier_than", {"value": self.later_or_equal_to}))

        return value, errors

    @abstractmethod
    def validate_exact_type(self, value) -> list[Error]:
        ...


class Date(DateBase[date]):
    """
    Accept ``datetime.date`` values.

    When type casting enabled, strings are converted to ``datetime.date`` using
    ``format`` option as strptime format.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param earlier_than: Accept only values earlier than option value.
    :param earlier_or_equal_to: Accept only values earlier than or equal to option
        value.
    :param later_than: Accept only values later than option value.
    :param later_or_equal_to: Accept only values later than or equal to option value.
    :param format: date format for type casting. See
        `strftime() and strptime() Behavior <https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior>`_
        for details.

    :param allowed: Allow only certain values.
    """  # noqa: E501

    def validate_exact_type(self, value) -> list[Error]:
        if not isinstance(value, date):
            return [self.error("unexpected_type", {"expected_type": type_name("date")})]
        else:
            return []

    def typecast(self, input):
        if isinstance(input, date):
            return input, []

        if not isinstance(input, str):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("date")})
            ]

        try:
            if self.format:
                return datetime.strptime(input, self.format).date(), []
            else:
                return date.fromisoformat(input), []

        except ValueError:
            return None, [self.error("invalid_date_format")]


class DateTime(DateBase[datetime]):
    """
    Accept ``datetime.datetime`` values.

    When type casting enabled, strings are converted to ``datetime.datetime`` using
    ``format`` option as strptime format.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param earlier_than: Accept only values earlier than option value.
    :param earlier_or_equal_to: Accept only values earlier than or equal to option
        value.
    :param later_than: Accept only values later than option value.
    :param later_or_equal_to: Accept only values later than or equal to option value.
    :param format: datetime format for type casting. See
        `strftime() and strptime() Behavior <https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior>`_
        for details.

    :param allowed: Allow only certain values.
    """  # noqa: E501

    def validate_exact_type(self, value) -> list[Error]:
        if not isinstance(value, datetime):
            return [
                self.error("unexpected_type", {"expected_type": type_name("datetime")})
            ]
        else:
            return []

    def typecast(self, input):
        if isinstance(input, datetime):
            return input, []

        if not isinstance(input, str):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("datetime")})
            ]

        try:
            if self.format:
                return datetime.strptime(input, self.format), []
            else:
                return datetime.fromisoformat(input), []

        except ValueError:
            return None, [self.error("invalid_datetime_format")]
