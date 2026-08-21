# 05 Pydantic v2 integration

Authority: current official Pydantic v2 documentation and package metadata listed in [00 Source manifest](00-source-manifest.md).

## Boundary

Use Pydantic v2 as the executable Python model and JSON Schema as a portable structural projection:

```text
Pydantic model and validators
    -> model_json_schema or TypeAdapter.json_schema
    -> reviewed Draft 2020-12 document
    -> portable validators, editors, generators, and OpenAPI projections
```

The reverse path is not automatic equivalence:

```text
external JSON instance
    -> JSON Schema validation at a document boundary
    -> Pydantic runtime validation and conversion
    -> application-level semantic checks
```

A generated schema contains only constraints and annotations represented or deliberately added during schema generation. It does not acquire application semantics that were never present in the model or hook.

## Generation APIs

Use `BaseModel.model_json_schema()` for a model class:

```python
schema = RetailLendingSystem.model_json_schema(
    by_alias=True,
    mode="validation",
    ref_template="#/$defs/{model}",
)
```

Use `TypeAdapter.json_schema()` for arbitrary supported types, including a union that is not itself a `BaseModel`:

```python
schema = TypeAdapter(Node).json_schema(
    by_alias=True,
    mode="validation",
    ref_template="#/$defs/{model}",
)
```

Both return JSON-serializable dictionaries. They do not serialize a model instance.

Pydantic v2 currently emits JSON Schema Draft 2020-12 compatible schemas and documents OpenAPI 3.1 compatibility. A standalone emitted document SHOULD still add an explicit `$schema` and a project-owned `$id`, then pass this skill's meta-schema and reference checks.

## `$defs` and reference templates

Pydantic normally places reusable model definitions under `$defs` and emits `$ref` entries to them.

`ref_template` changes the emitted reference strings. It does not move definitions out of `$defs` automatically. A custom template MUST remain resolvable in the final document or registry.

Do not treat generated `$defs` keys as permanent public API names unless the project tests and controls them. Model renames, generic specialization names, and generator changes can alter them.

## Aliases and external field names

Use aliases when Python identifiers differ from contract field names:

```python
class RelationshipCore(BaseModel):
    from_: Identifier = Field(alias="from")
```

Generate with `by_alias=True` so the schema describes the external field name. Configure validation by alias and, when needed, by field name explicitly. Serialize examples with `model_dump(mode="json", by_alias=True)`.

Pydantic distinguishes validation aliases and serialization aliases. A project MUST decide whether one JSON Schema describes accepted input, emitted output, or both. Generate separate validation and serialization schemas when the shapes differ.

## Discriminated unions

Prefer a discriminated union for tagged variants:

```python
Node = Annotated[
    ServiceNode | StoreNode | ContainerNode,
    Field(discriminator="kind"),
]
```

Each model branch SHOULD use `Literal` for the discriminator value. Pydantic can then validate efficiently and emit a union with branch references and discriminator metadata.

The portable JSON Schema validity still comes from `oneOf` branch constraints such as `const`. A consumer that ignores the OpenAPI-style `discriminator` annotation can still validate correctly.

## Recursive models

Use forward annotations and rebuild models after all types exist when Pydantic cannot resolve them automatically:

```python
class ContainerNode(BaseModel):
    children: list["Node"]

ContainerNode.model_rebuild(_types_namespace={"Node": Node})
```

Generated recursive models normally use `$defs` and `$ref`. Pydantic does not automatically invent a `$dynamicRef` extension protocol. Hand-author or post-process such a protocol only with matching runtime behavior and tests.

## Generic models

Pydantic generic models can generate schemas for concrete specializations. Generate the exact specialization consumed at the boundary. Do not publish the unspecialized Python generic as if JSON Schema had Python type variables.

Test the emitted definition names and reference graph if downstream tools depend on them. Prefer stable project-owned wrapper models for public contracts.

## Strict and non-strict runtime validation

