# JSON-LD skill build report

Build date: 2026-08-05 UTC.

## Delivery summary

The build produced a complete installable `json-ld` agent skill with 12 numbered standards references, 5 task guides, 4 APS processes, 6 required processing CLIs, a safe shared loader, a bounded offline profile engine, Pydantic v2 integration, a Draft 2020-12 application-profile schema, neutral JSON-LD examples, invalid fixtures, tests, and packaging metadata.

The skill keeps authored JSON-LD, expanded form, flattened graph, framed application profile, RDF dataset, and typed application models separate. It does not define the later application vocabulary, graph compiler, projection engine, or language server.

## Governing inputs

The supplied File Library contained `aps.md`, including the skill-authoring guide, template, build process, APS references, and generic platform adapter. The build followed its filename, frontmatter, layout, reference, guide, process, and text-hygiene rules.

No completed `pydantic-v2` skill or completed `json-schema-2020-12` skill was available in the supplied File Library. Only their build prompts were present. The implementation therefore used current official Pydantic v2 and JSON Schema Draft 2020-12 documentation directly and limited that material to the JSON-LD integration boundary.

## Sources consulted

The complete source, status, version, retrieval date, and use manifest is [references/00-source-manifest.md](references/00-source-manifest.md).

Primary authorities:

| Area | Authority | Verified status |
|---|---|---|
| JSON-LD syntax | W3C JSON-LD 1.1 | Recommendation, 16 July 2020 |
| Processing algorithms and API | W3C JSON-LD 1.1 Processing Algorithms and API | Recommendation, 16 July 2020 |
| Framing | W3C JSON-LD 1.1 Framing | Recommendation, 16 July 2020 |
| Processor tests | W3C JSON-LD API and Framing test suites | Current hosted manifests, exact PyLD-pinned commits recorded |
| RDF model | RDF 1.1 Concepts | Recommendation, 25 February 2014 |
| Dataset canonicalization | RDFC-1.0 | W3C Recommendation |
| Pydantic | Official Pydantic documentation and package release | 2.13.4 |
| JSON Schema | Official Draft 2020-12 publication | Draft 2020-12 |
| Default processor | Official PyLD package and source | 3.1.0 |

All technical claims in the skill cite source keys from the source manifest. Neutral `https://example.org/` identifiers are labelled as examples rather than W3C conventions.

## Processor evaluation

The evaluated routes were PyLD 3.1.0, RDFLib 7.6.0, TRLD 0.3.0, jsonld.js 9.0.0, and the included bounded profile engine. The full matrix is [references/10-processor-evaluation.md](references/10-processor-evaluation.md).

### Selected processor

**PyLD 3.1.0** is the default because it provides the required Python operation surface:

- expansion;
- compaction;
- flattening;
- framing;
- To-RDF and From-RDF operations;
- a custom document loader;
- normalization through its documented compatibility API;
- an upstream test harness with exact official-suite submodule pins;
- Python 3.10 or newer support;
- an active release current at the build date.

The scripts default to `--engine pyld`. They return `processor_unavailable` when PyLD is absent. They never silently fall back.

### Bounded offline engine

`--engine profile` selects `scripts/profile_engine.py`. It exists so the examples, safety controls, graph checks, Pydantic bridge, and semantic demonstrations can run offline when PyLD is unavailable.

It is not a general conforming processor. It supports only the declared profile used by the included examples. Unsupported areas are listed below and in the processor reference.

### Alternative route

`jsonld.js` 9.0.0 is the verified alternative implementation route when a reduced case exposes a PyLD defect or unsupported feature. A future Node adapter must retain the same pinned document-loader and provenance contract.

RDFLib remains useful at the RDF parse and serialization boundary. It was not selected as the full JSON-LD framing processor.

## Architecture and design choices

### Representation boundaries

The skill uses this inbound path:

```text
untrusted JSON bytes
  -> strict bounded JSON parser
  -> pinned local document loader
  -> context preflight
  -> expansion
  -> optional flattening
  -> framing
  -> Draft 2020-12 source-profile validation
  -> Pydantic source model
  -> canonical application model
  -> graph-wide target and uniqueness checks
```

Outbound processing validates the canonical Pydantic model, reconstructs identified JSON-LD source objects, applies the governed context, and then re-expands the output for semantic comparison.

### Identity

