# Performance — Recurring Patterns

## Single-Pass JSON Validation

Parse JSON and validate in one Rust call. Avoids intermediate Python dict.

```python
# Slow: two passes
obj = Model.model_validate(json.loads(raw_json))

# Fast: single Rust pass
obj = Model.model_validate_json(raw_json)
```

## model_construct() for Trusted Data

Skip all validation when data is already known-valid (e.g., from a trusted internal service or database).

```python
obj = Model.model_construct(field_a=1, field_b="trusted")
```

## TypeAdapter Singleton

Build the schema once at module level. Avoid re-instantiation in loops or request handlers.

```python
from pydantic import TypeAdapter

_adapter = TypeAdapter(list[int])

def validate(data):
    return _adapter.validate_python(data)
```

## Discriminated Union for O(1) Dispatch

Tag union members with `Literal` fields. Pydantic resolves the correct branch via a single field lookup.

```python
from typing import Literal, Union
from pydantic import BaseModel, Field

class Cat(BaseModel):
    kind: Literal["cat"]

class Dog(BaseModel):
    kind: Literal["dog"]

class Owner(BaseModel):
    pet: Union[Cat, Dog] = Field(discriminator="kind")
```

## TypedDict Over Nested Models

Use `TypedDict` for nested structures when you don't need model methods. ~2.5x faster validation.

```python
from typing_extensions import TypedDict
from pydantic import BaseModel

class Address(TypedDict):
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    address: Address  # faster than a nested BaseModel
```

## FailFast on Sequences

Short-circuit on first invalid item in a collection. Trades error completeness for speed.

```python
from typing import Annotated
from pydantic import FailFast, TypeAdapter

ta = TypeAdapter(Annotated[list[int], FailFast()])
ta.validate_python([1, "bad", 3])  # reports only index 1
```

## Strict Mode for Hot Paths

Disable coercion to skip conversion logic. Faster and more predictable.

```python
from pydantic import BaseModel, ConfigDict

class HotPathModel(BaseModel):
    model_config = ConfigDict(strict=True)
    x: int
    y: float
```

## Deferred Schema Build

Delay validator/serializer construction until first use. Useful for large model hierarchies at import time.

```python
from pydantic import BaseModel, ConfigDict

class LazyModel(BaseModel):
    model_config = ConfigDict(defer_build=True)
    data: dict
```
