# Keywords, object forms, and containers

Read this reference after [02 Contexts](02-contexts.md). The syntax rules come from JSON-LD 1.1 [S01]. Processing consequences come from the JSON-LD API [S02].

## Keyword rules

JSON-LD keywords begin with `@`. An agent MUST use keywords only where their object form permits them. A context MAY alias application-relevant keywords such as `@id` and `@type`, but `@context` itself MUST NOT be aliased. Unknown strings beginning with `@` are not ordinary application properties.

| Keyword | Main role | Important constraint |
|---|---|---|
| `@context` | Supplies term definitions and processing state | The value is null, an object, a string IRI, or an array of those forms |
| `@id` | Identifies a node or maps a term to an IRI | A node-reference object contains only `@id`, except for an optional `@index` in permitted processing forms |
| `@type` | Assigns node types or a value datatype | A node can have one or more types; a value object cannot combine `@type` with `@language` or `@direction` |
| `@value` | Holds a literal value | The surrounding object is a value object, not a node object |
| `@language` | Tags a string with a language | Use only with string values and never beside an ordinary datatype |
| `@direction` | Records base text direction | The value is `ltr` or `rtl`; RDF conversion requires an explicit direction strategy |
| `@index` | Carries an index annotation or map key | The value is a string; ordinary RDF conversion does not preserve it unless a strategy maps it |
| `@list` | Represents one ordered RDF collection | A list object cannot also describe a node |
| `@set` | Forces an array-shaped authoring form | It usually adds no distinct graph meaning beyond its values |
| `@graph` | Holds a graph or named graph contents | A top-level `@graph` wrapper can group nodes without creating a node |
| `@included` | Includes node objects without making them values of a property | The value is one or more node objects |
| `@reverse` | States relationships in the inverse direction | Expansion restores ordinary forward predicates |
| `@nest` | Groups compact properties under another object | Nesting changes authoring shape, not graph meaning |
| `@none` | Supplies a fallback map key | It represents no language, index, identifier, or type key, depending on the container |
| `@json` | Marks an opaque JSON literal datatype | Use through `@type`; it is not a node container |
| `@container` | Declares a compact collection or map shape | Only the combinations permitted by JSON-LD 1.1 are legal |

## Node objects and node references

A node object describes a graph node. It can carry `@id`, `@type`, properties, `@reverse`, `@graph`, `@included`, and other legal node-object entries.

```json
{
  "@id": "https://example.org/system/orders",
  "@type": "https://example.org/schema/Service",
  "https://example.org/term/label": [
    {"@value": "Orders"}
  ]
}
```

A node-reference object points to a node without defining its properties.

```json
{"@id": "https://example.org/system/orders"}
```

An agent MUST distinguish a reference from an embedded definition. Repeating an identified node with additional properties contributes more statements about the same node. It does not create a private nested copy.

## Value objects

A value object represents a literal.

```json
{"@value": "Service", "@language": "en"}
```

```json
{
  "@value": 0.98,
  "@type": "http://www.w3.org/2001/XMLSchema#decimal"
}
```

Application-relevant legal combinations include:

- `@value` alone.
- `@value` with `@type`.
- A string `@value` with `@language`, optionally with `@direction`.
- `@value` with `@index` where the expanded processing form permits the annotation.

A value object MUST NOT contain node properties, `@id`, `@graph`, `@list`, or both `@type` and `@language`. Native JSON values remain JSON values during JSON-LD processing, but RDF conversion can assign datatypes or transform them according to options. [S01][S02]

## List objects

A list object preserves order and allows repeated values.

```json
{
  "@list": [
    {"@id": "https://example.org/system/first"},
    {"@id": "https://example.org/system/second"}
  ]
}
```

A list is semantically different from an unordered multi-valued property. An agent MUST NOT replace a list with a set merely because both are JSON arrays in some representation. RDF conversion lowers a list to an RDF collection structure and reconstructs it when possible.

## Set objects

A set object forces a value to remain array-shaped in compact JSON-LD.

```json
{"@set": [{"@id": "https://example.org/system/orders"}]}
```

`@set` is generally a processing convenience. Expansion removes the wrapper and retains its values. It does not assert mathematical set semantics, uniqueness, or ordering.

## Graph objects and named graphs

A top-level graph wrapper can carry a collection of nodes:

```json
{
  "@context": "https://example.org/context/system-v1.jsonld",
  "@graph": [
    {"@id": "sys:base", "@type": "schema:System"},
    {"@id": "sys:base/service", "@type": "schema:Service"}
  ]
}
```

An object with both `@id` and `@graph` names a graph:

