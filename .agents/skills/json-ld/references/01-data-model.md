# Data model, forms, identity, and relationships

Authority: [S01], [S02], [S06], [S08].

## Core mental model

JSON-LD is JSON interpreted as Linked Data. A JSON parser sees objects, arrays, strings, numbers, booleans, and null. A JSON-LD processor additionally applies context rules so that local property names, types, and identifiers resolve to IRIs and graph values. [S01]

An agent MUST keep these responsibilities separate:

- `@context` establishes term meaning and selected compact authoring shapes.
- `@id` identifies a node or, in a term definition, a property.
- `@type` assigns one or more types to a node or datatype to a value.
- A non-keyword property normally denotes a directed predicate from the containing node to another node or a literal value.
- JSON Schema validates a selected JSON representation.
- Pydantic validates and executes a selected application representation.
- JSON-LD processing interprets linked-data syntax and transforms representations.
- A separate graph-validation step checks cross-node rules such as target existence and cardinality across documents.

JSON-LD context processing is not schema validation. A context can expand `links_to` to a stable predicate IRI, but it does not require the property, limit its count, or prove that a referenced node exists. JSON Schema can require an `@id` string, but it does not apply context expansion. Pydantic can validate a framed profile and run graph checks, but it does not perform JSON-LD expansion or RDF reasoning.

Several different JSON documents can describe the same graph. An embedded node, a top-level node plus a reference, a reverse property, and a flattened node map can preserve the same directed relation while presenting different JSON trees. Agents MUST compare graph meaning when semantic equivalence matters. They MUST NOT infer semantic inequality from changed object order, array order outside `@list`, keyword aliases, term selection, or embedding alone.

## Five representations that MUST remain distinct

### Authored document shape

This is the compact form a person or upstream system writes. It may use terms, compact IRIs, context-driven scalar coercion, container maps, embedding, and source-specific layout.

```json
{
  "@context": "https://example.org/context/system-v1.jsonld",
  "@id": "sys:domain/adaptor",
  "@type": "Adaptor",
  "label": "Domain adaptor",
  "links_to": "sys:base/service"
}
```

Use this form at a governed authoring boundary. Treat its context and base IRI as part of the contract.

### Application model shape

This is the stable data shape selected for application code. It SHOULD avoid arbitrary JSON-LD variability. It can use clean field names and typed unions after processing and framing.

```json
{
  "id": "sys:domain/adaptor",
  "kind": "Adaptor",
  "label": "Domain adaptor",
  "links_to": "sys:base/service"
}
```

Use this form inside application services and Pydantic models. Preserve source and JSON-LD provenance beside it rather than forcing every processing detail into business models.

### Expanded JSON-LD form

Expansion removes the context from the result, expands terms and compact IRIs, expresses values explicitly, and normally represents property values as arrays. [S02]

```json
[
  {
    "@id": "https://example.org/system/domain/adaptor",
    "@type": [
      "https://example.org/schema/Adaptor"
    ],
    "https://example.org/term/label": [
      {
        "@value": "Domain adaptor"
      }
    ],
    "https://example.org/term/links_to": [
      {
        "@id": "https://example.org/system/base/service"
      }
    ]
  }
]
```

Use expanded form at a semantic normalization boundary, when inspecting exact property IRIs, or before graph operations. Do not map arbitrary expanded data directly to a narrow Pydantic model unless an explicit adapter handles arrays, value objects, lists, graphs, and multiple types.

### Flattened node graph

Flattening first expands data, creates a node map, gathers each node's properties, assigns processing-local blank-node labels when needed, and replaces embedded node definitions with references. [S02]

```json
[
  {
    "@id": "https://example.org/system/domain/adaptor",
    "@type": [
      "https://example.org/schema/Adaptor"
    ],
    "https://example.org/term/links_to": [
      {
        "@id": "https://example.org/system/base/service"
      }
    ]
  },
  {
    "@id": "https://example.org/system/base/service",
    "@type": [
      "https://example.org/schema/Service"
    ]
  }
]
```

Use flattened form for registries, duplicate detection, target resolution, node merging, and graph inspection. Preserve graph names when named graphs matter.

### RDF dataset

An RDF dataset contains a default graph and zero or more named graphs. Each graph contains triples whose subject and predicate identify graph terms and whose object is a node or literal. JSON-LD can serialize an RDF dataset, and the API defines conversion in both directions. [S02] [S06]

Use the RDF boundary for interchange with RDF tools, dataset canonicalization, or exact graph comparison. Ordinary JSON-LD application processing does not require SPARQL, OWL, SHACL, or an RDF database.

