from __future__ import annotations

from typing import Any, Callable, ClassVar, Optional, Union

from goodboy.errors import Error, ErrorFormatter, get_formatter_class
from goodboy.i18n import I18nLoader, Translations, get_current_locale
from goodboy.schema import Schema, SchemaError


class Result:
    def __init__(
        self,
        value: Any,
        errors: list[Error],
        translations_getter: Callable[[list[str]], Translations] = None,
    ):
        self.value = value
        self.errors = errors
        self._translations_getter = translations_getter

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def format_errors(
        self,
        formatter: Union[ErrorFormatter, str],
        languages: Optional[list[str]] = None,
    ):
        translations: Optional[Translations]

        if not languages:
            languages = get_current_locale()

        if languages:
            if not self._translations_getter:
                raise ValueError("tranlations_getter is not set")

            translations = self._translations_getter(languages)
        else:
            translations = None

        if isinstance(formatter, str):
            formatter_class = get_formatter_class(formatter)
            formatter = formatter_class(translations)

        return formatter.format(self.errors)


class Validator:
    _i18n_loader: ClassVar[I18nLoader]

    def __init__(self, schema: Schema):
        self.schema = schema

    def validate(self, value, typecast: bool = False, context: dict = {}) -> Result:
        try:
            result_value = self.schema(value, typecast=typecast)
        except SchemaError as e:
            return Result(None, e.errors, self.__class__.get_translations)

        return Result(result_value, [], self.__class__.get_translations)

    @classmethod
    def get_translations(cls, languages: list = []) -> Translations:
        if not hasattr(cls, "_i18n_loader"):
            cls._i18n_loader = I18nLoader()

        return cls._i18n_loader.get_translations(languages)


def validate(schema: Schema, value, typecast: bool = False):
    validator = Validator(schema)
    return validator.validate(value, typecast=typecast)