```json
{
  "@id": "https://example.org/graph/base",
  "@graph": [
    {"@id": "https://example.org/system/base"}
  ]
}
```

An RDF dataset can hold statements in the default graph and in named graphs. A named graph IRI identifies the graph name. It does not automatically identify every node inside the graph.

## Included nodes

`@included` lets a node object include other node objects without asserting a property from the outer node to them.

```json
{
  "@id": "https://example.org/system/base",
  "@included": [
    {"@id": "https://example.org/system/base/service"}
  ]
}
```

Use `@included` when the included statements belong in the same document or graph but no application predicate should connect them. Do not mistake document co-location for a graph relationship.

## Reverse properties

A reverse relationship can be written explicitly:

```json
{
  "@id": "sys:orders-db",
  "@reverse": {
    "stores_in": {"@id": "sys:orders"}
  }
}
```

It describes the same directed edge as this forward form:

```json
{
  "@id": "sys:orders",
  "stores_in": {"@id": "sys:orders-db"}
}
```

A context can also define a reverse term with `@reverse`. A reverse property changes compact authoring direction. It does not invent an inverse application behavior or a separate predicate.

## Nested properties

A context can map a term to `@nest` or use `@nest` directly to group compact properties.

```json
{
  "@context": {
    "details": "@nest",
    "label": "https://example.org/term/label"
  },
  "@id": "https://example.org/system/base",
  "details": {
    "label": "Base system"
  }
}
```

Expansion treats `label` as a property of the outer node. `details` is not a predicate and does not survive as a graph edge. Use nesting only for a governed authoring profile.

## Language, index, identifier, and type maps

Containers can turn compact maps into explicit expanded objects.

### Language map

```json
{
  "@context": {
    "label": {
      "@id": "https://example.org/term/label",
      "@container": "@language"
    }
  },
  "label": {
    "en": "Service",
    "fr": "Service"
  }
}
```

Expansion yields language-tagged value objects.

### Index map

```json
{
  "@context": {
    "component": {
      "@id": "https://example.org/term/component",
      "@container": "@index"
    }
  },
  "component": {
    "primary": {"@id": "https://example.org/system/service"}
  }
}
```

Expansion attaches `"@index": "primary"` to the node object. The index is an annotation used by JSON-LD processing. It is not an RDF predicate unless an explicit profile maps it.

### Identifier map

```json
{
  "@context": {
    "members": {
      "@id": "https://example.org/term/member",
      "@container": "@id"
    }
  },
  "members": {
    "https://example.org/system/service": {
      "@type": "https://example.org/schema/Service"
    }
  }
}
```

The map key expands into the node's `@id`.

### Type map

```json
{
  "@context": {
    "members": {
      "@id": "https://example.org/term/member",
      "@container": "@type"
    }
  },
  "members": {
    "https://example.org/schema/Service": {
      "@id": "https://example.org/system/service"
    }
  }
}
```

The map key contributes a type to each mapped node.

The complete executable examples are in [`examples/containers/`](../examples/containers/).

## Permitted container combinations

A term definition can use one container keyword or one permitted array combination. JSON-LD 1.1 permits these application-relevant forms: [S01]

- One of `@set`, `@list`, `@language`, `@index`, `@id`, `@type`, or `@graph`.
- `@set` combined with one of `@index`, `@id`, `@graph`, `@type`, or `@language`.
- `@graph` combined with either `@id` or `@index`, optionally also with `@set`.

An agent MUST NOT invent other combinations. Container arrays are sets of keywords for validation purposes, even though their JSON order can differ.

## Blank and named nodes

A named node uses an absolute or compacted IRI identity. A blank node has a processor-local identifier such as `_:b0` or no authored identifier.

Blank-node labels are not durable cross-run identities. Processors can rename them during flattening, RDF conversion, or canonicalization. Use a named node when a record must be referenced across documents, governed, versioned, owned, or reconciled with a Pydantic object.

## Processing convenience versus graph meaning

The following differences can disappear after expansion or RDF conversion:

- Keyword aliases versus canonical keywords.
- Nesting with `@nest` versus un-nested properties.
- A scalar versus a one-element array where the context does not distinguish cardinality.
- A `@set` wrapper versus its values.
- A language, index, identifier, type, or graph map versus explicit objects.
- A reverse authoring form versus the equivalent forward edge.

The following differences remain semantically important:

- Different expanded IRIs.
- A literal versus a node reference.
- Different datatypes, language tags, or text directions.
- An ordered list versus unordered multiple values.
- Different graph names.
- Different named-node identifiers.

A semantic round trip MAY change formatting, order, aliases, map shape, or embedding. It MUST preserve the graph distinctions required by the profile.
