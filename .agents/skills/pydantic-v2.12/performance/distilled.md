# Pydantic v2 Performance

## pydantic-core Architecture (Rust Layer)

Pydantic v2 splits into two packages:

- pydantic (Python) -- model definition, field collection, config, validators/serializers registration.
- pydantic-core (Rust) -- validation and serialization execution, providing 5-20x speedup over Pydantic v1.

Communication between them uses a core schema: a structured Python `TypedDict` dictionary with a required `type` key. The `GenerateSchema` class converts model definitions into core schemas. Each model stores its core schema as `__pydantic_core_schema__`.

At runtime, `pydantic-core` exposes `SchemaValidator` and `SchemaSerializer` to execute validation and serialization against the core schema.

```python
from pydantic import BaseModel

class Model(BaseModel):
    foo: int

# Internally uses SchemaValidator.validate_python():
model = Model.model_validate({'foo': 1})
# Internally uses SchemaSerializer.to_python():
dumped = model.model_dump()
```

Core schemas also drive JSON Schema generation via the `GenerateJsonSchema` class, which maps each core schema type to its JSON Schema equivalent.

## model_validate_json() vs model_validate(json.loads(...))

Prefer `model_validate_json()` -- it parses JSON and validates in a single Rust pass, avoiding the intermediate Python dict.

```python
# Slow: parse in Python, then validate
obj = Model.model_validate(json.loads(raw_json))

# Fast: parse + validate in Rust
obj = Model.model_validate_json(raw_json)
```

Exception: models using `'before'` or `'wrap'` validators may sometimes be faster with the two-step approach due to how data is materialized. This edge case is being optimized in pydantic-core.

## model_construct() for Trusted Data

Skip validation entirely when data is already known-valid:

```python
# No validation, no coercion -- fields set directly
obj = Model.model_construct(foo=42)
```

- Returns a model instance without calling any validators.
- Field defaults are NOT applied unless passed explicitly (or use `_fields_set` parameter).
- Use only when the source data is fully trusted and already matches the expected types.

## TypeAdapter for Non-Model Validation

`TypeAdapter` wraps any type (not just `BaseModel`) with a validator and serializer. Instantiate once and reuse -- each instantiation builds a new core schema, validator, and serializer.

```python
# BAD: rebuilds validator on every call
def validate(data):
    adapter = TypeAdapter(list[int])
    return adapter.validate_python(data)

# GOOD: build once at module level
adapter = TypeAdapter(list[int])

def validate(data):
    return adapter.validate_python(data)
```

`TypeAdapter` also supports `validate_json()` for the same single-pass benefit as `model_validate_json()`.

## Strict Mode Performance

Strict mode disables type coercion (e.g., `"42"` will NOT become `int`). Performance implications:

- Faster in hot paths -- skips coercion logic, short-circuits on type mismatch.
- More predictable -- no implicit conversion overhead.
- Enable per-field, per-model, or per-validation call:

```python
from pydantic import BaseModel, Field

class Model(BaseModel):
    x: int = Field(strict=True)          # per-field

class StrictModel(BaseModel):
    model_config = {'strict': True}      # per-model
    x: int

Model.model_validate({'x': 1}, strict=True)  # per-call
```

## Schema Building Performance

Schema generation (core schema + validator + serializer construction) happens at class definition time. Minimize its cost:

- Avoid deeply nested model hierarchies -- each level adds schema-building overhead.
- Use `TypedDict` for nested structures instead of nested `BaseModel` subclasses (~2.5x faster validation).
- Reuse `TypeAdapter` instances -- don't re-instantiate.
- Use discriminated unions -- tagged unions resolve the correct branch via a single field lookup instead of trying each member.

```python
from typing import Literal
from pydantic import BaseModel, Field

class Cat(BaseModel):
    pet_type: Literal['cat'] = 'cat'
    name: str

class Dog(BaseModel):
    pet_type: Literal['dog'] = 'dog'
    name: str

class Owner(BaseModel):
    # Discriminated: O(1) dispatch on pet_type
    pet: Cat | Dog = Field(discriminator='pet_type')
```

## Annotation Resolution Process

Pydantic resolves type hints at runtime using `eval()` with assembled namespaces. This impacts class definition performance and correctness.

Resolution order for annotations (per base class in reverse MRO):

1. Fetch `__annotations__` from the class `__dict__`.
2. Evaluate each annotation string via `eval()` with:
   - globals: the defining module's `__dict__`.
   - locals (highest to lowest priority):
     - `{cls.__name__: cls}` (enables self-referencing).
     - `cls.__dict__` (class-level type aliases).
     - Parent frame locals (if class is defined inside a function).
3. If evaluation fails, annotation is kept as a string for later `model_rebuild()`.

`model_rebuild()` re-evaluates unresolved annotations:
- Uses an explicit `_types_namespace` dict if provided.
- Otherwise uses the caller's namespace.
- Merged with the model's parent namespace.

```python
from pydantic import BaseModel

class Foo(BaseModel):
    f: 'Bar'  # unresolved at definition

class Bar(BaseModel):
    x: int

Foo.model_rebuild()  # resolves 'Bar' from caller namespace
```

PEP 649 (Python 3.14) will introduce deferred evaluation of annotations, expected to greatly simplify this process.

## Validation Tips Quick Reference

```csv
Technique,Benefit
model_validate_json(),Single Rust pass for JSON parse + validate
model_construct(),Zero validation for trusted data
TypeAdapter at module level,Build validator/serializer once
list/dict over Sequence/Mapping,Skip abstract type checks
Any for unvalidated fields,No validation overhead
Discriminated unions,O(1) union dispatch
TypedDict over nested models,~2.5x faster (no model overhead)
Avoid 'wrap' validators,Prevents data materialization in Python
FailFast on sequences,Stop on first error (v2.8+)
strict=True,Skip coercion logic
```

## FailFast for Sequences

Short-circuit validation on the first failing item in a sequence. Trades error completeness for speed.

```python
from typing import Annotated
from pydantic import FailFast, TypeAdapter

ta = TypeAdapter(Annotated[list[bool], FailFast()])
ta.validate_python([True, 'invalid', False, 'also invalid'])
# Only reports error for index 1, stops there
```

## Avoid Primitive Subclasses

Do not attach extra state via subclasses of `str`, `int`, etc. Use a model instead:

```python
# BAD: subclass of str with extra attributes
class CompletedStr(str):
    def __init__(self, s: str):
        self.s = s
        self.done = False

# GOOD: plain model
class CompletedModel(BaseModel):
    s: str
    done: bool = False
```

Primitive subclasses add validation overhead and bypass pydantic-core optimizations.
