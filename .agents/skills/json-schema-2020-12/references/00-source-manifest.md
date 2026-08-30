# 00 Source manifest

## Authority order

Use sources in this order when they disagree:

1. Follow the supplied skill-authoring guide, template, build process, and repository instructions for packaging and file structure.
2. Follow the official JSON Schema Draft 2020-12 specifications and meta-schemas for JSON Schema meaning.
3. Follow official Pydantic v2 documentation for Pydantic APIs and runtime behavior.
4. Follow the official OpenAPI 3.1 specification only for OpenAPI interoperability.
5. Follow official implementation documentation for library-specific behavior.
6. Treat this skill's project conventions as local policy, never as additions to the standard.

The available File Library contained the flattened `aps.md` skill-authoring authority. It includes skill-authoring guide v1.0.0, APS specification v1.0, framework revision 1.2.2, the generic platform adaptor, the build process, and the canonical skill template. No installable or flattened skill named `pydantic-v2` was found after repeated exact-name and API-term searches. This build therefore uses the official Pydantic documentation as the Pydantic authority and limits this skill to the JSON Schema boundary.

## Retrieval record

All web sources were retrieved on 2026-08-05. URLs are recorded so an agent can recheck status when deliberately updating the skill. Do not fetch them during ordinary offline validation.

### JSON Schema authorities

| Source | Version or status | Use in this skill |
| --- | --- | --- |
| https://json-schema.org/draft/2020-12 | Draft 2020-12 release, published 2022-06-16 | Release index, meta-schema, vocabulary meta-schemas, release changes |
| https://json-schema.org/draft/2020-12/json-schema-core | `draft-bhutton-json-schema-01` | Resources, dialects, vocabularies, identifiers, references, applicators, annotations, output |
| https://json-schema.org/draft/2020-12/json-schema-validation | `draft-bhutton-json-schema-validation-01` | Validation, format, content, and metadata vocabularies |
| https://json-schema.org/draft/2020-12/schema | General-purpose Draft 2020-12 meta-schema | Schema validity and dialect identifier |
| https://json-schema.org/draft/2020-12/meta/core | Core vocabulary meta-schema | Core keyword syntax |
| https://json-schema.org/draft/2020-12/meta/applicator | Applicator vocabulary meta-schema | Applicator keyword syntax |
| https://json-schema.org/draft/2020-12/meta/validation | Validation vocabulary meta-schema | Assertion keyword syntax |
| https://json-schema.org/draft/2020-12/meta/unevaluated | Unevaluated vocabulary meta-schema | `unevaluatedProperties` and `unevaluatedItems` syntax |
| https://json-schema.org/draft/2020-12/meta/meta-data | Metadata vocabulary meta-schema | Annotation keyword syntax |
| https://json-schema.org/draft/2020-12/meta/format-annotation | Format annotation vocabulary meta-schema | Default format behavior |
| https://json-schema.org/draft/2020-12/meta/format-assertion | Format assertion vocabulary meta-schema | Optional format assertion dialects |
| https://json-schema.org/draft/2020-12/meta/content | Content vocabulary meta-schema | Encoded-content annotations |
| https://json-schema.org/understanding-json-schema/ | Official explanatory documentation | Non-normative teaching examples for objects, arrays, composition, and conditionals |
| https://github.com/json-schema-org/JSON-Schema-Test-Suite | Official test suite | Conformance reference; not vendored in this skill |
| https://bowtie.report/ | Bowtie implementation reporting | Independent implementation comparison reference; not required at runtime |
| https://www.rfc-editor.org/rfc/rfc3986 | RFC 3986 | URI-reference resolution model used by JSON Schema |
| https://www.rfc-editor.org/rfc/rfc6901 | RFC 6901 | JSON Pointer fragments and diagnostic paths |
| https://www.rfc-editor.org/rfc/rfc8259 | RFC 8259 | JSON data model and string interpretation |

Draft 2020-12 is the current official JSON Schema release listed by the JSON Schema project at retrieval time. Its core and validation texts retain IETF Internet-Draft headers; use the JSON Schema release index and canonical meta-schema URIs rather than inferring that the dialect is obsolete from an IETF expiry notice.

