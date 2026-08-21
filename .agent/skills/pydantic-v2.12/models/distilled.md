# Pydantic v2 Models

## BaseModel Fundamentals

Models are classes inheriting from `BaseModel` with annotated attributes as fields. Instantiation validates data; raises `ValidationError` on failure.

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    id: int
    name: str = 'Jane Doe'
    model_config = ConfigDict(str_max_length=10)

user = User(id='123')        # coerces '123' -> 123
assert user.id == 123         # access as attributes
assert user.name == 'Jane Doe'
user.id = 321                 # mutable by default
```

Fields are defined as type-annotated class attributes. Required fields have no default. Optional fields provide a default value or use `Field()`.

Data conversion (coercion) happens by default -- `int('123')` succeeds, tuples become lists, etc. Use `strict=True` or `ConfigDict(strict=True)` to disable coercion.

## Model Methods and Properties

### Serialization

```python
# To dict
d = user.model_dump()
d = user.model_dump(exclude_unset=True, exclude_none=True, by_alias=True)

# To JSON string
j = user.model_dump_json(indent=2)
```

`model_dump()` key parameters: `mode` (`'python'`/`'json'`), `include`, `exclude`, `by_alias`, `exclude_unset`, `exclude_defaults`, `exclude_none`, `round_trip`, `serialize_as_any`.

### Validation (Class Methods)

```python
# From dict
m = User.model_validate({'id': 123, 'name': 'James'})

# From JSON string/bytes
m = User.model_validate_json('{"id": 123, "name": "James"}')

# From string-keyed dict (coerces strings)
m = User.model_validate_strings({'id': '123', 'name': 'James'})
```

All `model_validate_*` methods accept `strict`, `extra`, `context`, `by_alias`, `by_name` parameters for fine-grained control.

### Construction Without Validation

```python
m = User.model_construct(id=123, name='trusted')
```

Skips all validation. Use only with pre-validated/trusted data. Default values still applied for missing fields. Does NOT call `__init__` or custom validators.

### JSON Schema

```python
schema = User.model_json_schema()
schema = User.model_json_schema(mode='serialization', by_alias=True)
```

### Copying

```python
copy = m.model_copy()                          # shallow copy
copy = m.model_copy(update={'name': 'New'})    # shallow + update (no validation on update)
copy = m.model_copy(deep=True)                 # deep copy
```

### Schema Rebuild

```python
class Foo(BaseModel):
    x: 'Bar'

class Bar(BaseModel):
    pass

Foo.model_rebuild()  # resolves forward ref 'Bar'
```

Call `model_rebuild()` after all referenced types are defined. Required for forward references and recursive models.

### Post-Init Hook

```python
from typing import Any

class MyModel(BaseModel):
    id: int

    def model_post_init(self, context: Any) -> None:
        # Called after validation, all fields available
        ...
```

### Instance Properties

```csv
Property,Type,Description
model_extra,"dict[str, Any] | None",Extra fields (when extra='allow')
model_fields_set,set[str],Fields explicitly provided at init
```

### Class Properties

```csv
Property,Type,Description
model_fields,"dict[str, FieldInfo]",Field name to FieldInfo mapping
model_computed_fields,"dict[str, ComputedFieldInfo]",Computed field mapping
model_config,ConfigDict,Model configuration
```

## RootModel

For models wrapping a single root value (lists, dicts, primitives) instead of named fields.

```python
from pydantic import RootModel

# Inline parametrization
Pets = RootModel[list[str]]
pets = Pets(['dog', 'cat'])
print(pets.root)            # ['dog', 'cat']
print(pets.model_dump())    # ['dog', 'cat']

