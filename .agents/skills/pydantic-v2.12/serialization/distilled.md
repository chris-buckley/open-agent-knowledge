# Pydantic v2 -- Serialization

## model_dump() and model_dump_json()

`model_dump()` returns a Python dict. `model_dump_json()` returns a JSON-encoded string.

Both accept the same parameter set:

```csv
Parameter,Type,Default,Effect
mode,'python' | 'json','python',"Python keeps native types (tuples, sets); JSON coerces to JSON-safe types (lists). Only applies to model_dump()."
include,set | dict | None,None,Whitelist of fields to include.
exclude,set | dict | None,None,Blacklist of fields to exclude.
by_alias,bool,False,Use serialization_alias (or alias) as keys.
exclude_unset,bool,False,Omit fields not explicitly set during instantiation (tracked via model_fields_set).
exclude_defaults,bool,False,Omit fields whose value equals the default (== comparison).
exclude_none,bool,False,Omit fields whose value is None.
round_trip,bool,False,Serialize in a way that allows lossless round-trip (validate -> dump -> validate).
warnings,bool | 'none' | 'warn' | 'error',True,Control serialization warnings.
context,Any | None,None,Arbitrary context dict passed to serializer functions via info.context.
serialize_as_any,bool,False,"Enable duck-typing serialization for all fields (serialize based on runtime type, not annotation)."
```

`model_dump_json()` additionally accepts `indent: int | None` for pretty-printing.

```python
from pydantic import BaseModel, Field

class M(BaseModel):
    foo: str = Field(serialization_alias='f')
    bar: tuple[int, ...] = ()

m = M(foo='hello', bar=(1, 2))

m.model_dump()                    # {'foo': 'hello', 'bar': (1, 2)}
m.model_dump(mode='json')         # {'foo': 'hello', 'bar': [1, 2]}
m.model_dump(by_alias=True)       # {'f': 'hello', 'bar': (1, 2)}
m.model_dump_json(indent=2)       # pretty JSON string
```

## Python Mode vs JSON Mode

- Python mode (`model_dump()` default): values keep their Python types. A `tuple` stays a `tuple`, a `set` stays a `set`, sub-models become dicts recursively.
- JSON mode (`model_dump_json()`, or `model_dump(mode='json')`): values are coerced to JSON-compatible types. Tuples become lists, datetimes become ISO strings, UUIDs become strings, sets become lists. Unsupported types raise `PydanticSerializationError`.

`model_dump(mode='json')` produces a Python dict with JSON-compatible values (useful when you need a dict but want JSON-safe types).

## Field Serializers

Only one serializer can be defined per field. Two modes exist: plain and wrap.

### PlainSerializer / WrapSerializer (Annotated pattern)

Reusable, type-level serializers via `Annotated`:

```python
from typing import Annotated
from pydantic import BaseModel, PlainSerializer, WrapSerializer, SerializerFunctionWrapHandler

# Plain: replaces default serialization entirely
DoubleInt = Annotated[int, PlainSerializer(lambda v: v * 2)]

class M(BaseModel):
    x: DoubleInt  # model_dump() -> {'x': 4} when x=2

# Wrap: calls handler to get default, then modifies
PlusOne = Annotated[int, WrapSerializer(lambda v, handler: handler(v) + 1)]
```

PlainSerializer constructor:
```python
PlainSerializer(func, *, return_type=PydanticUndefined, when_used='always')
```

WrapSerializer constructor:
```python
WrapSerializer(func, *, return_type=PydanticUndefined, when_used='always')
```

`when_used` values: `'always'`, `'unless-none'`, `'json'`, `'json-unless-none'`.

Key benefit: the `Annotated` pattern makes serializers reusable across models and composable in nested types like `list[DoubleInt]`.

### @field_serializer Decorator

Applied to instance methods or static methods. Key benefit: can target multiple fields at once.

```python
from pydantic import BaseModel, field_serializer, SerializerFunctionWrapHandler

class M(BaseModel):
    f1: str
    f2: str

    # Plain mode (default): replaces default serialization
    @field_serializer('f1', 'f2', mode='plain')
    def capitalize(self, value: str) -> str:
        return value.capitalize()
```

```python
class M2(BaseModel):
    number: int

    # Wrap mode: gets handler for default serialization
    @field_serializer('number', mode='wrap')
    def ser(self, value, handler: SerializerFunctionWrapHandler) -> int:
        return handler(value) + 1
```

