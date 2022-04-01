from __future__ import annotations

from typing import Any, Dict, Optional, Union

from goodboy.i18n import I18nLazyString, Translations, get_current_translations
from goodboy.i18n import lazy_gettext as _


class Message:
    """
    Error message class.

    Allows rendering different messages for different API formats. For example, when
    returning an error from JSON API, it allows you to get "not an object" instead of
    "not a dict".

    Default format should use native python names for data types ("str" instead of
    "string", "dict" instead of "object" and so on).

    When rendered with unknown format, default format is used.

    Example:

        >>> m = Message('Cannot be None', json='Cannot be null')
        >>> m.render()
        'Cannot be None'
        >>> m.render('json')
        'Cannot be null'
        >>> m.render('grpc')
        'Cannot be None'

    Messages can use string formatting (uses
    `str.format <https://docs.python.org/3/library/stdtypes.html#str.format>`_ method
    with kwargs), keyword arguments are passed to :meth:`render` method as dict.

    Formatting example:

        >>> m = Message('Must be less than {max_length} character long')
        >>> m.render(kwargs={'max_length': 100})
        'Must be less than 100 character long'

    Formatting arguments can be messages, too:

        >>> m = Message('Must be {type}')
        >>> m.render(kwargs={'type': Message('int', json='integer')})
        'Must be int'
        >>> m.render(kwargs={'type': Message('int', json='integer')}, format='json')
        'Must be integer'

    Format arguments are taken from error args (see :class:`~goodboy.errors.Error`).

    :param default: Default error message, should use native python type names.
    :param \\**other_formats: Error messages for other formats.

    TODO: Link i18n documentation.
    """

    def __init__(
        self,
        default: str | I18nLazyString,
        **other_formats: str | I18nLazyString,
    ) -> None:
        self._formats = {"default": default, **other_formats}

    def render(
        self,
        format: Optional[str] = None,
        kwargs: dict[str, Any] = {},
        translations: Optional[Translations] = None,
    ) -> str:
        """
        Render message.

        Evaluates lazy gettext values (see :func:`goodboy.i18n.lazy_gettext`) with
        specified or default translations.

        :param format: Output format. When rendered with unknown format, or no format
            specified, "default" format is used.
        :param kwargs: String formatting keyword arguments.
        :param translations: Translations object. When no translations specified, uses
            default goodboy translations.

        TODO: Link i18n documentation.
        """

        if format in self._formats:
            pattern = self._formats[format]
        else:
            pattern = self._formats["default"]

        if translations is None:
            translations = get_current_translations()

        if isinstance(pattern, I18nLazyString):
            pattern = pattern.translate(translations)

        kwargs = kwargs.copy()

        for key, argument in kwargs.items():
            if isinstance(argument, Message):
                kwargs[key] = argument.render(format, translations=translations)

        return pattern.format(**kwargs)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self._formats == other._formats

        return super().__eq__(other)

    def __repr__(self) -> str:
        arguments = [repr(self._formats["default"])]

        for format, pattern in self._formats.items():
            if format == "default":
                continue

            arguments.append(f"{format}={repr(pattern)}")

        arguments_repr = ", ".join(arguments)

        return f"Message({arguments_repr})"


class MessageCollection:
    def __init__(
        self,
        messages: dict[str, Union[Message, I18nLazyString, str]],
        parent: Optional["MessageCollection"] = None,
    ):
        self._messages: dict[str, Message] = {}

        for code, message in messages.items():
            if isinstance(message, str):
                self._messages[code] = Message(message)
            elif isinstance(message, dict):
                self._messages[code] = Message(**message)
            elif isinstance(message, Message):
                self._messages[code] = message
            else:
                type_ = type(message).__name__
                raise TypeError(f"unsupported type for message collection: '{type_}'")

        self._parent = parent

    def get_message(self, code: str) -> Message:
        try:
            return self[code]
        except KeyError:
            return Message(code)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self._messages == other._messages and self._parent == other._parent

        return super().__eq__(other)

    def __getitem__(self, code: str) -> Message:
        if code in self._messages:
            return self._messages[code]

        if self._parent:
            return self._parent.get_message(code)

        raise KeyError(code)


MessageCollectionType = Union[
    MessageCollection, Dict[str, Union[Message, I18nLazyString, str]]
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
        "invalid_regex": Message(_("must be valid regex")),
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
        # Callable
        "not_callable": Message(_("object is not callable")),
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

_TYPE_NAMES = MessageCollection({m.render(): m for m in _TYPE_NAMES_LIST})


def type_name(python_type_name: str) -> Message:
    return _TYPE_NAMES[python_type_name]
