from __future__ import annotations

from abc import abstractmethod
from datetime import date, datetime
from typing import Any, Generic, Optional, TypeVar, Union

from goodboy.errors import Error
from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Rule, SchemaWithUtils

D = TypeVar("D")


class DateBase(Generic[D], SchemaWithUtils):
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
        format: Optional[str] = None,
        allowed: Optional[list[Union[D, str]]] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self._earlier_than = self._typecast_optional_option(earlier_than)
        self._earlier_or_equal_to = self._typecast_optional_option(earlier_or_equal_to)
        self._later_than = self._typecast_optional_option(later_than)
        self._later_or_equal_to = self._typecast_optional_option(later_or_equal_to)
        self._format = format

        self._allowed: Optional[list[D]]

        if allowed is not None:
            self._allowed = list(map(self._typecast_option, allowed))
        else:
            self._allowed = None

    def _validate(
        self, value: Any, typecast: bool, context: dict[str, Any] = {}
    ) -> tuple[Optional[D], list[Error]]:
        type_errors = self._validate_exact_type(value)

        if type_errors:
            return value, type_errors

        errors = []

        if self._allowed is not None and value not in self._allowed:
            errors.append(self._error("not_allowed", {"allowed": self._allowed}))

        if self._earlier_than and value >= self._earlier_than:
            errors.append(
                self._error("later_or_equal_to", {"value": self._earlier_than})
            )

        if self._earlier_or_equal_to and value > self._earlier_or_equal_to:
            errors.append(
                self._error("later_than", {"value": self._earlier_or_equal_to})
            )

        if self._later_than and value <= self._later_than:
            errors.append(
                self._error("earlier_or_equal_to", {"value": self._later_than})
            )

        if self._later_or_equal_to and value < self._later_or_equal_to:
            errors.append(
                self._error("earlier_than", {"value": self._later_or_equal_to})
            )

        value, rule_errors = self._call_rules(value, typecast, context)

        return value, errors + rule_errors

    def _typecast_optional_option(self, input: Union[D, str, None]) -> Optional[D]:
        if input is None:
            return None

        return self._typecast_option(input)

    @abstractmethod
    def _validate_exact_type(self, value: Any) -> list[Error]:
        ...

    @abstractmethod
    def _typecast_option(self, input: Union[D, str]) -> D:
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

    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[Optional[date], list[Error]]:
        if isinstance(input, date):
            return input, []

        if not isinstance(input, str):
            return None, [
                self._error("unexpected_type", {"expected_type": type_name("date")})
            ]

        try:
            if context.get("date_format"):
                format = context.get("date_format")
            elif self._format:
                format = self._format
            else:
                format = None

            if format:
                return datetime.strptime(input, format).date(), []
            else:
                return date.fromisoformat(input), []

        except ValueError:
            return None, [self._error("invalid_date_format")]

    def _validate_exact_type(self, value: Any) -> list[Error]:
        if not isinstance(value, date):
            return [
                self._error("unexpected_type", {"expected_type": type_name("date")})
            ]
        else:
            return []

    def _typecast_option(self, input: Union[date, str]) -> date:
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

    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[Optional[datetime], list[Error]]:
        if isinstance(input, datetime):
            return input, []

        if not isinstance(input, str):
            return None, [
                self._error("unexpected_type", {"expected_type": type_name("datetime")})
            ]

        try:
            if context.get("date_format"):
                format = context.get("date_format")
            elif self._format:
                format = self._format
            else:
                format = None

            if format:
                return datetime.strptime(input, format), []
            else:
                return datetime.fromisoformat(input), []

        except ValueError:
            return None, [self._error("invalid_datetime_format")]

    def _validate_exact_type(self, value: Any) -> list[Error]:
        if not isinstance(value, datetime):
            return [
                self._error("unexpected_type", {"expected_type": type_name("datetime")})
            ]
        else:
            return []

    def _typecast_option(self, input: Union[datetime, str]) -> datetime:
        if isinstance(input, datetime):
            return input

        return datetime.fromisoformat(input)
