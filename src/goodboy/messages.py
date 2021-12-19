from __future__ import annotations

from typing import Dict, Optional, Union

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

        >>> e = Message("Cannot be None", json="Cannot be null")
        >>> e.get()
        "Cannot be None"
        >>> e.get("json")
        "Cannot be null"
    """

    def __init__(self, default_message, **other_messages):
        self.messages = {"default": default_message, **other_messages}

    def get(
        self,
        format: Optional[str] = None,
        translations: Optional[Translations] = None,
        format_args: list = [],
        format_kwargs: dict = {},
    ):
        if format not in self.messages:
            format = "default"

        message = self.messages[format]

        if isinstance(message, I18nLazyStub):
            if translations:
                message = message.eval(translations)
            else:
                message = message.get_original_message()

        return message.format(*format_args, **format_kwargs)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.messages == other.messages

        return super().__eq__(other)


class MessageCollection:
    def __init__(
        self,
        messages: dict[str, Union[Message, I18nLazyStub, str]],
        parent: Optional["MessageCollection"] = None,
    ):
        for code, message in messages.items():
            if not isinstance(message, Message):
                messages[code] = Message(message)

        self.messages = messages
        self.parent = parent

    def get_message(self, code: str) -> Message:
        try:
            return self[code]
        except KeyError:
            return Message(code)

    def __getitem__(self, code):
        if code in self.messages:
            return self.messages[code]

        if self.parent:
            return self.parent.get_message(code)

        raise KeyError(code)


MessageCollectionType = Union[
    MessageCollection, Dict[str, Union[Message, I18nLazyStub, str]]
]

DEFAULT_MESSAGES = MessageCollection(
    {
        # Common messages
        "cannot_be_none": Message(_("cannot be None"), json=_("cannot be null")),
        "cannot_be_blank": Message(_("cannot be blank")),
        "must_be_none": Message(_("must be None"), json=_("must be null")),
        "unexpected_type": Message(_('expected type is "{expected_type}"')),
        "not_allowed": Message(_("value is not allowed")),
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
        "key_errors": Message(_("key errors")),
        "value_errors": Message(_("value errors")),
        "required_key": Message(_("key is required")),
        "unknown_key": Message(_("unknown key")),
        # List messages
        "invalid_length": Message(_("must be {value} items long")),
        "too_long": Message(_("must be shorter than {value} items")),
        "too_short": Message(_("must be longer than {value} items")),
        # AnyOf
        "no_variant_found": Message(_("does not match any of the variants")),
    }
)


_TYPE_NAMES_LIST: list[Message] = [
    Message("dict", json="object"),
    Message("list", json="array"),
    Message("str", json="string"),
    Message("date", json="string"),
    Message("datetime", json="string"),
    Message("int", json="integer"),
    Message("float", json="number"),
    Message("bool", json="boolean"),
]

_TYPE_NAMES = MessageCollection({m.get(): m for m in _TYPE_NAMES_LIST})


def type_name(python_type_name: str):
    return _TYPE_NAMES[python_type_name]
