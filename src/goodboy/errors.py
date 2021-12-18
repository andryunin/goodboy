from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from goodboy.i18n import Translations
from goodboy.messages import DEFAULT_MESSAGES, Message, MessageCollection


class Error:
    def __init__(
        self,
        code: str,
        args: dict = {},
        nested_errors: dict = {},
        messages: MessageCollection = DEFAULT_MESSAGES,
    ):
        self.code = code
        self.args = args
        self.nested_errors: dict[str, Error] = nested_errors
        self.messages = messages

    def __str__(self):
        return self.code

    def __repr__(self):
        args = repr(self.args)
        nested = repr(self.nested_errors)

        return f"<{self.__class__.__name__} {self.code} {args} {nested}>"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.code == other.code and self.args == other.args

        return super().__eq__(other)

    def get_message(
        self, format: Optional[str] = None, translations: Optional[Translations] = None
    ):
        format_kwargs = self.args

        for key, value in format_kwargs.items():
            if isinstance(value, Message):
                format_kwargs[key] = value.get(format, translations)

        return self.messages.get_message(self.code).get(
            format, translations, format_kwargs=format_kwargs
        )


class ErrorFormatter(ABC):
    @abstractmethod
    def format(self, errors: list[Error]):
        ...


class I18nErrorFormatter(ErrorFormatter):
    @abstractmethod
    def __init__(self, translations: Optional[Translations] = None):
        self.translations = translations


class JSONErrorFormatter(I18nErrorFormatter):
    def __init__(self, translations: Optional[Translations] = None):
        super().__init__(translations)

    def format(self, errors: list[Error]):
        result = []

        for error in errors:
            result.append(self.format_error(error))

        return result

    def format_error(self, error: Error):
        args: dict[Any, Any] = {}

        for key, value in error.args.items():
            args[key] = self.format_argument_value(value)

        nested_errors: dict[Any, Any] = {}

        for key, nested_error in error.nested_errors.items():
            nested_errors[key] = self.format(nested_error)

        result = {
            "code": error.code,
            "message": error.get_message("json", self.translations),
        }

        if args:
            result["args"] = args

        if nested_errors:
            result["nested_errors"] = nested_errors

        return result

    def format_argument_value(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, int):
            return value
        elif isinstance(value, float):
            return value
        elif isinstance(value, Message):
            return value.get("json", self.translations)
        elif isinstance(value, list):
            return [self.format_argument_value(v) for v in value]
        else:
            raise ValueError(f"unexpected type of error argument: '{type(value)}'")


FORMATTERS: dict[str, type[I18nErrorFormatter]] = {"json": JSONErrorFormatter}


def get_formatter_class(code: str) -> type[I18nErrorFormatter]:
    if code not in FORMATTERS:
        raise ValueError(f"unknown error formatter code: '{code}'")

    return FORMATTERS[code]
