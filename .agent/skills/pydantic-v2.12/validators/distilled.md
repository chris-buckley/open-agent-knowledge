# Pydantic v2 -- Validators

## Field Validators

Four validator types, each usable via the Annotated pattern or the `@field_validator` decorator.

### AfterValidator

Runs after Pydantic's internal validation. Input is already the parsed type. Safest default choice.

```python
from typing import Annotated
from pydantic import AfterValidator, BaseModel, ValidationError

def is_even(value: int) -> int:
    if value % 2 == 1:
        raise ValueError(f'{value} is not an even number')
    return value

EvenNumber = Annotated[int, AfterValidator(is_even)]   # reusable type alias

class Model(BaseModel):
    number: EvenNumber
```

### BeforeValidator

Runs before Pydantic's internal parsing/coercion. Receives raw input (`Any`). Pydantic still validates the returned value against the field type.

```python
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator

def ensure_list(value: Any) -> Any:
    if not isinstance(value, list):
        return [value]
    return value

class Model(BaseModel):
    numbers: Annotated[list[int], BeforeValidator(ensure_list)]

Model(numbers=2)  # numbers=[2]
```

### PlainValidator

Replaces Pydantic's internal validation entirely. No further type checking occurs after this validator returns.

```python
from typing import Annotated, Any
from pydantic import BaseModel, PlainValidator

def val_number(value: Any) -> Any:
    if isinstance(value, int):
        return value * 2
    return value

class Model(BaseModel):
    number: Annotated[int, PlainValidator(val_number)]

Model(number='invalid')  # number='invalid' -- no type enforcement
```

### WrapValidator

Most flexible. Receives a `handler` callable to delegate to Pydantic's inner validation. Can run code before/after, catch errors, or skip the handler entirely.

```python
from typing import Any, Annotated
from pydantic import BaseModel, Field, ValidationError, ValidatorFunctionWrapHandler, WrapValidator

def truncate(value: Any, handler: ValidatorFunctionWrapHandler) -> str:
    try:
        return handler(value)
    except ValidationError as err:
        if err.errors()[0]['type'] == 'string_too_long':
            return handler(value[:5])
        raise

class Model(BaseModel):
    my_string: Annotated[str, Field(max_length=5), WrapValidator(truncate)]
```

## Annotated Pattern vs Decorator Pattern

### Annotated pattern -- reusable, composable

```python
from typing import Annotated
from pydantic import AfterValidator, BaseModel

EvenNumber = Annotated[int, AfterValidator(is_even)]

class Model1(BaseModel):
    my_number: EvenNumber

class Model2(BaseModel):
    other_number: Annotated[EvenNumber, AfterValidator(lambda v: v + 2)]

class Model3(BaseModel):
    list_of_even_numbers: list[EvenNumber]  # works inside generics
```

### Decorator pattern -- apply one function to multiple fields

```python
from pydantic import BaseModel, field_validator

class Model(BaseModel):
    f1: str
    f2: str

    @field_validator('f1', 'f2', mode='before')
    @classmethod
    def capitalize(cls, value: str) -> str:
        return value.capitalize()
```

## @field_validator Decorator

```python
@field_validator(*fields, mode='after', check_fields=True, json_schema_input_type=None)
@classmethod
def name(cls, value, info: ValidationInfo | None) -> ...:
    ...
```

`mode` options:

```csv
Mode,Input type,Pydantic runs after?,Signature
'after' (default),Parsed field type,Already ran,"(cls, value: FieldType) -> FieldType"
'before',Any (raw input),Runs after validator,"(cls, value: Any) -> Any"
'plain',Any (raw input),Does not run,"(cls, value: Any) -> Any"
'wrap',Any (raw input),Called via handler,"(cls, value: Any, handler) -> FieldType"
```

Applying to multiple / all fields:

```python
@field_validator('f1', 'f2', mode='after')  # specific fields
@field_validator('*', mode='before')         # all fields (including subclass fields)
```

