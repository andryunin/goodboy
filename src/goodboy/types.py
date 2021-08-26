from datetime import datetime

from goodboy.schema import Schema, Error, InvalidValueError


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

    def validate(self, value):
        if not isinstance(value, datetime):
            return [Error("invalid_type", {"expected_type": "datetime"})]

        errors = []

        if self.min and value < self.min:
            errors.append(Error("datetime.less_then", {"min": self.min}))

        if self.max and value >= self.max:
            errors.append(Error("datetime.more_or_equal_then", {"max": self.max}))

        return errors

    def typecast(self, value):
        if isinstance(value, datetime):
            return value

        if not isinstance(value, str):
            raise InvalidValueError([Error("datetime.invalid_type_to_cast")])

        try:
            if self.format:
                return datetime.strptime(value, self.format)
            else:
                return datetime.fromisoformat(value)

        except ValueError:
            raise InvalidValueError([Error("datetime.invalid_format")])
