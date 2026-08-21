# Build report: json-schema-2020-12 1.0.0

Build date: 2026-08-05

## Result

The build completed successfully.

The delivery is an installable agent skill for designing, generating, validating, composing, debugging, and evolving JSON Schema Draft 2020-12 contracts. It includes compact entry instructions, numbered technical references, task guides, APS processes, complete neutral examples, offline validation scripts, fixtures, tests, and integrity manifests.

The packaged tree contains `54` files. It contains no virtual environment, dependency copy, standards copy, cache directory, bytecode, editor state, or temporary output.

## Inputs read

The build read the available flattened `aps.md` skill-authoring authority before creating files. That authority contains the skill-authoring guide v1.0.0, APS specification v1.0, framework revision 1.2.2, canonical template, and build process.

Repeated File Library searches did not locate an installable or flattened skill named `pydantic-v2`. The build therefore used current official Pydantic v2 documentation as the Pydantic authority and confined this skill to the JSON Schema boundary.

The complete source and retrieval record is in [`references/00-source-manifest.md`](references/00-source-manifest.md). All web sources were retrieved on 2026-08-05.

## Standards and status

| Authority | Version or status used | Role |
| --- | --- | --- |
| JSON Schema | Draft 2020-12 release, published 2022-06-16 | Normative schema language, dialect, vocabularies, identifiers, references, validation, annotations, and output concepts |
| JSON Schema general meta-schema | `https://json-schema.org/draft/2020-12/schema` | Required standalone dialect and schema-validity gate |
| Pydantic | 2.13.4, released 2026-05-06 | Current JSON Schema generation APIs and executable model example |
| OpenAPI | 3.1.2, published 2025-09-19 | Bounded interoperability guidance only |
| `jsonschema` | 4.26.0, released 2026-01-07 | Default Draft 2020-12 validator and diagnostic API |
| `referencing` | 0.37.0, released 2025-10-13 | Explicit immutable resource registry |
| Bowtie | 2026.7.4 stable documentation | Documented route for running the official suite against `python-jsonschema` |

The JSON Schema Core and Validation documents retain IETF Internet-Draft headers. The JSON Schema project identifies Draft 2020-12 as its current release at the retrieval date, so the build uses the project release page and canonical meta-schema URI as the status authority.

## Default validator choice

The default stack is:

```text
Python >= 3.10
jsonschema[format-nongpl] == 4.26.0
referencing == 0.37.0
pydantic == 2.13.4
```

`jsonschema` was selected for these reasons:

- its current official documentation states full Draft 2020-12 support;
- `Draft202012Validator` prevents accidental selection of an older or implicit draft;
- `check_schema` provides a direct meta-schema gate;
- lazy error iteration exposes instance paths, schema paths, keywords, and nested context;
- current reference handling accepts an explicit `referencing.Registry`;
- the package is marked Production/Stable and supports current Python releases;
- Bowtie provides a direct `python-jsonschema` connector and can run the official Draft 2020-12 suite.

`referencing` is pinned because the scripts use its public immutable registry API and deliberately provide no retrieval callback.

`jschon` 0.11.1 was also examined. It offers Draft 2020-12, catalog, vocabulary, and output features, but its published package status remained Alpha at retrieval. It was not selected as the default. This is an implementation-risk choice, not a claim that its JSON Schema semantics are incorrect.

The build did not run the full official JSON Schema Test Suite or publish a Bowtie conformance score. It ran the focused acceptance fixtures shipped with this skill. The references require Bowtie or the official suite for a broader implementation qualification claim.

## Important design choices

### Explicit dialect, no fallback

Every standalone schema declares the exact Draft 2020-12 `$schema` URI. The scripts reject omission, a different dialect, and a different dialect inside an embedded resource. They never call a generic helper that can choose the newest installed draft.

### Canonical identity separated from storage

Schemas use stable `https://example.org/schema/...` identifiers. Local files are connected through an explicit registry manifest. Canonical `$id` values never become `file:` paths during offline use.

Registry manifest keys must be absolute, fragment-free resource URIs. Manifest paths must remain beneath the manifest directory. A caller can authorize an external local resource explicitly with `--resource URI=PATH`.

### Offline deterministic resolution

The registry has no network or filesystem retrieval callback. Missing resources fail instead of triggering hidden I/O. Duplicate URI mappings, mismatched `$id` values, invalid registered schemas, absent anchors, and references to non-schema JSON values fail with deterministic diagnostics.

