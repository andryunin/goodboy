import pytest

from goodboy.types import Int
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
        (["ru"], "Не может быть null"),
        (["en"], "Cannot be null"),
    ],
)
def test_messages_translation(languages, message):
    result = Validator(schema).validate(None)
    assert result.format_errors("json", languages=languages)[0]["message"] == message
