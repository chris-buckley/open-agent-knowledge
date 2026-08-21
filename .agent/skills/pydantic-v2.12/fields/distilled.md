# Pydantic v2 -- Fields

## Field() Function

`Field()` customizes model fields: defaults, aliases, constraints, JSON Schema metadata, and more. It returns a `FieldInfo` instance typed as `Any` so it can be assigned to annotated attributes.

```python
from pydantic import BaseModel, Field

class Model(BaseModel):
    name: str = Field(frozen=True)
```

Passing `...` (ellipsis) as default is allowed but discouraged -- it still means required, and confuses type checkers.

### Full Parameter Reference

```csv
Parameter,Type,Purpose
default,Any,Static default value. PydanticUndefined means required.
default_factory,"Callable[[], T] | Callable[[dict[str, Any]], T]",Callable producing defaults. Single-arg form receives already-validated data.
alias,str | None,Name used for both validation and serialization by alias.
alias_priority,int | None,"Controls precedence vs alias generators. 2 = field wins, 1 = generator wins."
validation_alias,str | AliasPath | AliasChoices | None,Alias used only during validation. Overrides alias for validation.
serialization_alias,str | None,Alias used only during serialization. Overrides alias for serialization.
title,str | None,Human-readable title (JSON Schema).
field_title_generator,"Callable[[str, FieldInfo], str] | None",Callable generating titles from field name.
description,str | None,Human-readable description (JSON Schema).
examples,list[Any] | None,Example values (JSON Schema).
exclude,bool | None,Exclude field from serialization output.
exclude_if,"Callable[[Any], bool] | None",Conditionally exclude based on field value.
discriminator,str | Discriminator | None,Field name or Discriminator for tagged unions.
json_schema_extra,"JsonDict | Callable[[JsonDict], None] | None",Extra JSON Schema properties (dict or mutating callable).
frozen,bool | None,Immutable field -- assignment after construction raises error.
validate_default,bool | None,Validate the default value on instantiation. Off by default.
repr,bool,Include field in __repr__. Default True.
deprecated,str | bool | Deprecated | None,Mark field deprecated. String = custom message.
pattern,str | re.Pattern[str] | None,Regex constraint for strings.
strict,bool | None,Enable strict-mode validation for this field.
gt / ge / lt / le,numeric,Numeric bound constraints.
multiple_of,float | None,Numeric multiple-of constraint.
min_length / max_length,int | None,Length constraints for strings/iterables.
max_digits / decimal_places,int | None,Decimal precision constraints.
allow_inf_nan,bool | None,Allow inf/-inf/nan for floats and Decimals.
coerce_numbers_to_str,bool | None,Coerce numbers to str (not in strict mode).
union_mode,"Literal['smart', 'left_to_right']",Union validation strategy.
fail_fast,bool | None,Stop on first error for iterable types.
init,bool | None,Include in dataclass __init__. Dataclasses only.
init_var,bool | None,Init-only variable. Dataclasses only.
kw_only,bool | None,Keyword-only in dataclass constructor. Dataclasses only.
```

## The Annotated Pattern vs Assignment Pattern

Two ways to attach `Field()` metadata:

```python
from typing import Annotated
from pydantic import BaseModel, Field

# Assignment pattern -- type checkers synthesize __init__ correctly for alias/default
class User(BaseModel):
    name: str = Field(alias='username')

# Annotated pattern -- cleaner for constraints; type checkers see the raw type
class Item(BaseModel):
    price: Annotated[float, Field(gt=0)]
```

When to use which:

- Use assignment when setting `default`, `default_factory`, or `alias` -- type checkers understand these.
- Use Annotated for constraints, metadata, and reusable types -- type checkers ignore the metadata.
- `Annotated` allows stacking multiple metadata: `Annotated[str, Field(strict=True), WithJsonSchema({...})]`.
- You can apply `Annotated` to inner types: `list[Annotated[int, Field(gt=0)]]`.

Careful with field vs type metadata placement:

```python
# WRONG -- deprecated applies to Optional wrapper, not the field:
field_bad: Annotated[int, Field(deprecated=True)] | None = None

# CORRECT -- deprecated is inside the full union type:
field_ok: Annotated[int | None, Field(deprecated=True)] = None
```

## Default Values

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = 'John Doe'                              # plain assignment
    age: int = Field(default=20)                        # explicit default
    id: str = Field(default_factory=lambda: 'auto')     # factory (no args)
```

### default_factory with Validated Data

The factory can accept a single `dict` argument containing already-validated fields (based on field ordering):

```python
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    email: EmailStr
    username: str = Field(default_factory=lambda data: data['email'])

User(email='a@b.com').username  # 'a@b.com'
```

The `username` field must be defined after `email` for this to work.

### Validate Default Values

Defaults are NOT validated by default. Enable per-field or model-wide:

```python
class User(BaseModel):
    age: int = Field(default='twelve', validate_default=True)  # raises ValidationError