### Open parent, closed leaves

`BaseSystem` is intentionally extensible. Known node and relationship leaves are closed, while reserved extension branches remain open and exclude base tags. `RetailLendingSystem` applies the parent and domain constraints to the same instance, then closes the complete leaf with `unevaluatedProperties: false`.

This teaches composition as logical constraint application. The skill never describes `allOf` as object-oriented inheritance or as value merging.

### Tagged unions

Node and relationship families use required `kind` tags constrained by `const`. This keeps `oneOf` branches disjoint and makes failures easier to diagnose.

### Fixed and dynamic recursion are separate

The system example uses ordinary `$ref` for fixed recursive containment. A separate tree example uses `$dynamicAnchor` and `$dynamicRef` only to demonstrate an extension that tightens every recursive depth.

### Structural and graph validation are separate gates

The schema requires relationship objects with `kind`, `from`, and `to`, but it does not claim that target strings resolve to objects. A missing-target fixture passes JSON Schema and fails the separate graph-target checker.

### Hand-authored and generated schemas have different jobs

The Pydantic example emits a corresponding portable shape with `BaseModel.model_json_schema()` and `TypeAdapter.json_schema()`. It is deliberately not byte-identical to the hand-authored extension contract, because Pydantic does not automatically generate the parent-composition and dynamic extension protocol taught by the hand-authored schemas.

### Ambiguous JSON is rejected

The shared loader rejects duplicate object member names instead of accepting the parser's last value silently.

### Regular-expression portability is disclosed

The schema gate does not use Python's `regex` format checker as proof of ECMA-262 portability. Instance validation uses the selected implementation's pattern engine. The references require portable constructs and target-runtime tests for sensitive expressions.

## Delivered structure

```text
json-schema-2020-12/
|-- SKILL.md
|-- LICENSE
|-- BUILD_REPORT.md
|-- PACKAGE_MANIFEST.txt
|-- SHA256SUMS.txt
|-- requirements.txt
|-- assets/
|   |-- constants/README.md
|   `-- formats/README.md
|-- references/
|   |-- 00-source-manifest.md
|   |-- 01-core-and-vocabularies.md
|   |-- 02-identifiers-and-references.md
|   |-- 03-validation-keywords.md
|   |-- 04-composition-and-extension.md
|   |-- 05-pydantic-v2-integration.md
|   |-- 06-openapi-3-1-interoperability.md
|   |-- 07-validation-and-diagnostics.md
|   `-- 08-error-catalog.md
|-- guides/
|   |-- author-a-schema-v1.0.0.guide.md
|   |-- split-a-schema-across-files-v1.0.0.guide.md
|   |-- design-an-extensible-contract-v1.0.0.guide.md
|   `-- debug-validation-v1.0.0.guide.md
|-- processes/
|   |-- generate-from-pydantic.md
|   |-- validate-schema-and-instance.md
|   `-- review-schema-change.md
|-- examples/
|   |-- registry.json
|   |-- system/
|   |-- extension/
|   |-- recursive/
|   |-- invalid/
|   `-- pydantic/
|-- scripts/
|   |-- _common.py
|   |-- validate_schema.py
|   |-- validate_instance.py
|   |-- check_references.py
|   `-- check_graph_targets.py
`-- tests/
    `-- test_examples.py
```

The user-suggested unnumbered reference names were adapted to the governing `NN-<name>.md` rule. Guide names were adapted to the governing versioned guide convention. The requested subject coverage and artifacts were preserved.

## Verification environment

```text
Python: 3.13.5
Operating system: Linux 6.18.35 x86_64
jsonschema: 4.26.0
referencing: 0.37.0
pydantic: 2.13.4
pytest installed in host: 9.0.2
```

The skill supports Python 3.10 or later according to the selected package baselines. This build was executed on Python 3.13.5.

A targeted dependency check confirmed all three pinned project packages at the exact required versions. A global host `pip check` also reported an unrelated pre-existing conflict: host package `moviepy 2.2.1` requires Pillow below 12 while the shared host has Pillow 12.2.0. The skill does not import MoviePy or Pillow, and the targeted dependency set is satisfied.

## Tests executed

### Static and packaging lint

A build-only lint checked:

- UTF-8 decoding and LF line endings;
- final newlines;
- no tab characters;
- no smart quotes;
- valid JSON with duplicate-key rejection;
- `SKILL.md` frontmatter and body order;
- numbered reference and versioned guide names;
- APS section order, non-empty instruction lines, and backticked tool IDs;
- every relative Markdown link;
- explicit Draft 2020-12 declarations on all standalone schemas;
- absence of older-draft schema keywords in runnable schemas;
- absence of canonical `file:` schema identifiers;
- required technical-coverage terms.

Result before packaging: `PASS`, 51 source files and 16 JSON documents checked. The final package manifests were added after this source lint and were checked again during archive verification.

### Python compilation

```bash
python -m compileall -q scripts examples/pydantic tests
```

Result: `PASS`.

### Unit and acceptance suite

```bash
python -m unittest discover -s tests -v
```

Result: `PASS`, 26 tests, 0 failures, 0 errors.

The tests cover:

- all seven standalone schemas against the Draft 2020-12 meta-schema;
- local and cross-file reference resolution without network access;
- a local fragment when the root has no `$id`;
- missing resources as hard failures;
- non-schema reference targets;
- missing and unsupported dialects;
- invalid and duplicate anchors;
- duplicate JSON object keys;
- registry path confinement;
- open and closed base contracts;
- domain-to-parent satisfaction;
- root and leaf `unevaluatedProperties` closure;
- tagged-union failure with nested missing-`currency` evidence;
- dynamic recursive rebinding and descendant failure paths;
- format annotation versus format assertion;
- unknown formats under each policy;
- Pydantic model and TypeAdapter generation determinism;
- aliases and recursive Pydantic runtime validation;
- exact instance and schema paths;
- structural success followed by graph-target failure.

### CLI help

Each command returned success for `--help`:

```text
scripts/validate_schema.py
scripts/validate_instance.py
scripts/check_references.py
scripts/check_graph_targets.py
```

### Schema and reference sweep

Every one of the seven standalone example schemas passed both:

```bash
python scripts/validate_schema.py SCHEMA
python scripts/check_references.py SCHEMA --registry examples/registry.json
```

Result: `PASS`, 7 schemas, 0 unresolved references.

### Instance and semantic matrix

| Case | Expected exit | Result |
| --- | ---: | --- |
| Base instance under open BaseSystem | 0 | PASS |
| Base instance under closed profile | 0 | PASS |
| Extra root field under closed profile | 1 | PASS |
| Retail lending instance under domain contract | 0 | PASS |
| Retail lending instance under parent contract | 0 | PASS |
| Unknown `debug` field under final retail closure | 1 | PASS |
| Loan-product child missing `currency` | 1 | PASS |
| Missing graph target under JSON Schema | 0 | PASS |
| Same missing graph target under graph checker | 1 | PASS |
| Valid graph targets | 0 | PASS |
| Strict recursive tree | 0 | PASS |
| Recursive child missing `tag` | 1 | PASS |
| Retail instance under Pydantic-generated schema | 0 | PASS |
| Known formats asserted for the valid retail fixture | 0 | PASS |
| Cross-file validation without registry | 2 | PASS |

Exit code 0 means valid, 1 means a claimed instance or graph failure, and 2 means a tool, schema, dialect, JSON, or resource failure.

### Pydantic regeneration

The build regenerated both committed Pydantic artifacts and compared raw bytes:

```bash
python examples/pydantic/model.py generate TEMP/generated.schema.json --mode validation
python examples/pydantic/model.py generate-node TEMP/node.generated.schema.json
cmp examples/pydantic/generated.schema.json TEMP/generated.schema.json
cmp examples/pydantic/node.generated.schema.json TEMP/node.generated.schema.json
```

Result: `PASS`; both outputs were byte-identical to the committed artifacts.

### Archive verification

The final archive was extracted into a new temporary directory. The extracted copy was checked for forbidden cache and environment entries, compiled, linted, swept across all schemas and references, and run through the 26-test suite.

Result: `PASS`.

A second independently written deterministic archive was compared with the delivered archive.

Result: `PASS`; the archives were byte-identical.

## Acceptance criteria