### Pydantic authorities

| Source | Version or status | Use in this skill |
| --- | --- | --- |
| https://pypi.org/project/pydantic/ | 2.13.4, released 2026-05-06 | Verified package version and Python support |
| https://docs.pydantic.dev/latest/concepts/json_schema/ | Current Pydantic v2 docs | `model_json_schema`, `TypeAdapter.json_schema`, modes, `$defs`, customization, reference templates |
| https://docs.pydantic.dev/latest/concepts/unions/ | Current Pydantic v2 docs | Discriminated unions |
| https://docs.pydantic.dev/latest/concepts/alias/ | Current Pydantic v2 docs | Validation and serialization aliases |
| https://docs.pydantic.dev/latest/concepts/strict_mode/ | Current Pydantic v2 docs | Strict and coercive validation boundaries |
| https://docs.pydantic.dev/latest/concepts/models/ | Current Pydantic v2 docs | Recursive and generic models, rebuild behavior |
| https://docs.pydantic.dev/latest/api/base_model/ | Current Pydantic v2 API | `BaseModel` API surface |
| https://docs.pydantic.dev/latest/api/type_adapter/ | Current Pydantic v2 API | `TypeAdapter` API surface |

### OpenAPI authority

| Source | Version or status | Use in this skill |
| --- | --- | --- |
| https://spec.openapis.org/oas/v3.1.2.html | OpenAPI 3.1.2, published 2025-09-19 | Schema Object dialect, components, references, discriminator, nullable unions |

### Python implementation authorities

| Source | Version or status | Use in this skill |
| --- | --- | --- |
| https://pypi.org/project/jsonschema/ | 4.26.0, released 2026-01-07 | Default validator version and Python support |
| https://python-jsonschema.readthedocs.io/en/stable/ | 4.26.0 docs | Validator, errors, format checking, and schema checking |
| https://python-jsonschema.readthedocs.io/en/stable/referencing/ | 4.26.0 docs | Explicit `referencing.Registry` construction |
| https://pypi.org/project/referencing/ | 0.37.0, released 2025-10-13 | Reference registry version and Python support |
| https://referencing.readthedocs.io/ | Current `referencing` docs | Resource and registry behavior |
| https://docs.bowtie.report/en/stable/cli/ | Bowtie 2026.7.4 stable documentation at retrieval | Official-suite execution and direct `python-jsonschema` connector |
| https://pypi.org/project/jschon/ | 0.11.1 at retrieval; Development Status: Alpha | Alternative evaluated, not selected |
| https://jschon.readthedocs.io/ | Current jschon docs | Alternative vocabulary and output model review |

## Selected baseline

The skill MUST use these versions for reproducible examples:

```text
Python >= 3.10
jsonschema[format-nongpl] == 4.26.0
referencing == 0.37.0
pydantic == 2.13.4
```

`jsonschema` is the default because the verified release supports Draft 2020-12, exposes lazy error iteration with instance and schema paths, delegates modern reference handling to an explicit immutable registry, is marked production/stable, and supports Python 3.10 and later. `referencing` is pinned because the scripts depend on its public registry API. Pydantic is needed only for the integration example and generation process.

Bowtie's stable CLI can run a local checkout of the official JSON Schema Test Suite and can connect directly to `python-jsonschema`. This build uses Bowtie as the documented qualification route but does not claim a fresh full-suite conformance score; its executed evidence is limited to the included acceptance fixtures.

`jschon` was evaluated because it supports Draft 2020-12, custom vocabularies, catalogs, and standard output formats. It was not selected as the default because its published package remained marked Alpha and its release was older than the selected maintained stack. This choice is an implementation decision, not a judgment about specification correctness.

## Source-use rules

- An agent MUST cite the applicable official specification section when adding or changing a technical rule in this skill.
- An agent MUST record a new retrieval date when changing a version-sensitive claim.
- An agent MUST NOT copy full standards or test suites into the skill.
- An agent MUST mark official explanatory documentation as non-normative when it simplifies a normative rule.
- An agent MUST record implementation differences instead of changing standard meaning to match a library.
- An agent MUST treat all identifiers under `https://example.org/` as examples, not live retrieval locations.
