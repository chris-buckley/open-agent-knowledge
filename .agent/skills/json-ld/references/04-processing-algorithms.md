# Processing algorithms

The JSON-LD API defines document loading, context processing, expansion, compaction, flattening, and RDF conversion [S02]. Framing is defined separately [S03]. These algorithms transform representations. They do not perform application validation, authorization, inference, or arbitrary RDF reasoning.

## Safe processing pipeline

Use this boundary for external JSON-LD:

```text
bytes
  -> bounded UTF-8 JSON parsing with duplicate-key rejection
  -> pinned document loading
  -> context preflight and context processing
  -> expansion
  -> optional flattening or framing
  -> application-profile validation
  -> graph-wide checks
```

The bundled scripts enforce the first four trust controls before invoking PyLD. Arbitrary network retrieval is disabled by default.

## Document loading

### Purpose

Document loading obtains the input document or a referenced remote context and returns the final document URL, media type, optional context URL, and parsed document.

### Safe input and output

Input:

```text
https://example.org/context/system-v1.jsonld
```

Pinned registry entry:

```json
{
  "path": "system-context.jsonld",
  "sha256": "<expected digest>",
  "content_type": "application/ld+json"
}
```

Output to the processor:

```json
{
  "documentUrl": "https://example.org/context/system-v1.jsonld",
  "contextUrl": null,
  "contentType": "application/ld+json",
  "document": {"@context": {}}
}
```

### Use case

Use a local exact-match registry for builds, tests, and ingestion. This makes the context bytes, URL, and digest reproducible.

### Failure

A context IRI absent from the registry fails with `remote_context_rejected`. The scripts do not silently fetch it.

### Possible transformation

HTTP redirects can change the final document URL and therefore the base used for relative resolution. The supplied loader avoids that uncertainty by refusing network access.

## Context processing

### Purpose

Context processing turns `@context` values into an active context containing term mappings, base, vocabulary, language, direction, protection, and scoped contexts.

### Minimal before and after

Before:

```json
{
  "@context": {
    "sys": {
      "@id": "https://example.org/system/",
      "@prefix": true
    },
    "links_to": {
      "@id": "https://example.org/term/links_to",
      "@type": "@id"
    }
  }
}
```

Conceptual active state:

```text
sys -> https://example.org/system/ as a prefix
links_to -> https://example.org/term/links_to
links_to values -> node identifiers
```

### Use case

Use context processing before interpreting any compact term or compact IRI.

### Failure

A protected term redefined with a different mapping fails. A cyclic remote context or context import fails.

### Possible transformation

Context processing itself does not rewrite the source JSON. It changes how later algorithms interpret it.

## Expansion

### Purpose

Expansion removes context-dependent abbreviations and produces a context-independent JSON-LD form. Properties use expanded IRIs. Most property values become arrays. Literals become value objects and references become node-reference objects.

### Before

```json
{
  "@context": {
    "sys": "https://example.org/system/",
    "term": "https://example.org/term/",
    "links_to": {
      "@id": "term:links_to",
      "@type": "@id"
    }
  },
  "@id": "sys:adaptor",
  "links_to": "sys:service"
}
```

### After

```json
[
  {
    "@id": "https://example.org/system/adaptor",
    "https://example.org/term/links_to": [
      {"@id": "https://example.org/system/service"}
    ]
  }
]
```

### Use case

Expand at an ingestion or comparison boundary to remove dependence on local terms and keyword aliases.

### Failure

A term definition that maps a node-reference field as a literal can yield a value object where the application expects `@id`. An invalid context can stop expansion before any graph is produced.

### What can change

Expansion can:

- introduce arrays around property values;
- replace terms and compact IRIs with absolute IRIs;
- replace scalar values with value objects;
- remove `@context`, maps, `@nest`, `@set`, and keyword aliases;
- reorder object members where the processor offers ordered output;
- drop properties that do not expand to an IRI, depending on processing and error policy.

The scripts install a strict dropped-property callback when PyLD exposes it. An application MUST still inspect processor diagnostics.

### Command

```bash
python scripts/expand.py examples/compact/system-bundle.jsonld \
  --registry examples/contexts/registry.json \
  --engine profile --raw
```

Use `--engine pyld` for general standards processing after installing the pinned dependencies.

## Compaction

### Purpose

Compaction applies a supplied context to expanded data. It chooses terms, compact IRIs, keyword aliases, scalar forms, maps, and containers to produce a concise document.

### Before

```json
[
  {
    "@id": "https://example.org/system/adaptor",
    "https://example.org/term/links_to": [
      {"@id": "https://example.org/system/service"}
    ]
  }
]
```

### After

```json
{
  "@context": "https://example.org/context/system-v1.jsonld",
  "@id": "sys:adaptor",
  "links_to": "sys:service"
}
```

The exact compact shape depends on the selected context and processor options.

### Use case

Compact when emitting a governed external document or restoring a human-oriented profile.

### Failure

Using the wrong context can map a familiar term to a different predicate. Compaction can also produce an array where an application expects a scalar when several values exist.

### What can change

Compaction can:

- choose different equivalent terms according to term-selection rules;
- collapse one-element arrays;
- introduce language, index, identifier, type, or graph maps;
- use `@nest`, aliases, prefixes, or `@vocab`;
- change member order and formatting.

Compaction does not delete graph facts merely to satisfy a Pydantic field. Frame or validate first, and reject cardinality conflicts explicitly.

### Command

