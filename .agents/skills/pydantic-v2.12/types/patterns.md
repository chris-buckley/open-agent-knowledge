# Types — Recurring Patterns

## Annotated Constrained Type Alias

The primary pattern for reusable, composable custom types. Stack constraints, validators, and serializers.

```python
from typing import Annotated
from pydantic import Field, AfterValidator, PlainSerializer, WithJsonSchema

Percentage = Annotated[float, Field(ge=0, le=100)]
NonEmptyStr = Annotated[str, Field(min_length=1)]
TrimmedFloat = Annotated[
    float,
    AfterValidator(lambda x: round(x, 2)),
    PlainSerializer(lambda x: f"{x:.2f}", return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
```

## Named Type Alias (for JSON Schema $defs)

Named aliases generate `$ref` definitions in JSON Schema instead of inlining.

```python
from typing import Annotated
from typing_extensions import TypeAliasType
from annotated_types import Gt

PositiveIntList = TypeAliasType("PositiveIntList", list[Annotated[int, Gt(0)]])
```

## Custom Type via __get_pydantic_core_schema__

Full control over validation and serialization for a custom class.

```python
from typing import Any
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler

class UserId(int):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(int))
```

## Third-Party Type Adapter

Wrap external types with Pydantic support using an Annotated marker class.

```python
from typing import Annotated, Any
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler

class _NumpyArrayAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(cls, _source: Any, _handler: GetCoreSchemaHandler):
        return core_schema.no_info_plain_validator_function(lambda v: v)

PydanticNumpyArray = Annotated[NumpyArrayType, _NumpyArrayAnnotation]
```

## Discriminated Union

Tag union members with `Literal` discriminator for O(1) dispatch and clear errors.

```python
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field

class Email(BaseModel):
    type: Literal["email"]
    address: str

class SMS(BaseModel):
    type: Literal["sms"]
    number: str

class Alert(BaseModel):
    channel: Union[Email, SMS] = Field(discriminator="type")
```

## Callable Discriminator

For unions where members have different discriminator field names.

```python
from typing import Annotated, Any, Union
from pydantic import BaseModel, Discriminator, Tag

def pick_type(v: Any) -> str:
    if isinstance(v, dict):
        return "a" if "x" in v else "b"
    return "a" if hasattr(v, "x") else "b"

class ModelA(BaseModel):
    x: int

class ModelB(BaseModel):
    y: str

class Container(BaseModel):
    item: Annotated[
        Union[Annotated[ModelA, Tag("a")], Annotated[ModelB, Tag("b")]],
        Discriminator(pick_type),
    ]
```

## TypeAdapter Singleton

Instantiate once at module level. Each instantiation builds a full schema — expensive in loops.

```python
from pydantic import TypeAdapter

IntList = TypeAdapter(list[int])  # module-level

def process(raw: str) -> list[int]:
    return IntList.validate_json(raw)
```

## Secret Wrapper

Hide sensitive values from repr, str, and serialization output.

```python
from pydantic import BaseModel, SecretStr

class DbConfig(BaseModel):
    host: str
    password: SecretStr

cfg = DbConfig(host="localhost", password="s3cret")
print(cfg.password)                     # SecretStr('**********')
print(cfg.password.get_secret_value())  # s3cret
```

## OnErrorOmit for Tolerant Collections

Silently drop invalid items instead of failing the entire collection.

```python
from pydantic import BaseModel, OnErrorOmit

class Feed(BaseModel):
    items: list[OnErrorOmit[int]]

Feed(items=[1, "bad", 3]).items  # [1, 3]
```