Canonical application identity uses expanded IRIs. Compact IRIs remain a serialization convenience. File paths, object order, labels, and blank-node labels are not treated as durable identities.

### Relationships

The examples demonstrate direct properties, reverse properties, and first-class relationship nodes. Relationship nodes carry their own identifiers, provenance, confidence, and effective dates where needed.

### Application profile

Framing produces one stable source shape for Pydantic and JSON Schema. Source models preserve JSON-LD keywords and references. Canonical application models do not expose context definitions. Expanded multi-value arrays are resolved before singular application fields are constructed.

### Semantic comparison

The PyLD route uses its normalization API with the implementation's historical `URDNA2015` option. The profile route compares a bounded named-node normal form and refuses to claim blank-node equivalence. Compact textual equality is never used as proof of graph equality.

## Security decisions

The supplied scripts make no arbitrary network requests. Their default security controls are:

- exact-match local context registry;
- HTTPS context identities;
- SHA-256 integrity pinning;
- allowed JSON-LD media types;
- no network fallback;
- duplicate JSON key rejection;
- UTF-8 enforcement;
- input, output, nesting, context-depth, and context-count limits;
- context-cycle detection;
- imported-context restrictions;
- protected-term enforcement;
- null-context protection;
- rejection of `file:`, `data:`, `ftp:`, `gopher:`, and unapproved resources;
- registry path traversal prevention;
- non-zero exits and machine-readable diagnostics;
- stable provenance containing source path, bytes, and digest.

A network-enabled loader is intentionally not included. [references/08-security.md](references/08-security.md) defines the additional redirect, address, timeout, streaming-size, caching, and isolation controls such an adapter would require.

## Examples delivered

The neutral model includes:

```text
Base system
├── Service
├── Store
└── Relationship

Domain extension
├── extends the base system
├── introduces an Adaptor
└── links the Adaptor to an inherited Service
```

The examples cover:

1. A reusable context document.
2. Compact JSON-LD.
3. Expanded JSON-LD.
4. Flattened JSON-LD.
5. A frame.
6. A framed application profile.
7. Direct and reverse relationships.
8. A first-class relationship node.
9. A cross-document node reference.
10. Pydantic models with JSON-LD aliases.
11. JSON-LD to Pydantic conversion.
12. Pydantic to JSON-LD conversion.
13. A missing graph target that passes JSON Schema but fails graph validation.
14. An untrusted remote context rejected by the safe loader.
15. A semantic round trip with changed compact text and equal compared graph meaning.
16. Language, index, identifier, type, list, set, and graph container examples.
17. A valid N-Quads dataset example.

## Tests executed

### Local test suite

Command:

```bash
pytest -q
```

Result:

```text
38 passed, 27 warnings in 16.15s
```

The warnings came from deprecated `Dataset.default_context` access inside the locally installed RDFLib 7.5.0 N-Quads parser. The skill requirements pin RDFLib 7.6.0. No test failed.

The local suite covers processing goldens, compaction round trips, direct and reverse equivalence, containers, safe registry loading, cycles, protected definitions, null contexts, invalid aliases, illegal containers, duplicate keys, forbidden schemes, RDF parsing, JSON Schema, Pydantic conversion, graph targets, CLIs, cross-document resolution, default-engine behavior, APS packaging, internal links, and required artifacts.

### Compile and CLI verification

Executed successfully:

```text
python -m compileall -q scripts examples/pydantic
make examples
make smoke
python scripts/expand.py ... --engine profile
python scripts/compact.py ... --engine profile
python scripts/flatten.py ... --engine profile
python scripts/frame.py ... --engine profile
python scripts/inspect_graph.py ... --engine profile
python scripts/semantic_roundtrip.py ... --engine profile
python examples/pydantic/jsonld_to_pydantic.py ... --engine profile
python examples/pydantic/pydantic_to_jsonld.py ... --engine profile
```

The semantic round trip reported equal named-node semantic digests and `textually_equal: false`. The complete graph inspector reported 6 defined nodes, 0 errors, and 0 warnings.

### Negative verification

The expected non-zero exits were observed:

| Case | Exit | Stable result |
|---|---:|---|
| Unapproved remote context | 2 | `remote_context_rejected` |
| Missing graph targets | 1 | two `missing_reference_target` diagnostics |
| Duplicate JSON key | 2 | `duplicate_key` at `$.@id` |
| Missing official-suite checkout | 2 | runner refused to proceed |