```bash
python scripts/compact.py examples/expanded/system-bundle.expanded.json \
  --context examples/contexts/system-context.jsonld \
  --registry examples/contexts/registry.json \
  --engine profile --raw
```

## Flattening

### Purpose

Flattening collects graph nodes into a node map, merges descriptions with the same identifier, and emits a top-level array or compact `@graph` form.

### Before

```json
{
  "@id": "https://example.org/system/a",
  "https://example.org/term/links_to": {
    "@id": "https://example.org/system/b",
    "https://example.org/term/label": "B"
  }
}
```

### After, simplified expanded form

```json
[
  {
    "@id": "https://example.org/system/a",
    "https://example.org/term/links_to": [
      {"@id": "https://example.org/system/b"}
    ]
  },
  {
    "@id": "https://example.org/system/b",
    "https://example.org/term/label": [
      {"@value": "B"}
    ]
  }
]
```

### Use case

Flatten before building a node registry, detecting duplicate application identities, or checking reference targets.

### Failure

Flattening can assign blank-node identifiers. An application that stores those labels as durable IDs will become unstable across processors or runs.

### What can change

Flattening can:

- move embedded node definitions to top-level nodes;
- replace embedded definitions with references;
- merge descriptions sharing an identifier;
- assign blank-node identifiers;
- reorder nodes and properties.

It does not select an application root or enforce an application shape.

### Command

```bash
python scripts/flatten.py examples/compact/system-bundle.jsonld \
  --registry examples/contexts/registry.json \
  --engine profile --raw
```

## Framing

Framing selects matching nodes and arranges them into a predictable tree. See [05 Framing](05-framing.md) for the complete application boundary.

Minimal use:

```bash
python scripts/frame.py examples/compact/system-bundle.jsonld \
  --frame examples/framed/system.frame.jsonld \
  --registry examples/contexts/registry.json \
  --engine profile --raw
```

The profile engine supports only the included frame pattern. PyLD is required for general framing.

## To-RDF conversion

### Purpose

To-RDF conversion turns expanded JSON-LD into an RDF dataset containing quads.

### Conceptual before

```json
{
  "@id": "https://example.org/system/a",
  "https://example.org/term/links_to": {
    "@id": "https://example.org/system/b"
  }
}
```

### N-Quads result

```text
<https://example.org/system/a> <https://example.org/term/links_to> <https://example.org/system/b> .
```

### Use case

Use RDF conversion when an RDF store, dataset comparison, RDF canonicalization, or RDF serialization is an actual boundary.

### Failure

Relative identifiers, invalid value objects, unsupported generalized RDF predicates, or an undeclared text-direction policy can fail or transform unexpectedly.

### What can change or be lost

- Compact document shape, aliases, nesting, and maps are lost.
- `@index` is not represented unless an option or vocabulary maps it.
- Native JSON values become RDF literals, including RDF JSON literals when `@json` is used.
- Lists become RDF collections.
- Blank-node labels can change.
- Directional language strings require the selected `rdfDirection` strategy.

## From-RDF conversion

### Purpose

From-RDF conversion turns an RDF dataset into expanded JSON-LD.

### Before

```text
<https://example.org/system/a> <https://example.org/term/links_to> <https://example.org/system/b> .
```

### After

```json
[
  {
    "@id": "https://example.org/system/a",
    "https://example.org/term/links_to": [
      {"@id": "https://example.org/system/b"}
    ]
  }
]
```

### Use case

Use it when RDF data must enter the JSON-LD pipeline before framing and Pydantic validation.

### Failure and transformations

RDF datasets do not preserve the original JSON spelling, object order, aliases, scalar-versus-array choices, or embedding. Native types can be reconstructed only under the selected options. Malformed RDF collections might remain as ordinary RDF nodes rather than become `@list` objects.

## Important API options

Verify option names against the selected processor. The W3C algorithms define the behavior, while a library defines its function signatures. Application-relevant options include: [S02][S03][S09]

- `base`: base IRI for resolving document-relative references.
- `compactArrays`: allow eligible one-element arrays to become scalars during compaction.
- `compactToRelative`: allow compacted IRIs to become relative to the base.
- `documentLoader`: resolve remote documents and contexts.
- `expandContext`: process an additional context before expansion.
- `extractAllScripts`: control extraction from HTML script elements where HTML input is supported.
- `ordered`: request deterministic lexicographic processing where the algorithm permits it.
- `processingMode`: select JSON-LD 1.1 behavior.
- `produceGeneralizedRdf`: permit generalized RDF output where supported.
- `rdfDirection`: choose how base direction maps through RDF.
- `useNativeTypes`: recover native JSON scalar types from RDF literals.
- `useRdfType`: preserve `rdf:type` as a predicate instead of converting it to `@type`.

Do not pass unverified flags from another implementation. The supplied adapter sets JSON-LD 1.1 processing, ordered output, a pinned document loader, and strict diagnostics where PyLD supports them.

## Determinism limits

`ordered` can make JSON output more reproducible. It does not make JSON object order semantic. Two correct processors can produce structurally different expanded, flattened, or framed JSON for the same graph.

Use these comparison levels deliberately:

1. Text comparison for exact golden formatting only.
2. Parsed JSON comparison when array order and blank-node labels are already controlled.
3. Expanded named-node normal form for the bounded examples.
4. RDFC-1.0 canonical N-Quads for a general RDF dataset when semantic equivalence must include blank nodes [S07].

The semantic round-trip script never treats compact textual equality as proof of graph equality.
