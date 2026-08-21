# Pydantic v2 Types -- Distilled Reference

## Standard Library Types

Pydantic validates all common Python built-in and stdlib types. By default, Pydantic operates in lax mode (coerces compatible inputs). Strict mode rejects non-exact types.

### Primitives

```csv
Type,Lax accepts,Strict accepts,Constraints
bool,"bool, int (0/1), float (0.0/1.0), str (true/false/yes/no/on/off/t/f/y/n), Decimal (0/1)",bool only,--
int,"int, float (exact), str (numeric), bytes (numeric), bool, Decimal (exact)",int only (bool forbidden),"gt, ge, lt, le, multiple_of"
float,"float, int, str (numeric), bytes (numeric), bool, Decimal",float or int (bool forbidden),"gt, ge, lt, le, multiple_of, allow_inf_nan"
str,"str, bytes/bytearray (UTF-8), enum .value",str only,"min_length, max_length, pattern, strip_whitespace, to_upper, to_lower"
bytes,"bytes, bytearray, str",bytes only (JSON: str),"min_length, max_length"
```

### Collections

```csv
Type,Lax accepts,Strict accepts
list[T],"list, tuple, set, frozenset, deque, dict_keys/values",list only (JSON: array)
"tuple[T, ...]",Same iterables as list,tuple only (JSON: array)
set[T],Same iterables as list,set only (JSON: array)
frozenset[T],Same iterables as list,frozenset only (JSON: array)
deque[T],Same iterables as list,deque only (JSON: array)
"dict[K, V]","dict, Mapping with .items()",dict only (JSON: object)
```

Collection constraints: `min_length`, `max_length` via `Field()` or `Len()` from `annotated_types`.

### Date/Time

```csv
Type,Lax accepts,Strict,Notes
datetime,"datetime, date, str, int/float (epoch), bytes",datetime only,JSON: str always accepted in strict
date,"date, datetime (exact), str, int/float (epoch)",date only,Format: YYYY-MM-DD
time,"time, str, int/float (seconds)",time only,Format: HH:MM:SS.ffffff
timedelta,"timedelta, str (ISO8601), int/float (seconds)",timedelta only,
```

### Other stdlib types

- `Decimal` -- supports `gt`, `ge`, `lt`, `le`, `max_digits`, `decimal_places`
- `UUID` -- accepts `str` or `UUID` instance; version-constrained via `UUID1`..`UUID8`
- `Path` -- accepts `str` or `Path`; see `FilePath`, `DirectoryPath`, `NewPath`
- `Enum` -- validates by value; `IntEnum` validated as integer subtype
- `Literal['a', 'b']` -- restricts to exact values
- `Pattern` (compiled regex) -- accepts `str` or `Pattern`
- `IPv4Address`, `IPv6Address`, `IPv4Network`, `IPv6Network`, `IPv4Interface`, `IPv6Interface`
- `Callable` -- Python only; checks `callable()` returns `True`
- `Type[X]` -- validates that input is a subclass of `X`
- `Any` -- accepts anything, no validation
- `None` / `type(None)` -- only `None` accepted

## Pydantic Constrained Types (Annotated Aliases)

These are `Annotated[base, constraint]` aliases. Import from `pydantic`:

### Numeric

```csv
Type,Definition,Constraint
PositiveInt,"Annotated[int, Gt(0)]",> 0
NegativeInt,"Annotated[int, Lt(0)]",< 0
NonPositiveInt,"Annotated[int, Le(0)]",<= 0
NonNegativeInt,"Annotated[int, Ge(0)]",>= 0
PositiveFloat,"Annotated[float, Gt(0)]",> 0
NegativeFloat,"Annotated[float, Lt(0)]",< 0
NonPositiveFloat,"Annotated[float, Le(0)]",<= 0
NonNegativeFloat,"Annotated[float, Ge(0)]",>= 0
FiniteFloat,"Annotated[float, AllowInfNan(False)]",No inf/nan
```

### Strict Types