Supported signatures (instance or static):
- `(self, value: Any, info: FieldSerializationInfo)` -- plain
- `(self, value: Any, nxt: SerializerFunctionWrapHandler, info: FieldSerializationInfo)` -- wrap
- `(value: Any, info: SerializationInfo)` -- plain, static/classmethod
- `(value: Any, nxt: SerializerFunctionWrapHandler, info: SerializationInfo)` -- wrap, static/classmethod

Parameters:

```csv
Parameter,Default,Description
*fields,required,Field names. Pass '*' to match all fields (including subclass fields).
mode,'plain','plain' or 'wrap'.
return_type,inferred,Optional explicit return type; builds extra validation on serialized value.
when_used,'always',"'always', 'unless-none', 'json', 'json-unless-none'."
check_fields,None,Set False to skip verifying field names exist (useful on base classes).
```

## Model Serializers

Customize serialization for the entire model via `@model_serializer`.

### Plain mode

Replaces default serialization entirely. Return value becomes the dump result.

```python
from pydantic import BaseModel, model_serializer

class User(BaseModel):
    username: str
    password: str

    @model_serializer(mode='plain')
    def serialize(self) -> str:
        return f'{self.username}-{self.password}'

User(username='foo', password='bar').model_dump()  # 'foo-bar'
```

### Wrap mode

Receives a handler that runs the default serialization. Modify the result before returning.

```python
from pydantic import BaseModel, SerializerFunctionWrapHandler, model_serializer

class User(BaseModel):
    username: str
    password: str

    @model_serializer(mode='wrap')
    def serialize(self, handler: SerializerFunctionWrapHandler) -> dict:
        data = handler(self)
        data['fields'] = list(data)
        return data
```

Supported signatures:

Plain mode:
- `(self)`
- `(self, info: SerializationInfo)`

Wrap mode:
- `(self, nxt: SerializerFunctionWrapHandler)`
- `(self, nxt: SerializerFunctionWrapHandler, info: SerializationInfo)`

Parameters: `mode='plain'` (default), `when_used='always'`, `return_type` (inferred if omitted).

## SerializationInfo

Both field and model serializer callables can optionally accept an `info` parameter providing runtime context:

```csv
Property,Description
info.mode,'python' or 'json' -- the current serialization mode.
info.context,User-defined context dict passed via model_dump(context=...).
info.by_alias,Whether by_alias=True was passed.
info.exclude_unset,Whether exclude_unset=True was passed.
info.exclude_defaults,Whether exclude_defaults=True was passed.
info.exclude_none,Whether exclude_none=True was passed.
info.serialize_as_any,Whether serialize_as_any=True was passed.
info.include,The include parameter value.
info.exclude,The exclude parameter value.
info.field_name,"(field serializers only, via FieldSerializationInfo) The current field name."
```

## Serialization Context

Pass arbitrary data to serializers at call time:

```python
from pydantic import BaseModel, FieldSerializationInfo, field_serializer

class M(BaseModel):
    text: str

    @field_serializer('text', mode='plain')
    @classmethod
    def clean(cls, v: str, info: FieldSerializationInfo) -> str:
        if isinstance(info.context, dict):
            stopwords = info.context.get('stopwords', set())
            v = ' '.join(w for w in v.split() if w.lower() not in stopwords)
        return v

m = M(text='This is an example document')
m.model_dump()                                          # no filtering
m.model_dump(context={'stopwords': ['this', 'is', 'an']})  # 'example document'
```

## SerializeAsAny and serialize_as_any

By default, Pydantic serializes a field value using the annotation's schema, not the runtime value's actual type. Subclass fields are truncated to the parent's fields.

### SerializeAsAny annotation (field level)

Opt specific fields into duck-typing serialization:

```python
from pydantic import BaseModel, SerializeAsAny

class User(BaseModel):
    name: str

class UserLogin(User):
    password: str

class Outer(BaseModel):
    as_any: SerializeAsAny[User]   # serializes all runtime fields
    as_user: User                  # serializes only User's fields

user = UserLogin(name='pydantic', password='hunter2')
Outer(as_any=user, as_user=user).model_dump()
# {'as_any': {'name': 'pydantic', 'password': 'hunter2'}, 'as_user': {'name': 'pydantic'}}
```

