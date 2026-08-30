---
name: pydantic-v2.12
description: Pydantic v2.12 — Python data validation using type annotations, powered by a Rust core for 5-20x speedup over v1.
user-invocable: true
---

# Pydantic v2 Skill

Pydantic 2.12 | https://docs.pydantic.dev/latest/ | Python >=3.10 | Build details: BUILD_INFO.md

Each topic folder (models, fields, validators, serialization, types, configuration, json-schema, errors, performance) holds distilled.md (full guide), patterns.md, pitfalls.md; api-reference holds distilled.md only (detailed lookup tables). Read them on demand for depth.

## Quick Reference

```python
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Annotated

# Define a model
class User(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)
    id: int
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r'^[\w.-]+@[\w.-]+\.\w+$')
    tags: list[str] = []

    @field_validator('name', mode='after')
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

# Validate
user = User.model_validate({'id': 1, 'name': 'Alice', 'email': 'a@b.com'})
user = User.model_validate_json('{"id":1,"name":"Alice","email":"a@b.com"}')

# Serialize
d = user.model_dump(exclude_unset=True)
j = user.model_dump_json(indent=2)

# JSON Schema
schema = User.model_json_schema()

# TypeAdapter for non-model types
from pydantic import TypeAdapter
ta = TypeAdapter(list[int])  # instantiate ONCE, reuse
result = ta.validate_python(['1', '2'])  # [1, 2]
```

### Essential Patterns

```csv
Pattern,Code
Validate dict,Model.model_validate(data)
Validate JSON,Model.model_validate_json(json_str)
Skip validation,Model.model_construct(**trusted_data)
Serialize to dict,m.model_dump()
Serialize to JSON,m.model_dump_json()
JSON Schema,Model.model_json_schema()
Copy with update,m.model_copy(update={'field': val})
Forward refs,Model.model_rebuild()
Non-model types,TypeAdapter(T).validate_python(data)
Reusable constraint,"MyType = Annotated[int, Field(gt=0)]"
```

## Models

Key concepts:
- BaseModel: Class with annotated fields. Instantiation validates; raises `ValidationError` on failure. Lax coercion by default (`'123'` -> `123`).
- RootModel: Wraps a single value (`RootModel[list[str]]`). Access via `.root`.
- Generic Models: `class Response(BaseModel, Generic[DataT])`. Parametrized classes cached at runtime.
- Dynamic creation: `create_model('Name', field=(type, default), __base__=...)`.
- Pydantic Dataclasses: Add validation to stdlib-style dataclasses. Lack `model_dump()` etc. — wrap with `TypeAdapter`.
- Extra data: `extra='ignore'` (default) | `'forbid'` | `'allow'`.
- Private attrs: `_name: T = PrivateAttr(default=...)`. Dunders ignored.
- Frozen: `ConfigDict(frozen=True)` prevents reassignment, but mutable values still mutable in-place.
- ORM mode: `ConfigDict(from_attributes=True)` to validate from object attributes.
- Forward refs: Use string annotations or `from __future__ import annotations`; call `Model.model_rebuild()` after referenced types are defined. `TypeAdapter` uses `defer_build=True` + `.rebuild()`. PEP 649 (Python 3.14) will simplify this.

## Fields

Key concepts:
- `Field()`: Customize defaults, aliases, constraints, JSON Schema metadata. Returns `FieldInfo`.
- Assignment vs Annotated: Use assignment (`= Field(alias=...)`) for defaults/aliases (type-checker visible). Use `Annotated[T, Field(gt=0)]` for constraints (reusable, composable).
- Aliases: `alias` (both), `validation_alias` (input only, supports `AliasPath`/`AliasChoices`), `serialization_alias` (output only). Precedence: field alias > generator (unless `alias_priority=1`).
- Constraints: `gt`/`ge`/`lt`/`le`/`multiple_of` (numeric), `min_length`/`max_length`/`pattern` (string/collection).
- `computed_field`: `@property` included in serialization. Requires return type annotation. Not validated.
- `default_factory`: Single-arg form `lambda data: data['prior_field']` for derived defaults (field-order dependent).
- Deprecated fields: `Field(deprecated='msg')` emits `DeprecationWarning` on access.
- Inspect: `Model.model_fields` -> `dict[str, FieldInfo]`, `Model.model_computed_fields`.