Pydantic normally performs useful coercion. Strict mode narrows coercion, but exact behavior can vary by type and whether validation starts from Python data or JSON text.

JSON Schema validates JSON values after parsing. It does not coerce `"1"` into `1`. Therefore a non-strict Pydantic model can accept inputs that its emitted JSON Schema rejects.

For a portable boundary, an agent SHOULD:

1. validate the incoming JSON representation before Pydantic coercion, or use a strict Pydantic boundary model;
2. test both accepted and rejected values against both validators;
3. document any intentional difference;
4. never claim runtime and schema equivalence without evidence.

The included example sets `strict=True` and `extra="forbid"` for leaf records to reduce divergence.

## Validation and serialization modes

`mode="validation"` describes values accepted by Pydantic validation.

`mode="serialization"` describes serialized output. Types such as `Decimal`, computed fields, serializers, and aliases can produce different schemas in the two modes.

Generate and version both when an API has different input and output contracts. Do not merge them by intuition.

## `json_schema_extra`

Use `json_schema_extra` at field or model level to add annotations or project-owned schema keywords:

```python
model_config = ConfigDict(
    json_schema_extra={
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://example.org/schema/retail-lending-pydantic",
    }
)
```

Pydantic accepts a dictionary or callable in supported locations. Treat the result as generated code: validate it, diff it, and test representative instances.

Adding an assertion through `json_schema_extra` does not automatically add matching Pydantic runtime validation. Conversely, a Python validator does not automatically become a portable JSON Schema assertion.

## Custom schema hooks

Use narrow, documented customization first:

- `Field` metadata for common constraints and annotations;
- `json_schema_extra` for additive schema metadata;
- `WithJsonSchema` for a deliberate type-level override;
- `__get_pydantic_json_schema__` for custom JSON Schema generation;
- a `GenerateJsonSchema` subclass for broad generation policy.

A custom JSON Schema hook changes the emitted schema. It does not change Pydantic core validation unless a matching core-schema or validator hook also exists.

Avoid depending on private `__pydantic_core_schema__` structure. Use documented public hooks.

## Constructs that do not map faithfully

Pydantic runtime behavior may exceed portable JSON Schema when it uses:

- arbitrary Python callables or external services;
- model or field validators with cross-field logic;
- context-dependent validation;
- Python object identity, classes, or protocols;
- coercion sequences and custom parsing;
- authorization, database lookups, or graph target checks;
- serializer logic that cannot be described structurally.

JSON Schema may exceed automatic Pydantic generation when it uses:

- custom vocabularies;
- `$dynamicAnchor` and `$dynamicRef` extension protocols;
- annotation collection and output requirements;
- complex `unevaluatedProperties` or `unevaluatedItems` composition;
- content-processing annotations;
- schema resources and bundling designed independently of Python models;
- assertions for which Pydantic needs a custom validator.

Do not force either system to pretend it implements the other. Define the boundary and add the missing check in the correct layer.

## Defaults differ

A Pydantic field default can populate a model when input omits the field. The emitted JSON Schema `default` remains an annotation for other validators.

Therefore:

- a JSON Schema validator will not construct the same model output merely from the schema;
- a field with a Pydantic default may be absent from `required`;
- downstream generators need their own documented default policy;
- validation should run again after any tool inserts defaults.

## Review checklist

Before publishing a generated schema, an agent MUST:

1. pin the Pydantic version used for generation;
2. choose validation or serialization mode;
3. choose alias behavior;
4. add and verify `$schema` and `$id`;
5. validate the generated schema against the Draft 2020-12 meta-schema;
6. resolve all generated references;
7. compare generated output with the committed artifact;
8. test valid and invalid instances in both Pydantic and JSON Schema;
9. list intentional runtime/schema differences;
10. run graph or business validation separately.

See [`examples/pydantic/model.py`](../examples/pydantic/model.py) and [generate from Pydantic](../processes/generate-from-pydantic.md).
