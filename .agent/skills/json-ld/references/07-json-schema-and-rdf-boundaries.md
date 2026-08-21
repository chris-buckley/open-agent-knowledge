# JSON Schema and RDF boundaries

JSON Schema, JSON-LD, Pydantic, and RDF serve different contracts. Keep their responsibilities explicit.

## JSON Schema boundary

JSON Schema Draft 2020-12 validates one selected JSON representation [S13]. It does not process a JSON-LD context or establish graph meaning.

A compact document and its expanded form usually need different schemas:

- Compact properties can use terms, compact IRIs, scalars, maps, and keyword aliases.
- Expanded properties use absolute IRIs and arrays of node, value, or list objects.
- A framed application profile can use a small, stable shape chosen for Pydantic.

A project SHOULD publish a schema for the representation that crosses its structural boundary. It SHOULD NOT attempt one schema that accepts every equivalent JSON-LD serialization.

## What JSON Schema can validate

A profile schema can require:

- `@id` and `@type` fields;
- allowed application type strings;
- node-reference object shape;
- arrays and cardinality in the framed representation;
- value types, ranges, patterns, and required properties;
- closed application objects with `unevaluatedProperties` or `additionalProperties` rules.

Example reference shape:

```json
{
  "type": "object",
  "required": ["@id"],
  "properties": {
    "@id": {"type": "string", "minLength": 1}
  },
  "additionalProperties": false
}
```

## What JSON Schema cannot establish

JSON Schema alone cannot prove that:

- a compact term expands to the intended IRI;
- a remote context is trusted or pinned;
- a reference target exists elsewhere in the graph;
- two embedded objects describe the same application record correctly;
- an IRI is owned by the claimed namespace authority;
- a reverse form and forward form are semantically equivalent;
- a frame selected the correct root;
- an RDF inference or graph-wide path constraint holds.

The same compact property name can carry different meaning under different contexts:

```json
{"@context": {"owner": "https://a.example/owner"}, "owner": "A"}
```

```json
{"@context": {"owner": "https://b.example/custodian"}, "owner": "A"}
```

A structural schema that sees only the key `owner` cannot establish which predicate it denotes.

## Application-profile schema

The bundled schema validates the framed source form:

[`examples/pydantic/application-profile.schema.json`](../examples/pydantic/application-profile.schema.json)

It intentionally does not claim full semantic validation. The missing-target fixture proves the boundary:

1. The reference object has a valid `@id` shape.
2. The JSON Schema passes.
3. The Pydantic graph check fails because the target registry has no matching node.

## RDF mental model

RDF describes statements as subject, predicate, and object. [S06]

```text
subject:   https://example.org/system/orders
predicate: https://example.org/term/links_to
object:    https://example.org/system/orders-db
```

- Subjects are IRIs or blank nodes.
- Predicates are IRIs in ordinary RDF 1.1.
- Objects are IRIs, blank nodes, or literals.
- A graph is a set of triples.
- An RDF dataset has one default graph and zero or more named graphs.
- A named graph pairs a graph name with a graph.

JSON-LD can represent this model while retaining JSON authoring conveniences.

## IRIs

An IRI globally identifies a node, predicate, class, graph name, or datatype. An absolute IRI is independent of a document base. A compact IRI becomes absolute only after context processing.

An application SHOULD use stable absolute identities at the canonical boundary. Compact IRIs are a serialization convenience.

## Literals

An RDF literal has a lexical or native value and a datatype or language tag. JSON-LD value objects can also carry text direction before RDF conversion.

Examples:

```json
{"@value": "Service", "@language": "en"}
```

```json
{
  "@value": "2026-08-05",
  "@type": "http://www.w3.org/2001/XMLSchema#date"
}
```

Application validation still determines allowed formats and ranges.

## Blank nodes

A blank node has graph-local existence without a durable IRI. Blank-node labels are serialization artifacts. They can change under flattening, merging, RDF parsing, or canonicalization.

Do not use blank nodes for records that need:

- cross-document references;
- durable Pydantic identity;
- ownership or audit trails;
- independent updates;
- stable relationship IDs;
- long-lived provenance.

## Lists

JSON-LD `@list` maps to an RDF collection, represented through linked RDF list nodes. Conversion can introduce blank nodes and several triples. From-RDF conversion can reconstruct a list only when the collection structure is well formed.

An ordinary array of multiple property values is not an RDF list.

## Native JSON values and `@json`

Ordinary JSON booleans and numbers can map to RDF typed literals. A value coerced to `@json` maps to an RDF JSON literal. This preserves an opaque JSON value at the RDF boundary, not its internal JSON properties as graph predicates.

Use `@json` for deliberately opaque payloads. Prefer graph modelling when relationships inside the payload need identity, queries, provenance, or validation.

## Directional language strings

JSON-LD can express `@language` and `@direction`. RDF 1.1 did not have one universal direct representation for base direction. The JSON-LD API therefore exposes an `rdfDirection` strategy. The selected strategy can create compound literals or i18n datatype IRIs [S02].

A pipeline MUST choose and record its direction strategy before RDF conversion. It MUST NOT silently drop direction when it matters.

## Named graphs and provenance

Named graphs can separate source documents, trust states, versions, tenants, or evidence groups. JSON-LD graph objects preserve graph names through `@id` plus `@graph`.

Do not merge named graphs into one application view unless the profile defines:

- which graphs participate;
- how conflicts are resolved;
- which provenance survives;
- whether the same node ID can have different statements in different graphs.

## Generalized RDF

Some processors can produce generalized RDF, which may allow blank-node predicates or other extensions beyond ordinary RDF 1.1. Use it only when a downstream system explicitly supports it. The default skill profile keeps ordinary predicate IRIs and does not require generalized RDF.

## Information transformed at the RDF boundary

RDF conversion normally does not preserve:

- source object member order;
- whitespace and formatting;
- keyword aliases;
- compact terms and prefixes;
- `@nest` grouping;
- compact maps and scalar-versus-array spelling;
- source file boundaries unless modelled;
- `@index` unless explicitly mapped;
- original blank-node labels.

RDF can preserve node identities, predicates, literals, lists, graph names, datatypes, and language information under the selected conversion options.

## Semantic comparison

Parsed JSON equality is insufficient for general graph equivalence. RDFC-1.0 defines deterministic RDF dataset canonicalization, including blank-node relabeling [S07]. PyLD exposes the historical `URDNA2015` normalization option. The skill labels that API name as an implementation compatibility surface, not the current W3C algorithm name.

Use RDFC-1.0 tooling when a general dataset equivalence proof is required. The profile engine compares only named-node examples and refuses blank-node normalization claims.

## Bounded RDF use

Ordinary JSON-LD application processing does not require SPARQL, OWL, SHACL, or an RDF store. Introduce those technologies only when the application has a clear query, inference, or graph-validation requirement that the current Pydantic, JSON Schema, and graph-check layers do not meet.
