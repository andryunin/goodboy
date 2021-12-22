from __future__ import annotations

import sys
from typing import Type

from goodboy.types.variants import AnyOf

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from goodboy.errors import Error
from goodboy.schema import Schema, SchemaError
from goodboy.types.dicts import Dict, Key
from goodboy.types.lists import List
from goodboy.types.numeric import Int
from goodboy.types.python import CallableValue
from goodboy.types.simple import Bool, Str


class DeclarativeSchemaFabric(Protocol):
    def option_dict_keys(self, schema_name: str, full_schema: Schema):
        ...

    def create(self, options: dict, builder: DeclarativeBuilder):
        ...


class SimpleDeclarativeSchemaFabric:
    def __init__(self, schema_class: Type[Schema], keys=[]):
        self.schema_class = schema_class
        self.keys = keys

    def option_dict_keys(self, schema_name: str, full_schema: Schema):
        def predicate(value):
            return value.get("schema") == schema_name

        return list(map(lambda key: key.with_predicate(predicate), self.keys))

    def create(self, options: dict, builder: DeclarativeBuilder):
        return self.schema_class(**options)


class DictDeclarativeSchemaFabric:
    def option_dict_keys(self, schema_name: str, full_schema: Schema):
        def predicate(value):
            return value.get("schema") == schema_name

        keys = [
            Key("allow_none", Bool()),
            Key("messages", MESSAGES_SCHEMA),
            Key("rules", RULES_SCHEMA),
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

    def create(self, options: dict, builder: DeclarativeBuilder):
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

        return Dict(**options)


class ListDeclarativeSchemaFabric:
    def option_dict_keys(self, schema_name: str, full_schema: Schema):
        def predicate(value):
            return value.get("schema") == schema_name

        keys = [
            Key("allow_none", Bool()),
            Key("messages", MESSAGES_SCHEMA),
            Key("rules", RULES_SCHEMA),
            Key("item", full_schema),
            Key("min_length", Int(greater_or_equal_to=0)),
            Key("max_length", Int(greater_or_equal_to=0)),
            Key("length", Int(greater_or_equal_to=0)),
        ]

        return list(map(lambda key: key.with_predicate(predicate), keys))

    def create(self, options: dict, builder: DeclarativeBuilder):
        if options.get("item"):
            options["item"] = builder.build(options["item"], False)

        return List(**options)


MESSAGES_SCHEMA = Dict(
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

RULES_SCHEMA = List(item=CallableValue())

DEFAULT_DECLARATIVE_SCHEMA_FABRICS: dict[str, DeclarativeSchemaFabric] = {
    "str": SimpleDeclarativeSchemaFabric(
        Str,
        [
            Key("allow_none", Bool()),
            Key("messages", MESSAGES_SCHEMA),
            Key("allow_blank", Bool()),
            Key("rules", RULES_SCHEMA),
            Key("min_length", Int(greater_or_equal_to=0)),
            Key("max_length", Int(greater_or_equal_to=0)),
            Key("length", Int(greater_or_equal_to=0)),
            Key("pattern", Str(is_regex=True)),
            Key("is_regex", Bool()),
            Key("allowed", List(item=Str())),
        ],
    ),
    "int": SimpleDeclarativeSchemaFabric(
        Int,
        [
            Key("allow_none", Bool()),
            Key("messages", MESSAGES_SCHEMA),
            Key("rules", RULES_SCHEMA),
            Key("less_than", Int()),
            Key("less_or_equal_to", Int()),
            Key("greater_than", Int()),
            Key("greater_or_equal_to", Int()),
            Key("allowed", List(item=Int())),
        ],
    ),
    "bool": SimpleDeclarativeSchemaFabric(
        Bool,
        [
            Key("allow_none", Bool()),
            Key("messages", MESSAGES_SCHEMA),
            Key("rules", RULES_SCHEMA),
            Key("only_false", Bool()),
            Key("only_true", Bool()),
            Key("cast_anything", Bool()),
        ],
    ),
    "dict": DictDeclarativeSchemaFabric(),
    "list": ListDeclarativeSchemaFabric(),
}


class DeclarationError(Exception):
    def __init__(self, errors: list[Error]):
        self.errors = errors


class DeclarativeBuilder:
    def __init__(
        self,
        fabrics: dict[
            str, DeclarativeSchemaFabric
        ] = DEFAULT_DECLARATIVE_SCHEMA_FABRICS,
    ):
        self.fabrics = fabrics

    def build(self, declaration, validate=True):
        if validate:
            try:
                self.validate(declaration)
            except SchemaError as e:
                raise DeclarationError(e.errors)

        schema_name = declaration["schema"]
        schema_fabric = self.fabrics[schema_name]

        declaration = declaration.copy()
        declaration.pop("schema")

        return schema_fabric.create(declaration, self)

    def validate(self, declaration):
        schema = self.declaration_schema()
        schema(declaration)

    def declaration_schema(self):
        schema_names = list(self.fabrics.keys())

        schema = Dict(
            keys=[
                Key("schema", Str(allowed=schema_names), required=True),
            ],
            keys_required_by_default=False,
        )

        for schema_name, fabric in self.fabrics.items():
            # TODO: use weakref of schema
            for key in fabric.option_dict_keys(schema_name, schema):
                schema.append_key(key)

        return schema
