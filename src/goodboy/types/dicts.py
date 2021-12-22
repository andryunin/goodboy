from __future__ import annotations

from typing import Callable, Optional

from goodboy.errors import Error
from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Rule, Schema, SchemaError
from goodboy.types.simple import Str


class Key:
    def __init__(
        self,
        name,
        schema: Optional[Schema] = None,
        required: Optional[bool] = None,
        predicate: Optional[Callable[[dict], bool]] = None,
    ):
        self.name = name
        self.schema = schema
        self.required = required
        self.predicate = predicate

    def predicate_result(self, prev_values: dict):
        if self.predicate:
            return self.predicate(prev_values)
        else:
            return True

    def validate(self, value, typecast: bool):
        if self.schema:
            return self.schema(value, typecast=typecast)
        else:
            return value

    def with_predicate(self, predicate: Callable[[dict], bool]) -> Key:
        return Key(self.name, self.schema, self.required, predicate)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return super().__eq__(other)


# TODO: maybe support non string keys?
class Dict(Schema):
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
    ):
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)
        self.keys = keys
        self.keys_required_by_default = keys_required_by_default
        self.key_schema = key_schema
        self.value_schema = value_schema

    def append_key(self, key: Key):
        self.keys = self.keys or []
        self.keys.append(key)

    def validate(self, value, typecast: bool, context: dict = {}):
        if not isinstance(value, dict):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("dict")})
            ]

        if self.keys is not None:
            (
                result_value,
                key_errors,
                value_errors,
                key_names_to_validate_by_key_schema,
            ) = self.validate_keys(value, typecast, context)
        else:
            result_value = value.copy()
            key_errors = {}
            value_errors = {}
            key_names_to_validate_by_key_schema = list(value.keys())

        if self.keys is None or self.key_schema or self.value_schema:
            unknown_key_names = []
        else:
            unknown_key_names = key_names_to_validate_by_key_schema

        if self.key_schema:
            key_schema_values, key_schema_errors = self.validate_keys_by_schema(
                value, key_names_to_validate_by_key_schema, typecast, context
            )

            result_value.update(key_schema_values)
            key_errors.update(key_schema_errors)

            key_names_to_validate_by_value_schema = list(key_schema_values.keys())
        else:
            key_names_to_validate_by_value_schema = key_names_to_validate_by_key_schema

        if self.value_schema:
            value_schema_values, value_schema_errors = self.validate_values_by_schema(
                value, key_names_to_validate_by_value_schema, typecast, context
            )

            result_value.update(value_schema_values)
            value_errors.update(value_schema_errors)

        if unknown_key_names:
            for key_name in unknown_key_names:
                key_errors[key_name] = [self.error("unknown_key")]

        errors: list[Error] = []

        if key_errors:
            errors.append(self.error("key_errors", nested_errors=key_errors))

        if value_errors:
            errors.append(self.error("value_errors", nested_errors=value_errors))

        result_value, rule_errors = self.call_rules(result_value, typecast, context)

        return result_value, errors + rule_errors

    def validate_keys(self, value, typecast: bool, context: dict):
        assert self.keys is not None

        result_value: dict = {}
        result_key_errors = {}
        result_value_errors = {}

        unknown_keys = list(value.keys())

        for key in self.keys:
            if not key.predicate_result(result_value):
                continue

            if key.name in unknown_keys:
                unknown_keys.remove(key.name)

                try:
                    key_value = key.validate(value[key.name], typecast)
                except SchemaError as e:
                    result_value_errors[key.name] = e.errors
                else:
                    result_value[key.name] = key_value
            else:
                if key.required is not None:
                    key_required = key.required
                else:
                    key_required = self.keys_required_by_default

                if key_required:
                    result_key_errors[key.name] = [self.error("required_key")]

        return result_value, result_key_errors, result_value_errors, unknown_keys

    def validate_keys_by_schema(
        self, value, key_names: list[str], typecast: bool, context: dict
    ) -> tuple[dict, dict[str, list[Error]]]:
        assert self.key_schema is not None

        result_value = {}
        result_errors = {}

        for key_name in key_names:
            try:
                # TODO: maybe allow keys to be modified here?
                self.key_schema(key_name, context=context)
            except SchemaError as e:
                result_errors[key_name] = e.errors
            else:
                result_value[key_name] = value[key_name]

        return result_value, result_errors

    def validate_values_by_schema(
        self, value, key_names: list[str], typecast: bool, context: dict
    ):
        assert self.value_schema is not None

        result_value = {}
        result_errors = {}

        for key_name in key_names:
            try:
                key_value = self.value_schema(
                    value[key_name], typecast=typecast, context=context
                )
            except SchemaError as e:
                result_errors[key_name] = e.errors
            else:
                result_value[key_name] = key_value

        return result_value, result_errors

    def typecast(self, input, context: dict = {}):
        return input, []