```csv
Type,Definition
StrictBool,"Annotated[bool, Strict()]"
StrictInt,"Annotated[int, Strict()]"
StrictFloat,"Annotated[float, Strict()]"
StrictStr,"Annotated[str, Strict()]"
StrictBytes,"Annotated[bytes, Strict()]"
```

### UUID Versions

`UUID1`, `UUID3`, `UUID4`, `UUID5`, `UUID6`, `UUID7`, `UUID8` -- each is `Annotated[UUID, UuidVersion(N)]`.

### Path Types

```csv
Type,Validates
FilePath,Path must point to an existing file
DirectoryPath,Path must point to an existing directory
NewPath,Path must NOT exist (parent must exist)
SocketPath,Path must point to an existing socket
```

### Date/Time Types

`PastDate`, `FutureDate`, `PastDatetime`, `FutureDatetime`, `AwareDatetime`, `NaiveDatetime`

## Constrained Type Functions (Legacy Style)

These return `Annotated` types. Prefer the `Annotated` pattern directly for new code.

```python
from pydantic import conint, confloat, constr, conbytes, conlist, conset, confrozenset, condecimal, condate

# Examples:
conint(gt=0, le=100)        # Annotated[int, Field(gt=0, le=100)]
confloat(ge=0.0, lt=1.0)    # Annotated[float, Field(ge=0.0, lt=1.0)]
constr(min_length=1, max_length=50, pattern=r'^[a-z]+$')
conbytes(min_length=1)
conlist(int, min_length=1)   # list[int] with min_length=1
conset(str, min_length=1)
condecimal(max_digits=10, decimal_places=2)
condate(gt=date(2020, 1, 1))
```

### StringConstraints (Annotated metadata)

```python
from typing import Annotated
from pydantic import StringConstraints

Username = Annotated[str, StringConstraints(
    min_length=3,
    max_length=20,
    pattern=r'^[a-zA-Z0-9_]+$',
    strip_whitespace=True,
    to_lower=True,
)]
```

## Network Types (`pydantic.networks`)

### URL Types

```csv
Type,Scheme,Host required,Max length
AnyUrl,Any,No,None
AnyHttpUrl,http/https,No,None
HttpUrl,http/https,No,2083
AnyWebsocketUrl,ws/wss,No,None
WebsocketUrl,ws/wss,No,2083
FileUrl,file,No,None
FtpUrl,ftp,No,None
```

URL objects expose: `scheme`, `host`, `username`, `password`, `port`, `path`, `query`, `fragment`.

### DSN Types (Database Connection Strings)

`PostgresDsn`, `CockroachDsn`, `AmqpDsn`, `RedisDsn`, `MongoDsn`, `KafkaDsn`, `NatsDsn`, `MySQLDsn`, `MariaDBDsn`, `ClickHouseDsn`, `SnowflakeDsn`

### Email Types

```python
from pydantic import BaseModel, EmailStr, NameEmail

class Contact(BaseModel):
    email: EmailStr          # validates email format, requires email-validator package
    named: NameEmail         # "John Doe <john@example.com>"
```

`EmailStr` requires the `email-validator` package: `pip install pydantic[email]`.

### IP Address Types

```csv
Type,Accepts
IPvAnyAddress,IPv4Address or IPv6Address
IPvAnyInterface,IPv4Interface or IPv6Interface
IPvAnyNetwork,IPv4Network or IPv6Network
```

Standard library `ipaddress.IPv4Address` and `IPv6Address` are also directly supported.

### Custom URL Constraints

```python
from typing import Annotated
from pydantic import TypeAdapter
from pydantic.networks import AnyUrl, UrlConstraints

MyUrl = Annotated[AnyUrl, UrlConstraints(
    allowed_schemes=['https'],
    max_length=500,
    host_required=True,
)]
```

## Secret Types

Values hidden in `repr()`, `str()`, and serialization. Access via `.get_secret_value()`.

