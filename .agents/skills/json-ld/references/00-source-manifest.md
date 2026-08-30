# Source manifest

Retrieved: 2026-08-05 UTC.

This manifest identifies the authority behind the skill. Later references cite source keys such as `[S01]`. W3C Recommendations govern JSON-LD meaning and processing. The repository skill-authoring guide governs packaging. Library documentation governs only library-specific API claims.

## Governing repository material

| Key | Source | Version or status | Role |
|---|---|---|---|
| S00 | Supplied `aps.md`, especially `_template/SKILL.md`, `guides/skill-authoring-v1.0.0.guide.md`, and `processes/build-skill.md` | APS v1.0, framework revision 1.2.2 | Skill structure, names, frontmatter, APS process syntax, and lint rules |

No completed `pydantic-v2` skill or completed `json-schema-2020-12` skill was available in the supplied File Library. The build therefore used current official Pydantic and JSON Schema sources directly and kept their material narrowly scoped to the JSON-LD integration boundary.

## Normative JSON-LD and RDF sources

| Key | Source | Version or status | URL | Used for |
|---|---|---|---|---|
| S01 | W3C JSON-LD 1.1, A JSON-based Serialization for Linked Data | W3C Recommendation, 16 July 2020 | https://www.w3.org/TR/json-ld11/ | Syntax, contexts, keywords, object forms, containers, identity, RDF mapping |
| S02 | W3C JSON-LD 1.1 Processing Algorithms and API | W3C Recommendation, 16 July 2020 | https://www.w3.org/TR/json-ld11-api/ | Context processing, expansion, compaction, flattening, RDF conversion, loading, options, errors |
| S03 | W3C JSON-LD 1.1 Framing | W3C Recommendation, 16 July 2020 | https://www.w3.org/TR/json-ld11-framing/ | Frame matching, embedding, explicit properties, defaults, named graphs, cycles |
| S04 | W3C JSON-LD API Test Suite | Current hosted suite and manifests | https://w3c.github.io/json-ld-api/tests/ | Conformance test vocabulary, manifests, comparison rules, negative tests |
| S05 | W3C JSON-LD Framing Test Suite | Current hosted suite and manifests | https://w3c.github.io/json-ld-framing/tests/ | Framing conformance cases |
| S06 | RDF 1.1 Concepts and Abstract Syntax | W3C Recommendation, 25 February 2014 | https://www.w3.org/TR/rdf11-concepts/ | RDF terms, graphs, datasets, blank nodes, literals, named graphs |
| S07 | RDF Dataset Canonicalization | W3C Recommendation, RDFC-1.0 | https://www.w3.org/TR/rdf-canon/ | Semantic comparison, canonical N-Quads, blank-node risks |
| S08 | RFC 3987, Internationalized Resource Identifiers | IETF Proposed Standard | https://www.rfc-editor.org/rfc/rfc3987 | IRI terminology and absolute identifiers |

## Processor and application-library sources

| Key | Source | Version or status | URL | Used for |
|---|---|---|---|---|
| S09 | PyLD package documentation and release | 3.1.0, released 19 June 2026, Python 3.10+ | https://pypi.org/project/PyLD/ | Default Python processor, supported operations, loader API, test runner, dependency floor |
| S10 | PyLD v3.1.0 source tree and changelog | Tag `v3.1.0`, tag commit prefix `104b85d` | https://github.com/digitalbazaar/pyld/tree/v3.1.0 | Source-level API verification and release changes |
| S11 | PyLD v3.1.0 specification submodules | API `289ebf3`; framing `fa22874`; normalization `fbcfce5` | https://github.com/digitalbazaar/pyld/tree/v3.1.0/specifications | Exact official-suite revisions pinned by the selected processor release |
| S12 | Pydantic documentation and package release | 2.13.4, released 6 May 2026 | https://docs.pydantic.dev/latest/ | Aliases, validation and serialization configuration, discriminated unions, model validators |
| S13 | JSON Schema Draft 2020-12 | Published 16 June 2022 | https://json-schema.org/draft/2020-12 | Structural application-profile schema boundary |
| S14 | RDFLib package | 7.6.0, released 12 February 2026 | https://pypi.org/project/rdflib/ | RDF parsing and serialization alternative, not the default JSON-LD framing engine |
| S15 | jsonld.js package | 9.0.0, published 21 November 2025 | https://www.npmjs.com/package/jsonld | Verified non-Python alternative route |
| S16 | TRLD package and project documentation | 0.3.0, released 6 June 2026 | https://pypi.org/project/trld/ | Python candidate comparison and published test limitations |
| S17 | JSON-LD project implementation list | Current site | https://json-ld.org/ | Implementation ecosystem and links to official suites and reports |

## Source precedence

1. Apply S01, S02, and S03 when deciding JSON-LD meaning or legal processing.
2. Apply S06 and S07 at the RDF and semantic-equivalence boundary.
3. Apply S00 only to skill packaging and APS process files.
4. Apply S09 through S16 only to the named implementation or integration API.
5. Treat all `https://example.org/` identifiers in this skill as neutral examples, not a W3C vocabulary.

## Known documentation conflict

PyLD documentation still describes normalization through the historical option name `URDNA2015`. The current W3C Recommendation names the standard RDFC-1.0 and includes URDNA2015 in an informative compatibility appendix. This skill uses PyLD's required option when calling PyLD, labels it accurately as a library API value, and cites RDFC-1.0 for the standards boundary. [S07] [S09]

Some historical processor documentation and older framing implementations expose values such as `@last` or `@link`. The JSON-LD 1.1 Framing Recommendation defines the interoperable `@embed` values `@always`, `@once`, and `@never`. This skill teaches those Recommendation values and does not depend on implementation extensions. [S03]
