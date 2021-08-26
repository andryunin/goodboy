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
        result = Result()

        try:
            result_value = self.schema(value, result, typecast=typecast)
        except InvalidValueError as e:
            result.set_errors(e.errors)
        else:
            result.set_value(result_value)

        return result


def validate(schema: Schema, value, typecast: bool = False):
    validator = Validator(schema)
    validator.validate(value, typecast=typecast)