Validation behavior is identical to the base type; only serialization changes. Static type checkers see the base type.

### serialize_as_any runtime setting

Applies duck-typing serialization to all fields for a single call:

```python
outer.model_dump(serialize_as_any=True)   # all subclass fields included
outer.model_dump(serialize_as_any=False)  # strict annotation-based serialization
```

Prefer `SerializeAsAny` on specific fields over the runtime flag when only certain fields need it.

## Field Inclusion and Exclusion

### At the field level

Use `Field(exclude=True)` to permanently exclude a field, or `Field(exclude_if=...)` with a predicate:

```python
from pydantic import BaseModel, Field

class Transaction(BaseModel):
    id: int
    private_id: int = Field(exclude=True)
    value: int = Field(ge=0, exclude_if=lambda v: v == 0)

Transaction(id=1, private_id=2, value=0).model_dump()  # {'id': 1}
```

Field-level `exclude=True` takes priority over `include` in serialization method parameters.

### At the method level (include / exclude parameters)

Pass `set` or `dict` to `model_dump()` / `model_dump_json()`:

```python
t.model_dump(exclude={'user', 'value'})                           # set: exclude whole fields
t.model_dump(exclude={'user': {'username', 'password'}, 'value': True})  # dict: nested exclusion
t.model_dump(include={'id': True, 'user': {'id'}})                # include specific nested fields
```

Sequences and dicts: use integer keys (including negative indices) or `'__all__'` to target items:

```python
user.model_dump(exclude={'hobbies': {-1: {'info'}}})          # exclude info from last hobby
user.model_dump(exclude={'hobbies': {'__all__': {'info'}}})   # exclude info from all hobbies
```

### Value-based exclusion

```csv
Parameter,Effect
exclude_unset=True,Omit fields not explicitly provided during instantiation (uses model_fields_set).
exclude_defaults=True,Omit fields whose value == the default.
exclude_none=True,Omit fields with None values.
```

Note: setting a field after instantiation adds it to `model_fields_set`, so `exclude_unset` will include it.

## Iterating Over Models

Models support iteration yielding `(field_name, field_value)` pairs. Sub-models are not recursively converted:

```python
for name, value in model:
    print(name, value)

dict(model)  # {'field': value, ...} -- sub-models stay as model instances
```

`RootModel` iteration yields `{'root': <value>}`.

## Pickling Support

Pydantic models support `pickle.dumps()` and `pickle.loads()` out of the box.

## JSON Parsing (model_validate_json)

`model_validate_json(json_data)` parses a JSON string directly into a model. Uses `jiter` (fast Rust-based parser) internally.

```python
from datetime import date
from pydantic import BaseModel, ConfigDict

class Event(BaseModel):
    model_config = ConfigDict(strict=True)
    when: date
    where: tuple[int, int]

Event.model_validate_json('{"when": "1987-01-28", "where": [51, -1]}')
# Event(when=date(1987, 1, 28), where=(51, -1))
```

In strict mode, `model_validate_json` accepts JSON strings for date/tuple types that `model_validate` (Python dict input) would reject. This is because JSON parsing applies JSON-to-Python coercion rules that differ from Python-to-Python strict validation.

### Partial JSON parsing

Via `pydantic_core.from_json(data, allow_partial=True)` -- useful for streaming/LLM outputs:

```python
from pydantic_core import from_json
from pydantic import BaseModel

result = from_json('["aa", "bb", "c', allow_partial=True)  # ['aa', 'bb']

class Dog(BaseModel):
    breed: str
    name: str
    friends: list = []

Dog.model_validate(from_json('{"breed": "lab", "name": "fluffy", "friends": ["buddy"', allow_partial=True))
```

For reliable partial parsing, give all fields default values.

### String caching

`cache_strings` setting (model config or `from_json`): `True`/`'all'` (default), `'keys'`, `False`/`'none'`. Caches strings under 64 chars in a 16K-entry cache for performance at slight memory cost.

## TypeAdapter Equivalents

For non-model types, use `TypeAdapter`:
- `TypeAdapter(T).dump_python(value)` -- equivalent to `model_dump()`
- `TypeAdapter(T).dump_json(value)` -- equivalent to `model_dump_json()`
- `TypeAdapter(T).validate_json(json_str)` -- equivalent to `model_validate_json()`