```python
from pydantic import BaseModel, SecretStr, SecretBytes, Secret

class Config(BaseModel):
    password: SecretStr       # str hidden in repr
    api_key: SecretBytes      # bytes hidden in repr
    token: Secret[int]        # generic Secret for any type

cfg = Config(password="s3cret", api_key=b"key123", token=42)
print(cfg.password)                       # SecretStr('**********')
print(cfg.password.get_secret_value())    # s3cret
print(cfg.model_dump())
# {'password': SecretStr('**********'), 'api_key': SecretBytes('**********'), 'token': Secret('**********')}
```

Subclass `Secret[T]` with custom `_display()` for custom masking.

## Special Types

### Json -- Parse JSON strings before validation

```python
from pydantic import BaseModel, Json

class Model(BaseModel):
    data: Json[list[int]]    # accepts JSON string, validates parsed result

m = Model(data='[1, 2, 3]')
print(m.data)  # [1, 2, 3]  (parsed Python list)
```

Use `round_trip=True` in `model_dump_json()` to serialize back to JSON string.

### ImportString -- Import Python objects from dotted paths

```python
from pydantic import BaseModel, ImportString

class Config(BaseModel):
    handler: ImportString

cfg = Config(handler='math.cos')
print(cfg.handler(0))  # 1.0
```

Accepts `module.attr` or `module:attr` syntax. Actual Python objects also accepted directly.

### JsonValue -- Any JSON-serializable value

```python
from pydantic import BaseModel, JsonValue

class Model(BaseModel):
    data: JsonValue    # str | int | float | bool | None | list | dict (recursive)
```

### OnErrorOmit -- Silently drop invalid items in collections

```python
from pydantic import BaseModel, OnErrorOmit

class Model(BaseModel):
    items: list[OnErrorOmit[int]]

m = Model(items=[1, 'bad', 3])
print(m.items)  # [1, 3]
```

### ByteSize -- Human-readable byte sizes

```python
from pydantic import BaseModel, ByteSize

class Cfg(BaseModel):
    max_size: ByteSize

c = Cfg(max_size='1.5 GiB')
print(c.max_size)                      # 1610612736
print(c.max_size.human_readable())     # '1.5GiB'
```

### Base64 Types

`Base64Bytes`, `Base64Str` -- standard base64 encoding/decoding.
`Base64UrlBytes`, `Base64UrlStr` -- URL-safe base64.

### PaymentCardNumber

Validates card numbers using Luhn algorithm. Provides `.masked` property and brand detection.

## Custom Types

### Using the Annotated Pattern (Recommended)

Compose constraints, validators, and serializers with `Annotated`:

```python
from typing import Annotated
from pydantic import Field, TypeAdapter, AfterValidator, PlainSerializer, WithJsonSchema

PositiveInt = Annotated[int, Field(gt=0)]

TruncatedFloat = Annotated[
    float,
    AfterValidator(lambda x: round(x, 1)),
    PlainSerializer(lambda x: f'{x:.1e}', return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization'),
]
```

### Named Type Aliases (for JSON Schema `$defs`)

```python
# Python 3.9+
from typing_extensions import TypeAliasType
PositiveIntList = TypeAliasType('PositiveIntList', list[Annotated[int, Gt(0)]])

# Python 3.12+
type PositiveIntList = list[Annotated[int, Gt(0)]]
```

Named aliases generate JSON Schema `$ref` definitions. Field-specific metadata (`alias`, `default`, `deprecated`) is NOT allowed in named aliases -- only type-level constraints.

### Customizing with `__get_pydantic_core_schema__`

For full control, implement this classmethod on your type or annotation class:

```python
from typing import Any
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler, TypeAdapter

class Username(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

ta = TypeAdapter(Username)
res = ta.validate_python('abc')
assert isinstance(res, Username)
```

### Handling Third-Party Types

Create an annotation class with `__get_pydantic_core_schema__` and wrap it with `Annotated`:

```python
from typing import Annotated, Any
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler

class _ThirdPartyAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler):
        return core_schema.json_or_python_schema(
            json_schema=core_schema.int_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ThirdPartyType),
                core_schema.int_schema(),
            ]),
        )

PydanticThirdParty = Annotated[ThirdPartyType, _ThirdPartyAnnotation]
```

