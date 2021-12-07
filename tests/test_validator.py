import pytest

from goodboy.i18n import set_default_locale
from goodboy.types.numeric import Int
from goodboy.validator import Validator

schema = Int()


def test_validate():
    assert Validator(schema).validate(42).is_valid
    assert not Validator(schema).validate("42").is_valid


def test_validate_with_typecast():
    assert Validator(schema).validate(42, typecast=True).is_valid
    assert Validator(schema).validate("42", typecast=True).is_valid


@pytest.mark.parametrize(
    "languages,message",
    [
        (["ru"], "не может быть null"),
        (["en"], "cannot be null"),
    ],
)
def test_messages_translation(languages, message):
    result = Validator(schema).validate(None)
    assert result.format_errors("json", languages=languages)[0]["message"] == message


@pytest.mark.parametrize(
    "languages,message",
    [
        (["ru"], "не может быть null"),
        (["en"], "cannot be null"),
    ],
)
def test_messages_translation_with_default_locale(languages, message):
    result = Validator(schema).validate(None)
    set_default_locale(languages)
    assert result.format_errors("json")[0]["message"] == message
