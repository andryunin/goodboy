from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from goodboy.i18n import Translations
from goodboy.messages import DEFAULT_MESSAGES, MessageCollection


class Error:
    def __init__(
        self, code: str, args: dict = {}, messages: MessageCollection = DEFAULT_MESSAGES
    ):
        self.code = code
        self.args = args
        self.messages = messages

    def __str__(self):
        return self.code

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.code} {repr(self.args)}>"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.code == other.code and self.args == other.args

        return super().__eq__(other)

    def get_message(
        self, format: Optional[str] = None, translations: Optional[Translations] = None
    ):
        return self.messages.get_message(self.code).get(format, translations)


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

        result = {
            "code": error.code,
            "message": error.get_message("json", self.translations),
        }

        if args:
            result["args"] = args

        return result


FORMATTERS: dict[str, type[I18nErrorFormatter]] = {"json": JSONErrorFormatter}


def get_formatter_class(code: str) -> type[I18nErrorFormatter]:
    if code not in FORMATTERS:
        raise ValueError(f"unknown error formatter code: '{code}'")

    return FORMATTERS[code]
