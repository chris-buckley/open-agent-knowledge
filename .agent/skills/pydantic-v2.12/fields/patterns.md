# Fields — Recurring Patterns

## Annotated Reusable Type

Define constrained types once, reuse across models. Preferred over per-field `Field()` for shared constraints.

```python
from typing import Annotated
from pydantic import Field

PositivePrice = Annotated[float, Field(gt=0, description="Price in USD")]
ShortStr = Annotated[str, Field(max_length=100)]
```

## Computed Field (Derived Property)

Include a `@property` in serialization output and JSON Schema without storing it as a field.

```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height
```

## Discriminated Union (Tagged)

Resolve union members via a literal discriminator field. O(1) dispatch, clear error messages.

```python
from typing import Literal, Union
from pydantic import BaseModel, Field

class Cat(BaseModel):
    kind: Literal["cat"]
    meows: int

class Dog(BaseModel):
    kind: Literal["dog"]
    barks: float

class Owner(BaseModel):
    pet: Union[Cat, Dog] = Field(discriminator="kind")
```

## AliasPath for Nested Input

Extract fields from nested structures without intermediate models.

```python
from pydantic import BaseModel, Field, AliasPath

class User(BaseModel):
    first: str = Field(validation_alias=AliasPath("names", 0))
    last: str = Field(validation_alias=AliasPath("names", 1))

User.model_validate({"names": ["Jane", "Doe"]})
```

## AliasChoices for Multi-Source Input

Accept a field from multiple possible names (API versioning, legacy compatibility).

```python
from pydantic import BaseModel, Field, AliasChoices

class Config(BaseModel):
    host: str = Field(validation_alias=AliasChoices("host", "hostname", "server"))
```

## Separate Validation and Serialization Aliases

Accept camelCase input, emit snake_case output (or vice versa).

```python
from pydantic import BaseModel, Field

class Event(BaseModel):
    start_time: str = Field(
        validation_alias="startTime",
        serialization_alias="start_time",
    )
```

## default_factory with Validated Data

Derive one field's default from another already-validated field. Fields are validated in declaration order.

```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    email: EmailStr
    username: str = Field(default_factory=lambda data: data["email"].split("@")[0])
```

## Conditional Field Exclusion

Exclude fields from serialization based on their runtime value.

```python
from pydantic import BaseModel, Field

class Event(BaseModel):
    name: str
    internal_id: str | None = Field(exclude_if=lambda v: v is None)
```

## Model-Wide Alias Generator

Auto-convert field names to camelCase/PascalCase for API contracts.

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class ApiResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        serialize_by_alias=True,
    )
    user_name: str
    created_at: str
```
