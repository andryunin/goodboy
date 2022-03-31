from __future__ import annotations

from typing import Any

from goodboy.errors import Error
from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType
from goodboy.schema import Rule, Schema, SchemaError, SchemaWithUtils


class AnyOf(SchemaWithUtils):
    """
    Accept value matches any of specified schemas, taking into account ``allow_none``
    option.

    :param schemas: List of schemas to match
    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    """

    def __init__(
        self,
        schemas: list[Schema],
        *,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
    ):
        super().__init__(messages=messages, rules=rules)
        self._schemas = schemas

    def __call__(
        self, value: Any, *, typecast: bool = False, context: dict[str, Any] = {}
    ) -> Any:
        value, errors = self._validate(value, typecast, context)

        if errors:
            raise SchemaError(errors)

        return value

    def _validate(
        self, value: Any, typecast: bool, context: dict[str, Any] = {}
    ) -> tuple[Any, list[Error]]:
        schema_errors = {}
        errors = []

        for schema_index, schema in enumerate(self._schemas):
            try:
                value = schema(value)
            except SchemaError as e:
                schema_errors[schema_index] = e.errors
            else:
                break
        else:
            errors.append(self._error("no_variant_found", {"errors": schema_errors}))

        value, rule_errors = self._call_rules(value, typecast, context)

        return value, errors + rule_errors

    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[Any, list[Error]]:
        raise NotImplementedError()
