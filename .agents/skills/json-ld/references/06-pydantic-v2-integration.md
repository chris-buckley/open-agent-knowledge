# Pydantic v2 integration

Pydantic validates typed Python application data. It does not process JSON-LD contexts, expand IRIs, compact documents, frame graphs, convert RDF, or infer graph meaning. Use a JSON-LD processor before Pydantic [S02][S03][S12].

## Integration boundary

Inbound:

```text
External JSON-LD
  -> safe document loading
  -> context processing
  -> expansion or framing
  -> stable source representation
  -> Pydantic validation
  -> canonical application model
  -> graph-wide validation
```

Outbound:

```text
Pydantic application model
  -> source representation with keyword aliases
  -> JSON-LD processor and governed context
  -> compact JSON-LD
  -> semantic verification
```

Do not pass arbitrary expanded JSON-LD directly into a business model. Expanded properties are absolute IRIs and their values are arrays even when the application expects one scalar.

## Separate source and application models

The source representation mirrors the selected framed JSON-LD profile. It can retain `@context`, `@id`, `@type`, node references, source document IDs, and provenance.

The canonical application model uses application names and stable discriminators. It should not carry context machinery unless the application needs to display or re-emit it.

```text
FramedSystemSource
  @context
  @id
  @type
  nodes: FramedNodeSource[]
  relationships: FramedRelationshipSource[]

ApplicationSystem
  id
  type = System
  nodes: Service | Store | Adaptor
  relationships: Relationship[]
  provenance
```

This separation prevents a context change or compact spelling from becoming a silent business-model change.

## Keyword aliases in Pydantic

Use Pydantic aliases for source fields that retain JSON-LD keywords.

```python
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field

class SourceModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_by_alias=True,
        validate_by_name=True,
    )

class NodeReference(SourceModel):
    id: str = Field(alias="@id")

class ServiceSource(SourceModel):
    id: str = Field(alias="@id")
    type: Literal["schema:Service"] = Field(alias="@type")
```

`validate_by_alias=True` accepts the external keyword spelling. `validate_by_name=True` accepts the Python field name where an internal caller needs it. Serializing with `model_dump(by_alias=True)` restores the keyword spelling. These are the current fine-grained configuration controls. The older broad `populate_by_name` setting should not be the first choice in new examples [S12].

Use `validation_alias` and `serialization_alias` when inbound and outbound spellings differ. Keep one canonical external form for the governed profile.

## Discriminated unions

Expanded JSON-LD can assign several type IRIs to one node. A Pydantic discriminator is normally a single application field. Convert the processed source types into an explicit application discriminator before validating a discriminated union.

```python
class Service(BaseModel):
    type: Literal["Service"]

class Store(BaseModel):
    type: Literal["Store"]

class Adaptor(BaseModel):
    type: Literal["Adaptor"]

Node = Annotated[Service | Store | Adaptor, Field(discriminator="type")]
```

The conversion MUST define what happens when:

- the node has no recognized application type;
- it has several recognized types;
- a type is inherited or inferred elsewhere;
- two contexts compact the same type IRI differently.

Discriminate on resolved type identity, not an unprocessed compact spelling.

## Reference objects and embedded objects

Use a small reference model for ordinary graph links:

```python
class NodeReference(BaseModel):
    id: str
```

Use an embedded object model only where the frame intentionally embeds the definition. Preserve the embedded object's `@id` so repeated embeddings can be reconciled to one application identity.

A node registry is usually safer than recursive object nesting:

```python
registry = {node.id: node for node in system.nodes}
target = registry[relationship.to_ref.id]
```

The registry MUST reject duplicate IDs. It MUST NOT let the last object in input order silently win.

## Arrays in expanded JSON-LD

Expanded property values are arrays. A source adapter MUST handle cardinality before constructing a singular field.

For a singular application label:

- zero values can be missing or defaulted according to the application profile;
- one value can be unwrapped after validating its value-object form;
- more than one value MUST be rejected or resolved by an explicit language, index, type, or priority policy.

Do not select the first array element merely because a processor returned it first.

## Model-level graph checks

Pydantic model validators can enforce graph-wide application invariants after structural parsing.

The bundled example checks:

- duplicate node IDs;
- duplicate relationship IDs;
- relationship `from` and `to` targets;
- adaptor links to existing nodes;
- an externally selected root identifier.

Pydantic validation context can carry a known external registry or source selection:

```python
System.model_validate(data, context={"external_ids": {"sys:base"}})
```

Use validation context for invocation-specific facts. Do not hide durable application truth in ambient global state.

## Missing targets

This reference is structurally valid:

```json
{"@id": "sys:missing"}
```

JSON Schema and Pydantic can validate that it has an `@id` string. Only a node registry or external resolver can establish whether the target exists. Treat absence as a graph-wide semantic error.

The fixture [`examples/invalid/missing-target.framed.jsonld`](../examples/invalid/missing-target.framed.jsonld) passes its JSON Schema but fails the application graph validator.

## Preserving provenance

Record enough information to reproduce each typed record:

- source path or source document IRI;
- source document SHA-256;
- context IRI and pinned context SHA-256;
- processor name and version;
- processing mode and material options;
- frame IRI or path and SHA-256;
- selected root `@id`;
- original node `@id`;
- source JSON path where available;
- validation profile version.

Do not attach all source machinery to every business field. Store a compact provenance object or registry that links the application record back to the preserved source artifact.

## JSON-LD to Pydantic

The executable example follows this sequence:

1. Safely load and frame the source graph.
2. Validate the framed source representation.
3. Convert JSON-LD type IRIs and references to application fields.
4. Validate the canonical model with graph context.
5. Emit canonical JSON with deterministic sorting.

Run:

```bash
python examples/pydantic/jsonld_to_pydantic.py \
  examples/compact/system-bundle.jsonld \
  --engine profile \
  --external-id sys:base
```

See [`examples/pydantic/models.py`](../examples/pydantic/models.py).

## Pydantic to JSON-LD

Outbound conversion MUST restore stable graph identities before compaction.

1. Validate the canonical application model.
2. Convert every application node and relationship to a source representation with `@id` and `@type`.
3. Use reference objects for graph edges.
4. Attach the governed context IRI.
5. Compact with the selected processor when the intermediate form is expanded.
6. Expand the emitted document again and compare semantic form.

Run:

```bash
python examples/pydantic/pydantic_to_jsonld.py \
  examples/pydantic/application-system.json \
  --engine profile
```

Textual output can differ from the original while graph meaning remains equivalent.

## Preventing context leakage

A business model generally should not expose:

- term definitions;
- remote context URLs as mutable user fields;
- processor options;
- keyword aliases;
- compact IRI prefixes as application identity.

Keep those facts in source models, processing configuration, and provenance. Expose resolved identities and application types to the canonical model.

## Validation order

Use this order so errors retain their correct layer:

1. JSON syntax and resource limits.
2. Context and JSON-LD processing.
3. Framed source-model validation.
4. JSON Schema validation where portability is required.
5. Canonical Pydantic model validation.
6. Graph-wide target, uniqueness, and external-resolution checks.

A later layer MUST NOT relabel an earlier context error as a generic model error.