- Pass `check_fields=False` when the validator is on a base class and the field exists only on subclasses.
- `'after'` is the default mode and can be omitted.

`json_schema_input_type`: When a `before`/`wrap` validator widens the accepted input, pass this to fix the generated JSON Schema:

```python
@field_validator('value', mode='before', json_schema_input_type=Union[int, str])
```

For `plain` validators, `json_schema_input_type` defaults to `Any` (field type is discarded).

## Model Validators

Validate across the entire model's data. Defined with `@model_validator`.

### mode='after' -- post-initialization hook

Receives `self` (the fully constructed model instance). Must return `self` (or a compatible instance).

```python
from typing_extensions import Self
from pydantic import BaseModel, model_validator

class UserModel(BaseModel):
    password: str
    password_repeat: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError('Passwords do not match')
        return self
```

### mode='before' -- raw data, pre-construction

Receives `cls` and the raw input (`Any`). A classmethod.

```python
from typing import Any
from pydantic import BaseModel, model_validator

class UserModel(BaseModel):
    username: str

    @model_validator(mode='before')
    @classmethod
    def check_card_number_not_present(cls, data: Any) -> Any:
        if isinstance(data, dict) and 'card_number' in data:
            raise ValueError("'card_number' should not be included")
        return data
```

### mode='wrap' -- full control

Receives `cls`, raw data, and a `handler`. Call `handler(data)` to run standard validation.

```python
import logging
from typing import Any
from typing_extensions import Self
from pydantic import BaseModel, ModelWrapValidatorHandler, ValidationError, model_validator

class UserModel(BaseModel):
    username: str

    @model_validator(mode='wrap')
    @classmethod
    def log_failed_validation(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        try:
            return handler(data)
        except ValidationError:
            logging.error('Model %s failed to validate with data %s', cls, data)
            raise
```

Inheritance: A model validator on a base class runs for subclass instances. Overriding it in a subclass replaces (does not chain) the base version.

## Raising Validation Errors

Three exception types are caught by Pydantic:

```csv
Exception,Notes
ValueError,Most common. Message becomes the error msg.
AssertionError,Via assert statements. Skipped when Python runs with -O.
PydanticCustomError,"Custom error type, message template, and context dict."
```

```python
from pydantic_core import PydanticCustomError

raise PydanticCustomError(
    'the_answer_error',          # type
    '{number} is the answer!',   # message template
    {'number': v},               # context dict
)
```

## ValidationInfo

Both field and model validator callables can accept an optional `info: ValidationInfo` parameter.

```csv
Property,Description
info.data,dict of already-validated field values. None for model validators.
info.context,User-supplied context dict (or None).
info.field_name,Current field name (str). Only for field validators.
info.mode,"'python', 'json', or 'strings'."
info.config,The model's CoreConfig.
```

### Using info.data (cross-field access)

```python
from pydantic import BaseModel, ValidationInfo, field_validator

class UserModel(BaseModel):
    password: str
    password_repeat: str  # defined after password

    @field_validator('password_repeat', mode='after')
    @classmethod
    def check_passwords_match(cls, value: str, info: ValidationInfo) -> str:
        if value != info.data['password']:
            raise ValueError('Passwords do not match')
        return value
```

Fields are validated in definition order. `info.data` only contains fields defined *before* the current one.

## Validation Context

Pass arbitrary data into validators via `context`:

```python
from pydantic import BaseModel, ValidationInfo, field_validator

class Model(BaseModel):
    text: str

    @field_validator('text', mode='after')
    @classmethod
    def remove_stopwords(cls, v: str, info: ValidationInfo) -> str:
        if isinstance(info.context, dict):
            stopwords = info.context.get('stopwords', set())
            v = ' '.join(w for w in v.split() if w.lower() not in stopwords)
        return v

Model.model_validate({'text': 'This is an example'}, context={'stopwords': ['this', 'is']})
# text='an example'
```

Context is passed to `model_validate()`, `model_validate_json()`, and `TypeAdapter.validate_*()`. It is not available when calling `Model(...)` directly (see pitfalls).

