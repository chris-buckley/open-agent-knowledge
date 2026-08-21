# Processor evaluation

The project needs JSON-LD 1.1 expansion, compaction, flattening, framing, controlled document loading, reproducible offline use, and useful diagnostics in Python. This evaluation uses official project documentation and releases listed in [00 Source manifest](00-source-manifest.md).

## Decision

Use **PyLD 3.1.0** as the default processor [S09][S10]. Pin the exact version. Supply the skill's local document loader. Run the upstream test harness against the exact suite revisions pinned by the release.

The scripts default to `--engine pyld`. They fail with `processor_unavailable` when PyLD is absent. They never silently substitute the bounded profile engine.

Use `--engine profile` only for the bundled examples, offline smoke tests, and teaching demonstrations. It is not a general conforming JSON-LD processor.

## Candidate matrix

| Candidate | JSON-LD 1.1 operations | Framing | Loader control | Official-suite evidence | Python and maintenance | Decision |
|---|---|---|---|---|---|---|
| PyLD 3.1.0 | Expansion, compaction, flattening, framing, RDF conversion, normalization | Yes | Custom `documentLoader` | Source release pins API, framing, and normalization suite commits; package documents test runner | Python 3.10+; release 19 June 2026 | Default |
| RDFLib 7.6.0 | RDF graph and dataset parsing or serialization, including JSON-LD integration | Not a full JSON-LD framing API | Application controls RDF source handling | RDF-focused project rather than selected JSON-LD API conformance route | Active Python library; release 12 February 2026 | Optional RDF boundary only |
| TRLD 0.3.0 | Project implements a Python JSON-LD processing subset | No complete framing surface documented | Local processing possible | Project page publishes test results and limitations rather than full selected requirements | Release 6 June 2026 | Not selected |
| jsonld.js 9.0.0 | Full JavaScript JSON-LD API surface | Yes | Custom loader supported by project APIs | Listed by JSON-LD project and used widely in the ecosystem | Node route; published 21 November 2025 | Verified alternative implementation route |
| Bundled profile engine | Included compact examples, expansion, compaction, flattening, simple frame, named-node comparison | Included frame pattern only | Exact local registry | No official conformance claim | Python standard library plus skill code | Smoke tests only |

## Why PyLD

PyLD exposes the complete operation set required by this skill, including framing. Its loader hook allows the application to refuse network access and supply pinned local documents. Its v3.1.0 release supports current Python versions and records the exact official test-suite revisions used by its source checkout [S09][S11].

The project also documents its own test runner. This gives the skill a bounded path to run official expansion, compaction, flattening, framing, context, negative, and normalization cases without vendoring the large suites.

## PyLD adapter design

[`scripts/jsonld_common.py`](../scripts/jsonld_common.py) is the only direct PyLD adapter. It:

- imports PyLD lazily;
- sets JSON-LD 1.1 processing mode;
- requests ordered output;
- supplies the exact-match local document loader;
- expands before compaction, flattening, or framing so preflight and diagnostics are consistent;
- sets explicit frame defaults used by the application profile;
- emits machine-readable errors;
- refuses hidden fallback;
- uses the implementation's historical `URDNA2015` option only when semantic normalization is requested.

Keep library-specific options in this adapter. Do not spread PyLD calls through business models.

## Remote loading

PyLD can use a network document loader, but this skill does not enable it. The adapter supplies `LocalDocumentRegistry.pyld_loader()` for every operation.

A future network adapter MUST remain separate and implement [08 Security](08-security.md). It MUST not replace the safe default.

## Error quality

PyLD raises structured JSON-LD errors with codes and details. The adapter preserves the original exception text and available details inside a stable skill error envelope.

Processor messages can contain algorithm vocabulary that is difficult for application authors. [09 Error catalog](09-error-catalog.md) maps the common classes to practical fixes. The adapter MUST NOT alter a processor error into a misleading schema or Pydantic error.

## Deterministic offline use

Reproducibility requires more than a pinned processor version. Pin:

- source bytes;
- context and imported-context bytes;
- frame bytes;
- processor version;
- processing mode;
- base IRI;
- algorithm options;
- official suite commits;
- Python version.

Ordered JSON output is useful for golden tests. It is not a semantic guarantee. Use RDF dataset canonicalization when general graph equivalence, including blank nodes, must be established [S07].

## Unsupported or bounded features

The skill does not claim that PyLD or the profile engine performs:

- SHACL validation;
- OWL inference;
- application authorization;
- graph target existence checks;
- namespace ownership verification;
- current RDFC-1.0 under a newly named API option.

The PyLD API still exposes historical normalization naming. The adapter records this mismatch and does not relabel `URDNA2015` as the current W3C algorithm.

The bundled profile engine does not fully implement:

- all context-processing edge cases;
- arbitrary framing and every embedding mode;
- HTML input extraction;
- To-RDF or From-RDF algorithms;
- generalized RDF;
- directional RDF strategies;
- RDF dataset canonicalization with blank nodes;
- the complete official error taxonomy;
- official test-suite conformance.

It MUST raise or be treated as unsupported outside its declared profile.

## Alternative implementation route

When a requirement exposes a verified PyLD defect or missing feature:

1. Reduce the case to an official test or minimal fixture.
2. Confirm the normative result in S01 through S03.
3. Test the pinned `jsonld.js` alternative in an isolated Node adapter.
4. Keep the same local document registry contract and provenance fields.
5. Compare expanded or canonical RDF output, not compact text.
6. Record the processor switch as part of the build or document provenance.
7. Do not silently mix outputs from two processors in one graph.

## Version policy

A processor update is a contract change review, even when the public API is compatible. Before updating:

- read the release notes;
- compare official suite pins;
- run all skill tests and official subsets;
- regenerate golden outputs;
- review ordering, blank-node, frame, and error changes;
- update [00 Source manifest](00-source-manifest.md), the build report, requirements, and hashes.
