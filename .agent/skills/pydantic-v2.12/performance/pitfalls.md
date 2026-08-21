# Pydantic v2 Performance Pitfalls

## P1: Reinstantiating TypeAdapter in Functions

Every `TypeAdapter(...)` call builds a full core schema, validator, and serializer. Creating one inside a frequently called function multiplies this cost.

```python
# WRONG: schema rebuilt on every call
def process(items):
    ta = TypeAdapter(list[int])
    return ta.validate_python(items)

# FIX: instantiate at module scope
ta = TypeAdapter(list[int])
def process(items):
    return ta.validate_python(items)
```

## P2: Using model_validate(json.loads(...)) Instead of model_validate_json()

The two-step approach parses JSON into a Python dict first, then validates the dict. `model_validate_json()` does both in Rust in a single pass.

```python
# SLOW
obj = Model.model_validate(json.loads(payload))

# FAST
obj = Model.model_validate_json(payload)
```

Exception: models with `'before'` or `'wrap'` validators may not benefit in all cases.

## P3: Using Sequence/Mapping Instead of list/dict

`Sequence` triggers `isinstance(value, Sequence)` and attempts validation against multiple concrete types (`list`, `tuple`, etc.). If you know the concrete type, declare it directly.

```python
# SLOW: abstract type, multiple validation attempts
class Model(BaseModel):
    items: Sequence[int]

# FAST: concrete type, single validation path
class Model(BaseModel):
    items: list[int]
```

Same applies to `Mapping` vs `dict`.

## P4: Deeply Nested BaseModel Hierarchies

Each nested `BaseModel` carries overhead: schema construction, `__init__` wrapping, model metadata. For data-only nested structures, `TypedDict` is ~2.5x faster.

```python
# SLOWER
class Inner(BaseModel):
    a: str
    b: int

class Outer(BaseModel):
    inner: Inner

# FASTER
class Inner(TypedDict):
    a: str
    b: int

class Outer(TypedDict):
    inner: Inner

ta = TypeAdapter(Outer)
```

Use `BaseModel` when you need methods, validators, or serialization customization on the nested type. Use `TypedDict` when it is pure data.

## P5: Untagged Unions

Plain unions (`A | B | C`) try each member type in order until one succeeds. Discriminated unions dispatch in O(1) via a tag field.

```python
# SLOW: tries Cat, then Dog, then Fish in order
class Owner(BaseModel):
    pet: Cat | Dog | Fish

# FAST: single lookup on pet_type
class Owner(BaseModel):
    pet: Cat | Dog | Fish = Field(discriminator='pet_type')
```

Always add a `Literal` discriminator field to union members when possible.

## P6: Wrap Validators Materializing Data in Python

Wrap validators intercept the validation pipeline and require data to be materialized as Python objects, breaking the Rust fast path.

```python
# Causes Python-side materialization
@field_validator('data', mode='wrap')
def validate_data(cls, v, handler):
    result = handler(v)
    return result

# Prefer 'before' or 'after' validators when possible
@field_validator('data', mode='after')
def validate_data(cls, v):
    return v
```

Only use `mode='wrap'` when you genuinely need to intercept and conditionally delegate.

## P7: Validating Fields That Don't Need It

Every typed field is validated. If a field can accept anything and validation adds no value, annotate it as `Any`.

```python
# Unnecessary: validates opaque payload structure
class Model(BaseModel):
    metadata: dict[str, list[dict[str, Any]]]

# Faster: skip validation on opaque data
class Model(BaseModel):
    metadata: Any
```

## P8: model_construct() Misuse

`model_construct()` skips all validation. Pitfalls:

- Field defaults are not applied -- you must pass every field explicitly or accept `None`/missing attributes.
- No type coercion -- passing `"42"` for an `int` field stays as `"42"`.
- No validator execution -- custom `@field_validator` and `@model_validator` are skipped.
- Nested models are not constructed -- nested dicts remain as dicts.

```python
class Inner(BaseModel):
    x: int = 0

class Outer(BaseModel):
    inner: Inner
    name: str = "default"

# Pitfall: name won't be "default", inner stays a dict
obj = Outer.model_construct(inner={'x': 1})
# obj.name -> AttributeError (not set)
# obj.inner -> {'x': 1}  (not an Inner instance)
```

Only use with fully pre-validated, pre-typed data.

## P9: Forward References and model_rebuild() Cost

Unresolved forward references result in a `MockCoreSchema` placeholder. The model is non-functional until `model_rebuild()` is called. Each rebuild re-evaluates annotations and regenerates the core schema.

```python
class Foo(BaseModel):
    f: 'Bar'  # MockCoreSchema until rebuilt

class Bar(BaseModel):
    x: int

# Must rebuild to make Foo functional
Foo.model_rebuild()
```

Pitfalls:
- Forgetting `model_rebuild()` leads to runtime errors on first validation.
- Rebuilding in a loop wastes schema construction time.
- When defined inside a function, parent frame locals are stored via weak references and may be garbage collected, causing rebuild to fail outside the function.

## P10: Ignoring FailFast on Large Sequences

Without `FailFast`, validation of a 10,000-element list reports errors for every invalid item. If you only need to know the first failure, use `FailFast` to stop early.

```python
from typing import Annotated
from pydantic import FailFast, TypeAdapter

# Without FailFast: validates all 10,000 items, collects all errors
ta_slow = TypeAdapter(list[int])

# With FailFast: stops at first error
ta_fast = TypeAdapter(Annotated[list[int], FailFast()])
```

Trade-off: you lose visibility into subsequent errors.

## P11: Subclassing Primitives for Extra State

Subclassing `str`, `int`, etc. to attach extra attributes bypasses pydantic-core's optimized Rust validators and adds overhead at every validation.

```python
# BAD
class TaggedStr(str):
    tag: str = ""

# GOOD
class TaggedValue(BaseModel):
    value: str
    tag: str = ""
```

## P12: Schema Generation at Import Time

All `BaseModel` subclasses build their core schema at class definition (import) time. Large model hierarchies in eagerly-imported modules slow down application startup.

Mitigations:
- Lazy-import modules with heavy model definitions.
- Use `from __future__ import annotations` to defer annotation evaluation (reduces initial eval work, but schema is still built at class definition).
- PEP 649 (Python 3.14) will further improve deferred annotation handling.