### Artifact lint

A separate lint verified:

- every ordinary JSON and JSON-LD fixture parses;
- every relative Markdown link resolves;
- process files contain required APS sections;
- APS instructions have no blank lines and use normative directives;
- process and tool IDs are backticked;
- no tabs or smart quotes appear in delivery text.

### Official W3C suites

The build environment did not contain PyLD 3.1.0 or pre-checked-out official suite repositories. The official suites were therefore **not run**, and this delivery does not claim a fresh official conformance result.

The skill includes `scripts/run_official_subset.py`, which requires a complete trusted PyLD v3.1.0 checkout and verifies:

- PyLD tag commit prefix `104b85d`;
- API suite prefix `289ebf3`;
- framing suite prefix `fa22874`;
- normalization suite prefix `fbcfce5`.

The runner never clones or downloads code. It refuses revision mismatches before invoking the upstream harness.

## Verification environment

| Component | Build environment |
|---|---|
| Python | 3.13.5 |
| Pydantic | 2.13.4 |
| jsonschema | 4.26.0 |
| pytest | 9.0.2 |
| RDFLib | 7.5.0 locally installed; 7.6.0 pinned for installation |
| PyLD | Not installed in the build sandbox; 3.1.0 pinned for installation |
| Network from scripts | Disabled by design |

## Unsupported features and limits

The skill does not claim to provide:

- a system or domain vocabulary;
- a graph compiler;
- a projection engine;
- a language server;
- SHACL validation;
- OWL inference;
- SPARQL processing;
- application authorization;
- namespace ownership proof;
- automatic graph target discovery outside approved registries;
- arbitrary remote context loading;
- a new RDFC-1.0-named PyLD option.

The bounded profile engine does not claim full support for:

- all JSON-LD context edge cases;
- arbitrary framing and all named-graph cases;
- HTML extraction;
- To-RDF or From-RDF algorithms;
- generalized RDF;
- RDF direction strategies;
- blank-node dataset canonicalization;
- the complete official error taxonomy;
- official suite conformance.

Use the pinned PyLD engine for ordinary standards processing. Use RDFC-1.0-capable tooling when a general blank-node dataset equivalence proof is required.

## Specification and implementation conflicts

### Framing embed values

Historical framing implementations and documents used values such as `@link`, `@first`, or `@last`. The JSON-LD 1.1 Framing Recommendation permits only `@always`, `@once`, and `@never`. The skill teaches and uses only those three values.

### Dataset normalization naming

PyLD exposes `URDNA2015` as its normalization algorithm option. The current W3C standard is RDFC-1.0. The adapter preserves the actual library option name and does not describe it as the current standard name.

### Library capability boundary

RDFLib can process RDF and JSON-LD serializations, but it is not presented as the selected complete JSON-LD API and framing implementation. TRLD was not selected because its documented capability and conformance surface did not meet the full requirements. The profile engine is explicitly bounded rather than presented as a hidden fallback.

## Important artifact hashes before release packaging

| Artifact | SHA-256 |
|---|---|
| `SKILL.md` | `67a315a6f81aec192cd1ffee6d02e3a72584cd7fec5b88103b3fbfe7ab5ebe27` |
| `examples/contexts/system-context.jsonld` | `27a70c090ae7205c95ebae579472992d6f12a051783c32e63f502a31030b9d18` |
| `examples/framed/system.frame.jsonld` | `4f8080489a2220c0a258aa895430835ea17f66147e9bc0059f7d995b80865053` |
| `examples/pydantic/application-profile.schema.json` | `4622ea8472e228af5ea020d9d343247529d77789892357991d94925b74d57e3c` |
| `examples/pydantic/models.py` | `f5e107d41d7bf018b4ffe38a8d44b2cd60f9450ab0b35dd646d0f2c9de64e78b` |
| `scripts/jsonld_common.py` | `544d2f957127bcd1ce5bb48888b78041d2351a36b94c1a0e4770bb1b9b0b5cd5` |
| `scripts/profile_engine.py` | `f1214c6f038c3d472fa593cc3c169e76dce6044a258a005c16a0ac3939b181d2` |

`SHA256SUMS` covers every delivered file except itself. The separate release manifest covers the final archive, build report, entrypoint, and internal checksum manifest.
