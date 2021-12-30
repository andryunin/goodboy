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
        nested_errors: dict[str, list[Error]] = {},
        messages: MessageCollection = DEFAULT_MESSAGES,
    ):
        self.code = code
        self.args = args
        self.nested_errors = nested_errors
        self.messages = messages

    def __str__(self):
        return self.code

    def __repr__(self):
        args = repr(self.args)
        nested = repr(self.nested_errors)

        return f"<{self.__class__.__name__} {self.code} {args} {nested}>"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.code == other.code
                and self.args == other.args
                and self.nested_errors == other.nested_errors
            )

        return super().__eq__(other)

    def get_message(
        self, format: Optional[str] = None, translations: Optional[Translations] = None
    ):
        return self.messages.get_message(self.code).render(
            format, self.args, translations
        )


class ErrorFormatter(ABC):
    @abstractmethod
    def format(self, errors: list[Error]):
        ...


class I18nErrorFormatter(ErrorFormatter):
    @abstractmethod
    def __init__(self, translations: Optional[Translations] = None):
        self._translations = translations


class JSONErrorFormatter(I18nErrorFormatter):
    def __init__(self, translations: Optional[Translations] = None):
        super().__init__(translations)

    def format(self, errors: list[Error]):
        result = []

        for error in errors:
            result.append(self._format_error(error))

        return result

    def _format_error(self, error: Error):
        args: dict[Any, Any] = {}

        for key, value in error.args.items():
            args[key] = self._format_argument_value(value)

        formatted_nested_errors: dict[Any, Any] = {}

        for key, nested_errors in error.nested_errors.items():
            formatted_nested_errors[key] = self.format(nested_errors)

        result = {
            "code": error.code,
            "message": error.get_message("json", self._translations),
        }

        if args:
            result["args"] = args

        if formatted_nested_errors:
            result["nested_errors"] = formatted_nested_errors

        return result

    def _format_argument_value(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, int):
            return value
        elif isinstance(value, float):
            return value
        elif isinstance(value, Message):
            return value.render("json", self._translations)
        elif isinstance(value, list):
            return [self._format_argument_value(v) for v in value]
        else:
            raise ValueError(f"unexpected type of error argument: '{type(value)}'")


class TextErrorFormatter(I18nErrorFormatter):
    def __init__(self, translations: Optional[Translations] = None):
        super().__init__(translations)

    def format(self, errors: list[Error]):
        lines = self._format_level(errors, 0)
        return "\n".join(lines)

    def _format_level(self, errors: list[Error], level):
        lines = []

        for error in errors:
            indent = self._indent(level)
            code = error.code
            message = error.get_message(translations=self._translations)

            if error.args:
                args = " " + repr(error.args)
            else:
                args = ""

            lines.append(f"{indent}{code}: {message}. {args}")

            for nested_key, nested_errors in error.nested_errors.items():
                key_indent = self._indent(level + 1)
                lines.append(f"{key_indent}{nested_key}:")
                lines += self._format_level(nested_errors, level + 2)

        return lines

    def _indent(self, level):
        return "    " * level


_FORMATTERS: dict[str, type[I18nErrorFormatter]] = {
    "json": JSONErrorFormatter,
    "text": TextErrorFormatter,
}


def get_formatter_class(code: str) -> type[I18nErrorFormatter]:
    if code not in _FORMATTERS:
        raise ValueError(f"unknown error formatter code: '{code}'")

    return _FORMATTERS[code]
