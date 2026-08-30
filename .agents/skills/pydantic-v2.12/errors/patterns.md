# Errors — Recurring Patterns

## Basic Catch and Report

Standard pattern for catching validation failures and extracting structured error details.

```python
from pydantic import BaseModel, ValidationError

class Item(BaseModel):
    name: str
    price: float

try:
    Item(name="widget", price="free")
except ValidationError as e:
    for err in e.errors():
        loc = ".".join(str(x) for x in err["loc"])
        print(f"{loc}: {err['msg']} (type={err['type']})")
```

## Custom Error Messages (Post-Processing)

Map machine-readable error types to user-friendly messages after catching.

```python
MESSAGES = {
    "missing": "This field is required.",
    "int_parsing": "Must be a whole number.",
    "string_too_short": "Too short (min {min_length} chars).",
}

def friendly_errors(e: ValidationError) -> list[dict]:
    result = []
    for err in e.errors():
        tpl = MESSAGES.get(err["type"])
        msg = tpl.format(**err.get("ctx", {})) if tpl else err["msg"]
        result.append({"field": err["loc"], "message": msg})
    return result
```

## PydanticCustomError in Validators

Produce custom error types with template messages for domain-specific validation.

```python
from pydantic_core import PydanticCustomError
from pydantic import BaseModel, field_validator

class Order(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def check_positive(cls, v: int) -> int:
        if v <= 0:
            raise PydanticCustomError(
                "positive_required",
                "Must be positive, got {value}",
                {"value": v},
            )
        return v
```

## FastAPI Error Propagation

Let FastAPI handle ValidationError for request bodies automatically; catch manually for custom logic.

```python
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError

class Payload(BaseModel):
    threshold: float

def apply(raw: dict):
    try:
        return Payload(**raw)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
```

## Batch Error Collection

Validate many records and collect all failures with record indices.

```python
all_errors = []
for i, record in enumerate(records):
    try:
        Model(**record)
    except ValidationError as e:
        for err in e.errors():
            all_errors.append({"record": i, "loc": err["loc"], "msg": err["msg"]})
```

## Error Filtering by Type

Separate different error categories for targeted handling.

```python
try:
    Model(**data)
except ValidationError as e:
    missing = [err for err in e.errors() if err["type"] == "missing"]
    type_errs = [err for err in e.errors() if err["type"].endswith("_type")]
```

## Dot-Notation Location Formatting

Convert the tuple-based `loc` path to human-readable dot notation.

```python
def loc_to_dot(loc: tuple) -> str:
    parts = []
    for x in loc:
        if isinstance(x, int):
            parts.append(f"[{x}]")
        else:
            parts.append(f".{x}" if parts else x)
    return "".join(parts)

# ("items", 1, "name") -> "items[1].name"
```