```

Or model-wide via `model_config = ConfigDict(validate_default=True)`.

### Mutable Default Values

Unlike dataclasses, Pydantic deep-copies mutable defaults per instance automatically:

```python
class Model(BaseModel):
    items: list[dict[str, int]] = [{}]

m1 = Model()
m1.items[0]['a'] = 1
Model().items  # [{}] -- not contaminated
```

## Field Aliases

Three alias parameters control validation and serialization naming:

```csv
Parameter,Affects,Type
alias,Both validation and serialization,str
validation_alias,Validation only,str | AliasPath | AliasChoices
serialization_alias,Serialization only,str
```

`validation_alias` overrides `alias` for validation. `serialization_alias` overrides `alias` for serialization.

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(alias='username')

user = User(username='johndoe')
user.model_dump(by_alias=True)   # {'username': 'johndoe'}
```

### AliasPath -- Nested Data Access

```python
from pydantic import BaseModel, Field, AliasPath

class User(BaseModel):
    first_name: str = Field(validation_alias=AliasPath('names', 0))
    last_name: str = Field(validation_alias=AliasPath('names', 1))

User.model_validate({'names': ['John', 'Doe']})
```

`AliasPath` accepts strings (dict keys) and ints (list indices) as path segments.

### AliasChoices -- Multiple Accepted Names

```python
from pydantic import BaseModel, Field, AliasChoices

class User(BaseModel):
    first_name: str = Field(validation_alias=AliasChoices('first_name', 'fname'))
```

Combine with `AliasPath`:

```python
from pydantic import BaseModel, Field, AliasPath, AliasChoices

class User(BaseModel):
    name: str = Field(
        validation_alias=AliasChoices('name', AliasPath('data', 'name'))
    )
```

### AliasGenerator -- Model-Wide Alias Generation

```python
from pydantic import AliasGenerator, BaseModel, ConfigDict

class Tree(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=lambda s: s.upper(),
            serialization_alias=lambda s: s.title(),
        )
    )
    age: int
    height: float

t = Tree.model_validate({'AGE': 12, 'HEIGHT': 1.2})
t.model_dump(by_alias=True)  # {'Age': 12, 'Height': 1.2}
```

Built-in generators: `pydantic.alias_generators.to_pascal`, `to_camel`, `to_snake`.

### Alias Precedence

- Field-level alias overrides generator-generated alias by default.
- `alias_priority=2`: field alias wins (default when alias is set).
- `alias_priority=1`: generator overrides field alias.

### Alias Configuration

Validation (ConfigDict or runtime):
- `validate_by_alias` (default `True`): accept aliases during validation.
- `validate_by_name` (default `False`): accept field names during validation.
- Cannot set both to `False`.

Serialization:
- `serialize_by_alias` (ConfigDict, default `False`): serialize using aliases.
- `model_dump(by_alias=True)` / `model_dump_json(by_alias=True)`: runtime override.

## Field Constraints

### Numeric Constraints

```python
from decimal import Decimal
from pydantic import BaseModel, Field

class Model(BaseModel):
    positive: int = Field(gt=0)
    bounded: float = Field(ge=0.0, le=100.0)
    precise: Decimal = Field(max_digits=5, decimal_places=2)
    step: int = Field(multiple_of=5)
```

```csv
Constraint,Meaning
gt,Greater than
ge,Greater than or equal
lt,Less than
le,Less than or equal
multiple_of,Must be a multiple of this value
allow_inf_nan,Allow inf/-inf/nan (float/Decimal)
max_digits,Max total digits (Decimal)
decimal_places,Max decimal places (Decimal)
```

### String Constraints

```python
class Model(BaseModel):
    short: str = Field(max_length=3)
    code: str = Field(pattern=r'^[A-Z]{3}$')
```

```csv
Constraint,Meaning
min_length,Minimum length
max_length,Maximum length
pattern,Regex pattern (str or compiled)
```

### Collection Constraints

`min_length` and `max_length` also apply to lists, sets, tuples, and other iterables.

## Strict Fields

Per-field strict mode rejects type coercion:

```python
class User(BaseModel):
    name: str = Field(strict=True)   # 'John' OK, 123 rejected
    age: int = Field(strict=False)   # '42' coerced to 42
```

## Discriminator -- Tagged Unions

### By Field Name

```python
from typing import Literal, Union
from pydantic import BaseModel, Field

class Cat(BaseModel):
    pet_type: Literal['cat']
    age: int

class Dog(BaseModel):
    pet_type: Literal['dog']
    age: int

class Model(BaseModel):
    pet: Union[Cat, Dog] = Field(discriminator='pet_type')

Model.model_validate({'pet': {'pet_type': 'cat', 'age': 12}})
# pet=Cat(pet_type='cat', age=12)
```

### By Custom Discriminator Function

When union members have different discriminator field names:

