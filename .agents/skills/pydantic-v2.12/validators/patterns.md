# Validators — Recurring Patterns

## Reusable Annotated Validator

Define a validator once as a type alias, reuse across models and inside generics.

```python
from typing import Annotated
from pydantic import AfterValidator, BaseModel

def _check_even(v: int) -> int:
    if v % 2 != 0:
        raise ValueError(f"{v} is not even")
    return v

EvenInt = Annotated[int, AfterValidator(_check_even)]

class Model(BaseModel):
    count: EvenInt
    scores: list[EvenInt]  # works inside generics
```

## BeforeValidator for Input Normalization

Transform raw input before Pydantic's type parsing. Useful for accepting flexible input formats.

```python
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator

def ensure_list(v: Any) -> Any:
    return [v] if not isinstance(v, list) else v

FlexList = Annotated[list[int], BeforeValidator(ensure_list)]

class Model(BaseModel):
    items: FlexList

Model(items=42)  # items=[42]
```

## WrapValidator for Error Recovery

Catch validation errors and apply fallback logic without failing.

```python
from typing import Any, Annotated
from pydantic import BaseModel, Field, ValidationError, WrapValidator, ValidatorFunctionWrapHandler

def truncate_on_overflow(v: Any, handler: ValidatorFunctionWrapHandler) -> str:
    try:
        return handler(v)
    except ValidationError:
        return handler(str(v)[:100])

SafeStr = Annotated[str, Field(max_length=100), WrapValidator(truncate_on_overflow)]
```

## Cross-Field Validation (model_validator after)

Validate relationships between fields after all individual fields pass.

```python
from typing_extensions import Self
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start: str
    end: str

    @model_validator(mode="after")
    def check_order(self) -> Self:
        if self.start > self.end:
            raise ValueError("start must precede end")
        return self
```

## Raw Input Screening (model_validator before)

Reject or transform raw input before any field parsing begins.

```python
from typing import Any
from pydantic import BaseModel, model_validator

class SafeInput(BaseModel):
    data: dict[str, str]

    @model_validator(mode="before")
    @classmethod
    def strip_nulls(cls, values: Any) -> Any:
        if isinstance(values, dict):
            return {k: v for k, v in values.items() if v is not None}
        return values
```

## Validation Context Injection

Pass runtime context into validators via `model_validate()`.

```python
from pydantic import BaseModel, ValidationInfo, field_validator

class Document(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def filter_words(cls, v: str, info: ValidationInfo) -> str:
        if isinstance(info.context, dict):
            banned = info.context.get("banned_words", set())
            v = " ".join(w for w in v.split() if w not in banned)
        return v

Document.model_validate({"text": "hello world"}, context={"banned_words": {"world"}})
```

## Multi-Field Decorator

Apply one validator function to multiple fields with `@field_validator`.

```python
from pydantic import BaseModel, field_validator

class Form(BaseModel):
    first_name: str
    last_name: str

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_and_title(cls, v: str) -> str:
        return v.strip().title()
```

## Conditional Default via PydanticUseDefault

In a before/wrap validator, raise `PydanticUseDefault` to fall back to the field's default.

```python
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator
from pydantic_core import PydanticUseDefault

def null_means_default(v: Any) -> Any:
    if v is None:
        raise PydanticUseDefault()
    return v

class Config(BaseModel):
    retries: Annotated[int, BeforeValidator(null_means_default)] = 3

Config(retries=None)  # retries=3
```

## @validate_call for Function Arguments

Apply Pydantic validation to any function's parameters.

```python
from pydantic import validate_call

@validate_call
def send_email(to: str, subject: str, retries: int = 3) -> None:
    ...

send_email(to="a@b.com", subject="Hi", retries="5")  # retries coerced to 5
```
