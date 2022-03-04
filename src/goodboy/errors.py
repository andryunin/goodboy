from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from goodboy.i18n import I18nLazyString, Translations
from goodboy.messages import DEFAULT_MESSAGES, Message, MessageCollection


class Error:
    """
    Error consists of error code, arguments and message.

    Error can contain nested errors (for example, :class:`~goodboy.types.dicts.Dict`
    returns error "key_error" with nested errors for each invalid key).

    Message argument is optional. If no message specified, default message for error
    code will be used.

    :param code: Error code.
    :param args: Error arguments, used as format kwargs for message.
    :param nested_errors: Nested error dictionary.
    :param message: Optional error message, can be :class:`~goodboy.messages.Message`,
        `str`, or :func:`goodboy.i18n.lazy_gettext` value.

    """

    def __init__(
        self,
        code: str,
        args: dict = {},
        nested_errors: dict[str, list[Error]] = {},
        message: Optional[Union[Message, str, I18nLazyString]] = None,
    ):
        self.code = code
        self.args = args
        self.nested_errors = nested_errors

        if message:
            if isinstance(message, Message):
                self._message = message
            else:
                self._message = Message(message)

        else:
            self._message = DEFAULT_MESSAGES.get_message(self.code)

    def get_message(
        self, format: Optional[str] = None, translations: Optional[Translations] = None
    ):
        """
        Get message specified for input format and translated with specified
        :class:`~goodboy.i18n.Translations` instance.
        """

        format_kwargs = self.args

        for key, value in format_kwargs.items():
            if isinstance(value, Message):
                format_kwargs[key] = value.render(format, translations)

        return self._message.render(format, format_kwargs, translations)

    @property
    def message(self):
        """
        Get message for default format and translated to default language.
        """

        return self.get_message()

    def __str__(self):
        return self.code

    def __repr__(self):
        arguments = [
            repr(self.code),
            repr(self.args),
            repr(self.nested_errors),
            repr(self._message),
        ]
        arguments_repr = ", ".join(arguments)

        return f"Error({arguments_repr})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.code == other.code
                and self.args == other.args
                and self.nested_errors == other.nested_errors
                and self._message == other._message
            )

        return super().__eq__(other)


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
