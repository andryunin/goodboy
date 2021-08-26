from abc import ABC, abstractmethod


class Error:
    def __init__(self, code: str, args: dict = {}):
        self.code = code
        self.args = args

    def __str__(self):
        return self.code

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.code} {repr(self.args)}>"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.code == other.code and self.args == other.args

        return super().__eq__(other)


class InvalidValueError(Exception):
    def __init__(self, errors: list[Error]):
        self.errors = errors


class Schema(ABC):
    def __init__(self, *, allow_none: bool = False):
        self.allow_none = allow_none

    def __call__(self, value, *, typecast=False):
        if value is None and not self.allow_none:
            return InvalidValueError([Error("cannot_be_none")])

        if typecast:
            value = self.typecast(value)

        errors = self.validate(value)

        if errors:
            raise InvalidValueError(errors)

        return value

    @abstractmethod
    def validate(self, value) -> list[Error]:
        ...

    @abstractmethod
    def typecast(self, value):
        ...
