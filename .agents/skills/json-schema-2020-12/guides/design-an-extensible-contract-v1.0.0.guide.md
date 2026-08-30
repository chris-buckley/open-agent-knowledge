# Design an extensible contract

## Purpose

Use this guide to design a base record that domain adaptors can constrain without breaking parent validation.

## Procedure

1. Decide whether the base owns the complete future field and kind set.
2. Use a closed base only when no external extension is permitted.
3. For an extensible base, define common object cores without `additionalProperties: false`.
4. Define each known leaf kind as a tagged branch and close that leaf after all shared and leaf fields apply.
5. Reserve an extension branch whose tag excludes every known base tag.
6. Define relationships as first-class objects when they need identity, kind, endpoint fields, or metadata.
7. Give relationship kinds the same non-overlapping tag discipline as node kinds.
8. Let the root base validate common fields and extension branches without final closure.
9. Build the domain adaptor with `allOf`: one parent `$ref` and one or more domain constraints.
10. Replace extensible arrays with domain-specific tagged unions in the domain branch.
11. Close the final domain root with `unevaluatedProperties: false`.
12. Use ordinary recursive `$ref` for fixed recursive containment.
13. Use `$dynamicRef` only when a domain extension must tighten every recursive descendant.
14. Validate one domain instance against both the domain adaptor and the base.
15. Add an unknown-property fixture and prove final closure rejects it.
16. Add an unknown-domain-kind fixture and prove the domain union rejects it even when the base extension branch accepts its shape.
17. List graph rules, such as target existence and permitted endpoint kinds, for a separate semantic validator.

## Pattern selection

Use this decision table:

| Need | Pattern |
| --- | --- |
| No future properties or kinds | Closed base with `additionalProperties: false` |
| Shared core plus independent extensions | Open core plus extension branch |
| Complete leaf assembled from several schemas | `allOf` plus leaf `unevaluatedProperties: false` |
| Known polymorphic family | Required tag plus `oneOf` and branch `const` |
| Domain must satisfy parent | Parent `$ref` and domain constraints in `allOf` |
| Fixed recursive shape | Recursive `$ref` |
| Recursive shape tightened by extension | `$dynamicAnchor` and `$dynamicRef` protocol |
| Relationship target must exist | Post-schema graph check |

## Failure traps

Do not:

- call `allOf` inheritance;
- put `additionalProperties: false` in a core intended for extension;
- depend on overlapping structural `oneOf` branches;
- use `default` to imply field insertion;
- use `$ref` as an application relationship;
- assume `uniqueItems` makes object IDs unique;
- add custom vocabulary semantics without a custom dialect and implementation.

## Authorities

Read [03 Validation keywords](../references/03-validation-keywords.md) and [04 Composition and extension](../references/04-composition-and-extension.md). Study [`examples/system/schema/system.schema.json`](../examples/system/schema/system.schema.json) and [`examples/extension/schema/retail-lending.schema.json`](../examples/extension/schema/retail-lending.schema.json).
