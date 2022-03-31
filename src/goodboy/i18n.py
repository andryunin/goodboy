from __future__ import annotations

import gettext
import sys
import threading
from pathlib import Path
from typing import Iterable, Optional

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


class Translations(Protocol):
    """
    Translations object protocol.

    Translations object can be any object with ``gettext(message: str)`` and
    ``ngettext(singular: str, plural: str, number: int)`` methods.

    By default, goodboy uses ``gettext.GNUTranslations`` with included messages (see
    :func:`load_default_messages`).
    """

    def gettext(self, message: str) -> str:
        ...

    def ngettext(self, singular: str, plural: str, number: int) -> str:
        ...


def default_messages_path() -> Path:
    """
    Get path of included messages.
    """

    return Path(__file__).joinpath("..", "locale").resolve()


def load_default_messages(languages: Optional[Iterable[str]] = None) -> Translations:
    """
    Get translations object (instance of ``gettext.GNUTranslations``) with included
    messages.

    :param languages: Languages list in order to try. If None, system language will be
        used.
    """

    return gettext.translation("goodboy", default_messages_path(), languages)


class I18nLoader:
    """
    Cached loader for included messages.
    """

    def __init__(self) -> None:
        self._cache: dict[tuple[str, ...], Translations] = {}

    def get_translations(self, languages: Iterable[str]) -> Translations:
        """
        Get translations object for specified languages.

        :param languages: Languages list in order to try.
        """
        # Make hashable tuple from unhashable list
        languages = tuple(languages)

        if languages not in self._cache:
            self._cache[languages] = load_default_messages(languages)

        return self._cache[languages]


class I18nLazyString:
    """
    Translated string representation before it actually evaluated with
    :class:`Translations` instance. Returned by :func:`lazy_gettext`, evaluated on
    :class:`~goodboy.messages.Message` render.
    """

    def __init__(self, message: str):
        self._message = message

    def translate(self, translations: Translations) -> str:
        """
        Get translated message.
        """

        return translations.gettext(self._message)

    def __repr__(self) -> str:
        message_repr = repr(self._message)
        return f"_({message_repr})"


def lazy_gettext(message: str) -> I18nLazyString:
    """
    Lazy version of gettext. Returns :class:`I18nLazyString`.
    """

    return I18nLazyString(message)


_process_locale: Optional[list[str]]
_process_translations: Translations


class ThreadingLocalLocale(threading.local):
    def __init__(self) -> None:
        self.locale: Optional[list[str]] = None
        self.locale_is_set: bool = False
        self.translations: Optional[Translations] = None


_thread_locale = ThreadingLocalLocale()


def set_process_locale(
    languages: Optional[list[str]],
    translations: Optional[Translations] = None,
) -> None:
    """
    Set locale for process. If translations is ``None``, default messages are
    loaded. If included messages not found for specified languages, NullTranslations
    will be used.

    .. warning::
        Setting locale for process is not thread-safe itself, so use it carefully if
        your process uses multiple threads.

        Best place to set process locale is on application start.
    """

    global _process_locale
    global _process_translations

    _process_locale = languages

    if translations:
        _process_translations = translations
    else:
        try:
            _process_translations = load_default_messages(languages)
        except FileNotFoundError:
            _process_translations = gettext.NullTranslations()


def set_thread_locale(
    languages: Optional[list[str]],
    translations: Optional[Translations] = None,
) -> None:
    """
    Set locale for current thread. If translations is ``None``, default messages
    are lazy loaded on first message translation. If included messages not found for
    specified languages, NullTranslations will be used.
    """

    _thread_locale.locale = languages
    _thread_locale.locale_is_set = True

    if translations:
        _thread_locale.translations = translations
    else:
        try:
            _thread_locale.translations = load_default_messages(languages)
        except FileNotFoundError:
            _thread_locale.translations = gettext.NullTranslations()


def get_current_locale() -> Optional[list[str]]:
    """
    Returns current locale. Function will return first present value in the following
    order:

        1. Thread locale.
        2. Process locale.
        3. Default locale ("en").

    Current locale can be changed with :func:`set_process_locale` and
    :func:`set_thread_locale`.
    """

    if getattr(_thread_locale, "locale_is_set", False):
        return _thread_locale.locale
    else:
        return _process_locale


def get_current_translations() -> Translations:
    """
    Returns translations object for current locale (see :func:`get_current_locale`).
    """

    if getattr(_thread_locale, "locale_is_set", False):
        if not _thread_locale.translations:
            _thread_locale.translations = load_default_messages(_thread_locale.locale)

        return _thread_locale.translations
    else:
        return _process_translations


set_process_locale(["en"])