## Recommended architectural boundaries

| Boundary | Preferred representation | Reason |
|---|---|---|
| Human or source authoring | Compact JSON-LD with a pinned context | Readable and governed |
| Untrusted ingress | Raw bytes plus provenance, then safe JSON parsing | Security and auditability |
| Meaning normalization | Expanded JSON-LD | Full property and type IRIs |
| Node registry and target checks | Flattened expanded graph | One logical entry per named node |
| Application validation | Framed compact application profile | Predictable arrays, embedding, and field names |
| Typed runtime | Canonical Pydantic application model | Executable application rules |
| Interchange with RDF systems | RDF dataset or N-Quads | Graph-native interchange |
| Semantic equality or signing | Canonicalized RDF dataset when available | Serialization-independent comparison |

An application MAY select a different boundary form, but it MUST document which forms are accepted and emitted. It MUST NOT accept arbitrary compact JSON-LD directly into a narrow application model merely because the input is valid JSON.

## Node definitions and node references

A node object describes zero or more properties of a node. A node reference is a node object containing only `@id`. [S01]

Definition:

```json
{
  "@id": "sys:base/service",
  "@type": "Service",
  "label": "Inherited service"
}
```

Reference:

```json
{
  "@id": "sys:base/service"
}
```

An agent MUST distinguish them. A reference does not define the target node's type or properties. Embedding a definition under another node does not make that node subordinate in graph identity. The same identified node can be defined elsewhere and referenced from many documents.

Use a node reference when:

- The target is defined in another part of the document or another governed document.
- Repeating the full definition would create conflicting copies.
- The relationship should remain a link rather than imply ownership.
- A frame or application registry will resolve the target later.

Use an embedded node definition when:

- The authored profile intentionally co-locates the definition.
- The embedded object carries properties, not only `@id`.
- The application boundary expects the embedded shape.
- Identity remains explicit when the node must be referenced elsewhere.

A processor can change embedding during framing without changing node identity. Application code MUST use `@id`, not object location, as the identity key.

## Named nodes and blank nodes

A named node uses an IRI as its identifier. A blank node lacks a global IRI and may receive a processing-local identifier beginning with `_:`. Blank-node identifiers are not durable identifiers across documents or processing runs. [S01] [S06] [S07]

Use a named node for anything that must support:

- Cross-document references.
- Durable provenance.
- Stable updates or renames.
- Independent approval or ownership.
- Deduplication across sources.
- Audit logs and generated artifacts.
- Relationship properties or lifecycle.

Use a blank node only when the node is genuinely local, has no independent lifecycle, will not be referenced outside the containing graph, and does not need a stable audit identity. A blank node MUST NOT be used as a convenient substitute for an identifier that the application will later need.

## Identifier strategy

### Absolute IRIs are the semantic identity

The expanded `@id` SHOULD be an absolute IRI controlled by a stable namespace owner. Compact IRIs and human-readable terms are authoring conveniences. Their expansion is the identity.

```text
Compact:  sys:orders/database
Expanded: https://example.org/system/orders/database
```

The context MUST define `sys` consistently wherever that compact IRI is used.

### Namespace ownership

A project SHOULD allocate separate namespaces for entities, relationships, schemas, and vocabulary terms. This is a project convention, not a W3C requirement.

```text
https://example.org/system/
https://example.org/relationship/
https://example.org/schema/
https://example.org/term/
https://example.org/document/
```

Namespace policy SHOULD state:

- Who controls allocation.
- Whether identifiers are case-sensitive.
- Which characters are permitted in slugs.
- Whether identifiers may be reused after deletion.
- How redirects or equivalence are recorded after migration.
- How test and production namespaces differ.

### Stable identity MUST be independent of file path

A file location identifies a source document. It SHOULD NOT silently define entity identity. Moving `systems/orders.jsonld` to `platform/orders.jsonld` must not change `https://example.org/system/orders` unless the entity itself changed identity.

Record source location separately, for example:

```json
{
  "@id": "sys:orders",
  "source_document": "doc:systems-orders-v3"
}
```

### Entity, schema, and source identities are different

- Entity identity names a thing in the represented domain.
- Schema identity names a structural or semantic contract.
- Vocabulary identity names a class or property meaning.
- Document identity names a source artifact or published representation.

Do not use the schema's `$id` as the entity's `@id`. Do not use a file URL as the entity identity merely because the entity is serialized there.

