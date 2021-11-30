from goodboy.validator import Validator
from goodboy.types import Int


schema = Int()


def test_validate():
    assert Validator(schema).validate(42).is_valid
    assert not Validator(schema).validate("42").is_valid


def test_validate_with_typecast():
    assert Validator(schema).validate(42, typecast=True).is_valid
    assert Validator(schema).validate("42", typecast=True).is_valid
