# Pydantic v2 Models -- Common Pitfalls

## 1. Field Name Colliding with Type Name

Naming a field the same as its type annotation shadows the built-in type and breaks validation.

```python
# WRONG -- shadows `int` type
class Boo(BaseModel):
    int: Optional[int] = None   # evaluates as int: None = None

# CORRECT
class Boo(BaseModel):
    value: Optional[int] = None
```

## 2. Extra Data Silently Ignored by Default

By default `extra='ignore'`, so unexpected fields vanish without warning. If you want strict input checking, set `extra='forbid'`.

```python
class M(BaseModel):
    x: int

M(x=1, typo_field='oops')  # no error, typo_field silently dropped
```

## 3. model_construct() Skips ALL Validation

`model_construct()` creates potentially invalid model instances. No type coercion, no validators, no `__init__` call. Nested dicts are NOT converted to sub-models.

```python
m = User.model_construct(id='not-an-int')  # no error, m.id == 'not-an-int'
```

In Pydantic v2, the performance gap between validation and `model_construct()` is much smaller -- profile before assuming it is faster.

## 4. Frozen Does Not Mean Truly Immutable

`frozen=True` only prevents attribute reassignment. Mutable field values (lists, dicts, sets) can still be mutated in-place.

```python
class M(BaseModel):
    model_config = ConfigDict(frozen=True)
    items: list[int]

m = M(items=[1, 2])
m.items.append(3)  # succeeds -- list is still mutable
m.items = [4, 5]   # raises ValidationError
```

## 5. model_copy(update=) Does Not Validate

The `update` dict in `model_copy()` is applied directly without validation. You must trust this data.

```python
m = User(id=1, name='Alice')
bad = m.model_copy(update={'id': 'not-a-number'})  # no error
```

## 6. Accessing model_fields on Instance Is Deprecated

In v2, `model_fields` is a class property. Accessing it on instances will stop working in v3.

```python
# DEPRECATED
m = User(id=1)
m.model_fields  # works in v2 with warning, breaks in v3

# CORRECT
User.model_fields
```

## 7. Parametrized Generics in isinstance()

Do NOT use `isinstance(obj, MyModel[int])`. It does not work as expected for parametrized generics. Use the unparameterized base or create an explicit subclass.

```python
# WRONG
isinstance(m, Response[int])

# CORRECT
isinstance(m, Response)
# or
class IntResponse(Response[int]): ...
isinstance(m, IntResponse)
```

## 8. Unparameterized Generics Can Lose Data

When a generic model with a bounded type variable is used without parametrization, validation uses the bound type, potentially discarding subclass fields.

```python
class ItemBase(BaseModel): ...
class IntItem(ItemBase):
    value: int

class Holder(BaseModel, Generic[T]):  # T bound to ItemBase
    item: T

Holder(item={'value': 1}).item       # ItemBase() -- value field lost
Holder[IntItem](item={'value': 1})   # IntItem(value=1) -- correct
```

## 9. Custom __init__ Loses Validation Parameters

Defining a custom `__init__` on a model bypasses pydantic-core validation. Strictness, extra data handling, and validation context are all lost. Use `model_post_init()` or validators instead.

```python
# AVOID
class M(BaseModel):
    x: int
    def __init__(self, **data):
        super().__init__(**data)  # must call super, but still loses params

# PREFER
class M(BaseModel):
    x: int
    def model_post_init(self, context):
        # safe post-init logic here
        ...
```

## 10. Forgetting model_rebuild() for Forward References

If a model references a type defined later, schema operations fail until `model_rebuild()` is called.

```python
class Foo(BaseModel):
    bar: 'Bar'

class Bar(BaseModel):
    x: int

# Without this, Foo.model_json_schema() raises PydanticUserError
Foo.model_rebuild()
```

## 11. Pydantic Dataclasses Lack Model Methods

Pydantic dataclasses do NOT have `model_dump()`, `model_validate()`, `model_json_schema()`, etc. Wrap with `TypeAdapter` to access them.

```python
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

@dataclass
class User:
    id: int

adapter = TypeAdapter(User)
schema = adapter.json_schema()
user = adapter.validate_python({'id': '42'})
d = adapter.dump_python(user)
```

## 12. Using Deprecated V1 Methods

These V1 methods are deprecated in v2 and will be removed in v3:

```csv
Deprecated,Replacement
.dict(),.model_dump()
.json(),.model_dump_json()
.parse_obj(),.model_validate()
.parse_raw(),.model_validate_json()
.from_orm(),.model_validate() with from_attributes=True
.schema(),.model_json_schema()
.construct(),.model_construct()
.copy(),.model_copy()
.update_forward_refs(),.model_rebuild()
.__fields__,.model_fields (class property)
.__fields_set__,.model_fields_set
```

## 13. Missing ClassVar Annotation on Constants

Without `ClassVar`, a class-level attribute with a type annotation becomes a model field.

```python
from typing import ClassVar

# WRONG -- MAX becomes a required field
class Config(BaseModel):
    MAX: int = 100

# CORRECT
class Config(BaseModel):
    MAX: ClassVar[int] = 100
```

## 14. Private Attribute Dunder Names Ignored

Dunder names (`__attr__`) are completely ignored by Pydantic -- they are not treated as private attributes.

```python
class M(BaseModel):
    __my_attr__: int = PrivateAttr(default=1)  # silently ignored

    _my_attr: int = PrivateAttr(default=1)     # works correctly
```

## 15. Data Coercion Surprises

Default (lax) mode performs coercion that can lose precision or behave unexpectedly:

```python
class M(BaseModel):
    a: int
    b: float
    c: str

M(a=3.0, b='2.72', c=b'binary data')
# a=3 (float truncated), b=2.72 (string parsed), c='binary data' (bytes decoded)
```

Use `ConfigDict(strict=True)` or per-field `Annotated[int, Strict()]` to require exact types.

## 16. Stdlib Dataclass Fields Not Validated Standalone

Stdlib `@dataclasses.dataclass` does NOT validate on its own. Validation only happens when the dataclass is used inside a Pydantic model or `TypeAdapter`.

```python
import dataclasses

@dataclasses.dataclass
class User:
    name: str

u = User(name=['not', 'a', 'string'])  # no error from stdlib
# Validation only triggers when used in a Pydantic context
```

## 17. model_validate_json Is Stricter Than model_validate

JSON mode validation is stricter than Python mode by default. For example, `model_validate({'name': 123})` may coerce int to str in Python mode, but `model_validate_json('{"name": 123}')` will reject it.

## 18. Revalidation of Model Instances Skipped by Default

When passing an existing model instance to another model's field, it is assumed valid and NOT re-validated. Set `revalidate_instances='always'` if you need re-validation.

```python
class Inner(BaseModel):
    x: int

class Outer(BaseModel):
    model_config = ConfigDict(revalidate_instances='always')
    inner: Inner
```