| Criterion | Result | Evidence |
| --- | --- | --- |
| Official grounding | PASS | Numbered references and source manifest use official standards and implementation documentation |
| Draft 2020-12 syntax | PASS | Seven meta-valid schemas; no legacy syntax in runnable schemas |
| Older-draft isolation | PASS | Older forms appear only as marked migration notes |
| Identity and references | PASS | `$id`, `$ref`, anchors, dynamic references, base changes, registries, bundling, cycles, and recursion covered |
| `allOf` meaning | PASS | Explicitly described only as applying all constraints |
| Extensible closure | PASS | Working `unevaluatedProperties` base and retail fixtures |
| Hand-authored and generated schemas | PASS | Complete examples for both |
| Claimed valid examples | PASS | Unit suite and CLI matrix |
| Claimed invalid examples | PASS | Exact closure, union, recursion, format, reference, and graph failures tested |
| Offline cross-file and recursion | PASS | No retrieval callback; registry and dynamic-recursion tests |
| Semantic limits | PASS | Graph target gap is demonstrated and checked separately |
| Scope boundary | PASS | No system vocabulary, graph compiler, projection engine, or language server built |
| Offline ordinary use | PASS | Sources, rules, procedures, examples, scripts, and tests are included |
| Scripts and tests | PASS | Four CLIs, schema sweep, matrix, regeneration, and 26 tests passed |
| Clean archive | PASS | Extracted package contains no cache, environment, or generated clutter |

## Known limits

- The scripts execute only the general Draft 2020-12 dialect. They do not load arbitrary custom meta-schemas or implement custom vocabulary code.
- The scripts never retrieve network resources. Every external resource must be preloaded through the local manifest or `--resource`.
- `assert-known` format behavior is limited to checkers registered by the pinned `jsonschema[format-nongpl]` environment. Critical format edge cases still need project tests.
- Pattern evaluation uses the selected Python implementation's regular-expression engine. The skill teaches a portable ECMA-262 subset but does not provide a separate ECMAScript regex interpreter.
- The graph checker demonstrates only recursive node-ID uniqueness and relationship endpoint existence within one System document. It does not enforce endpoint-kind rules, authorization, cross-document integrity, JSON-LD expansion, or acyclicity.
- The Pydantic-generated schema is corresponding, not logically proven equivalent to the hand-authored contract.
- Pydantic custom validators, coercion, serializers, context, external calls, and graph rules can require runtime checks that the generated JSON Schema cannot express.
- Some valid JSON Schema constructs, including custom vocabularies, dynamic extension protocols, annotation output, and complex unevaluated composition, require custom Pydantic handling.
- The OpenAPI material is an interoperability guide. The skill does not build an OpenAPI document or projection engine.
- The full official JSON Schema Test Suite and Bowtie report were not rerun for this delivery.
- Operational limits for hostile schema size, instance size, recursion depth, total errors, and time remain deployment policy. The references require callers to set them.

## Conflicts and disagreements

No supplied technical example was found to conflict with the normative JSON Schema, Pydantic, or OpenAPI authorities.

The following non-technical adaptations were required:

- the governing authoring guide required numbered reference files, so the requested descriptive reference names received `00-` through `08-` prefixes;
- the governing authoring guide required versioned guide names, so each requested guide received `-v1.0.0.guide.md`;
- no `pydantic-v2` skill was available, so current official Pydantic v2 documentation supplied that boundary material.

The build records implementation differences instead of changing standard meaning. In particular, it does not treat optional format checking, Python regular expressions, Pydantic defaults, OpenAPI discriminators, or graph target existence as core JSON Schema behavior.

## Important artifact hashes

These hashes identify important payload files before archive packaging:

```text
9e683660bcdfb1b2aa2c60edb91ce9c73be0218605122baa938507fd5ece0cef  SKILL.md
4c11c9add863318776cb859e07292a9593c37cd74cc6bf8a0fb886f1b89bf066  references/00-source-manifest.md
4c3b45ba35298017221f53d93b7d3639a6445e5e882ace905f87e5bc3b9b4ad4  examples/system/schema/system.schema.json
2f19107888a564be4645b0bedec201ac0cb013dcfd9838fefd69e85f0f63752a  examples/extension/schema/retail-lending.schema.json
a600d93b5f7ce23e5ac2ff8ed689695d4d59b0a01b7439382c9642b665c72c65  examples/pydantic/generated.schema.json
bc45fc8fb7a7a6a6f92ff13177ca6f9b96eece555f1c1b9d3cf9df10fe960f0e  scripts/validate_instance.py
40a30a5495df70269da31cea3f2f69886a6ed696d328763614700eb360e1080c  tests/test_examples.py
8b9bf05f796ba41d912a1fc47998898dd931c4aad5b19d4b19497146fbce6324  requirements.txt
```

[`SHA256SUMS.txt`](SHA256SUMS.txt) contains the complete per-file payload hash set, excluding the hash file itself. The external delivery report records the final archive size and SHA-256 digest.
