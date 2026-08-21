# JSON Schema — Recurring Patterns

## Validation vs Serialization Mode

Generate different schemas depending on the consumer (input validation vs output documentation).

```python
schema_in = Model.model_json_schema(mode="validation")    # what the model accepts
schema_out = Model.model_json_schema(mode="serialization") # what model_dump() produces
```

## WithJsonSchema Override

Replace the generated schema for a custom or third-party type without touching core schema.

```python
from typing import Annotated
from pydantic import BaseModel, WithJsonSchema

GeoJson = Annotated[
    dict,
    WithJsonSchema({"type": "object", "properties": {"lat": {"type": "number"}, "lng": {"type": "number"}}}),
]

class Location(BaseModel):
    coords: GeoJson
```

## SkipJsonSchema for Internal Fields

Exclude fields from the public schema while keeping them in the model.

```python
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

class Model(BaseModel):
    public_id: int
    internal_state: SkipJsonSchema[dict] = {}  # excluded from schema
```

## json_schema_extra for OpenAPI Extensions

Inject vendor-specific extensions or extra metadata.

```python
from pydantic import BaseModel, ConfigDict

class Endpoint(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"x-api-version": "2.0", "x-deprecated-since": "1.5"}
    )
    path: str
```

## Multi-Model Combined Schema

Generate a single schema document with `$defs` for multiple models (useful for code generators).

```python
from pydantic import BaseModel
from pydantic.json_schema import models_json_schema

class Foo(BaseModel):
    a: str

class Bar(BaseModel):
    b: int

_, combined = models_json_schema(
    [(Foo, "validation"), (Bar, "validation")],
    title="MyAPI",
)
```

## Custom Ref Template for OpenAPI

Change `$ref` paths to match OpenAPI component schema layout.

```python
schema = Model.model_json_schema(
    ref_template="#/components/schemas/{model}"
)
```

## GenerateJsonSchema Subclass

Override the generator for project-wide schema customizations.

```python
from pydantic.json_schema import GenerateJsonSchema

class StrictSchema(GenerateJsonSchema):
    def generate(self, schema, mode="validation"):
        result = super().generate(schema, mode=mode)
        result["additionalProperties"] = False
        return result

Model.model_json_schema(schema_generator=StrictSchema)
```

## Merging Annotated json_schema_extra

Stack multiple `json_schema_extra` dicts across `Annotated` layers — they merge additively.

```python
from typing import Annotated
from pydantic import Field, TypeAdapter

BaseType = Annotated[int, Field(json_schema_extra={"x-source": "base"})]
Extended = Annotated[BaseType, Field(json_schema_extra={"x-extended": True})]

TypeAdapter(Extended).json_schema()
# {"type": "integer", "x-source": "base", "x-extended": true}
```