## Validators

Key concepts:
- Four types: `AfterValidator` (safest default), `BeforeValidator` (raw input), `PlainValidator` (replaces Pydantic), `WrapValidator` (handler for full control).
- Annotated pattern for reusable validators: `EvenInt = Annotated[int, AfterValidator(is_even)]`.
- `@field_validator`: Decorator targeting specific fields. Modes: `after` (default), `before`, `plain`, `wrap`. Must be `@classmethod`.
- `@model_validator`: Cross-field validation. `mode='after'` receives `self`, `mode='before'` receives raw `Any` data.
- `@validate_call`: Validate function arguments via type annotations.
- Raising errors: Use `ValueError`, `AssertionError`, or `PydanticCustomError`. Never raise `ValidationError` directly.
- `info.data`: Only contains fields defined BEFORE current field (definition order).
- Context: Pass via `model_validate(..., context={})`; read as `info.context` in validators and serializers (`model_dump(context={})`). Always `None` with `Model(...)` direct instantiation.
- Ordering: Before/wrap run right-to-left; after runs left-to-right in `Annotated`.

## Serialization

Key concepts:
- `model_dump()`: To dict. Key params: `mode`, `include`/`exclude`, `by_alias`, `exclude_unset`, `exclude_none`, `serialize_as_any`, `context`.
- `model_dump_json()`: To JSON string. Same params + `indent`.
- Python vs JSON mode: `model_dump()` keeps native types; `model_dump(mode='json')` coerces to JSON-safe types (returns dict, not string).
- Field serializers: `PlainSerializer`/`WrapSerializer` (Annotated, reusable) or `@field_serializer` (decorator, multi-field). One per field.
- Model serializers: `@model_serializer(mode='plain'|'wrap')`.
- SerializeAsAny: Opt-in duck-typing serialization for subclass fields. Per-field annotation or `serialize_as_any=True` runtime flag (global).
- Exclusion: `Field(exclude=True)`, `Field(exclude_if=predicate)`, or `model_dump(exclude={...})`. Field-level `exclude=True` overrides `include`.
- Partial JSON: `from_json(data, allow_partial=True)` for streaming/LLM output. Requires defaults on all fields.

## Types

Key concepts:
- Primitives: `bool`, `int`, `float`, `str`, `bytes` with lax coercion by default. `StrictInt` etc. for no coercion.
- Collections: `list`, `tuple`, `set`, `frozenset`, `deque`, `dict` with item-level validation.
- Constrained types: `PositiveInt`, `NonNegativeFloat`, `constr(pattern=...)` (legacy), `Annotated[int, Field(gt=0)]` (preferred).
- Network: `HttpUrl`, `EmailStr` (needs `email-validator`), `IPvAnyAddress`, DSN types.
- Secret: `SecretStr`, `SecretBytes`, `Secret[T]`. Masked in repr/serialization.
- Special: `Json[T]` (parse JSON string), `ImportString`, `ByteSize`, `OnErrorOmit`, `PaymentCardNumber`.
- Unions: Smart mode (default, best match) | `left_to_right` | discriminated (O(1) via `Literal` tag field).
- Custom types: `__get_pydantic_core_schema__` for full control. `GetPydanticSchema` for inline.
- TypeAdapter: Validate/serialize any type. Instantiate once at module level, reuse. Key methods: `validate_python()`, `validate_json()`, `dump_python()`, `dump_json()` (returns `bytes`), `json_schema()`.

## Configuration

Key concepts:
- `model_config = ConfigDict(...)`: Set on model class. Key options: `strict`, `frozen`, `extra`, `validate_assignment`, `from_attributes`, `alias_generator`.
- Strict mode levels: per-call (`strict=True`), per-field (`Field(strict=True)`), per-model (`ConfigDict(strict=True)`).
- Inheritance: Child merges with parent config, child overrides per-key.
- Propagation: Config does NOT cross Pydantic model boundaries. Does propagate into stdlib TypedDicts/dataclasses.
- Alias generators: `to_pascal`, `to_camel`, `to_snake` from `pydantic.alias_generators`. `AliasGenerator` for separate validation/serialization aliases.
- v2.11+ changes: `validate_by_name`/`validate_by_alias` replace `populate_by_name`. `serialize_by_alias` (default changing to `True` in v3).
- Pydantic Settings: Separate package. Field priority: CLI > init kwargs > env vars > dotenv > secrets > defaults. `env_prefix`, `env_nested_delimiter`, dotenv files, secrets dirs.

