from datetime import datetime

from goodboy.schema import Schema, Error, SchemaError


class AnyType(Schema):
    def validate(self, value, typecast):
        return value, []

    def typecast(self, value):
        return value, []


class DateTime(Schema):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        min: datetime = None,
        max: datetime = None,
        format: str = None,
    ):
        super().__init__(allow_none=allow_none)
        self.min = min
        self.max = max
        self.format = format

    def validate(self, value, typecast):
        if not isinstance(value, datetime):
            return None, [Error("invalid_type", {"expected_type": "datetime"})]

        errors = []

        if self.min and value < self.min:
            errors.append(Error("datetime.less_then", {"min": self.min}))

        if self.max and value >= self.max:
            errors.append(Error("datetime.more_or_equal_then", {"max": self.max}))

        return value, errors

    def typecast(self, value):
        if isinstance(value, datetime):
            return value, []

        if not isinstance(value, str):
            return None, [Error("datetime.invalid_type_to_cast")]

        try:
            if self.format:
                return datetime.strptime(value, self.format), []
            else:
                return datetime.fromisoformat(value), []

        except ValueError:
            return None, [Error("datetime.invalid_format")]


class Int(Schema):
    def __init__(
        self,
        *,
        allow_none: bool = False,
        min: int = None,
        max: int = None,
    ):
        super().__init__(allow_none=allow_none)
        self.min = min
        self.max = max

    def validate(self, value, typecast):
        if not isinstance(value, int):
            return None, [Error("invalid_type", {"expected_type": "int"})]

        errors = []

        if self.min is not None and value < self.min:
            errors.append(Error("int.less_then", {"min": self.min}))

        if self.max is not None and value >= self.max:
            errors.append(Error("int.more_or_equal_then", {"max": self.max}))

        return value, errors

    def typecast(self, value):
        if isinstance(value, int):
            return value, []

        if not isinstance(value, str):
            return None, [Error("int.invalid_type_to_cast")]

        try:
            return int(value), []
        except ValueError:
            return None, [Error("int.invalid_format")]


class Key:
    def __init__(self, name, schema: Schema = None, required: bool = True):
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
        keys: list[Key] = None,
    ):
        super().__init__(allow_none=allow_none)
        self.keys = keys

    def validate(self, value, typecast):
        if not isinstance(value, dict):
            return None, [Error("invalid_type", {"expected_type": "dict"})]

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
                    key_errors[key.name] = [Error("dict.required_key")]

            for key in value_keys:
                key_errors[key] = [Error("dict.unknown_key")]

        if key_errors:
            return None, [Error("dict.keys_error", {"keys": key_errors})]

        return key_values, []

    def typecast(self, value):
        return value, []
