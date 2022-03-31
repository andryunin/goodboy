from __future__ import annotations

from typing import Any, Callable, Optional

from goodboy.errors import Error
from goodboy.schema import SchemaWithUtils


class CallableValue(SchemaWithUtils):
    """
    Accept callable python objects.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    """

    def _validate(
        self, value: Any, typecast: bool, context: dict[str, Any] = {}
    ) -> tuple[Optional[Callable[..., Any]], list[Error]]:
        errors = []

        if not callable(value):
            errors.append(self._error("not_callable"))

        value, rule_errors = self._call_rules(value, typecast, context)

        return value, errors + rule_errors

    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[Any, list[Error]]:
        return input, []
