from __future__ import annotations

import gettext
import sys
import threading
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional, Union

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol


class Translations(Protocol):
    def gettext(self, message):
        ...


def default_messages_path() -> Path:
    """
    Get path of included messages.
    """
    return Path(__file__).joinpath("..", "locale").resolve()


def load_default_messages(languages: Iterable[str] = None) -> Translations:
    """
    Get translations object (instance of ``gettext.GNUTranslations``) with included
    messages.

    :param languages:
        Languages list in order to try. If None, system language will be used.
    """
    return gettext.translation("goodboy", default_messages_path(), languages)


class I18nLoader:
    def __init__(self):
        self._cache: dict[tuple[str, ...], Translations] = {}

    def get_translations(self, languages: Iterable[str]) -> Translations:
        # Make hashable tuple from unhashable list
        languages = tuple(languages)

        if languages not in self._cache:
            self._cache[languages] = load_default_messages(languages)

        return self._cache[languages]


class I18nLazyStub:
    def __init__(self, message: str):
        self.message = message

    def eval(self, translations) -> str:
        return translations.gettext(self.message)

    def get_original_message(self) -> str:
        return self.message


def lazy_gettext(message):
    return I18nLazyStub(message)


global_locale: Optional[list[str]] = ["en"]
thread_locale = threading.local()


class DefaultLocaleScope(Enum):
    GLOBAL = 0
    THREAD = 1


def set_default_locale(
    languages: Optional[list[str]],
    scope: DefaultLocaleScope = DefaultLocaleScope.GLOBAL,
):
    global global_locale

    if scope == DefaultLocaleScope.GLOBAL:
        global_locale = languages
    elif scope == DefaultLocaleScope.THREAD:
        thread_locale.locale = languages
        thread_locale.locale_is_set = True
    else:
        raise ValueError(f"unexpected default locale scope: {repr(scope)}")


def get_default_locale() -> Union[list[str], None]:
    if getattr(thread_locale, "locale_is_set", False):
        return thread_locale.locale
    else:
        return global_locale
