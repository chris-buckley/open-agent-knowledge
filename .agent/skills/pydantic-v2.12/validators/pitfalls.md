# Pydantic v2 Validators -- Pitfalls

## 1. Default values are NOT validated

Custom validators do not run on default values unless `validate_default=True` is set on the field or in the model config.

```python
from pydantic import BaseModel, Field, field_validator

class Model(BaseModel):
    x: int = Field(default=-1, validate_default=True)

    @field_validator('x', mode='after')
    @classmethod
    def must_be_positive(cls, v: int) -> int:
        assert v > 0
        return v
# Without validate_default=True, x=-1 would silently pass.
```

## 2. info.data only contains fields defined BEFORE the current field

Fields are validated in definition order. Accessing a later-defined field from `info.data` raises `KeyError`.

```python
class Model(BaseModel):
    password: str
    password_repeat: str  # must come AFTER password
    username: str         # NOT available in password_repeat's validator

    @field_validator('password_repeat', mode='after')
    @classmethod
    def check(cls, v: str, info: ValidationInfo) -> str:
        info.data['password']   # OK -- defined before
        # info.data['username'] # KeyError -- defined after
        return v
```

Reorder fields or use a `@model_validator(mode='after')` for cross-field checks that need all fields.

## 3. Before/wrap validators receive Any -- handle every input shape

Before validators get raw, unprocessed input. Do not assume the type matches the annotation.

```python
@field_validator('numbers', mode='before')
@classmethod
def ensure_list(cls, value: Any) -> Any:
    # value could be a str, int, dict, None, etc.
    if not isinstance(value, list):
        return [value]
    return value
```

Also check for other sequence types (tuple, set) if you want to handle those gracefully.

## 4. PlainValidator skips ALL Pydantic type checking

The field type annotation becomes purely decorative. Pydantic performs zero internal validation.

```python
class Model(BaseModel):
    number: Annotated[int, PlainValidator(lambda v: v)]

Model(number='not_an_int')  # Passes -- number='not_an_int'
```

Use PlainValidator only when you want complete control and are prepared to handle all type enforcement yourself.

## 5. assert statements are stripped by python -O

`AssertionError` works as a validation error, but `assert` statements are removed when Python runs with the `-O` (optimize) flag. In production with `-O`, those validators silently pass.

Prefer `raise ValueError(...)` or `PydanticCustomError` for validators that must run in all environments.

## 6. Validation context is None when calling Model(...) directly

Context is only available via `model_validate()` / `model_validate_json()`. Direct instantiation does not pass context.

```python
Model(text='hello')                          # info.context is None
Model.model_validate({'text': 'hello'}, context={'key': 'val'})  # info.context is {'key': 'val'}
```

If you need context with `Model(...)`, use the `ContextVar` + custom `__init__` workaround (see distilled.md).

## 7. Do not mutate values in before validators when raising later

If a before validator mutates its input and then raises an error, the mutated value may leak to other validators (especially with unions). Return new values instead of mutating in-place.

```python
# BAD -- mutates input dict
@model_validator(mode='before')
@classmethod
def check(cls, data: Any) -> Any:
    if isinstance(data, dict):
        data['extra'] = True   # mutation leaks if ValueError raised later
        if some_condition:
            raise ValueError('bad')
    return data

# GOOD -- return a copy
@model_validator(mode='before')
@classmethod
def check(cls, data: Any) -> Any:
    if isinstance(data, dict):
        data = {**data, 'extra': True}
        if some_condition:
            raise ValueError('bad')
    return data
```

## 8. Decorator validators must be @classmethod

Missing `@classmethod` causes a runtime error. The `@classmethod` decorator must come directly below `@field_validator` / `@model_validator(mode='before'|'wrap')`.

```python
# CORRECT
@field_validator('x', mode='after')
@classmethod
def validate_x(cls, v: int) -> int: ...

# WRONG -- will error
@field_validator('x', mode='after')
def validate_x(cls, v: int) -> int: ...
```

Exception: `@model_validator(mode='after')` is an instance method (receives `self`), not a classmethod.

## 9. Must return the value from every validator

All validators must return the (possibly transformed) value. Forgetting the `return` statement silently sets the field to `None`.

```python
# BUG -- returns None implicitly
@field_validator('name', mode='after')
@classmethod
def strip_name(cls, v: str) -> str:
    v.strip()  # forgot return

# CORRECT
@field_validator('name', mode='after')
@classmethod
def strip_name(cls, v: str) -> str:
    return v.strip()
```

Same for `@model_validator(mode='after')` -- must `return self`.

## 10. Model validator inheritance: override replaces, does not chain

Defining a model validator with the same name in a subclass fully replaces the parent's version. There is no automatic chaining.

```python
class Base(BaseModel):
    @model_validator(mode='after')
    def check(self) -> Self:
        # this will NOT run for Child instances
        ...

class Child(Base):
    @model_validator(mode='after')
    def check(self) -> Self:
        # completely replaces Base.check
        ...
```

Call `super()` explicitly if you want to chain behavior.

## 11. @validate_call raises ValidationError, not TypeError

Missing required arguments produce a `ValidationError` instead of the standard `TypeError`. Code that catches `TypeError` for missing args will break.

## 12. Annotated ordering matters

Before/wrap validators run right-to-left; after validators run left-to-right. Placing validators in the wrong order produces unexpected execution sequences.

```python
# Execution: wrap_outer -> before_inner -> Pydantic -> after_first -> after_second
name: Annotated[
    str,
    AfterValidator(after_first),
    AfterValidator(after_second),
    BeforeValidator(before_inner),
    WrapValidator(wrap_outer),
]
```

## 13. info.data is None inside model validators

`ValidationInfo.data` is only populated for field validators. For model validators, `info.data` is `None`. Use `self` (after mode) or `data` parameter (before/wrap mode) instead.
