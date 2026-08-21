# Split a schema across files

## Purpose

Use this guide to divide a contract into independent schema resources without changing reference meaning or requiring network access.

## Procedure

1. Identify module boundaries by ownership and reuse, not merely by file size.
2. Give each standalone resource the Draft 2020-12 `$schema` declaration.
3. Give each public resource a stable absolute `$id`.
4. Keep private definitions under `$defs` when no independent identity is needed.
5. Add `$anchor` only for a stable named entry point inside a resource.
6. Use `$dynamicAnchor` only for a recursive extension protocol.
7. Write `$ref` values against canonical resource IDs, not local paths.
8. Create a registry manifest that maps every canonical URI to a local file:

```json
{
  "https://example.org/schema/system": "system/schema/system.schema.json",
  "https://example.org/schema/retail-lending": "extension/schema/retail-lending.schema.json"
}
```

9. Resolve all relative `$id` and `$ref` values under RFC 3986 before approving the split.
10. Run the static reference checker from the root module:

```bash
python scripts/check_references.py ROOT.schema.json --registry registry.json
```

11. Validate representative instances using the same registry.
12. Delete one required registry entry in a temporary test and prove resolution fails rather than fetching or guessing.
13. Move a local file in a temporary test and prove canonical references still work after updating only the registry.
14. Preserve every original `$id` when creating a compound schema document or bundle.
15. Do not rewrite canonical IDs to `file:` URIs during packaging.
16. Document resource ownership, compatibility policy, and release lifecycle separately from the filesystem tree.

## Relative-reference check

For every relative reference, record:

```text
source resource URI
base URI at the reference location
authored reference
resolved absolute URI
registered local resource
```

Do not accept an explanation based only on where files happen to sit.

## Bundle check

A bundle MUST:

- retain each embedded resource `$id`;
- retain references that use those canonical IDs;
- expose the same validation results as the unbundled registry;
- avoid duplicate or conflicting resource identities;
- include no hidden network fallback.

## Authorities

Read [02 Identifiers and references](../references/02-identifiers-and-references.md) and [07 Validation and diagnostics](../references/07-validation-and-diagnostics.md).
