from __future__ import annotations

from typing import Callable, Optional

from goodboy.messages import DEFAULT_MESSAGES, MessageCollectionType, type_name
from goodboy.schema import Schema, SchemaError


class Key:
    def __init__(
        self,
        name,
        schema: Optional[Schema] = None,
        required: bool = True,
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


# TODO: key_schema and value_schema params for dynamic dicts
class Dict(Schema):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollectionType = DEFAULT_MESSAGES,
        keys: Optional[list[Key]] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
        self.keys = keys

    def validate(self, value, typecast):
        if not isinstance(value, dict):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("dict")})
            ]

        result_value = {}
        key_errors = {}
        value_errors = {}

        if self.keys is not None:
            value_keys = list(value.keys())

            for key in self.keys:
                if not key.predicate_result(result_value):
                    continue

                if key.name in value_keys:
                    value_keys.remove(key.name)

                    try:
                        key_value = key.validate(value[key.name], typecast)
                    except SchemaError as e:
                        value_errors[key.name] = e.errors
                    else:
                        result_value[key.name] = key_value

                elif key.required:
                    key_errors[key.name] = [self.error("required_key")]

            for key in value_keys:
                key_errors[key] = [self.error("unknown_key")]

        errors = []

        if key_errors:
            errors.append(self.error("key_errors", nested_errors=key_errors))

        if value_errors:
            errors.append(self.error("value_errors", nested_errors=value_errors))

        if errors:
            return None, errors

        return result_value, []

    def typecast(self, input):
        return input, []
