# Framing and application profiles

JSON-LD framing selects graph nodes and arranges them into a predictable JSON tree [S03]. It is often the bridge between externally variable JSON-LD and a stable Pydantic application profile. Framing is a graph query and shaping operation. It is not structural validation, graph integrity validation, authorization, or RDF reasoning.

## Architectural role

```text
External JSON-LD
  -> expansion
  -> frame against governed profile
  -> predictable application-shaped JSON
  -> JSON Schema validation
  -> Pydantic validation
  -> graph-wide checks
```

An application SHOULD validate the framed profile rather than accept arbitrary expanded objects directly. Expanded JSON-LD makes every property multi-valued and can expose shapes that do not correspond naturally to application fields.

## Frame structure

A frame is JSON-LD. It can contain a context, identifier and type match patterns, property subframes, reverse properties, named-graph frames, defaults, and framing flags.

```json
{
  "@context": "https://example.org/context/system-v1.jsonld",
  "@type": "schema:System",
  "@embed": "@once",
  "@explicit": true,
  "@requireAll": false,
  "@omitDefault": true,
  "nodes": {
    "@embed": "@always"
  },
  "relationships": {
    "@embed": "@always"
  }
}
```

The complete frame is [`examples/framed/system.frame.jsonld`](../examples/framed/system.frame.jsonld).

## Identifier and type matching

A frame can select nodes by `@id`, by `@type`, or by the presence and values of properties.

Type match:

```json
{"@type": "https://example.org/schema/System"}
```

Identifier match:

```json
{"@id": "https://example.org/system/domain"}
```

A frame with several constraints follows the framing matching rules. It is not equivalent to a Pydantic discriminated union. Use the frame to select graph nodes, then use a stable application field such as `type` for Pydantic discrimination.

## Embedding behavior

The `@embed` flag controls whether a referenced node is included as a nested object or left as a reference. JSON-LD 1.1 framing defines exactly these values: [S03]

- `@always`: embed every matching occurrence, subject to cycle handling.
- `@never`: keep references rather than embedding.
- `@once`: embed one eligible occurrence and use references for later occurrences. This is the default.

Other historical values such as `@link` and `@last` are not valid JSON-LD 1.1 Recommendation values. A governed profile MUST use the three interoperable values above.

Embedding can make data convenient for an application, but it does not create a new node. An identified object nested in two places still describes one graph node. A profile MUST protect against cyclic Python object construction and accidental identity loss.

## Explicit properties

Set `@explicit` to true when output should include only properties present in the frame. This is useful for a narrow application profile and for preventing external context data from leaking into business models.

```json
{
  "@type": "schema:System",
  "@explicit": true,
  "label": {},
  "nodes": {}
}
```

`@explicit` is a shaping rule. It does not prove that omitted graph facts were unsafe, irrelevant, or invalid. Preserve the source document and expanded graph when provenance or later reprocessing matters.

## Required matching

`@requireAll` controls how property constraints participate in matching.

- With `false`, a frame can match when any relevant frame property matches according to the framing algorithm.
- With `true`, all relevant frame properties must match.

This flag does not make the corresponding output fields required for application validation. Use JSON Schema and Pydantic for that requirement.

## Defaults and omitted defaults

A property subframe can define `@default` for nodes that lack the property.

```json
{
  "label": {
    "@default": "Unnamed"
  }
}
```

`@omitDefault` controls whether missing properties without a useful value are omitted rather than emitted with the framing preserve marker and then cleaned for output.

Defaults introduced by framing are representation defaults. They are not graph assertions unless the application later writes them as data. A profile MUST record whether a default is source data, a framing default, or a Pydantic default.

## Reverse relationships

A frame can request reverse relationships with `@reverse` or a reverse term. This lets an application receive incoming edges without changing the graph direction.

```json
{
  "@reverse": {
    "https://example.org/term/links_to": {}
  }
}
```

Reverse output can be application-friendly, but it remains a view over forward graph statements.

## Named graphs