### Most-Used ConfigDict Options

```csv
Option,Default,Purpose
strict,False,Disable type coercion
frozen,False,Immutable instances
extra,'ignore','forbid'/'allow'/'ignore' extra fields
validate_assignment,False,Re-validate on attribute set
from_attributes,False,ORM mode
alias_generator,None,Auto-generate aliases
str_strip_whitespace,False,Strip whitespace from strings
validate_default,False,Validate default values
arbitrary_types_allowed,False,Allow non-pydantic field types
ser_json_temporal,'iso8601',Temporal serialization format
```

## JSON Schema

Key concepts:
- `model_json_schema()`: Returns `dict` (not JSON string). Compliant with Draft 2020-12 / OpenAPI 3.1.0.
- Modes: `'validation'` (input schema, default) vs `'serialization'` (output schema). Differ for `Decimal`, computed fields, custom serializers.
- Customization: `Field(title=, description=, examples=, json_schema_extra=)`, `WithJsonSchema` (replaces base schema), `SkipJsonSchema` (exclude from schema).
- `$ref` and `$defs`: Sub-models stored in `$defs`, referenced via `$ref`. `ref_template` for OpenAPI. Modified sub-models get inlined.
- `GenerateJsonSchema`: Subclass for advanced customization. Single-use instances.
- `models_json_schema()`: Multi-model combined schema with shared `$defs`.
- `by_alias=True` is the default for JSON schema generation.

## Errors

Key concepts:
- `ValidationError`: Data validation failure. `.errors()` returns `list[ErrorDetails]`, `.error_count()`, `.json()`.
- `ErrorDetails`: `type` (machine code), `loc` (path tuple), `msg` (human message), `input`, `ctx`, `url`.
- Common types: `missing`, `extra_forbidden`, `*_type` (wrong type), `*_parsing` (string parse fail), `value_error`/`assertion_error` (from validators), `greater_than`/`string_too_long` (constraints).
- Custom messages: Post-process `e.errors()` with a type-to-message mapping. Use `PydanticCustomError` in validators.
- `PydanticUserError`: Definition-time usage error (`TypeError` subclass). Key codes: `class-not-fully-defined`, `decorator-missing-field`, `validator-instance-method`, `config-both`, `removed-kwargs`.
- Two hierarchies: `ValidationError` (bad data, runtime) vs `PydanticUserError` (bad API usage, definition time). Different `except` clauses needed.

## Performance

### Performance Tips

```csv
Technique,Benefit
model_validate_json(),Single Rust pass (JSON + validate)
model_construct(),Zero validation for trusted data
TypeAdapter at module level,Build schema once (never create in loops)
list/dict over Sequence/Mapping,Skip abstract type checks
Discriminated unions,O(1) dispatch vs try-each
TypedDict for nested data,~2.5x faster than nested BaseModel
strict=True,Skip coercion logic
FailFast on sequences,Stop on first error (v2.8+)
Avoid wrap validators,Prevent Python materialization
Any for opaque fields,Skip validation entirely
```

## API Reference

### Key Imports

