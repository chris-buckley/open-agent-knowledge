# 04 Composition and extension

Authority: JSON Schema Draft 2020-12 Core and the official object, composition, and conditional guides listed in [00 Source manifest](00-source-manifest.md).

## Composition semantics

`allOf` means that every subschema applies and every subschema must validate.

`anyOf` means that at least one subschema must validate.

`oneOf` means that exactly one subschema must validate.

`not` means that its subschema must fail.

`if` selects whether `then` or `else` applies. `if` does not itself make the whole schema fail. An absent `then` or `else` behaves like `true`.

These are logical applicators. They do not copy JSON, merge object properties, instantiate classes, or decide a programming-language subtype.

## `allOf` is not inheritance

Do not describe `allOf` as object-oriented inheritance. It applies all constraints independently. A closed base does not become open because another branch declares more properties. No branch overrides another branch.

Schema composition does not merge instance values. It only evaluates the same instance against several schemas.

Annotations can arise from several successful branches. Validation success does not tell an application how to resolve competing `default`, `title`, or other annotation values. Define an application policy when annotation precedence matters.

## `oneOf` diagnostics

`oneOf` fails when zero branches match and when more than one branch matches. Structural unions with similar branches can therefore produce large nested error trees.

Prefer tagged unions:

```json
{
  "oneOf": [
    {
      "type": "object",
      "properties": {"kind": {"const": "service"}},
      "required": ["kind", "endpoint"]
    },
    {
      "type": "object",
      "properties": {"kind": {"const": "store"}},
      "required": ["kind", "engine"]
    }
  ]
}
```

Each branch SHOULD constrain the tag with `const` so branches cannot overlap. A discriminator annotation in another ecosystem does not replace these assertions.

When debugging `oneOf`, inspect every child error. First ask whether no branch matched or several did. Then group failures by branch and instance path.

## Closed base record

A base intended never to be extended MAY close itself:

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "string"}
  },
  "required": ["id"],
  "additionalProperties": false
}
```

Use this only when the base owns the complete property set. A later `allOf` branch cannot add a property to this object.

## Extensible base record

An extensible base MUST leave extension points open. It SHOULD constrain the common core and reserve tag space without closing the final object.

The included `BaseSystem` uses:

- `NodeCore` and `RelationshipCore` for common fields;
- closed known leaf kinds;
- open `ExtensionNode` and `ExtensionRelationship` branches whose tags exclude known base tags;
- an open root `System` contract;
- a separate `ClosedBaseSystem` leaf profile.

This lets a domain instance satisfy the base through the extension branch while a domain schema applies a stricter known branch.

## Domain adaptor that satisfies a parent

A domain adaptor SHOULD apply the parent contract and its domain constraints to the same instance:

```json
{
  "allOf": [
    {"$ref": "https://example.org/schema/system"},
    {
      "type": "object",
      "properties": {
        "domain": {"const": "retail-lending"},
        "nodes": {
          "type": "array",
          "items": {"$ref": "#/$defs/RetailNode"}
        }
      },
      "required": ["domain"]
    }
  ],
  "unevaluatedProperties": false
}
```

This is constraint composition, not inheritance. Validate representative domain instances against both the adaptor and the parent as a regression test.

## Closing an extended leaf

Put `unevaluatedProperties: false` on the final composed object after every allowed branch has had a chance to evaluate its fields.

For a leaf kind:

```json
{
  "allOf": [
    {"$ref": "https://example.org/schema/system#/$defs/NodeCore"},
    {
      "type": "object",
      "properties": {
        "kind": {"const": "loan-product"},
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"}
      },
      "required": ["currency"]
    }
  ],
  "unevaluatedProperties": false
}
```

Do not place `additionalProperties: false` inside `NodeCore`; doing so would reject the extension fields.

## Discriminated node family

A node family SHOULD use one required tag field and non-overlapping branches. Each public branch SHOULD define its complete leaf closure.

The base and retail examples use `kind` tags such as:

```text
service
store
container
loan-product
repayment-structure
```

These names are example project conventions. JSON Schema does not reserve them.

## Discriminated relationship family

Model a relationship as an ordinary first-class object when it needs an identifier or attached data:

```json
{
  "id": "relationship:loan-uses-monthly",
  "kind": "uses-repayment-structure",
  "from": "node:home-loan",
  "to": "node:monthly"
}
```

Use a tagged `oneOf` for relationship kinds. JSON Schema can validate the fields and tag. It cannot generally prove that `from` and `to` resolve to existing nodes or permitted endpoint kinds.

## Recursive containment

Use a recursive node definition when nested containers have the same union:

```json
{
  "$defs": {
    "Container": {
      "type": "object",
      "properties": {
        "kind": {"const": "container"},
        "children": {
          "type": "array",
          "items": {"$ref": "#/$defs/Node"}
        }
      },
      "required": ["kind", "children"]
    },
    "Node": {
      "oneOf": [
        {"$ref": "#/$defs/Container"},
        {"$ref": "#/$defs/Leaf"}
      ]
    }
  }
}
```

Use `$dynamicRef` only when an extending schema must tighten every descendant. See [02 Identifiers and references](02-identifiers-and-references.md) and the recursive fixtures.

## Cross-file schema modules

A module SHOULD:

1. declare Draft 2020-12 explicitly;
2. own a stable absolute `$id`;
3. expose intended entry points through resource IDs or anchors;
4. keep internal `$defs` private unless consumers need them;
5. resolve all dependencies from an explicit registry;
6. avoid canonical `file:` identifiers;
7. preserve IDs when bundled.

A project SHOULD separate namespace ownership from file layout. Moving `schema/system.schema.json` must not change `https://example.org/schema/system`.

