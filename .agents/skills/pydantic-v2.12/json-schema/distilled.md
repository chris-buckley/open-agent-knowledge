# Pydantic v2 -- JSON Schema & JSON Encoding

Pydantic generates JSON Schema compliant with JSON Schema Draft 2020-12 and OpenAPI 3.1.0.

## Generating JSON Schema

### model_json_schema()

Returns a jsonable `dict[str, Any]` (not a JSON string -- call `json.dumps()` on it for that).

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

schema = User.model_json_schema()  # dict
# json.dumps(schema) -> JSON string
```

Signature:

```python
BaseModel.model_json_schema(
    by_alias: bool = True,
    ref_template: str = '#/$defs/{model}',
    schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema,
    mode: JsonSchemaMode = 'validation',
) -> dict[str, Any]
```

Key parameters:
- `by_alias` -- use field aliases as keys (default `True`); set `False` for attribute names.
- `ref_template` -- format string for `$ref` values (default `'#/$defs/{model}'`).
- `schema_generator` -- custom `GenerateJsonSchema` subclass.
- `mode` -- `'validation'` (default) or `'serialization'`.

### TypeAdapter.json_schema()

For arbitrary types (not just BaseModel):

```python
from pydantic import TypeAdapter

ta = TypeAdapter(list[int])
ta.json_schema()  # {'items': {'type': 'integer'}, 'type': 'array'}
```

### models_json_schema() -- multi-model top-level schema

Generates a combined `$defs`-only schema for multiple models:

```python
from pydantic import BaseModel
from pydantic.json_schema import models_json_schema

class Foo(BaseModel):
    a: str

class Bar(BaseModel):
    c: int

_, top_level = models_json_schema(
    [(Foo, 'validation'), (Bar, 'validation')],
    title='My Schema',
)
# top_level has $defs with Foo and Bar, plus title
```

## JSON Schema Generation Modes

`JsonSchemaMode = Literal['validation', 'serialization']`

- `'validation'` (default): schema describes what the model accepts as input.
- `'serialization'`: schema describes what the model outputs when serialized.

Difference matters for types like `Decimal` (accepts `number | string` in validation, outputs only `string` in serialization), computed fields (serialization-only), and custom serializers.

```python
from decimal import Decimal
from pydantic import BaseModel

class Model(BaseModel):
    a: Decimal = Decimal('12.34')

Model.model_json_schema(mode='validation')
# a: anyOf [{type: number}, {type: string, pattern: ...}]

Model.model_json_schema(mode='serialization')
# a: {type: string, pattern: ...}
```

Override per-model with `ConfigDict(json_schema_mode_override=...)`.

## Customizing JSON Schema

### Field-Level Customization

Use `Field()` parameters that affect only JSON Schema output:

```csv
Parameter,Purpose
title,Override auto-generated title
description,Field description
examples,Example values
json_schema_extra,Dict or callable to merge/modify schema
field_title_generator,"Callable[[str, FieldInfo], str] for programmatic titles"
```

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    age: int = Field(description='Age of the user')
    name: str = Field(title='Username')
```

### Model-Level Customization (ConfigDict)

Relevant config options:
- `title` -- model title in schema.
- `json_schema_extra` -- dict or callable applied to the model schema.
- `json_schema_mode_override` -- force a specific mode.
- `field_title_generator` -- applied to all fields.
- `model_title_generator` -- `Callable[[type], str]` for the model title.

```python
from pydantic import BaseModel, ConfigDict

class Person(BaseModel):
    model_config = ConfigDict(
        field_title_generator=lambda name, info: name.upper(),
        model_title_generator=lambda cls: f'Schema-{cls.__name__}',
    )
    name: str
    age: int
```

### json_schema_extra

With a dict -- merged into the schema:

```python
model_config = ConfigDict(
    json_schema_extra={'examples': [{'a': 'Foo'}]}
)
```

With a callable -- mutates the schema dict in place:

```python
def pop_default(s):
    s.pop('default')

class Model(BaseModel):
    a: int = Field(default=1, json_schema_extra=pop_default)
```

Merging across Annotated layers (v2.9+): multiple `json_schema_extra` dicts on the same field are merged additively:

```python
from typing import Annotated
from pydantic import Field, TypeAdapter

ExternalType = Annotated[int, Field(json_schema_extra={'key1': 'value1'})]
ta = TypeAdapter(
    Annotated[ExternalType, Field(json_schema_extra={'key2': 'value2'})]
)
ta.json_schema()  # {key1: value1, key2: value2, type: integer}
```

Mixing dict and callable `json_schema_extra` in the same annotation stack is not supported.