```python
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Discriminator, Field, Tag

class Cat(BaseModel):
    pet_type: Literal['cat']
    age: int

class Dog(BaseModel):
    pet_kind: Literal['dog']
    age: int

def pet_discriminator(v):
    if isinstance(v, dict):
        return v.get('pet_type', v.get('pet_kind'))
    return getattr(v, 'pet_type', getattr(v, 'pet_kind', None))

class Model(BaseModel):
    pet: Union[Annotated[Cat, Tag('cat')], Annotated[Dog, Tag('dog')]] = Field(
        discriminator=Discriminator(pet_discriminator)
    )
```

## Excluding Fields from Serialization

```python
class User(BaseModel):
    name: str
    age: int = Field(exclude=True)

User(name='John', age=42).model_dump()  # {'name': 'John'}
```

Conditional exclusion:

```python
class User(BaseModel):
    name: str
    secret: str | None = Field(exclude_if=lambda v: v is None)
```

## Frozen (Immutable) Fields

```python
class User(BaseModel):
    name: str = Field(frozen=True)
    age: int

user = User(name='John', age=42)
user.name = 'Jane'  # raises ValidationError: "Field is frozen"
```

## Deprecated Fields

Three forms:

```python
from typing import Annotated
from typing_extensions import deprecated
from pydantic import BaseModel, Field

class Model(BaseModel):
    # String message:
    a: Annotated[int, Field(deprecated='Use field_b instead')]

    # Boolean (generic message):
    b: Annotated[int, Field(deprecated=True)]

    # @deprecated decorator instance:
    c: Annotated[int, deprecated('Use field_b instead')]
```

Effects:
- Runtime `DeprecationWarning` when accessing the field.
- `"deprecated": true` in JSON Schema output.

To suppress warnings in validators:

```python
import warnings
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

class Model(BaseModel):
    old: int = Field(deprecated='Use new instead')

    @model_validator(mode='after')
    def fix(self) -> Self:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.old = self.old * 2
        return self
```

## Customizing JSON Schema Per-Field

Parameters that only affect JSON Schema generation:

```python
class Model(BaseModel):
    name: str = Field(
        title='Full Name',
        description='The user full name',
        examples=['John Doe', 'Jane Doe'],
        json_schema_extra={'x-custom': True},
    )
```

`json_schema_extra` accepts a dict (merged into schema) or a `Callable[[JsonDict], None]` (mutates schema dict in-place).

## The computed_field Decorator

Include `@property` or `@cached_property` in serialization and JSON Schema:

```python
from pydantic import BaseModel, computed_field

class Box(BaseModel):
    width: float
    height: float
    depth: float

    @computed_field
    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth

b = Box(width=1, height=2, depth=3)
b.model_dump()  # {'width': 1.0, 'height': 2.0, 'depth': 3.0, 'volume': 6.0}
```

Key points:
- Must use `@property` (or `@cached_property`) below `@computed_field`.
- Return type annotation is required.
- Appears as `readOnly` in JSON Schema (serialization mode).
- Pydantic does NOT validate the property return value or manage cache invalidation.
- Supports `alias`, `title`, `description`, `deprecated`, `repr`, `return_type`, `json_schema_extra`, `examples`.

Deprecating computed fields:

```python
from typing_extensions import deprecated
from pydantic import BaseModel, computed_field

class Box(BaseModel):
    width: float

    @computed_field
    @property
    @deprecated("'area' is deprecated")
    def area(self) -> float:
        return self.width ** 2
```

## Inspecting Model Fields

### model_fields

`Model.model_fields` returns `dict[str, FieldInfo]`:

```python
from typing import Annotated
from pydantic import BaseModel, Field, WithJsonSchema

class Model(BaseModel):
    a: Annotated[int, Field(gt=1), WithJsonSchema({'extra': 'data'}), Field(alias='b')] = 1

info = Model.model_fields['a']
info.annotation   # <class 'int'>
info.alias        # 'b'
info.metadata     # [Gt(gt=1), WithJsonSchema(json_schema={'extra': 'data'}, mode=None)]
```

### model_computed_fields

`Model.model_computed_fields` returns `dict[str, ComputedFieldInfo]`.

### FieldInfo Key Attributes

```csv
Attribute,Description
.annotation,The resolved type annotation
.default,Default value (PydanticUndefined if required)
.default_factory,Default factory callable or None
.alias,The alias string or None
.validation_alias,Validation alias (str/AliasPath/AliasChoices)
.serialization_alias,Serialization alias string
.metadata,List of constraint/metadata objects from Annotated
.is_required(),True if no default or default_factory
.get_default(call_default_factory=True),"Retrieve default, optionally calling factory"
```

### FieldInfo.asdict()

Returns `{'annotation': ..., 'metadata': [...], 'attributes': {...}}`.

## Field Representation

Control `__repr__` inclusion:

```python
class User(BaseModel):
    name: str = Field(repr=True)
    age: int = Field(repr=False)

print(User(name='John', age=42))  # name='John'
```
