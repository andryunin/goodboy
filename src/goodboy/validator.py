from typing import Any

from goodboy.schema import Schema, Error, InvalidValueError


class Result:
    def __init__(self, value: Any, errors: list[Error]):
        self.value = value
        self.errors = errors

    @property
    def is_valid(self) -> bool:
        return not self.errors


class Validator:
    def __init__(self, schema: Schema):
        self.schema = schema

    def validate(self, value, typecast: bool = False) -> Result:
        try:
            result_value = self.schema(value, typecast=typecast)
        except InvalidValueError as e:
            return Result(None, e.errors)

        return Result(result_value, [])


def validate(schema: Schema, value, typecast: bool = False):
    validator = Validator(schema)
    return validator.validate(value, typecast=typecast)
