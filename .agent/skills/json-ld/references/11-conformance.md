# Conformance and verification

Conformance has three levels in this skill:

1. Normative behavior from the W3C Recommendations [S01][S02][S03].
2. Processor conformance tested by official JSON-LD suites [S04][S05].
3. Application-profile verification for the bundled neutral examples.

Passing the application tests does not prove full processor conformance. Passing a processor suite does not prove an application's graph targets, provenance, or business constraints.

## Official suite revisions

PyLD v3.1.0 pins these specification repositories in its source tree [S11]:

| Suite | Required commit prefix |
|---|---|
| JSON-LD API | `289ebf3` |
| JSON-LD Framing | `fa22874` |
| RDF normalization | `fbcfce5` |

The PyLD tag commit prefix is `104b85d`.

[`scripts/run_official_subset.py`](../scripts/run_official_subset.py) verifies these revisions before invoking the upstream test harness. It does not clone repositories or make network requests.

## Official test categories

A practical verification run SHOULD cover:

- expansion;
- compaction;
- flattening;
- context processing;
- document loading;
- To-RDF and From-RDF;
- framing;
- positive syntax and algorithm cases;
- negative error cases;
- RDF normalization or canonicalization compatibility where selected.

The official manifests define test types, inputs, options, expected outputs, and negative error codes [S04][S05]. Use the manifest comparison rules. Do not replace them with ad hoc JSON string comparison.

## Running the pinned upstream suites

Prepare a complete, trusted PyLD v3.1.0 checkout with its specification submodules already present. Then run:

```bash
python scripts/run_official_subset.py --pyld-source /path/to/pyld-v3.1.0 --mode full
```

The script:

1. Checks the PyLD checkout revision.
2. Checks each suite revision.
3. Refuses a mismatch.
4. Runs the project's documented test harness with caller-supplied extra arguments.
5. Propagates the upstream exit code.

Use `--help` for the exact interface. The script never downloads missing submodules.

## Included application tests

The local pytest suite verifies:

- expansion golden output;
- compaction and semantic re-expansion;
- flattening golden output;
- framing golden output;
- context arrays and local registry loading;
- context cycle rejection;
- protected-term rejection;
- remote-context rejection;
- duplicate-key rejection;
- output determinism for the bounded examples;
- container-map expansion;
- JSON Schema validation;
- Pydantic source and canonical models;
- missing-target graph validation;
- JSON-LD to Pydantic conversion;
- Pydantic to JSON-LD conversion;
- CLI success and non-zero failures;
- packaging names and text hygiene.

Run:

```bash
pytest -q
```

## Golden examples

Generated goldens are stored under:

- [`examples/expanded/`](../examples/expanded/)
- [`examples/flattened/`](../examples/flattened/)
- [`examples/framed/`](../examples/framed/)
- [`examples/containers/`](../examples/containers/)
- [`examples/rdf/`](../examples/rdf/)

Goldens are exact outputs for the pinned profile engine and checked example configuration. They are teaching and regression assets. They are not a replacement for W3C expected-result files.

## Semantic round trip

[`scripts/semantic_roundtrip.py`](../scripts/semantic_roundtrip.py) performs:

```text
input
  -> expansion A
  -> compaction under selected context
  -> expansion B
  -> semantic comparison
```

With PyLD it uses RDF normalization through the implementation API. With the profile engine it compares a deterministic normal form only when every node is named. It rejects blank-node equivalence claims.

A successful semantic round trip permits formatting, object order, aliases, embedding, maps, and scalar-versus-array spelling to change. It does not prove that application defaults, provenance, or graph names were preserved unless the profile includes and checks them.

## Local document loading test

Every processing test uses [`examples/contexts/registry.json`](../examples/contexts/registry.json). The registry pins the context and records its content type and SHA-256.

Tests MUST fail when:

- the IRI is absent;
- the digest changes;
- the local file is missing;
- the scheme is rejected;
- the context chain is cyclic.

## Negative tests

Each invalid fixture has one primary intended failure:

| Fixture | Intended layer |
|---|---|
| `duplicate-key.json` | JSON parser |
| `untrusted-remote-context.jsonld` | Security loader |
| `cyclic-context-document.jsonld` | Context preflight or processing |
| `protected-term-redefinition.jsonld` | Context processing |
| `relative-identifier.jsonld` | Graph inspection policy |
| `missing-target.jsonld` | Graph target validation |
| `missing-target.framed.jsonld` | Pydantic graph validation after JSON Schema passes |

Tests SHOULD assert the stable error code and non-zero exit status, not the entire processor prose message.

## Determinism checks

For exact goldens:

- serialize UTF-8 JSON with sorted object keys and stable indentation;
- sort semantically unordered application arrays by stable identifier;
- preserve `@list` and declared application sequence order;
- pin all inputs and versions;
- do not compare raw blank-node labels across processors.

## Build verification

A release build MUST:

1. Run `python -m compileall` over scripts and examples.
2. Run the complete local pytest suite.
3. Run all six CLI scripts on valid examples.
4. Run invalid fixtures and verify non-zero exits.
5. Run the Pydantic conversion examples.
6. Run the official suite subset when the pinned checkout is available.
7. Regenerate and compare goldens.
8. Remove caches and virtual environments.
9. Create an archive with one `json-ld/` root.
10. Produce SHA-256 manifests.

## Current delivery limitation

The build environment used for this delivery did not contain PyLD or pre-checked-out official suite repositories. The complete local profile tests were therefore executed with the explicit bounded profile engine. The official runner and exact suite pins are included, but an official W3C suite result MUST NOT be claimed until it is run in an environment with the pinned PyLD checkout and dependencies.
