from __future__ import annotations

from abc import abstractmethod
from datetime import date, datetime
from typing import Generic, Optional, TypeVar, Union

from goodboy.errors import Error
from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Rule, Schema

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
        rules: list[Rule] = [],
        earlier_than: Optional[Union[D, str]] = None,
        earlier_or_equal_to: Optional[Union[D, str]] = None,
        later_than: Optional[Union[D, str]] = None,
        later_or_equal_to: Optional[Union[D, str]] = None,
        format: str = None,
        allowed: Optional[list[Union[D, str]]] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self.earlier_than = self._typecast_option(earlier_than)
        self.earlier_or_equal_to = self._typecast_option(earlier_or_equal_to)
        self.later_than = self._typecast_option(later_than)
        self.later_or_equal_to = self._typecast_option(later_or_equal_to)
        self.format = format

        if allowed:
            self.allowed = list(map(self._typecast_option, allowed))
        else:
            self.allowed = allowed

    def validate(self, value, typecast: bool, context: dict = {}):
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

        value, rule_errors = self.call_rules(value, typecast, context)

        return value, errors + rule_errors

    @abstractmethod
    def validate_exact_type(self, value) -> list[Error]:
        ...

    @abstractmethod
    def _typecast_option(self, input: Optional[Union[D, str]]) -> Optional[D]:
        ...


class Date(DateBase[date]):
    """
    Accept ``datetime.date`` values.

    When type casting enabled, strings are converted to ``datetime.date`` using
    ``format`` option as strptime format.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
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

    def typecast(self, input, context: dict = {}):
        if isinstance(input, date):
            return input, []

        if not isinstance(input, str):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("date")})
            ]

        try:
            if context.get("date_format"):
                format = context.get("date_format")
            elif self.format:
                format = self.format
            else:
                format = None

            if format:
                return datetime.strptime(input, format).date(), []
            else:
                return date.fromisoformat(input), []

        except ValueError:
            return None, [self.error("invalid_date_format")]

    def _typecast_option(self, input: Optional[Union[date, str]]) -> Optional[date]:
        if input is None:
            return None

        if isinstance(input, date):
            return input

        return date.fromisoformat(input)


class DateTime(DateBase[datetime]):
    """
    Accept ``datetime.datetime`` values.

    When type casting enabled, strings are converted to ``datetime.datetime`` using
    ``format`` option as strptime format.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
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

    def typecast(self, input, context: dict = {}):
        if isinstance(input, datetime):
            return input, []

        if not isinstance(input, str):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("datetime")})
            ]

        try:
            if context.get("date_format"):
                format = context.get("date_format")
            elif self.format:
                format = self.format
            else:
                format = None

            if format:
                return datetime.strptime(input, format), []
            else:
                return datetime.fromisoformat(input), []

        except ValueError:
            return None, [self.error("invalid_datetime_format")]

    def _typecast_option(
        self, input: Optional[Union[datetime, str]]
    ) -> Optional[datetime]:
        if input is None:
            return None

        if isinstance(input, datetime):
            return input

        return datetime.fromisoformat(input)
