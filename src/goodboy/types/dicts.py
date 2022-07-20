from __future__ import annotations

from typing import Any, Callable, Mapping, Optional, Union

from goodboy.errors import Error
from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Rule, Schema, SchemaError, SchemaWithUtils
from goodboy.types.simple import Str


class Key:
    """
    Dict key.

    :param name: Key name.
    :param schema: Value schema.
    :param required: Is key required.
    :param defaukt: Default key value.
    :param predicate: Key is allowed only if predicate returns true.
    """

    def __init__(
        self,
        name: str,
        schema: Optional[Schema] = None,
        *,
        required: Optional[bool] = None,
        default: Optional[Any] = None,
        predicate: Optional[Callable[[Mapping[str, Any]], bool]] = None,
    ):
        if default and required:
            raise ValueError("key with default value cannot be required")

        self.required = required
        self.name = name
        self.default = default
        self._schema = schema
        self._predicate = predicate

    def predicate_result(self, prev_values: Mapping[str, Any]) -> bool:
        if self._predicate:
            return self._predicate(prev_values)
        else:
            return True

    def validate(self, value: Any, typecast: bool, context: dict[str, Any]) -> Any:
        if self._schema:
            return self._schema(value, typecast=typecast, context=context)
        else:
            return value

    def with_predicate(self, predicate: Callable[[Mapping[str, Any]], bool]) -> Key:
        return Key(self.name, self._schema, required=self.required, predicate=predicate)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return super().__eq__(other)


# TODO: maybe support non string keys?
class Dict(SchemaWithUtils):
    """
    Accept ``dict`` value. Only string keys supported.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    :param keys: List of allowed keys
    :param key_schema: Schema to validate dict keys (only Str is supported)
    :param value_schema: Schema to validate dict key values
    :param keys_required_by_default: default required flag for ``keys``.
    """

    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
        keys: Optional[list[Key]] = None,
        key_schema: Optional[Str] = None,
        value_schema: Optional[Schema] = None,
        keys_required_by_default: bool = True,
    ) -> None:
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self._keys = keys
        self._keys_required_by_default = keys_required_by_default
        self._key_schema = key_schema
        self._value_schema = value_schema

    def append_key(self, key: Key) -> None:
        self._keys = self._keys or []
        self._keys.append(key)

    def _validate(
        self, value: Any, typecast: bool, context: dict[str, Any] = {}
    ) -> tuple[Optional[dict[str, Any]], list[Error]]:
        if not isinstance(value, dict):
            return None, [
                self._error("unexpected_type", {"expected_type": type_name("dict")})
            ]

        if self._keys is not None:
            (
                result_value,
                key_errors,
                value_errors,
                key_names_to_validate_by_key_schema,
            ) = self._validate_keys(value, typecast, context)
        else:
            result_value = value.copy()
            key_errors = {}
            value_errors = {}
            key_names_to_validate_by_key_schema = list(value.keys())

        if self._keys is None or self._key_schema or self._value_schema:
            unknown_key_names = []
        else:
            unknown_key_names = key_names_to_validate_by_key_schema

        if self._key_schema:
            key_schema_values, key_schema_errors = self._validate_keys_by_schema(
                value, key_names_to_validate_by_key_schema, typecast, context
            )

            result_value.update(key_schema_values)
            key_errors.update(key_schema_errors)

            key_names_to_validate_by_value_schema = list(key_schema_values.keys())
        else:
            key_names_to_validate_by_value_schema = key_names_to_validate_by_key_schema

        if self._value_schema:
            value_schema_values, value_schema_errors = self._validate_values_by_schema(
                value, key_names_to_validate_by_value_schema, typecast, context
            )

            result_value.update(value_schema_values)
            value_errors.update(value_schema_errors)

        if unknown_key_names:
            for key_name in unknown_key_names:
                key_errors[key_name] = [self._error("unknown_key")]

        errors: list[Error] = []

        if key_errors:
            errors.append(self._error("key_errors", nested_errors=key_errors))

        if value_errors:
            errors.append(self._error("value_errors", nested_errors=value_errors))

        result_value, rule_errors = self._call_rules(result_value, typecast, context)

        self._merge_rule_errors(rule_errors, errors)

        return result_value, errors

    def _merge_rule_errors(self, rule_errors: list[Error], to: list[Error]):
        for rule_error in rule_errors:
            if rule_error.code not in ["key_errors", "value_errors"]:
                to.append(rule_error)
                continue

            for to_error in to:
                if to_error.code == rule_error.code:
                    to_error.merge_nested_errors(rule_error.nested_errors)
                    break
            else:
                to.append(rule_error)

    def _validate_keys(
        self, value: dict[str, Any], typecast: bool, context: dict[str, Any]
    ) -> tuple[
        dict[str, Any],
        dict[Union[str, int], list[Error]],
        dict[Union[str, int], list[Error]],
        list[str],
    ]:
        assert self._keys is not None

        result_value: dict[str, Any] = {}
        result_key_errors: dict[Union[str, int], list[Error]] = {}
        result_value_errors: dict[Union[str, int], list[Error]] = {}

        unknown_keys = list(value.keys())

        for key in self._keys:
            if not key.predicate_result(result_value):
                continue

            if key.name in unknown_keys:
                unknown_keys.remove(key.name)

                try:
                    key_value = key.validate(value[key.name], typecast, context)
                except SchemaError as e:
                    result_value_errors[key.name] = e.errors
                else:
                    result_value[key.name] = key_value
            elif key.default:
                result_value[key.name] = key.default
            else:
                if key.required is not None:
                    key_required = key.required
                else:
                    key_required = self._keys_required_by_default

                if key_required:
                    result_key_errors[key.name] = [self._error("required_key")]

        return result_value, result_key_errors, result_value_errors, unknown_keys

    def _validate_keys_by_schema(
        self,
        value: dict[str, Any],
        key_names: list[str],
        typecast: bool,
        context: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[Union[str, int], list[Error]]]:
        assert self._key_schema is not None

        result_value: dict[str, Any] = {}
        result_errors: dict[Union[str, int], list[Error]] = {}

        for key_name in key_names:
            try:
                # TODO: maybe allow keys to be modified here?
                self._key_schema(key_name, context=context)
            except SchemaError as e:
                result_errors[key_name] = e.errors
            else:
                result_value[key_name] = value[key_name]

        return result_value, result_errors

    def _validate_values_by_schema(
        self,
        value: dict[str, Any],
        key_names: list[str],
        typecast: bool,
        context: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[Union[str, int], list[Error]]]:
        assert self._value_schema is not None

        result_value: dict[str, Any] = {}
        result_errors: dict[Union[str, int], list[Error]] = {}

        for key_name in key_names:
            try:
                key_value = self._value_schema(
                    value[key_name], typecast=typecast, context=context
                )
            except SchemaError as e:
                result_errors[key_name] = e.errors
            else:
                result_value[key_name] = key_value

        return result_value, result_errors

    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[Any, list[Error]]:
        return input, []
