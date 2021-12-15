from __future__ import annotations

from abc import abstractmethod
from typing import Generic, Optional, TypeVar

from goodboy.errors import Error
from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Rule, Schema

N = TypeVar("N")


class NumericBase(Generic[N], Schema):
    """
    Abstract base class for Int/Float schemas, should not be used directly. Use
    :class:`Int` or :class:`Float` instead.
    """

    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
        less_than: Optional[N] = None,
        less_or_equal_to: Optional[N] = None,
        greater_than: Optional[N] = None,
        greater_or_equal_to: Optional[N] = None,
        allowed: Optional[list[N]] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self.less_than = less_than
        self.less_or_equal_to = less_or_equal_to
        self.greater_than = greater_than
        self.greater_or_equal_to = greater_or_equal_to
        self.allowed = allowed

    def validate(self, value, typecast: bool, context: dict = {}):
        value, type_errors = self.validate_exact_type(value)

        if type_errors:
            return None, type_errors

        errors = []

        if self.allowed is not None and value not in self.allowed:
            errors.append(self.error("not_allowed", {"allowed": self.allowed}))

        if self.less_than is not None and value >= self.less_than:
            errors.append(self.error("greater_or_equal_to", {"value": self.less_than}))

        if self.less_or_equal_to is not None and value > self.less_or_equal_to:
            errors.append(self.error("greater_than", {"value": self.less_or_equal_to}))

        if self.greater_than is not None and value <= self.greater_than:
            errors.append(self.error("less_or_equal_to", {"value": self.greater_than}))

        if self.greater_or_equal_to is not None and value < self.greater_or_equal_to:
            errors.append(self.error("less_than", {"value": self.greater_or_equal_to}))

        value, rule_errors = self.call_rules(value, typecast, context)

        return value, errors + rule_errors

    @abstractmethod
    def validate_exact_type(self, value) -> tuple[N, list[Error]]:
        ...


class Float(NumericBase[float]):
    """
    Accept ``float`` values. Integer values are converted to floats.

    When type casting enabled, strings and other values with magic method
    `__float__ <https://docs.python.org/3/reference/datamodel.html#object.__float__>`_
    are converted to floats.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    :param less_than: Accept only values less than option value.
    :param less_or_equal_to: Accept only values less than or equal to option value.
    :param greater_than: Accept only values greater than option value.
    :param greater_or_equal_to: Accept only values greater than or equal to option
        value.
    :param allowed: Allow only certain values.
    """

    def validate_exact_type(self, value):
        if isinstance(value, float):
            return value, []
        elif isinstance(value, int):
            return float(value), []
        else:
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("float")})
            ]

    def typecast(self, input, context: dict = {}):
        if isinstance(input, float):
            return input, []

        if isinstance(input, int):
            return float(input), []

        if not isinstance(input, str):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("float")})
            ]

        try:
            return float(input), []
        except ValueError:
            return None, [self.error("invalid_numeric_format")]


class Int(NumericBase[int]):
    """
    Accept ``int`` values.

    When type casting enabled, strings and other values with magic method
    `__int__ <https://docs.python.org/3/reference/datamodel.html#object.__int__>`_ are
    converted to integers.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    :param less_than: Accept only values less than option value.
    :param less_or_equal_to: Accept only values less than or equal to option value.
    :param greater_than: Accept only values greater than option value.
    :param greater_or_equal_to: Accept only values greater than or equal to option
        value.
    :param allowed: Allow only certain values.
    """

    def validate_exact_type(self, value):
        if not isinstance(value, int):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("int")})
            ]
        else:
            return value, []

    def typecast(self, input, context: dict = {}):
        if isinstance(input, int):
            return input, []

        if not isinstance(input, str):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("int")})
            ]

        try:
            return int(input), []
        except ValueError:
            return None, [self.error("invalid_integer_format")]
