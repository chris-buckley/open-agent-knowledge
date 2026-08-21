# Error catalog

Report the earliest failing layer and preserve the original processor cause. A useful diagnostic names the file, JSON path, JSON-LD identifier, processing stage, and suggested correction. Do not collapse every failure into `invalid JSON-LD`.

## Diagnostic record

Use this shape for machine-readable errors:

```json
{
  "ok": false,
  "error": {
    "code": "protected_term_redefinition",
    "message": "A protected term has a conflicting definition",
    "stage": "context_processing",
    "path": "$.@context.links_to",
    "identifier": "https://example.org/term/links_to",
    "details": {},
    "suggestion": "Keep the original protected definition or publish a new context version."
  }
}
```

The bundled scripts use a stable subset of these fields. Processor-native details remain in `details` when available.

## Error layers

| Layer | Examples |
|---|---|
| JSON syntax and resource | invalid UTF-8, duplicate key, size or depth exceeded |
| Document loading | unpinned context, disallowed scheme, missing file, digest mismatch, content-type rejection |
| Context processing | invalid term definition, protected-term redefinition, cyclic context, invalid import |
| Expansion and compaction | invalid IRI mapping, dropped property, value-object conflict, invalid reverse property |
| Flattening and framing | no match, ambiguous roots, illegal frame, cycle or embedding growth |
| JSON Schema | required property, union, type, or closed-object failure |
| Pydantic | alias, discriminator, scalar, field, or model validation failure |
| Graph-wide semantics | duplicate identity, absent target, conflicting record, unresolved external target |
| RDF boundary | invalid quad, unsupported direction strategy, malformed list, generalized RDF mismatch |
| Security policy | untrusted resource, limit exceeded, unauthorized resolution |

## Core script error codes

| Code | Meaning | Practical fix |
|---|---|---|
| `input_unavailable` | The input path cannot be read | Correct permissions or path |
| `input_not_file` | The path is not a regular file | Supply one JSON or JSON-LD file |
| `input_too_large` | Source exceeds the configured byte limit | Reject, split, or deliberately raise the governed limit |
| `invalid_utf8` | Source bytes are not UTF-8 | Convert the source to UTF-8 without data loss |
| `json_syntax_error` | JSON parsing failed | Correct the reported line and column |
| `duplicate_key` | An object repeats a member name | Keep one unambiguous value or use an array |
| `json_depth_exceeded` | Nesting exceeds the limit | Reject malicious input or simplify the document |
| `invalid_registry` | Registry structure or version is invalid | Use the documented version 1 registry shape |
| `registry_scheme_rejected` | A registry IRI is not HTTPS | Assign an HTTPS identity and keep local bytes pinned |
| `registry_path_escape` | A registry path escapes its directory | Place the file under the registry root |
| `remote_scheme_rejected` | The document uses a forbidden scheme | Use an approved HTTPS IRI in the registry |
| `remote_context_rejected` | A remote IRI is not pinned | Review and add an exact registry entry with digest |
| `integrity_mismatch` | Pinned bytes do not match SHA-256 | Restore reviewed bytes or publish and approve a new version |
| `content_type_rejected` | Registered media type is unsupported | Use reviewed JSON-LD-compatible content |
| `cyclic_context` | Context references form a cycle | Break the cycle and make imports acyclic |
| `context_depth_exceeded` | Context chain exceeds its limit | Flatten context dependencies or reject the input |
| `invalid_context_definition` | A context entry has an illegal type or combination | Correct it against [02 Contexts](02-contexts.md) |
| `invalid_context_nullification` | Null context would remove protected terms | Keep protected definitions or begin a new controlled scope |
| `protected_term_redefinition` | A protected mapping changed | Preserve it or version the contract |
| `processor_unavailable` | PyLD is not installed for the requested engine | Install pinned requirements or explicitly use profile mode for bundled examples |
| `processor_error` | The selected processor rejected the operation | Preserve native details and map them by stage |
| `output_too_large` | Serialized result exceeds output limits | Reduce scope, frame narrowly, or raise a governed limit |
| `profile_feature_unsupported` | Bounded profile engine received an unsupported feature | Run the default PyLD engine |
| `profile_blank_node_normalization_unsupported` | Profile engine cannot prove equivalence with blank nodes | Use RDFC-capable normalization through PyLD or another conforming tool |

## Invalid context definitions

Symptoms include an illegal `@container`, a non-string `@id` mapping, an invalid `@direction`, or incompatible `@type` and `@language` coercion.

Fix procedure:

