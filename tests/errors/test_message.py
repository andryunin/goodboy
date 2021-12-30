import pytest

from goodboy.i18n import lazy_gettext as _
from goodboy.messages import Message
from tests.conftest import TranslationsMock


@pytest.fixture
def cannot_be_none():
    return Message("Cannot be None", json="Cannot be null")


def test_renders_default_message_with_default_format(cannot_be_none):
    assert cannot_be_none.render() == "Cannot be None"
    assert cannot_be_none.render("default") == "Cannot be None"


def test_renders_specific_message_for_known_format(cannot_be_none):
    assert cannot_be_none.render("json") == "Cannot be null"


def test_renders_default_message_for_unknown_format(cannot_be_none):
    assert cannot_be_none.render("grpc") == "Cannot be None"


def test_performs_string_formatting():
    message = Message('should be "{type}"')
    assert message.render(kwargs={"type": "int"}) == 'should be "int"'


def test_renders_message_arguments_for_string_formatting():
    message = Message('should be "{type}"')
    kwargs = {"type": Message("int", json="integer")}

    assert message.render(kwargs=kwargs) == 'should be "int"'
    assert message.render(kwargs=kwargs, format="json") == 'should be "integer"'


def test_evaluates_lazy_i18n():
    message = Message(_("Cannot be None"), json=_("Cannot be null"))

    t = TranslationsMock(
        {
            "Cannot be None": "Не может быть None",
            "Cannot be null": "Не может быть null",
        }
    )

    assert message.render(translations=t) == "Не может быть None"
    assert message.render(translations=t, format="json") == "Не может быть null"


def test_representation(cannot_be_none):
    assert repr(cannot_be_none) == "Message('Cannot be None', json='Cannot be null')"
