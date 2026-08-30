# Models — Recurring Patterns

## Immutable Value Object

Frozen model with value semantics. Use for domain entities that should not change after creation.

```python
from pydantic import BaseModel, ConfigDict

class Money(BaseModel):
    model_config = ConfigDict(frozen=True)
    amount: int
    currency: str = "USD"

# Hashable (if all fields are hashable), comparable, safe as dict key
price = Money(amount=999, currency="USD")
```

## RootModel Wrapper

Wrap a single collection or primitive with validation. Use for typed lists, lookup dicts, or newtype wrappers.

```python
from pydantic import RootModel

class Tags(RootModel[list[str]]):
    def __contains__(self, item: str) -> bool:
        return item in self.root

tags = Tags(["python", "pydantic"])
tags.model_dump()  # ["python", "pydantic"]
```

## Generic Response Envelope

Parametrized model for typed API responses. Build once, reuse across endpoints.

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T
    ok: bool = True

Response[list[str]](data=["a", "b"])
```

## ORM / from_attributes Bridge

Validate from object attributes (SQLAlchemy rows, dataclasses, namedtuples) without manual dict conversion.

```python
from pydantic import BaseModel, ConfigDict

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

user_read = UserRead.model_validate(orm_user)  # reads attrs, not dict keys
```

## model_construct() Fast Path

Skip validation for pre-validated or trusted data. Useful in bulk ETL or internal service-to-service calls.

```python
obj = Model.model_construct(field_a=1, field_b="trusted")
# No validators, no coercion — fields set directly
```

## Dynamic Model Factory

Generate models at runtime from schemas, configs, or database metadata.

```python
from pydantic import create_model, Field

fields = {"name": (str, ...), "age": (int, Field(ge=0))}
UserModel = create_model("UserModel", **fields)
```

## Nested Model Composition

Models as field types create hierarchical validation. Dicts are auto-promoted to the nested model.

```python
class Address(BaseModel):
    city: str

class User(BaseModel):
    address: Address

User(address={"city": "NYC"})  # dict auto-converted to Address
```

## Abstract Base Model

Combine ABC with BaseModel for enforcing method contracts on validated models.

```python
import abc
from pydantic import BaseModel

class Shape(BaseModel, abc.ABC):
    @abc.abstractmethod
    def area(self) -> float: ...

class Circle(Shape):
    radius: float
    def area(self) -> float:
        return 3.14159 * self.radius ** 2
```

## Extra Fields as Typed Dict

Allow extra fields with a specific value type using `__pydantic_extra__` annotation.

```python
from pydantic import BaseModel, ConfigDict, Field

class Metadata(BaseModel):
    __pydantic_extra__: dict[str, int] = Field(init=False)
    model_config = ConfigDict(extra="allow")
    name: str

m = Metadata(name="test", count="42")  # count coerced to int
```
