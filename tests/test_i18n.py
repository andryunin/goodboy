import threading

from goodboy.i18n import get_current_locale, set_process_locale, set_thread_locale


def test_set_process_locale():
    set_process_locale(["process_locale_name"])
    assert get_current_locale() == ["process_locale_name"]


def test_set_thread_locale():
    set_process_locale(["main_thread_locale"])

    child_locales = {}

    def child_thread_target():
        child_locales["before"] = get_current_locale()
        set_thread_locale(["child_thread_locale"])
        child_locales["after"] = get_current_locale()

    child_thread = threading.Thread(target=child_thread_target)
    child_thread.start()
    child_thread.join()

    assert get_current_locale() == ["main_thread_locale"]
    assert child_locales["before"] == ["main_thread_locale"]
    assert child_locales["after"] == ["child_thread_locale"]
