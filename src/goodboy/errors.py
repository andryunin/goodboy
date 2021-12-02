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


class ErrorFormatter(ABC):
    @abstractmethod
    def format(self, errors: list[Error], languages: list[str] = []):
        ...


class JSONErrorFormatter(ErrorFormatter):
    def format(self, errors: list[Error], languages: list[str] = []):
        result = []

        for error in errors:
            result.append(self.format_error(error))

        return result

    def format_error(self, error: Error):
        args = {}

        for key, value in error.args.items():
            if isinstance(value, str):
                args[key] = value
            elif isinstance(value, int):
                args[key] = value
            elif isinstance(value, float):
                args[key] = value
            elif isinstance(value, Error):
                args[key] = self.format_error(value)
            else:
                raise ValueError(
                    f"unexpected type of error argument '{key}': '{type(value)}'"
                )

        if args:
            return {"code": error.code, "args": args}
        else:
            return {"code": error.code}


FORMATTERS = {"json": JSONErrorFormatter()}


def get_formatter(code: str) -> ErrorFormatter:
    if code not in FORMATTERS:
        raise ValueError(f"unknown error formatter code: '{code}'")

    return FORMATTERS[code]