## Versioned identifiers

JSON Schema does not define a universal schema-versioning policy. Choose one project convention and document compatibility.

Useful patterns include:

```text
immutable major URI: https://example.org/schema/system/v1
immutable release URI: https://example.org/schema/system/1.2.0
moving channel URI: https://example.org/schema/system/latest
```

A stable unversioned URI MAY identify an evolving compatible contract, but only a project release policy can define what compatible means. Do not infer compatibility from an unchanged `$id` alone.

A breaking change SHOULD receive a new immutable identifier or a new negotiated version. A registry SHOULD pin the intended version rather than depend on a mutable network response.

## Extension fields

Two common extension styles are project conventions:

- a reserved property prefix such as `x-project-` combined with `patternProperties`;
- an explicit `extensions` object whose values follow a known extension schema.

Example prefix policy:

```json
{
  "type": "object",
  "patternProperties": {
    "^x-project-[a-z0-9-]+$": true
  }
}
```

This permits extension data structurally. It does not assign semantics or ownership. A project MUST define those separately.

## Custom vocabularies

Use a custom vocabulary only when custom keywords need portable schema-processing semantics, not merely extra documentation fields.

A vocabulary author MUST define:

- a stable vocabulary URI;
- keyword syntax and semantics;
- applicator, assertion, and annotation behavior;
- interaction with other vocabularies;
- a vocabulary meta-schema;
- implementation support and failure behavior;
- test cases and output expectations.

An application schema cannot make an unknown required vocabulary work by adding `$vocabulary` directly. Define a custom meta-schema and refer to it with `$schema`.

Prefer namespaced annotations for simple project metadata when no evaluator needs standardized behavior.

## Standard behavior and project conventions

| Concern | JSON Schema standard behavior | Example project convention |
| --- | --- | --- |
| Schema identity | `$id` identifies a schema resource | `https://example.org/schema/system` namespace |
| Object identity | Ordinary instance data only | strings such as `node:orders` |
| Relationship | Ordinary object shape | `kind`, `from`, and `to` fields |
| Extension namespace | Not prescribed | `x-project-*` fields or domain tags |
| Compatibility | Not prescribed | major-version URI policy |
| Graph target existence | Not generally enforced | post-schema graph checker |
| Ownership and approval | Not prescribed | metadata and governance layer |

An agent MUST label every local choice as a convention and MUST NOT present it as a W3C, IETF, JSON Schema, Pydantic, or OpenAPI requirement.