```python
# Core
from pydantic import BaseModel, RootModel, Field, ConfigDict, TypeAdapter, PrivateAttr, computed_field

# Validators
from pydantic import (
    AfterValidator, BeforeValidator, PlainValidator, WrapValidator,
    field_validator, model_validator, validate_call,
    InstanceOf, SkipValidation,
)

# Serializers
from pydantic import (
    PlainSerializer, WrapSerializer, SerializeAsAny,
    field_serializer, model_serializer,
)

# Aliases
from pydantic import AliasPath, AliasChoices, AliasGenerator
from pydantic.alias_generators import to_pascal, to_camel, to_snake

# JSON Schema
from pydantic import WithJsonSchema
from pydantic.json_schema import SkipJsonSchema, GenerateJsonSchema, models_json_schema

# Types
from pydantic import (
    PositiveInt, NonNegativeInt, StrictStr, StrictInt,
    SecretStr, Json, ImportString, ByteSize, OnErrorOmit, FailFast,
    Discriminator, Tag,
)
from pydantic.networks import HttpUrl, EmailStr, AnyUrl, IPvAnyAddress

# Errors
from pydantic import ValidationError, PydanticUserError
from pydantic_core import PydanticCustomError, PydanticUseDefault, PydanticOmit, from_json

# Settings (separate package)
from pydantic_settings import BaseSettings, SettingsConfigDict
```

## Common Pitfalls

Grouped summary of 152 pitfalls across all topics. Full details in each topic's pitfalls.md.

### Surprising Defaults

```csv
Pitfall,Topic,Fix
Extra fields silently ignored,Models,Set extra='forbid'
Defaults not validated,"Fields, Validators",Set validate_default=True
"Serialization uses field names, not aliases",Serialization,by_alias=True or ConfigDict(serialize_by_alias=True)
Subclass fields silently dropped,Serialization,SerializeAsAny[T] or serialize_as_any=True
Model instances not re-validated,Models,ConfigDict(revalidate_instances='always')
model_copy(update=) skips validation,Models,Validate manually if needed
```

### Validation Gotchas

```csv
Pitfall,Topic,Fix
info.data only has prior fields,Validators,Reorder fields or use @model_validator
Before validators get Any,Validators,Type-check inputs defensively
PlainValidator skips all type checking,Validators,Handle type enforcement yourself
assert stripped by python -O,Validators,Use raise ValueError(...)
Must return value from validators,Validators,Always return v
@classmethod required on decorators,"Validators, Errors",Add @classmethod below @field_validator
```

### Type & Coercion Surprises

```csv
Pitfall,Topic,Fix
bool accepted as int in lax mode,Types,Use StrictInt
JSON strict mode more lenient than Python,"Types, JSON Schema",By design (JSON has fewer native types)
EmailStr requires email-validator,Types,pip install pydantic[email]
TypeAdapter.dump_json() returns bytes,Types,Call .decode()
Smart union mode not guaranteed stable,Types,Use discriminated unions
```

### Serialization Traps

```csv
Pitfall,Topic,Fix
dict(model) doesn't recurse sub-models,Serialization,Use model_dump()
"mode='json' returns dict, not string",Serialization,Use model_dump_json() for strings
Only one serializer per field,Serialization,Combine logic into one
Field(exclude=True) overrides include,Serialization,By design
when_used='json' invisible in Python mode,Serialization,Test with both modes
```

### Schema & Config Issues

```csv
Pitfall,Topic,Fix
"model_json_schema() returns dict, not string",JSON Schema,Call json.dumps()
GenerateJsonSchema is single-use,JSON Schema,New instance per call
Config doesn't propagate across model boundaries,Configuration,Set config on each model
frozen=True doesn't make mutable values immutable,"Models, Config",By design
json_schema_extra callable must mutate in-place,"Fields, JSON Schema",Don't return a new dict
```

### Performance Anti-Patterns

```csv
Pitfall,Topic,Fix
json.loads() + model_validate(),Performance,Use model_validate_json()
Sequence/Mapping abstract types,Performance,Use list/dict
Deeply nested BaseModel hierarchies,Performance,Use TypedDict for data-only
Untagged unions,Performance,Add discriminator field
```

### V1 to V2 Migration

```csv
Deprecated,Replacement
.dict(),.model_dump()
.json(),.model_dump_json()
.parse_obj(),.model_validate()
.parse_raw(),.model_validate_json()
.from_orm(),.model_validate() + from_attributes=True
.schema(),.model_json_schema()
.construct(),.model_construct()
Field(regex=),Field(pattern=)
Field(min_items=),Field(min_length=)
populate_by_name,validate_by_name + validate_by_alias
class Config:,model_config = ConfigDict(...)
json_encoders,@field_serializer / PlainSerializer
```
