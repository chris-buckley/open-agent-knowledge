# Serialization — Recurring Patterns

## Reusable Annotated Serializer

Define serialization logic as a type alias. Composable in nested types.

```python
from typing import Annotated
from pydantic import BaseModel, PlainSerializer

EpochSeconds = Annotated[
    datetime,
    PlainSerializer(lambda v: int(v.timestamp()), return_type=int),
]

class Event(BaseModel):
    created: EpochSeconds
```

## Mode-Aware Serializer

Produce different output for Python vs JSON serialization modes.

```python
from pydantic import BaseModel, field_serializer, FieldSerializationInfo

class Model(BaseModel):
    data: bytes

    @field_serializer("data")
    def ser_data(self, v: bytes, info: FieldSerializationInfo) -> str | bytes:
        if info.mode == "json":
            return v.hex()
        return v
```

## Serialization Context

Pass runtime data into serializers for dynamic behavior.

```python
from pydantic import BaseModel, field_serializer, FieldSerializationInfo

class Article(BaseModel):
    body: str

    @field_serializer("body")
    @classmethod
    def trim_body(cls, v: str, info: FieldSerializationInfo) -> str:
        if isinstance(info.context, dict):
            max_len = info.context.get("max_body_length", 0)
            if max_len and len(v) > max_len:
                return v[:max_len] + "..."
        return v

article.model_dump(context={"max_body_length": 200})
```

## PATCH-Friendly exclude_unset

Serialize only fields that were explicitly provided. Essential for HTTP PATCH operations.

```python
from pydantic import BaseModel

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None

update = UserUpdate(name="new_name")
update.model_dump(exclude_unset=True)  # {"name": "new_name"} — email omitted
```

## SerializeAsAny for Subclass Fields

Include subclass fields in serialization output when the annotation is a base type.

```python
from pydantic import BaseModel, SerializeAsAny

class Animal(BaseModel):
    name: str

class Dog(Animal):
    breed: str

class Zoo(BaseModel):
    resident: SerializeAsAny[Animal]

zoo = Zoo(resident=Dog(name="Rex", breed="Lab"))
zoo.model_dump()  # {"resident": {"name": "Rex", "breed": "Lab"}}
```

## Wrap Serializer for Post-Processing

Run default serialization, then modify the result.

```python
from pydantic import BaseModel, model_serializer, SerializerFunctionWrapHandler

class Audit(BaseModel):
    user: str
    action: str

    @model_serializer(mode="wrap")
    def add_meta(self, handler: SerializerFunctionWrapHandler) -> dict:
        data = handler(self)
        data["_version"] = 2
        return data
```

## Nested Field Inclusion/Exclusion

Selectively include or exclude nested fields at serialization time.

```python
user.model_dump(include={"id": True, "address": {"city"}})
user.model_dump(exclude={"address": {"zip_code"}})
user.model_dump(exclude={"items": {"__all__": {"internal_id"}}})  # all items
```

## Partial JSON Parsing (LLM Streaming)

Parse incomplete JSON for streaming/progressive validation.

```python
from pydantic_core import from_json
from pydantic import BaseModel

class Chunk(BaseModel):
    text: str = ""
    done: bool = False

partial = '{"text": "hello", "done'
Chunk.model_validate(from_json(partial, allow_partial=True))
```
