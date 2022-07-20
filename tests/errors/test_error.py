from goodboy.errors import Error
from goodboy.i18n import lazy_gettext
from goodboy.messages import Message


def test_equality():
    assert Error("oops", {"arg": "val"}) == Error("oops", {"arg": "val"})


def test_message_as_message_instance():
    error = Error("oops", message=Message("Oops!", json="JSON oops!"))

    assert error.get_message() == error.message == "Oops!"
    assert error.get_message("json") == "JSON oops!"


def test_message_as_str():
    error = Error("oops", message="oops!")

    assert error.get_message() == error.message == "oops!"
    assert error.get_message("json") == "oops!"


def test_message_as_lazy_gettext_string():
    error = Error("oops", message=lazy_gettext("oops!"))

    assert error.get_message() == error.message == "oops!"
    assert error.get_message("json") == "oops!"


def test_merge_nested_errors_when_key_not_exists():
    nested_errors = {"key": [Error("key_oops")]}

    error = Error("oops")
    error.merge_nested_errors(nested_errors)

    assert error.nested_errors == nested_errors


def test_merge_nested_errors_when_key_already_exists():
    nested_errors = {"key": [Error("key_oops_2")]}

    error = Error("oops", nested_errors={"key": [Error("key_oops_1")]})
    error.merge_nested_errors(nested_errors)

    assert error.nested_errors == {"key": [Error("key_oops_1"), Error("key_oops_2")]}
