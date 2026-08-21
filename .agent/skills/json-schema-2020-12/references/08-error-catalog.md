# 08 Error catalog

The codes in this file are skill-local diagnostic conventions. They are not JSON Schema standard error codes.

## Error record

A machine-readable error SHOULD include:

```json
{
  "code": "JS2020-008",
  "document": "instance.json",
  "instancePath": "/nodes/0",
  "schemaResource": "https://example.org/schema/retail-lending",
  "schemaPath": "/$defs/RetailNode/oneOf",
  "keyword": "oneOf",
  "message": "...",
  "cause": "...",
  "repair": "..."
}
```

Omit fields that do not apply. Never invent a path that the validator did not report.

## Catalog

| Code | Category | Meaning | Required response |
| --- | --- | --- | --- |
| `JS2020-001` | JSON | A schema, instance, or registry file is not valid unambiguous JSON, including duplicate object keys. | Report file and parser details or duplicate key; do not continue. |
| `JS2020-002` | Dialect | `$schema` is missing, malformed, or unsupported. | Report the found value; require an explicit supported dialect. |
| `JS2020-003` | Schema | The schema fails its declared meta-schema. | Report schema location and meta-schema location; fix before instance validation. |
| `JS2020-004` | Vocabulary | A required vocabulary is unsupported. | Name the dialect and vocabulary URI; refuse processing. |
| `JS2020-005` | Registry | A registry URI or path is unsafe, a key disagrees with the resource `$id`, or one URI maps to conflicting contents. | Report the manifest entry and preserve one canonical owner; require explicit authorization for external paths. |
| `JS2020-006` | Reference | `$ref` or the initial `$dynamicRef` target cannot resolve. | Report authored reference, current base, absolute URI, and source path; do not fetch implicitly. |
| `JS2020-007` | Anchor | A JSON Pointer, `$anchor`, or `$dynamicAnchor` fragment is absent or invalid. | Report resource URI and fragment; repair the target or reference. |
| `JS2020-008` | Instance | A valid schema rejects an instance. | Report instance path, schema resource, schema path, keyword, and nested context. |
| `JS2020-009` | Union | `oneOf` matched zero branches. | Preserve child errors grouped by branch; inspect the discriminator and required fields. |
| `JS2020-010` | Union | `oneOf` matched more than one branch. | Identify overlapping branches; add mutually exclusive tag assertions. |
| `JS2020-011` | Closure | `additionalProperties` rejects an extension field declared elsewhere. | Move closure to the complete leaf and use `unevaluatedProperties` when composition is intended. |
| `JS2020-012` | Closure | `unevaluatedProperties` or `unevaluatedItems` rejects a location. | Identify which successful branches evaluated locations; add the field to an applicable branch or remove it. |
| `JS2020-013` | Format | Assertion was requested but no checker exists for a used format. | Register and test a checker, choose annotation policy, or replace the format with portable assertions. |
| `JS2020-014` | Content | A caller assumed content annotations decoded or validated a string. | Run a separate bounded content processor and report its result separately. |
| `JS2020-015` | Recursion | Recursive evaluation fails at a descendant or exceeds an operational bound. | Report deepest paths and selected resource; distinguish schema failure from resource limits. |
| `JS2020-016` | Graph | A structurally valid reference field names no application object. | Run the graph checker; report source relationship and missing target. |
| `JS2020-017` | Graph | Application object identifiers are duplicated. | Report every conflicting instance path; apply project uniqueness policy. |
| `JS2020-018` | Pydantic | Pydantic accepts a value rejected by the schema, or the reverse. | Compare strictness, aliases, mode, custom validators, and schema extras; document or remove the divergence. |
| `JS2020-019` | Pydantic | Regenerated schema differs from the committed artifact. | Pin versions, inspect the semantic diff, rerun fixtures, and review compatibility before updating. |
| `JS2020-020` | OpenAPI | An OpenAPI projection drops or changes JSON Schema behavior. | Name the dialect or keyword difference; retain the root schema and reject lossy projection unless approved. |

## Common diagnoses

### Extra property after `allOf`

Symptom: a property declared in one branch is rejected by `additionalProperties: false` in another.

Cause: `additionalProperties` only recognizes sibling property declarations.

Repair: keep the extensible base open and use `unevaluatedProperties: false` at the final composed leaf.

### Default did not appear

Symptom: a missing property remains absent after validation.

Cause: `default` is an annotation.

Repair: add a separate construction/defaulting step, define conflict rules, and validate the resulting instance.

### Invalid URI passed

Symptom: a string with `format: uri` validates.

Cause: format assertion was not enabled, or the implementation lacks the checker.

Repair: disclose and enable assertion policy, require a checker, and add portable structural constraints where needed.

### Relative reference looked in the wrong place

Symptom: a loader searched beside the file but the resolved URI points elsewhere.

Cause: `$id` changed the base URI.

Repair: compute the RFC 3986 result, register that canonical URI, and stop using filesystem adjacency as reference semantics.

### Missing target passed JSON Schema

Symptom: `"to": "node:missing"` validates as a string.

Cause: JSON Schema checked the reference-object shape, not graph referential integrity.

Repair: run the graph validation layer after structural validation.

### Pydantic default differs from JSON Schema

Symptom: Pydantic constructs a field that a general JSON Schema validator leaves absent.

Cause: Pydantic runtime defaults and JSON Schema annotations have different behavior.

Repair: separate accepted input, constructed model, and serialized output; publish the appropriate schema mode and defaulting policy.
