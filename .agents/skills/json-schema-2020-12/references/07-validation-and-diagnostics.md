# 07 Validation and diagnostics

Authority: official `jsonschema` 4.26.0, `referencing` 0.37.0, and JSON Schema Draft 2020-12 documentation listed in [00 Source manifest](00-source-manifest.md).

## Default Python stack

Use:

```text
jsonschema[format-nongpl] == 4.26.0
referencing == 0.37.0
```

This stack supports Draft 2020-12, explicit resource registries, lazy error iteration, nested error context, instance paths, schema paths, and Python 3.10 or later.

The skill uses `Draft202012Validator` directly. It does not call a generic helper that chooses the latest installed draft when `$schema` is absent.

## Conformance posture

Bowtie can connect directly to `python-jsonschema` and run the official JSON Schema Test Suite, including a local Draft 2020-12 checkout. Use that route when qualifying an implementation or platform release.

This skill build runs its own focused acceptance fixtures rather than the entire official suite. An agent MUST NOT turn those fixture results into a blanket conformance claim.

## Install

From the skill root:

```bash
python -m pip install -r requirements.txt
```

The scripts use only local files and in-memory registries. They have no retrieval callback and therefore cannot fetch a missing URI.

## Validate a schema

```bash
python scripts/validate_schema.py examples/system/schema/system.schema.json
```

This gate:

1. parses UTF-8 JSON;
2. requires the exact Draft 2020-12 `$schema` URI;
3. calls `Draft202012Validator.check_schema`;
4. reports the schema location and meta-schema location on failure;
5. exits non-zero on error.

Meta-schema validation checks syntax. It does not dereference every cross-file `$ref`, prove useful constraints, or test instances.

## Check references

```bash
python scripts/check_references.py \
  examples/extension/schema/retail-lending.schema.json \
  --registry examples/registry.json
```

The checker resolves every `$ref` and the initial target of every `$dynamicRef` in the root and registered documents. It also rejects a resolved target that is not an object or boolean schema. It reports:

- source document;
- JSON Pointer to the keyword;
- authored reference;
- resolved absolute URI;
- success or failure.

It does not pretend that static lookup proves dynamic-scope selection. Run recursive instance fixtures for that behavior.

## Validate an instance

```bash
python scripts/validate_instance.py \
  examples/extension/schema/retail-lending.schema.json \
  examples/extension/retail-lending.valid.json \
  --registry examples/registry.json
```

The validator:

- selects `Draft202012Validator` explicitly;
- validates the root schema first;
- resolves only preloaded resources;
- sorts top-level errors deterministically;
- reports instance and schema JSON Pointers;
- includes nested `oneOf` context;
- returns 0 for valid, 1 for invalid, and 2 for tool, schema, dialect, JSON, or resource failures.

Use `--json` for machine-readable output.

## Format policy

Default annotation behavior:

```bash
python scripts/validate_instance.py SCHEMA INSTANCE --format-policy annotation
```

Assert every known format:

```bash
python scripts/validate_instance.py SCHEMA INSTANCE --format-policy assert-known
```

Assertion mode fails before instance validation when a used format lacks a registered checker. This avoids silently treating a project-specific format as enforced.

A registered checker is still an implementation of the format specification. Test critical edge cases and do not rely on `format` alone for security.

The selected Python implementation also supplies the regular-expression engine used for `pattern` and `patternProperties`. The schema checker does not pre-validate expressions with Python's `regex` format checker, because doing so would not prove ECMA-262 portability.

## Local registry manifest

A manifest maps canonical schema URIs to local paths:

```json
{
  "https://example.org/schema/system": "system/schema/system.schema.json"
}
```

Paths are relative to the manifest. Each loaded schema MUST declare Draft 2020-12. A declared `$id`, when present, MUST equal the manifest key.

Manifest keys MUST be absolute, fragment-free resource URIs. Manifest paths MUST stay beneath the manifest directory; use an explicit `--resource URI=PATH` argument for a deliberate external file. This separates a portable checked manifest from caller-authorized filesystem access.

Add one resource without a manifest:

```bash
python scripts/validate_instance.py SCHEMA INSTANCE \
  --resource https://example.org/schema/system=examples/system/schema/system.schema.json
```

The scripts reject conflicting resources registered under one URI. They do not scan directories or use filename guesses.

## Schema errors and instance errors

Treat these categories separately:

- JSON parse error: the document is not JSON.
- dialect error: `$schema` is missing or unsupported.
- schema error: the schema fails its meta-schema.
- resource error: a reference target is unavailable or ambiguous.
- instance error: a valid schema rejects an instance.
- graph or business error: the instance is structurally valid but violates application semantics.

Do not summarize all categories as "validation failed". The repair owner and safe next action differ.

## Error paths

Report both:

- instance path: where the failing value appears in the instance;
- schema path: where the failing keyword appears in the evaluated schema.

Use JSON Pointer notation. An empty pointer means the document root.

For references, also report the target resource URI. A schema path alone can be ambiguous after evaluation crosses resources.

## Diagnosing `oneOf`

A top-level `oneOf` message is a summary. Inspect its `context` children.

Use this sequence:

1. read the tag value and instance path;
2. count branches that fully matched;
3. when zero matched, group child errors by branch;
4. when several matched, find missing tag constraints or overly broad branches;
5. prefer a required `const` tag over structural inference;
6. remove duplicate noise only after preserving complete machine-readable details.

The invalid node fixture omits `currency` from a `loan-product` branch and exercises nested diagnostics.

## Recursive structures

For recursion failures, report the deepest failing instance path and the schema resource selected at that depth. Do not truncate the only useful nested error.

Set application limits for input bytes, nesting depth, total nodes, total errors, and execution time. The specification does not impose operational limits.

## Unsupported vocabularies

The selected scripts support the general Draft 2020-12 dialect. They do not execute arbitrary custom vocabulary code.

A custom dialect runner MUST:

1. load the declared meta-schema;
2. inspect `$vocabulary` at its resource root;
3. prove support for every vocabulary marked `true`;
4. refuse processing when required support is absent;
5. report optional unsupported vocabularies;
6. preserve unknown annotations in output if its output model requires them.

## Graph target check

After structural validation, run:

```bash
python scripts/check_graph_targets.py examples/extension/retail-lending.valid.json
```

The script recursively indexes node IDs and checks relationship `from` and `to` values. It also reports duplicate or malformed node IDs. It is deliberately separate from JSON Schema validation.

## Test suite

Run:

```bash
python -m unittest discover -s tests -v
```

The included tests cover:

- meta-schema validity for every standalone schema;
- offline cross-file resolution;
- hard failure for a missing resource;
- base and domain validation;
- parent-contract satisfaction;
- `unevaluatedProperties` closure;
- recursive dynamic-reference rebinding;
- Pydantic generation determinism and aliases;
- format annotation and assertion policies;
- exact instance and schema paths;
- structural success followed by graph-target failure.

The skill does not vendor or claim to rerun the entire official JSON Schema Test Suite. Use that suite or Bowtie when qualifying a validator implementation beyond these skill fixtures.

## Deterministic operating rules

An agent MUST:

- pin dependency versions for reproducible evidence;
- sort diagnostics before snapshotting them;
- avoid network retrieval by default;
- make the dialect explicit;
- validate schemas before instances;
- fail on inaccessible references;
- state the format policy;
- preserve complete nested errors in machine output;
- run semantic checks as separate named gates;
- remove caches and generated clutter before packaging.
