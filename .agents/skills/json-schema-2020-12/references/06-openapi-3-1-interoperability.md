# 06 OpenAPI 3.1 interoperability

Authority: OpenAPI Specification 3.1.2 and JSON Schema Draft 2020-12, listed in [00 Source manifest](00-source-manifest.md).

## Relationship

An OpenAPI 3.1 Schema Object is a superset of JSON Schema Draft 2020-12. OpenAPI 3.1.2 identifies its base Schema Object dialect as:

```text
https://spec.openapis.org/oas/3.1/dialect/base
```

The OpenAPI dialect requires the general Draft 2020-12 vocabularies plus the OpenAPI base vocabulary. OpenAPI-specific schema keywords are not automatically meaningful to a general JSON Schema validator.

OpenAPI is one projection target. Do not make an OpenAPI document the root authority for a general system contract unless the contract is inherently an HTTP API description.

## Dialect selection

An OpenAPI document MAY set `jsonSchemaDialect` as the default for Schema Objects that do not declare their own `$schema`. The OpenAPI version supplies a default OAS dialect when the field is absent.

A reusable general JSON Schema SHOULD retain its own Draft 2020-12 `$schema` and canonical `$id` outside OpenAPI. A projection step MAY adapt it to the OAS dialect and document any OpenAPI vocabulary added.

A validator MUST select the correct dialect for the context. Do not validate every Schema Object only against the general JSON Schema meta-schema and assume all OpenAPI annotations were understood.

## Components and reusable schemas

`components.schemas` stores reusable Schema Objects inside an OpenAPI document:

```yaml
components:
  schemas:
    System:
      type: object
      properties:
        id:
          type: string
```

A component key such as `System` is a document-local lookup name, not automatically a canonical schema URI. Preserve or assign `$id` according to the projection policy when independent identity matters.

Use references such as:

```yaml
$ref: '#/components/schemas/System'
```

Within a Schema Object, `$ref` follows JSON Schema semantics, including the application of sibling schema keywords. Outside Schema Objects, OpenAPI Reference Objects have OpenAPI-defined behavior. An agent MUST identify which object type it is editing before relying on sibling fields.

## Discriminators

The OpenAPI `discriminator` helps consumers select or document a union branch. It does not change JSON Schema validation results.

Keep the actual tag assertions:

```yaml
oneOf:
  - $ref: '#/components/schemas/ServiceNode'
  - $ref: '#/components/schemas/StoreNode'
discriminator:
  propertyName: kind
```

Each branch SHOULD still require `kind` and constrain it with `const`. A discriminator mapping MAY provide explicit names, but it does not repair overlapping or under-constrained branches.

Do not use `allOf` plus discriminator as a claim of object-oriented inheritance. OpenAPI explicitly treats discriminator behavior separately from validation.

## Nullable values

OpenAPI 3.1 uses JSON Schema unions for null:

```yaml
type: [string, 'null']
```

or:

```yaml
anyOf:
  - type: string
  - type: 'null'
```

Do not use the OpenAPI 3.0 `nullable: true` pattern in a 3.1 JSON Schema projection.

## Read and write annotations

`readOnly` and `writeOnly` retain JSON Schema annotation semantics. OpenAPI tooling may use them to derive request and response presentations, but the underlying validator does not automatically remove, reject, or insert properties.

An API contract MUST define request and response schemas or processing rules explicitly when those differences are security-relevant.

## When not to force a schema into OpenAPI

Keep a schema outside OpenAPI when it primarily describes:

- repository or configuration files;
- event, storage, or compiler intermediate forms unrelated to one HTTP operation;
- a compound schema document with independent resources;
- custom vocabularies unsupported by target OpenAPI tooling;
- dynamic recursive extension behavior that target generators cannot preserve;
- graph-wide semantic rules;
- a canonical domain model projected to several protocols.

A projection MAY reference or copy a bounded API-facing subset. It MUST record transformations, lost annotations, changed identifiers, and unsupported keywords.

## Interoperability review

An agent SHOULD:

1. identify the source schema dialect and the target OpenAPI version;
2. preserve JSON Schema assertions wherever possible;
3. add OpenAPI annotations without treating them as assertions;
4. convert nullable values to JSON Schema unions;
5. verify `$ref` targets in the final OpenAPI document;
6. test tagged unions without depending on discriminator behavior;
7. run both an OpenAPI document validator and a Draft 2020-12-capable schema validator where appropriate;
8. reject a projection that silently drops required custom vocabulary behavior;
9. keep the general schema as the root model when OpenAPI is only one output.