### GetPydanticSchema -- Reduce Boilerplate

```python
from pydantic import BaseModel, GetPydanticSchema
from pydantic_core import core_schema

class Model(BaseModel):
    y: Annotated[str, GetPydanticSchema(
        lambda tp, handler: core_schema.no_info_after_validator_function(
            lambda x: x * 2, handler(tp)
        )
    )]
```

### Priority Order for Custom Types

1. Use built-in `Annotated` markers (`AfterValidator`, `Field`, etc.) when possible.
2. Use `GetPydanticSchema` or a marker class with `__get_pydantic_core_schema__` for deeper customization.
3. Implement `__get_pydantic_core_schema__` on the type itself only when you need a truly distinct custom type.

## Union Types

### Union Modes

```csv
Mode,Behavior,Set via
smart (default),"Tries all members, picks best match by exactness + valid fields count",Default
left_to_right,"Tries members in order, returns first match",Field(union_mode='left_to_right')
discriminated,Uses a discriminator field to pick exactly one member,Field(discriminator='field') or Discriminator(callable)
```

### Smart Mode Algorithm

1. Try all members left to right, scoring each by exactness (exact type > strict match > lax match).
2. For models/dataclasses/TypedDicts: the member with the highest "valid fields set" count wins. Exactness is a tiebreaker.
3. For other types: highest exactness score wins.

### Discriminated Unions (Recommended)

```python
from typing import Literal, Union
from pydantic import BaseModel, Field

class Cat(BaseModel):
    pet_type: Literal['cat']
    meows: int

class Dog(BaseModel):
    pet_type: Literal['dog']
    barks: float

class Model(BaseModel):
    pet: Union[Cat, Dog] = Field(discriminator='pet_type')
```

### Callable Discriminators

For unions without a common literal field, use `Discriminator` with a callable:

```python
from typing import Annotated, Any, Union
from pydantic import BaseModel, Discriminator, Tag

def get_type(v: Any) -> str:
    if isinstance(v, dict):
        return v.get('fruit', v.get('filling'))
    return getattr(v, 'fruit', getattr(v, 'filling', None))

class Model(BaseModel):
    dessert: Annotated[
        Union[
            Annotated[ApplePie, Tag('apple')],
            Annotated[PumpkinPie, Tag('pumpkin')],
        ],
        Discriminator(get_type),
    ]
```

Callable discriminators must handle both `dict` and model instance inputs (used during serialization too).

### Nested Discriminated Unions

```python
Cat = Annotated[Union[BlackCat, WhiteCat], Field(discriminator='color')]
Pet = Annotated[Union[Cat, Dog], Field(discriminator='pet_type')]
```

## TypeAdapter

Validate/serialize non-BaseModel types (primitives, TypedDicts, dataclasses, unions, etc.):

```python
from pydantic import TypeAdapter

ta = TypeAdapter(list[int])
result = ta.validate_python(['1', '2', '3'])   # [1, 2, 3]
json_bytes = ta.dump_json(result)               # b'[1,2,3]'  (returns bytes, not str)
schema = ta.json_schema()
```

### Key Methods

```csv
Method,Description
validate_python(data),Validate Python objects
validate_json(data),Validate JSON string/bytes
validate_strings(data),Validate with all values as strings
dump_python(obj),Serialize to Python dict/list
dump_json(obj),Serialize to JSON bytes
json_schema(),Generate JSON Schema
rebuild(),Rebuild schema (for forward refs)
```

### Performance Note

Creating a `TypeAdapter` has non-trivial overhead (schema generation). Create once, reuse in loops.

### Deferred Build

```python
from pydantic import ConfigDict, TypeAdapter

ta = TypeAdapter('MyType', config=ConfigDict(defer_build=True))
MyType = int
ta.rebuild()
```

## Strict Mode

### Three Ways to Enable

1. Per validation call:
```python
Model.model_validate(data, strict=True)
TypeAdapter(int).validate_python('123', strict=True)  # raises
```

