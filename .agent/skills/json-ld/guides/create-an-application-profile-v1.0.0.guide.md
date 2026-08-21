# Create a JSON-LD application profile

Use this guide to turn variable JSON-LD graph input into a stable Pydantic and JSON Schema boundary. Read [05 Framing](../references/05-framing.md), [06 Pydantic](../references/06-pydantic-v2-integration.md), and [07 Boundaries](../references/07-json-schema-and-rdf-boundaries.md).

## Procedure

1. Name the application root type and root-selection rule.
2. List the exact node and relationship types the application accepts.
3. Decide which graph facts remain references and which may be embedded.
4. Define a frame with explicit matching and embedding flags.
5. Keep graph cycles as references or bounded embeddings.
6. Define a source Pydantic model that mirrors the framed JSON-LD shape.
7. Alias retained JSON-LD keywords such as `@id` and `@type`.
8. Define a separate canonical application model with resolved type discriminators.
9. Decide how zero, one, and several expanded values map to each field.
10. Define a Draft 2020-12 schema for the framed source representation.
11. Add model-level duplicate and target checks.
12. Define the approved external identifier registry.
13. Preserve source, context, processor, frame, root, and digest provenance.
14. Test unknown types, multiple types, duplicate IDs, missing targets, and several roots.
15. Test outbound conversion and semantic re-expansion.

## Stable-profile rules

- Do not validate arbitrary compact JSON-LD as the canonical model.
- Do not expose context term definitions as mutable business fields.
- Do not select the first value when cardinality is ambiguous.
- Do not let embedding remove `@id`.
- Do not let JSON Schema success stand in for target existence.
- Do not let Pydantic imply JSON-LD processing.
- Do not discard source artifacts needed for reprocessing or audit.

## Required artifacts

Produce:

1. A versioned frame.
2. A framed valid example.
3. A source-model schema.
4. Source and canonical Pydantic models.
5. Inbound and outbound adapters.
6. Graph-wide validators.
7. Semantic round-trip tests.
8. A provenance contract.
