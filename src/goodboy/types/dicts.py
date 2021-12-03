from __future__ import annotations

from typing import Optional

from goodboy.messages import DEFAULT_MESSAGES, MessageCollection, type_name
from goodboy.schema import Schema, SchemaError


class Key:
    def __init__(self, name, schema: Optional[Schema] = None, required: bool = True):
        self.name = name
        self.schema = schema
        self.required = required

    def validate(self, value, typecast):
        return self.schema(value, typecast=typecast)


# TODO: key_schema and key_value params for dynamic keys
# TODO: conditional validation
class Dict(Schema):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: MessageCollection = DEFAULT_MESSAGES,
        keys: Optional[list[Key]] = None,
    ):
        super().__init__(allow_none=allow_none, messages=messages)
        self.keys = keys

    def validate(self, value, typecast):
        if not isinstance(value, dict):
            return None, [
                self.error("unexpected_type", {"expected_type": type_name("dict")})
            ]

        key_errors = {}
        key_values = {}

        if self.keys:
            value_keys = list(value.keys())

            for key in self.keys:
                if key.name in value_keys:
                    value_keys.remove(key.name)

                    try:
                        key_value = key.validate(value[key.name], typecast)
                    except SchemaError as e:
                        key_errors[key.name] = e.errors
                    else:
                        key_values[key.name] = key_value
                elif key.required:
                    key_errors[key.name] = [self.error("required_key")]

            for key in value_keys:
                key_errors[key] = [self.error("unknown_key")]

        if key_errors:
            return None, [self.error("keys_error", key_errors)]

        return key_values, []

    def typecast(self, value):
        return value, []