### WithJsonSchema Annotation

Override the base JSON schema for a type without implementing `__get_pydantic_core_schema__`. This replaces the entire generated schema for the annotated type -- you must include `type` etc.

```python
from typing import Annotated
from pydantic import BaseModel, WithJsonSchema

MyInt = Annotated[
    int,
    WithJsonSchema({'type': 'integer', 'examples': [1, 0, -1]}),
]

class Model(BaseModel):
    a: MyInt
```

`WithJsonSchema` accepts an optional `mode` parameter (`'validation'` or `'serialization'`) to provide different schemas per mode.

Preferred over `__get_pydantic_json_schema__` for most use cases.

### SkipJsonSchema Annotation

Exclude a field (or part of a union branch) from the JSON schema entirely:

```python
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

class Model(BaseModel):
    a: int | None = None                         # both int and null in schema
    b: int | SkipJsonSchema[None] = None          # only int in schema
    c: SkipJsonSchema[int | None] = None          # field excluded entirely
```

### Implementing __get_pydantic_json_schema__

For custom types that need full control over JSON schema generation. Receives the core schema and a handler; call `handler(core_schema)` to get the base schema, then modify:

```python
from typing import Any
from pydantic_core import core_schema as cs
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, TypeAdapter
from pydantic.json_schema import JsonSchemaValue

class Person:
    name: str
    age: int

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> cs.CoreSchema:
        return cs.typed_dict_schema({
            'name': cs.typed_dict_field(cs.str_schema()),
            'age': cs.typed_dict_field(cs.int_schema()),
        })

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema['title'] = 'Person'
        json_schema['examples'] = [{'name': 'John', 'age': 25}]
        return json_schema
```

Important: call `handler.resolve_ref_schema(json_schema)` before modifying if the schema might be a `$ref`.

### Implementing __get_pydantic_core_schema__

Controls both validation/serialization behavior AND the resulting JSON schema (since JSON schema is derived from the core schema). For custom types used as field annotations or `Annotated` metadata.

Two positional arguments:
1. The type annotation (e.g., `TheType[int]`).
2. A handler to call the next schema implementer.

For custom types, you typically do NOT call `handler(source)` (it will raise `PydanticSchemaGenerationError`). For `Annotated` metadata, you typically DO call `handler(source)` to get the inner schema and wrap/modify it.

## $ref Handling and Definitions

- Sub-models are stored under `$defs` and referenced via `$ref`.
- Default ref template: `'#/$defs/{model}'`.
- Customize with `ref_template` parameter (e.g., for OpenAPI):

```python
adapter.json_schema(ref_template='#/components/schemas/{model}')
# $ref values become "#/components/schemas/Foo" etc.
# definitions still stored under $defs key
```

- Sub-models with Field modifications (custom title, description, default) are inlined instead of referenced.
- `Optional[X]` generates `anyOf: [{$ref: ...}, {type: null}]`.

## Unions in JSON Schema

Union types produce `anyOf` by default:

```python
from pydantic import BaseModel, TypeAdapter

class Cat(BaseModel):
    name: str
    color: str

class Dog(BaseModel):
    name: str
    breed: str

ta = TypeAdapter(Cat | Dog)
ta.json_schema()
# {$defs: {Cat: {...}, Dog: {...}}, anyOf: [{$ref: ...Cat}, {$ref: ...Dog}]}
```

`GenerateJsonSchema` accepts `union_format` parameter:
- `'any_of'` (default): uses `anyOf` keyword.
- `'primitive_type_array'`: uses `type` as an array of strings for primitive unions; falls back to `anyOf` if any branch is non-primitive or has constraints.

## GenerateJsonSchema -- Advanced Customization

Subclass `GenerateJsonSchema` to customize the entire generation process. Pass via `schema_generator=` parameter.

### Override generate() for global modifications

```python
from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema

class MyGenerator(GenerateJsonSchema):
    def generate(self, schema, mode='validation'):
        json_schema = super().generate(schema, mode=mode)
        json_schema['title'] = 'Custom Title'
        json_schema['$schema'] = self.schema_dialect
        return json_schema

MyModel.model_json_schema(schema_generator=MyGenerator)
```

### Skip non-serializable fields

```python
from pydantic_core import PydanticOmit, core_schema
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue

class SkipInvalidSchema(GenerateJsonSchema):
    def handle_invalid_for_json_schema(
        self, schema: core_schema.CoreSchema, error_info: str
    ) -> JsonSchemaValue:
        raise PydanticOmit  # silently omit the field
```

### Customize sorting

