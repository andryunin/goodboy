from typing import Any, Union

from goodboy.errors import Error, ErrorFormatter, get_formatter
from goodboy.schema import Schema, SchemaError


class Result:
    def __init__(self, value: Any, errors: list[Error]):
        self.value = value
        self.errors = errors

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def format_errors(
        self,
        formatter: Union[ErrorFormatter, str],
        languages: list = [],
    ):
        if isinstance(formatter, str):
            formatter = get_formatter(formatter)

        return formatter.format(self.errors, languages=languages)


class Validator:
    def __init__(self, schema: Schema):
        self.schema = schema

    def validate(self, value, typecast: bool = False) -> Result:
        try:
            result_value = self.schema(value, typecast=typecast)
        except SchemaError as e:
            return Result(None, e.errors)

        return Result(result_value, [])


def validate(schema: Schema, value, typecast: bool = False):
    validator = Validator(schema)
    return validator.validate(value, typecast=typecast)