### Version vocabulary and documents deliberately

Vocabulary terms SHOULD retain stable IRIs while their compatible descriptions evolve. Introduce a new term IRI when meaning changes incompatibly. A context document SHOULD have an immutable versioned URL, even when it maps stable term IRIs.

Example:

```text
Context document: https://example.org/context/system-v1.jsonld
Property identity: https://example.org/term/links_to
Schema identity:   https://example.org/schema/system-profile/1.0
```

A document version can change while entity identity remains stable. Record document version, content hash, or revision metadata separately.

### Human-readable slugs

Readable slugs improve diagnostics and authoring, but they MUST NOT be treated as display labels. A label can change without changing identity. A slug change SHOULD preserve the original IRI or record an explicit migration. Silent IRI changes create new graph nodes.

### Example identifier conventions

The following patterns are illustrative project conventions, not W3C requirements:

```text
system:orders
system:orders/database
relationship:orders-stores-in-orders-db
schema:System
term:stores_in
```

A corresponding context could map them to owned absolute IRI namespaces. A project MAY use URNs, HTTPS IRIs, DIDs, or another valid IRI scheme, but it SHOULD prefer identifiers with clear governance and long-term control.

## Relationship representations

JSON-LD does not assign application behavior to a relationship term. A property IRI gives the predicate stable meaning. Application behavior, validation, ownership, or generation rules require explicit application contracts.

### Direct property

```json
{
  "@context": {
    "sys": {
      "@id": "https://example.org/system/",
      "@prefix": true
    },
    "stores_in": {
      "@id": "https://example.org/term/stores_in",
      "@type": "@id"
    }
  },
  "@id": "sys:orders",
  "stores_in": "sys:orders-db"
}
```

The graph edge is:

```text
sys:orders --term:stores_in--> sys:orders-db
```

Use a direct property for the ordinary case where the edge needs no independent identity or properties.

### Reverse property

```json
{
  "@context": {
    "sys": {
      "@id": "https://example.org/system/",
      "@prefix": true
    },
    "stores_in": {
      "@id": "https://example.org/term/stores_in",
      "@type": "@id"
    }
  },
  "@id": "sys:orders-db",
  "@reverse": {
    "stores_in": {
      "@id": "sys:orders"
    }
  }
}
```

This describes the same directed edge. `@reverse` changes the authoring direction, not the predicate direction. Use it when the document naturally starts from the object or when a reverse term improves a compact profile.

A term definition can also use `@reverse` to define a reverse property alias. Agents MUST expand before comparing direct and reverse authoring forms.

### First-class relationship node

```json
{
  "@context": "https://example.org/context/system-v1.jsonld",
  "@id": "rel:orders-storage",
  "@type": "Relationship",
  "kind": "term:stores_in",
  "from": "sys:orders",
  "to": "sys:orders-db",
  "confidence": 0.98,
  "source_document": "doc:architecture-review"
}
```

This is an application-level relationship model. JSON-LD sees a node with properties. The application decides that `kind`, `from`, and `to` encode an edge.

Promote a relationship to a first-class node when it needs one or more of:

- Provenance or evidence.
- Confidence or quality state.
- Ownership or approval.
- Effective dates or temporal versions.
- Constraints or qualifiers.
- An independent identifier.
- Independent lifecycle or audit history.
- Generator or compiler instructions.
- References from other nodes.

A first-class relationship node can coexist with a direct edge, but the project MUST define whether both are required and how consistency is checked. JSON-LD will not automatically infer the direct edge from the reified node.

## Neutral base and extension example

The skill examples model this structure:

```text
Base system
|- Service
`- Store

Domain extension
|- extends the base system
|- introduces an Adaptor
`- links the Adaptor to the inherited Service
```

The base and domain documents preserve stable node identities across files. The domain document contains a node reference to the inherited service. The combined bundle lets the frame embed the service into the application profile. The relationship node carries its own identifier and provenance fields.

Use these examples only to learn JSON-LD mechanics. They do not define the future system vocabulary, compiler, projection engine, or domain ontology.

## Provenance chain

A reliable pipeline SHOULD retain at least:

```text
source bytes and SHA-256
-> source document path or IRI
-> resolved context IRIs and hashes
-> processor name, version, and options
-> expanded or framed artifact hash
-> graph node @id
-> Pydantic model identity
```

Provenance SHOULD remain metadata about processing. Do not confuse the source document identity with the represented entity identity. The included scripts emit source paths, byte counts, hashes, and context preflight results in their machine-readable envelopes.