Default: keys sorted alphabetically except `properties` (preserves field order). Override `sort()`:

```python
class NoSortSchema(GenerateJsonSchema):
    def sort(self, value, parent_key=None):
        return value  # no-op, preserve insertion order
```

### Key overridable methods

```csv
Method,Purpose
"generate(schema, mode)",Top-level entry; returns final schema with $defs
generate_inner(schema),Per-schema dispatch (calls type-specific methods)
"sort(value, parent_key)",Controls key ordering
{type}_schema(schema),"Per-type handlers: str_schema, int_schema, model_schema, union_schema, etc."
handle_invalid_for_json_schema(...),"Called for types with no JSON representation (Callable, isinstance checks)"
resolve_ref_schema(json_schema),Dereferences a $ref to the actual schema dict
get_defs_ref(...),Controls definition naming
encode_default(...),Encodes default values for inclusion in schema
```

### Key attributes

```csv
Attribute,Type,Description
schema_dialect,str,'https://json-schema.org/draft/2020-12/schema'
by_alias,bool,Whether to use aliases
ref_template,str,Reference format template
definitions,"dict[DefsRef, JsonSchemaValue]",Accumulated definitions
ignored_warning_kinds,set[JsonSchemaWarningKind],Warnings to suppress
```

Important: a `GenerateJsonSchema` instance is single-use. After calling `generate()` or `generate_definitions()`, create a new instance for the next schema.

## JSON Parsing (Encoding/Decoding)

### model_validate_json() -- parse JSON string to model

```python
from datetime import date
from pydantic import BaseModel, ConfigDict

class Event(BaseModel):
    model_config = ConfigDict(strict=True)
    when: date
    where: tuple[int, int]

json_data = '{"when": "1987-01-28", "where": [51, -1]}'
event = Event.model_validate_json(json_data)
# Works: JSON strings are accepted for date even in strict mode
```

Also available: `TypeAdapter(T).validate_json(json_bytes_or_str)`.

### model_dump_json() -- serialize model to JSON string

```python
json_str: str = event.model_dump_json()
```

Also: `TypeAdapter(T).dump_json(instance)` returns `bytes`.

### Strict JSON Parsing

With `ConfigDict(strict=True)`, `model_validate_json()` still accepts JSON-native coercions (string to date, array to tuple) because they come from JSON. But `model_validate()` (dict input) rejects them -- strings are not dates, lists are not tuples.

This is the key difference: JSON parsing is more lenient than Python dict validation in strict mode.

### Partial JSON Parsing

Use `pydantic_core.from_json()` for incomplete JSON (useful for LLM streaming output):

```python
from pydantic_core import from_json
from pydantic import BaseModel

class Dog(BaseModel):
    breed: str
    name: str
    friends: list = []

partial = '{"breed": "lab", "name": "fluffy", "friends": ["buddy", "spot'
dog = Dog.model_validate(from_json(partial, allow_partial=True))
# Dog(breed='lab', name='fluffy', friends=['buddy'])
```

For reliable partial parsing, give all fields default values. Incomplete dict keys and string values are dropped.

### Caching Strings

`cache_strings` setting (ConfigDict or `from_json()`):
- `True` / `'all'` (default): cache all parsed strings.
- `'keys'`: cache only dict keys.
- `False` / `'none'`: no caching.

Only strings with `len < 64` are cached. Caching improves performance but slightly increases memory.

### JSON Parser

Pydantic uses jiter (v2.5+), a fast iterable JSON parser. Supports `inf`/`NaN` deserialization.

## Miscellaneous Notes

- `Optional[T]` schema includes `null` as allowed type.
- `Decimal` is serialized/exposed as a string in JSON schema.
- `namedtuple` is not preserved in JSON schema (no JSON equivalent).
- Model description is taken from the class docstring or `Field(description=...)`.
- Schema uses aliases as keys by default; pass `by_alias=False` for attribute names.
- Sub-models with Field modifications (custom title, description, default) are recursively inlined rather than `$ref`'d.

## Type Aliases Quick Reference

```python
from pydantic.json_schema import (
    JsonSchemaValue,        # dict[str, Any]
    JsonSchemaMode,         # Literal['validation', 'serialization']
    GenerateJsonSchema,     # The generator class
    WithJsonSchema,         # Annotation to override schema
    SkipJsonSchema,         # Annotation to exclude from schema
    model_json_schema,      # Standalone function (same as BaseModel.model_json_schema)
    models_json_schema,     # Multi-model schema generation
    DEFAULT_REF_TEMPLATE,   # '#/$defs/{model}'
)
```
