from __future__ import annotations

import sys
from typing import Any, Mapping, Type

from goodboy.types.dates import Date, DateTime
from goodboy.types.variants import AnyOf

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from goodboy.errors import Error
from goodboy.schema import Schema, SchemaError
from goodboy.types.dicts import Dict, Key
from goodboy.types.lists import List
from goodboy.types.numeric import Float, Int
from goodboy.types.python import CallableValue
from goodboy.types.simple import AnyValue, Bool, NoneValue, Str


class DeclarativeSchemaFabric(Protocol):
    def option_dict_keys(self, schema_name: str, full_schema: Schema) -> list[Key]:
        ...

    def create(self, options: dict[str, Any], builder: DeclarativeBuilder) -> Schema:
        ...


class SimpleDeclarativeSchemaFabric:
    def __init__(self, schema_class: Type[Schema], keys: list[Key] = []) -> None:
        self._schema_class = schema_class
        self._keys = keys

    def option_dict_keys(self, schema_name: str, full_schema: Schema) -> list[Key]:
        def predicate(value: Mapping[str, Any]) -> bool:
            return value.get("type") == schema_name

        return list(map(lambda key: key.with_predicate(predicate), self._keys))

    def create(self, options: dict[str, Any], builder: DeclarativeBuilder) -> Schema:
        return self._schema_class(**options)  # type: ignore


class DictDeclarativeSchemaFabric:
    def option_dict_keys(self, schema_name: str, full_schema: Schema) -> list[Key]:
        def predicate(value: Mapping[str, Any]) -> bool:
            return value.get("type") == schema_name

        keys = [
            Key("allow_none", Bool()),
            Key("messages", _MESSAGES_SCHEMA),
            Key("rules", _RULES_SCHEMA),
            Key(
                "keys",
                List(
                    item=Dict(
                        keys=[
                            Key("name", Str(), required=True),
                            Key("schema", full_schema),
                            Key("required", Bool(allow_none=True)),
                            Key("predicate", CallableValue(allow_none=True)),
                        ],
                        keys_required_by_default=False,
                    )
                ),
            ),
            Key("key_schema", full_schema),
            Key("value_schema", full_schema),
            Key("keys_required_by_default", Bool()),
        ]

        return list(map(lambda key: key.with_predicate(predicate), keys))

    def create(self, options: dict[str, Any], builder: DeclarativeBuilder) -> Schema:
        if options.get("keys"):
            keys = []

            for key_options in options["keys"]:
                if "schema" in key_options:
                    key_options["schema"] = builder.build(key_options["schema"], False)

                keys.append(Key(**key_options))

            options["keys"] = keys

        if options.get("key_schema"):
            options["key_schema"] = builder.build(options["key_schema"], False)

        if options.get("value_schema"):
            options["value_schema"] = builder.build(options["value_schema"], False)

        return self._schema_class()(**options)

    def _schema_class(self) -> Type[Dict]:
        return Dict


class ListDeclarativeSchemaFabric:
    def option_dict_keys(self, schema_name: str, full_schema: Schema) -> list[Key]:
        def predicate(value: Mapping[str, Any]) -> bool:
            return value.get("type") == schema_name

        keys = [
            Key("allow_none", Bool()),
            Key("messages", _MESSAGES_SCHEMA),
            Key("rules", _RULES_SCHEMA),
            Key("item", full_schema),
            Key("min_length", Int(greater_or_equal_to=0)),
            Key("max_length", Int(greater_or_equal_to=0)),
            Key("length", Int(greater_or_equal_to=0)),
        ]

        return list(map(lambda key: key.with_predicate(predicate), keys))

    def create(self, options: dict[str, Any], builder: DeclarativeBuilder) -> Schema:
        if options.get("item"):
            options["item"] = builder.build(options["item"], False)

        return self._schema_class()(**options)

    def _schema_class(self) -> Type[List]:
        return List


class AnyOfDeclarativeSchemaFabric:
    def option_dict_keys(self, schema_name: str, full_schema: Schema) -> list[Key]:
        def predicate(value: Mapping[str, Any]) -> bool:
            return value.get("type") == schema_name

        keys = [
            Key("schemas", List(item=full_schema)),
            Key("messages", _MESSAGES_SCHEMA),
            Key("rules", _RULES_SCHEMA),
        ]

        return list(map(lambda key: key.with_predicate(predicate), keys))

    def create(self, options: dict[str, Any], builder: DeclarativeBuilder) -> Schema:
        options["schemas"] = list(map(builder.build, options["schemas"]))
        return AnyOf(**options)


_MESSAGES_SCHEMA = Dict(
    key_schema=Str(),
    value_schema=AnyOf(
        [
            Str(),
            Dict(
                keys=[
                    Key("default", Str(), required=True),
                ],
                key_schema=Str(),
                value_schema=Str(),
            ),
        ]
    ),
)

_RULES_SCHEMA = List(item=CallableValue())

