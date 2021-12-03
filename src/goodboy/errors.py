from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from goodboy.i18n import I18nLazyStub, Translations
from goodboy.i18n import lazy_gettext as _


class Message:
    """
    Error message class, allows using different messages for different input formats.

    For example, when returning an error from the JSON API, it allows you to get "is
    not an object" instead of "is not a dict".

    Default format is "python", which means that primary error messages should use
    python names for data types ("str" instead of "string", "dict" instead of "object"
    and so on).

        >>> e = ErrorMessage("Cannot be None", json="Cannot be null")
        >>> e.get()
        "Cannot be None"
        >>> e.get("json")
        "Cannot be null"
    """

    def __init__(self, default_message, **other_messages):
        self.messages = {"default": default_message, **other_messages}

    def get(
        self, format: Optional[str] = None, translations: Optional[Translations] = None
    ):
        if format not in self.messages:
            format = "default"

        message = self.messages[format]

        if isinstance(message, I18nLazyStub):
            if translations:
                message = message.eval(translations)
            else:
                message = message.get_original_message()

        return message


class MessageCollection:
    def __init__(
        self, messages: dict[str, Message], parent: Optional["MessageCollection"] = None
    ):
        self.messages = messages
        self.parent = parent

    def get_message(self, code: str) -> Message:
        if code in self.messages:
            return self.messages[code]

        if self.parent:
            return self.parent.get_message(code)

        return Message(code)


DEFAULT_MESSAGES = MessageCollection(
    {
        # Common messages
        "cannot_be_none": Message(_("cannot be None"), json=_("cannot be null")),
        "cannot_be_blank": Message(_("cannot be blank")),
        "unexpected_type": Message(_('expected type is "{type}"')),
        # Date/DateTime messages
        "earlier_or_equal_to": Message(_("must be later than {value}")),
        "earlier_than": Message(_("must be later or equal to {value}")),
        "later_or_equal_to": Message(_("must be earlier than {value}")),
        "later_than": Message(_("must be earlier or equal to {value}")),
        "invalid_date_format": Message(_("invalid date format")),
        "invalid_datetime_format": Message(_("invalid date and time format")),
        # Numeric messages
        "greater_or_equal_to": Message(_("must be less than {value}")),
        "greater_than": Message(_("must be less or equal to {value}")),
        "less_or_equal_to": Message(_("must be greater than {value}")),
        "less_than": Message(_("must be greater or equal to {value}")),
        "invalid_integer_format": Message(_("invalid integer format")),
        "invalid_numeric_format": Message(_("invalid numeric format")),
        # String messages
        "invalid_string_format": Message(_("invalid string format")),
        "invalid_string_length": Message(_("must be {value} characters long")),
        "string_too_long": Message(_("must be shorter than {value} characters")),
        "string_too_short": Message(_("must be longer than {value} characters")),
        # Dict messages
        "keys_error": Message(_("key errors")),
        "required_key": Message(_("key is required")),
        "unknown_key": Message(_("unknown key")),
    }
)


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
