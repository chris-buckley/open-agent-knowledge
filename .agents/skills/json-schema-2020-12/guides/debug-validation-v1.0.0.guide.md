# Debug validation

## Purpose

Use this guide to isolate a failure without confusing JSON parsing, dialect selection, schema validity, reference resolution, instance validation, or semantic validation.

## Procedure

1. Reproduce the failure with pinned dependencies and local fixtures.
2. Parse the schema, instance, and registry as JSON.
3. Check the root `$schema` value before reading any instance error.
4. Validate the schema against the Draft 2020-12 meta-schema:

```bash
python scripts/validate_schema.py SCHEMA
```

5. Resolve the complete local reference graph:

```bash
python scripts/check_references.py SCHEMA --registry REGISTRY
```

6. Validate the smallest failing instance and request JSON output:

```bash
python scripts/validate_instance.py SCHEMA INSTANCE --registry REGISTRY --json
```

7. Read the instance path, schema path, keyword, and nested context.
8. For `oneOf`, determine whether zero or multiple branches matched.
9. For an extra property, identify which schema object contains `additionalProperties` or `unevaluatedProperties`.
10. For a relative reference, compute the base URI at that exact schema location.
11. For a format issue, repeat with both annotation and assertion policies and record the checker set.
12. For recursion, inspect the deepest failing path and the resource selected at that depth.
13. For Pydantic divergence, compare aliases, strictness, validation mode, serialization mode, defaults, custom validators, and schema extras.
14. After structural success, run graph and business checks separately.
15. Add the minimized failure as a regression fixture before changing the schema.
16. Rerun all valid, invalid, parent-contract, recursive, and Pydantic fixtures.
17. Record the root cause and why the chosen fix preserves compatibility.

## Useful commands

Validate the known invalid root-property fixture:

```bash
python scripts/validate_instance.py \
  examples/extension/schema/retail-lending.schema.json \
  examples/invalid/retail-lending.invalid.json \
  --registry examples/registry.json
```

Exercise nested `oneOf` diagnostics:

```bash
python scripts/validate_instance.py \
  examples/extension/schema/retail-lending.schema.json \
  examples/invalid/retail-lending-node.invalid.json \
  --registry examples/registry.json --json
```

Prove that structural target shape and graph target existence differ:

```bash
python scripts/validate_instance.py \
  examples/extension/schema/retail-lending.schema.json \
  examples/extension/retail-lending.missing-target.json \
  --registry examples/registry.json
python scripts/check_graph_targets.py \
  examples/extension/retail-lending.missing-target.json
```

## Authorities

Read [07 Validation and diagnostics](../references/07-validation-and-diagnostics.md) and [08 Error catalog](../references/08-error-catalog.md).