A frame can match graph objects and named graphs. A profile MUST decide whether it is framing:

- nodes from the merged default view;
- a particular named graph;
- graph objects as application records;
- nodes grouped by graph provenance.

Do not discard graph names when they distinguish source, tenancy, version, or trust state. The supplied neutral profile does not use named graphs, so it makes no cross-graph merge claim.

## Cycles

Graph cycles are normal. A service can link to an adaptor that links back to the service. A framed JSON tree cannot embed a cycle indefinitely.

Use one or more of these controls:

- Keep some edges as reference objects.
- Use `@once` or `@never` for recursive paths.
- Build an application node registry keyed by `@id`.
- Limit object nesting and reject unexpected expansion growth.
- Preserve identity when converting embedded objects into Pydantic models.

A Pydantic application profile SHOULD represent general graph links as typed references and resolve them through a registry rather than recursively nesting an unbounded graph.

## Deterministic application expectations

Framing algorithms can reorder objects and can choose different legal embeddings when input order or frame options differ. An application that requires reproducible output MUST:

1. Pin the processor and version.
2. Pin the frame bytes and context bytes.
3. Set all material framing options explicitly.
4. Use ordered processing where supported.
5. Sort semantically unordered application collections by stable identifiers after framing.
6. Reject duplicate identifiers before choosing one record.
7. Test cycles, repeated references, missing values, and named graphs.

Do not use JSON member order to select an owner, preferred relationship, or winning record.

## Stable application profile

The bundled framed form uses these principles:

- The root is one `System` selected by identifier or external selection.
- Node and relationship collections are explicit arrays.
- Every application node carries `@id` and `@type` in the source representation.
- Relationship endpoints are reference objects.
- The application conversion maps JSON-LD types to short discriminators only after framing.
- Unknown graph facts stay in the preserved source artifact, not the canonical business model.
- Duplicate IDs and missing targets are graph-wide validation errors.

See:

- [`examples/framed/domain-extension.framed.jsonld`](../examples/framed/domain-extension.framed.jsonld)
- [`examples/pydantic/application-profile.schema.json`](../examples/pydantic/application-profile.schema.json)
- [`examples/pydantic/models.py`](../examples/pydantic/models.py)

## Practical framing workflow

1. Load source JSON with duplicate-key rejection and resource limits.
2. Resolve every remote context through the pinned local registry.
3. Expand the complete input graph.
4. Flatten when you need to inspect identities before selection.
5. Select the intended root explicitly when several systems match.
6. Apply the governed frame with explicit flags.
7. Canonicalize collection order by stable ID where order is not meaningful.
8. Validate the framed JSON with its Draft 2020-12 application schema.
9. Validate and convert it with Pydantic.
10. Run graph-wide duplicate and target checks.
11. Preserve the source digest, context digest, processor version, frame digest, and selected root in provenance.

## Failure patterns

| Symptom | Likely cause | Fix |
|---|---|---|
| Empty framed output | `@id`, `@type`, graph, or property constraints do not match | Inspect expanded IRIs and frame the intended graph |
| Several roots | Frame is too broad or the input has several valid matches | Supply a root identifier or reject ambiguity |
| Repeated large objects | `@embed` is too permissive | Use `@once`, `@never`, or reference subframes |
| Missing property | `@explicit` omitted it, the source lacks it, or its IRI differs | Inspect expanded input and frame mappings |
| Unexpected default | Frame introduced `@default` | Label and validate representation defaults separately |
| Recursive output or memory growth | Cyclic graph plus aggressive embedding | Keep recursive links as references and apply limits |
| Output passes frame but fails model | Framing selected data but did not enforce application constraints | Treat the Pydantic failure as expected application validation |

## Processor boundary

PyLD 3.1.0 is the default framing processor [S09][S10]. The bundled profile engine implements only the included neutral frame pattern. It MUST fail or be treated as unsupported for arbitrary frames, advanced named-graph framing, `@link` object identity, and complete framing conformance.
