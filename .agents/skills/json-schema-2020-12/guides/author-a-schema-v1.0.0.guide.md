# Author a schema

## Purpose

Use this guide to create one standalone JSON Schema Draft 2020-12 document and prove its basic correctness.

## Inputs

Prepare:

- the instance boundary and intended consumers;
- valid and invalid example instances;
- a canonical schema URI;
- a decision on whether the root is open or closed;
- any external schema resource URIs;
- application rules that must remain outside JSON Schema.

## Procedure

1. Write the instance shape before writing keywords. Separate JSON fields from graph-wide or business rules.
2. Create a schema object with the exact Draft 2020-12 `$schema` URI.
3. Assign a stable absolute `$id` without a non-empty fragment.
4. Add `title` and a short `description` for the root contract.
5. Add explicit `type` constraints wherever type is part of the contract.
6. Add `properties` and `required` independently for object records.
7. Put reusable private subschemas in `$defs`.
8. Use tagged `oneOf` branches for polymorphic records.
9. Keep an extensible base open; close a complete leaf with `unevaluatedProperties: false` when composition contributes fields.
10. Use `prefixItems` and `items` for Draft 2020-12 tuple or array behavior.
11. Treat `format`, content keywords, defaults, and documentation fields as annotations unless an explicit policy says otherwise.
12. Add one valid fixture and one invalid fixture for each important constraint.
13. Validate the schema:

```bash
python scripts/validate_schema.py path/to/schema.json
```

14. Check its references with an explicit registry:

```bash
python scripts/check_references.py path/to/schema.json --registry path/to/registry.json
```

15. Validate both fixtures:

```bash
python scripts/validate_instance.py path/to/schema.json path/to/valid.json --registry path/to/registry.json
python scripts/validate_instance.py path/to/schema.json path/to/invalid.json --registry path/to/registry.json
```

16. Run a separate semantic checker for graph, ownership, authorization, or cross-document rules.
17. Record the dialect, canonical ID, dependency URIs, format policy, and known semantic limits in the change review.

## Review questions

- Does the schema describe the accepted JSON representation rather than an in-memory object after coercion?
- Does every standalone document declare Draft 2020-12?
- Does every public resource have a stable identifier?
- Can every reference resolve without network access?
- Are `oneOf` branches mutually exclusive?
- Does closure occur only where the complete field set is known?
- Do valid examples pass and invalid examples fail for the claimed reason?
- Are defaults and annotations described without implying validator side effects?
- Are graph-wide rules named and checked elsewhere?

## Authorities

Read [01 Core and vocabularies](../references/01-core-and-vocabularies.md), [02 Identifiers and references](../references/02-identifiers-and-references.md), [03 Validation keywords](../references/03-validation-keywords.md), and [04 Composition and extension](../references/04-composition-and-extension.md).