2. Per field:
```python
from pydantic import BaseModel, Field, StrictInt

class User(BaseModel):
    name: str
    age: int = Field(strict=True)  # or use StrictInt
    # age: StrictInt  # equivalent
    # age: Annotated[int, Strict()]  # also equivalent
```

3. Per model (ConfigDict):
```python
from pydantic import BaseModel, ConfigDict, Field

class User(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str                       # strict
    age: int = Field(strict=False)  # override: lax for this field
```

### JSON Strict Mode Exception

Date/time types accept ISO format strings even in strict mode when validating JSON (since JSON has no native date type).

## Forward Annotations and `model_rebuild()`

### Forward References

Use string annotations or `from __future__ import annotations`:

```python
from __future__ import annotations
from pydantic import BaseModel

class Foo(BaseModel):
    a: int = 123
    sibling: Foo | None = None        # self-reference works

# Or without future import:
class Bar(BaseModel):
    sibling: 'Bar | None' = None      # quoted string
```

### Cyclic References

Pydantic detects cyclic references during validation and raises `ValidationError` with `type='recursion_loop'` instead of `RecursionError`. During serialization, cyclic references raise `ValueError` with "Circular reference detected".

### model_rebuild()

Call `model_rebuild()` when a forward-referenced type is defined after the model:

```python
from pydantic import BaseModel

class Foo(BaseModel):
    bar: 'Bar | None' = None

class Bar(BaseModel):
    value: int

Foo.model_rebuild()  # resolves the forward reference to Bar
```

### TypeAdapter.rebuild()

```python
ta = TypeAdapter('MyType', config=ConfigDict(defer_build=True))
MyType = int
ta.rebuild()  # resolves forward ref
```

## Types Quick-Reference Table

```csv
Import,Type,Use case
pydantic,"PositiveInt, NegativeInt, NonNegativeInt, NonPositiveInt",Constrained integers
pydantic,"PositiveFloat, NegativeFloat, NonNegativeFloat, NonPositiveFloat, FiniteFloat",Constrained floats
pydantic,"StrictBool, StrictInt, StrictFloat, StrictStr, StrictBytes",No coercion
pydantic,UUID1..UUID8,Version-specific UUIDs
pydantic,"FilePath, DirectoryPath, NewPath",Path validation
pydantic,"PastDate, FutureDate, PastDatetime, FutureDatetime",Time-bounded dates
pydantic,"AwareDatetime, NaiveDatetime",Timezone-aware/naive datetimes
pydantic,"SecretStr, SecretBytes, Secret[T]",Hide sensitive values
pydantic,Json[T],Parse JSON string then validate
pydantic,ImportString,Import Python object from dotted path
pydantic,JsonValue,Any JSON-serializable value
pydantic,ByteSize,Human-readable byte sizes
pydantic,"Base64Bytes, Base64Str",Base64 encoding/decoding
pydantic,PaymentCardNumber,Luhn-validated card numbers
pydantic,OnErrorOmit,Drop invalid collection items
pydantic,"conint, confloat, constr, conbytes, conlist, conset, condecimal, condate",Constrained types (legacy functions)
pydantic,StringConstraints,String constraint metadata
pydantic,"Strict, AllowInfNan",Annotated metadata classes
pydantic.networks,"EmailStr, NameEmail",Email validation
pydantic.networks,"AnyUrl, HttpUrl, AnyHttpUrl, FileUrl, FtpUrl",URL validation
pydantic.networks,"WebsocketUrl, AnyWebsocketUrl",WebSocket URLs
pydantic.networks,"PostgresDsn, RedisDsn, MongoDsn, etc.",Database DSNs
pydantic.networks,"IPvAnyAddress, IPvAnyInterface, IPvAnyNetwork",IP addresses/networks
pydantic,"Discriminator, Tag",Discriminated union support
pydantic,TypeAdapter,Validate non-BaseModel types
pydantic,GetPydanticSchema,Inline custom schema
```
