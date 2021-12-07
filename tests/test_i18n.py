import threading

from goodboy.i18n import DefaultLocaleScope, get_default_locale, set_default_locale


def test_global_default_locale():
    set_default_locale(["global_test"], DefaultLocaleScope.GLOBAL)
    assert get_default_locale() == ["global_test"]


def test_thread_default_locale():
    set_default_locale(["main_thread_locale"], DefaultLocaleScope.GLOBAL)

    child_locales = {}

    def child_thread_target():
        child_locales["before"] = get_default_locale()
        set_default_locale(["child_thread_locale"], DefaultLocaleScope.THREAD)
        child_locales["after"] = get_default_locale()

    child_thread = threading.Thread(target=child_thread_target)
    child_thread.start()
    child_thread.join()

    assert get_default_locale() == ["main_thread_locale"]
    assert child_locales["before"] == ["main_thread_locale"]
    assert child_locales["after"] == ["child_thread_locale"]