# Subclass with custom methods
class Pets(RootModel[list[str]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]
```

`RootModel` accepts root value as first positional arg or via `model_validate()`. The value is stored in the `.root` attribute.

`model_construct(root=value)` accepts the root positionally.

## Generic Models

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

DataT = TypeVar('DataT')

class Response(BaseModel, Generic[DataT]):
    data: DataT

# Parametrize with concrete types
print(Response[int](data=1))           # data=1
print(Response[str](data='value'))     # data='value'
```

Python 3.12+ syntax:
```python
class Response[DataT](BaseModel):
    data: DataT
```

Key behaviors:
- Parametrized classes are cached at runtime (minimal overhead).
- Subclasses preserving generics must also inherit `Generic[T]`.
- Unparameterized type variables: uses bound/constraint/default if set, else `Any`.
- Use `model_parametrized_name()` to customize generated class names.
- Do NOT use parametrized generics in `isinstance()` checks.

Partial parametrization:
```python
class Base(BaseModel, Generic[TypeX, TypeY]):
    x: TypeX
    y: TypeY

class Child(Base[int, TypeY], Generic[TypeY, TypeZ]):
    z: TypeZ
```

## Dynamic Model Creation

```python
from pydantic import BaseModel, Field, create_model

# Simple: field=type or field=(type, default)
DynModel = create_model('DynModel', foo=str, bar=(int, 123))

# With Field(), aliases, private attrs
from pydantic import PrivateAttr
DynModel = create_model(
    'DynModel',
    foo=(str, Field(alias='FOO')),
    _private=(int, PrivateAttr(default=1)),
)

# Extending a base model
class FooModel(BaseModel):
    foo: str

BarModel = create_model('BarModel', apple=(str, 'russet'), __base__=FooModel)

# Adding validators
from pydantic import field_validator

def alphanum(cls, v):
    assert v.isalnum(), 'must be alphanumeric'
    return v

UserModel = create_model(
    'UserModel',
    username=(str, ...),
    __validators__={'check': field_validator('username')(alphanum)},
)
```

Special kwargs: `__config__` (ConfigDict), `__base__` (parent model), `__validators__` (validator dict).

## Pydantic Dataclasses vs BaseModel

Pydantic dataclasses add validation to stdlib-style dataclasses. They are NOT a replacement for `BaseModel` -- they lack `model_dump`, `model_validate`, etc. Use `TypeAdapter` to get those methods.

```python
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict

@dataclass
class User:
    id: int
    name: str = 'John Doe'

# Config via decorator arg or class attribute
@dataclass(config=ConfigDict(strict=True))
class StrictUser:
    id: int

@dataclass
class ConfigUser:
    id: int
    __pydantic_config__ = ConfigDict(validate_assignment=True)
```

Key differences from BaseModel:
- No `model_dump()`, `model_validate()`, etc. (wrap with `TypeAdapter` if needed).
- `extra='allow'` supported but extra fields omitted from `__repr__`.
- `__post_init__()` called between `before` and `after` model validators.
- `rebuild_dataclass()` replaces `model_rebuild()`.
- `is_pydantic_dataclass()` to distinguish from stdlib dataclasses.
- Stdlib dataclasses used as BaseModel field types get validated automatically.
- Both `pydantic.Field()` and `dataclasses.field()` work for field definitions.

## Nested Models

Models used as field type annotations create hierarchical validation. Dicts are auto-converted to the nested model type.

```python
class Address(BaseModel):
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    address: Address

# Dict auto-converted to Address
u = User(name='Alice', address={'city': 'NYC', 'zip_code': '10001'})
```

Self-referencing models are supported via forward annotations (string refs) and `model_rebuild()`.

## Extra Data Handling

Controlled by `model_config['extra']`:

```csv
Value,Behavior
'ignore' (default),Extra fields silently dropped
'forbid',Raises ValidationError on extra fields
'allow',Extra fields stored in __pydantic_extra__ dict and included in model_dump()
```

```python
class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')
    x: int

class Flexible(BaseModel):
    model_config = ConfigDict(extra='allow')
    x: int

m = Flexible(x=1, y='extra')
assert m.model_extra == {'y': 'extra'}
```

The `model_validate_*()` methods accept an `extra` parameter to override the model config per call.

## Private Attributes and Class Variables

### Private Attributes

Names with leading underscore become private attributes -- not validated, not in schema, not set via `__init__`.

```python
from datetime import datetime
from pydantic import BaseModel, PrivateAttr

class MyModel(BaseModel):
    _created_at: datetime = PrivateAttr(default_factory=datetime.now)
    _secret: str = PrivateAttr(default='hidden')

m = MyModel()
print(m._created_at)  # set via default_factory
```

Rules:
- Must start with single underscore.
- Dunder names (`__attr__`) are completely ignored.
- Use `PrivateAttr(default=...)` or `PrivateAttr(default_factory=...)`.
- Can also be set in `model_post_init()`.

### Class Variables

Annotated with `ClassVar` -- treated as class-level constants, not fields.

```python
from typing import ClassVar
from pydantic import BaseModel

class Config(BaseModel):
    MAX_RETRIES: ClassVar[int] = 3
    name: str

m = Config(name='test')
assert 'MAX_RETRIES' not in m.model_dump()
assert Config.MAX_RETRIES == 3
```

## Faux Immutability (Frozen)

```python
from pydantic import BaseModel, ConfigDict

class Immutable(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    tags: list[str]

m = Immutable(name='test', tags=['a'])
m.name = 'other'    # raises ValidationError: Instance is frozen
m.tags.append('b')  # WORKS -- frozen only prevents attribute reassignment
```

`frozen=True` prevents attribute reassignment but does NOT make mutable field values (dicts, lists) truly immutable.

## Abstract Base Classes

```python
import abc
from pydantic import BaseModel

class Animal(BaseModel, abc.ABC):
    name: str

    @abc.abstractmethod
    def speak(self) -> str: ...

class Dog(Animal):
    def speak(self) -> str:
        return f'{self.name} says woof'
```

## Model Signature and Pattern Matching

### Signature

Model `__init__` signature is auto-generated from fields. Useful for introspection (FastAPI, hypothesis).

```python
import inspect
from pydantic import BaseModel, Field

class M(BaseModel):
    id: int
    name: str = Field(alias='user_name')

print(inspect.signature(M))
# (*, id: int, user_name: str) -> None
```

Aliases used in signature when they are valid Python identifiers. `**data` added when `extra='allow'`.

### Structural Pattern Matching (Python 3.10+)

```python
match pet:
    case Pet(species='dog', name=dog_name):
        print(f'{dog_name} is a dog')
    case _:
        print('No match')
```

## Arbitrary Class Instances (ORM Mode)

Validate from object attributes instead of dicts:

```python
class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

orm_obj = SomeOrmClass(id=1, name='Alice')
m = UserModel.model_validate(orm_obj)
# or per-call: UserModel.model_validate(orm_obj, from_attributes=True)
```

## Attribute Copies

Arguments passed to the constructor are copied during validation. The original input is not mutated. This behavior can be controlled with `model_config['revalidate_instances']`.

## Field Ordering

Field order is preserved in: JSON Schema output, validation errors, serialization output. Fields appear in declaration order regardless of how data is provided.
