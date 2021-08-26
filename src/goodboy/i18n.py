import gettext
from pathlib import Path


def default_messages_path() -> Path:
    """
    Get path of included messages.
    """
    return Path(__file__).joinpath("..", "locale").resolve()


def get_default_translations(languages: list[str] = None):
    """
    Get translations object (instance of ``gettext.GNUTranslations``) with included
    messages.

    :param languages:
        Languages list in order to try. If None, system language will be used.
    """
    return gettext.translation("goodboy", default_messages_path(), languages)