_DEFAULT_DECLARATIVE_SCHEMA_FABRICS: dict[str, DeclarativeSchemaFabric] = {
    # Simple
    "any": SimpleDeclarativeSchemaFabric(
        AnyValue,
        [
            Key("allow_none", Bool()),
            Key("messages", _MESSAGES_SCHEMA),
            Key("rules", _RULES_SCHEMA),
            Key("allowed", List(item=AnyValue())),
        ],
    ),
    "none": SimpleDeclarativeSchemaFabric(
        NoneValue,
        [
            Key("messages", _MESSAGES_SCHEMA),
            Key("rules", _RULES_SCHEMA),
        ],
    ),
    "str": SimpleDeclarativeSchemaFabric(
        Str,
        [
            Key("allow_none", Bool()),
            Key("messages", _MESSAGES_SCHEMA),
            Key("allow_blank", Bool()),
            Key("rules", _RULES_SCHEMA),
            Key("min_length", Int(greater_or_equal_to=0)),
            Key("max_length", Int(greater_or_equal_to=0)),
            Key("length", Int(greater_or_equal_to=0)),
            Key("pattern", Str(is_regex=True)),
            Key("is_regex", Bool()),
            Key("allowed", List(item=Str())),
        ],
    ),
    "bool": SimpleDeclarativeSchemaFabric(
        Bool,
        [
            Key("allow_none", Bool()),
            Key("messages", _MESSAGES_SCHEMA),
            Key("rules", _RULES_SCHEMA),
            Key("only_false", Bool()),
            Key("only_true", Bool()),
            Key("cast_anything", Bool()),
        ],
    ),
    # Date/Datetime
    "date": SimpleDeclarativeSchemaFabric(
        Date,
        [
            Key("allow_none", Bool()),
            Key("messages", _MESSAGES_SCHEMA),
            Key("rules", _RULES_SCHEMA),
            Key("earlier_than", Date()),
            Key("earlier_or_equal_to", Date()),
            Key("later_than", Date()),
            Key("later_or_equal_to", Date()),
            Key("format", Str()),
            Key("allowed", List(item=Date())),
        ],
    ),
    "datetime": SimpleDeclarativeSchemaFabric(
        DateTime,
        [
            Key("allow_none", Bool()),
            Key("messages", _MESSAGES_SCHEMA),
            Key("rules", _RULES_SCHEMA),
            Key("earlier_than", DateTime()),
            Key("earlier_or_equal_to", DateTime()),
            Key("later_than", DateTime()),
            Key("later_or_equal_to", DateTime()),
            Key("format", Str()),
            Key("allowed", List(item=DateTime())),
        ],
    ),
    # Numeric
    "int": SimpleDeclarativeSchemaFabric(
        Int,
        [
            Key("allow_none", Bool()),
            Key("messages", _MESSAGES_SCHEMA),
            Key("rules", _RULES_SCHEMA),
            Key("less_than", Int()),
            Key("less_or_equal_to", Int()),
            Key("greater_than", Int()),
            Key("greater_or_equal_to", Int()),
            Key("allowed", List(item=Int())),
        ],
    ),
    "float": SimpleDeclarativeSchemaFabric(
        Float,
        [
            Key("allow_none", Bool()),
            Key("messages", _MESSAGES_SCHEMA),
            Key("rules", _RULES_SCHEMA),
            Key("less_than", Float()),
            Key("less_or_equal_to", Float()),
            Key("greater_than", Float()),
            Key("greater_or_equal_to", Float()),
            Key("allowed", List(item=Float())),
        ],
    ),
    # Dict
    "dict": DictDeclarativeSchemaFabric(),
    # List
    "list": ListDeclarativeSchemaFabric(),
    # Variants
    "any_of": AnyOfDeclarativeSchemaFabric(),
}


class DeclarationError(Exception):
    def __init__(self, errors: list[Error]) -> None:
        self.errors = errors


class DeclarativeBuilder:
    def __init__(
        self,
        fabrics: dict[
            str, DeclarativeSchemaFabric
        ] = _DEFAULT_DECLARATIVE_SCHEMA_FABRICS,
    ):
        self._fabrics = fabrics

    def build(
        self, declaration: dict[str, Any], validate: bool = True, typecast: bool = True
    ) -> Schema:
        if validate:
            try:
                declaration = self.validate(declaration, typecast=typecast)
            except SchemaError as e:
                raise DeclarationError(e.errors)

        schema_name = declaration["type"]
        schema_fabric = self._fabrics[schema_name]

        declaration = declaration.copy()
        declaration.pop("type")

        return schema_fabric.create(declaration, self)

    def validate(
        self, declaration: dict[str, Any], typecast: bool = True
    ) -> dict[str, Any]:
        schema = self.declaration_schema()
        return schema(declaration, typecast=typecast)  # type: ignore

    def declaration_schema(self) -> Dict:
        schema_names = list(self._fabrics.keys())

        schema = Dict(
            keys=[
                Key("type", Str(allowed=schema_names), required=True),
            ],
            keys_required_by_default=False,
        )

        for schema_name, fabric in self._fabrics.items():
            # TODO: use weakref of schema
            for key in fabric.option_dict_keys(schema_name, schema):
                schema.append_key(key)

        return schema


DEFAULT_DECLARATIVE_BUILDER = DeclarativeBuilder()


def build(
    declaration: dict[str, Any], validate: bool = True, typecast: bool = True
) -> Schema:
    return DEFAULT_DECLARATIVE_BUILDER.build(declaration, validate, typecast)