1. Inspect the exact active context entry.
2. Expand prefixes used inside the definition.
3. Verify the legal expanded term-definition keys and combinations [S01][S02].
4. Check whether a previous scoped or protected definition is active.
5. Version and retest the context.

## Unknown or dropped terms

A compact property can disappear during expansion when it does not map to a keyword or IRI.

Fix:

- add a deliberate term definition;
- correct the spelling;
- remove an accidental `@vocab` assumption;
- enable strict dropped-property diagnostics;
- reject the document if the property is application-relevant.

Do not silently preserve unknown compact keys in a canonical graph model.

## Relative identifiers

A relative `@id` can remain unresolved when no base is available or can resolve differently under a different retrieval URL.

Fix:

- use an absolute IRI or compact IRI under a pinned context;
- set a controlled base at the document boundary;
- reject relative application identities after expansion.

[`examples/invalid/relative-identifier.jsonld`](../examples/invalid/relative-identifier.jsonld) demonstrates the graph diagnostic.

## Unexpected arrays

Expanded JSON-LD makes property values arrays. A Pydantic singular field therefore cannot consume expanded input directly.

Fix:

1. Frame or adapt to the application profile.
2. Reject multiple values for a singular field unless an explicit selection policy exists.
3. Use language, index, or type maps when the compact profile needs keyed selection.

## Value object where a reference was expected

Symptom:

```json
{"@value": "sys:service"}
```

Expected:

```json
{"@id": "https://example.org/system/service"}
```

Fix the term definition to use `"@type": "@id"`, or author an explicit reference object. Then expand again and validate the target registry.

## Lost identity through embedding

A conversion can map an embedded node to a nested anonymous Pydantic object and discard its `@id`.

Fix:

- preserve `@id` in the source model;
- reconcile embedded descriptions through a registry;
- keep recursive edges as references;
- reject two different application records for one graph ID.

## Blank-node instability

A blank-node label changes between runs or processors.

Fix:

- assign a stable IRI when the node requires durable identity;
- use RDFC-1.0 canonicalization only for dataset comparison, not as a substitute for application identifiers;
- never persist raw blank-node labels as cross-document IDs.

## Context-loading failures

Differentiate:

- absent registry entry;
- missing local file;
- digest mismatch;
- rejected media type;
- cycle;
- import error;
- processor loader contract error.

The loader diagnostic should name the requested IRI and pinned path without exposing secrets.

## Framing mismatches

An empty frame result often means the compact frame type or property expanded to a different IRI than the source. Inspect both the expanded input and expanded frame.

Several results mean the frame is too broad or the root selection is ambiguous. Do not pick the first result. Require a root `@id` or an explicit application selection rule.

## Duplicate application identities

Two source objects can share one `@id`. JSON-LD treats their compatible properties as statements about one node. An application profile may still receive conflicting scalar values or type combinations.

Fix:

1. Merge statements by graph identity before constructing application records.
2. Detect incompatible scalar or ownership claims.
3. Reject ambiguity rather than use source order.
4. Preserve every contributing source path in provenance.

## Multiple graph nodes resolving to one typed record

This can happen when an application normalizes IDs, aliases external identities, or maps several JSON-LD types to one business key.

Fix:

- make the normalization rule explicit and collision checked;
- retain original graph IDs;
- require one authoritative merge policy;
- report every colliding node and source.

## Missing target

A reference has a legal shape but its `@id` is absent from the local graph and approved external registry.

Fix:

- include the target document;
- add the target to an explicit external registry;
- correct the identifier;
- reject the graph when the relationship requires a closed target set.

Do not call this a JSON Schema error.

## Non-deterministic order

The output changes because the application used JSON member order, set-like array order, blank-node labels, or first-match behavior.

Fix:

- set ordered processing where supported;
- sort semantically unordered records by stable ID;
- preserve list order only for `@list` or application-ordered fields;
- reject duplicates before sorting;
- compare canonical graph form where appropriate.

## Debug sequence

1. Reproduce with pinned source, context, frame, processor, and options.
2. Validate UTF-8 JSON and reject duplicate keys.
3. Preflight and load every context through the registry.
4. Expand and inspect absolute property IRIs.
5. Classify each value as node reference, node definition, value, or list.
6. Flatten and inspect identity collisions and unresolved relative IDs.
7. Expand the frame and inspect its match IRIs.
8. Validate the framed source with JSON Schema.
9. Validate source and canonical Pydantic models.
10. Run graph target and external registry checks.
11. Compare semantic form rather than compact text.