### ContextVar workaround for direct instantiation

```python
from contextvars import ContextVar
from contextlib import contextmanager
from typing import Any
from collections.abc import Generator
from pydantic import BaseModel, ValidationInfo, field_validator

_init_context_var = ContextVar('_init_context_var', default=None)

@contextmanager
def init_context(value: dict[str, Any]) -> Generator[None]:
    token = _init_context_var.set(value)
    try:
        yield
    finally:
        _init_context_var.reset(token)

class Model(BaseModel):
    my_number: int

    def __init__(self, /, **data: Any) -> None:
        self.__pydantic_validator__.validate_python(
            data, self_instance=self, context=_init_context_var.get(),
        )

    @field_validator('my_number')
    @classmethod
    def multiply_with_context(cls, value: int, info: ValidationInfo) -> int:
        if isinstance(info.context, dict):
            value = value * info.context.get('multiplier', 1)
        return value

with init_context({'multiplier': 3}):
    print(Model(my_number=2))  # my_number=6
```

## Ordering of Validators

When using the Annotated pattern, execution order is:

1. `BeforeValidator` and `WrapValidator` run right to left.
2. Pydantic's internal validation runs.
3. `AfterValidator` runs left to right.

```python
from pydantic import AfterValidator, BeforeValidator, WrapValidator

name: Annotated[
    str,
    AfterValidator(runs_3rd),
    AfterValidator(runs_4th),
    BeforeValidator(runs_2nd),
    WrapValidator(runs_1st),
]
```

Decorator-based validators are internally converted to their Annotated counterparts and appended after existing metadata. The same ordering logic applies.

## @validate_call Decorator

Validates function arguments (and optionally the return value) using type annotations.

```python
from pydantic import validate_call, ValidationError

@validate_call
def repeat(s: str, count: int, *, separator: bytes = b'') -> bytes:
    b = s.encode()
    return separator.join(b for _ in range(count))

repeat('hello', 3)            # b'hellohellohello'
repeat('x', '4', separator=b' ')  # b'x x x x' -- coerces '4' -> 4
```

Key options:

```python
@validate_call(config=ConfigDict(...), validate_return=True)
```

```csv
Parameter,Default,Description
config,None,"ConfigDict for validation behavior (e.g. strict=True, arbitrary_types_allowed=True)."
validate_return,False,"When True, also validates the return value."
```

Features:
- Works with all parameter kinds: positional, keyword, `*args`, `**kwargs`, positional-only, keyword-only.
- Works with async functions.
- Use `Annotated[int, Field(gt=10)]` for field constraints on parameters.
- Access the original undecorated function via `.raw_function`.
- Missing required arguments raise `ValidationError` (not `TypeError`).

```python
from typing import Annotated
from pydantic import Field, validate_call

@validate_call
def how_many(num: Annotated[int, Field(gt=10)]):
    return num
```

## Special Types

```csv
Type,Import,Purpose
InstanceOf[T],pydantic.InstanceOf,Validates value is an instance of T. No coercion.
SkipValidation[T],pydantic.SkipValidation,Skips all validation for the annotated type.
"ValidateAs(type, transform)",pydantic.ValidateAs,"Validates as one type, then transforms to another."
PydanticUseDefault,pydantic_core.PydanticUseDefault,Raise in a before/wrap validator to use the field's default value.
```

```python
from pydantic import BaseModel, InstanceOf, SkipValidation

class Basket(BaseModel):
    fruits: list[InstanceOf[Fruit]]   # each element must be a Fruit instance

class Loose(BaseModel):
    names: list[SkipValidation[str]]  # no validation at all -- accepts anything
```

```python
from pydantic_core import PydanticUseDefault
from pydantic import BaseModel, BeforeValidator
from typing import Annotated, Any

def default_if_none(value: Any) -> Any:
    if value is None:
        raise PydanticUseDefault()
    return value

class Model(BaseModel):
    name: Annotated[str, BeforeValidator(default_if_none)] = 'default_name'

Model(name=None)  # name='default_name'
```
