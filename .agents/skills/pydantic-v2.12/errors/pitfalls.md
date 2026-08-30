# Pydantic v2 Errors -- Pitfalls

## 1. Raising ValidationError directly from validators

Wrong: Raising `ValidationError` yourself inside a validator.
Right: Raise `ValueError` or `AssertionError`. Pydantic catches them and wraps them into the final `ValidationError`.

```python
# WRONG -- do not do this
@field_validator('x')
@classmethod
def check(cls, v):
    raise ValidationError(...)  # no -- Pydantic raises this for you

# RIGHT
@field_validator('x')
@classmethod
def check(cls, v):
    if v < 0:
        raise ValueError('must be non-negative')
    return v
```

## 2. Field name shadows its type annotation

Naming a field the same as its type (e.g. `int`, `date`, `str`) causes the annotation to resolve to the field's default value instead of the type. This produces confusing `none_required` errors.

```python
# BROKEN -- 'int' resolves to the field default, not the type
class M(BaseModel):
    int: Optional[int] = None  # validation of M(int=123) fails

# FIX -- use a different name or qualified import
import datetime
class M(BaseModel):
    date: datetime.date = Field(description='A date')
```

## 3. Forgetting model_rebuild() for forward references

If type `B` is referenced before it is defined, the model won't validate until `model_rebuild()` is called after both types exist.

```python
class Foo(BaseModel):
    bar: Optional['Bar'] = None

class Bar(BaseModel):
    x: int

Foo.model_rebuild()  # required -- without this, Foo(bar={'x': 1}) raises PydanticUserError
```

## 4. Mutating errors() dicts without copying

`e.errors()` returns a new list each call, but the dicts inside share references to internal data. If you mutate `loc` or other fields for display, you are modifying the return value in place. This is mostly harmless but can cause confusion if you call `e.errors()` again and compare.

## 5. Confusing _type vs _parsing error codes

- `string_type` / `int_type` / `float_type` -- wrong Python type entirely (e.g. `None` for `int`)
- `int_parsing` / `float_parsing` -- correct concept but the string value can't be converted (e.g. `'abc'` for `int`)

Handle these separately when building custom error messages.

## 6. extra_forbidden only fires with explicit config

By default, extra fields are ignored (Pydantic v2 default is `extra='ignore'`). You only get `extra_forbidden` errors if you set `model_config = ConfigDict(extra='forbid')`. If you rely on strict input validation, you must opt in.

## 7. Catching the wrong exception for usage errors

- `ValidationError` = data validation failure (at runtime with bad data)
- `PydanticUserError` = incorrect API usage (at class definition or schema build time)

These are different exception hierarchies. A `try/except ValidationError` will not catch `PydanticUserError` (which is a `TypeError`).

```python
# To catch both (rare, but useful in dynamic model construction):
from pydantic import ValidationError, PydanticUserError

try:
    model_cls = build_dynamic_model(spec)
    instance = model_cls(**data)
except PydanticUserError as e:
    print(f"Model definition error: {e.code} -- {e.message}")
except ValidationError as e:
    print(f"Data validation failed: {e.error_count()} errors")
```

## 8. Validator field names as a list instead of separate args

```python
# WRONG -- raises PydanticUserError (validator-invalid-fields)
@field_validator(['a', 'b'])
@classmethod
def check(cls, v): ...

# RIGHT -- separate string arguments
@field_validator('a', 'b')
@classmethod
def check(cls, v): ...
```

## 9. Instance method validators (missing @classmethod)

`@field_validator` functions must be class methods. If the first parameter is `self` instead of `cls`, Pydantic raises `PydanticUserError` with code `validator-instance-method`.

```python
# WRONG
@field_validator('x')
def check(self, v): ...

# RIGHT
@field_validator('x')
@classmethod
def check(cls, v): ...
```

## 10. Using discriminator with validators on the discriminator field

Before/wrap/plain validators on a discriminator field are forbidden because the discriminator must be read before validation to pick the right union member. Drop the discriminator and use a plain `Union` if you need to transform the tag value.

## 11. Config and model_config both defined

Using both the old `class Config` inner class and the new `model_config = ConfigDict(...)` attribute raises `PydanticUserError` with code `config-both`. Always use `model_config`.

## 12. TypeAdapter config for types that carry their own config

Passing `config=ConfigDict(...)` to `TypeAdapter(SomeModel)` when `SomeModel` is a `BaseModel`, `TypedDict`, or dataclass that already has its own config raises `type-adapter-config-unused`. Set the config on the type itself.

## 13. @validate_call decorator ordering

`@classmethod` / `@staticmethod` / `@property` must come before (above) `@validate_call`, not after. Wrong order raises `PydanticUserError`.

```python
# WRONG
@validate_call
@classmethod
def f(cls): ...

# RIGHT
@classmethod
@validate_call
def f(cls): ...
```

## 14. Assuming loc is always a flat tuple

For nested models, lists, and dicts, `loc` can be deeply nested: `('items', 1, 'address', 'zip_code')`. Always handle both `str` and `int` elements when formatting `loc` for display.

## 15. V1 keyword arguments in Field()

Using removed V1 arguments like `regex`, `min_items`, `max_items` raises `PydanticUserError` with code `removed-kwargs`. V2 equivalents:

```csv
V1 keyword,V2 equivalent
regex,pattern
min_items,min_length
max_items,max_length
allow_mutation,frozen (inverted)
```
