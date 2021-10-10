from datetime import datetime

from goodboy.schema import Schema, Error


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
