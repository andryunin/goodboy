from goodboy.i18n import get_default_translations

__version__ = "0.1.0"


def hello_world():
    t = get_default_translations(["en"])
    print(t.gettext("hello world"))
