# Design a JSON-LD context

Use this guide to create or revise a governed JSON-LD 1.1 context. Read [02 Contexts](../references/02-contexts.md) and [08 Security](../references/08-security.md) first.

## Inputs

Collect:

- the stable vocabulary IRIs;
- the compact terms authors need;
- each property's expected value kind;
- intended containers and scoped contexts;
- namespace ownership and version policy;
- the application profile and processor versions;
- the local context registry policy.

## Procedure

1. List every compact term and the absolute IRI it must denote.
2. Separate entity identifiers, vocabulary identifiers, document identifiers, and source locations.
3. Define explicit prefix terms with `@prefix: true`.
4. Use `@vocab` only when unknown terms may safely expand into that namespace.
5. Use `@base` only for a controlled document boundary.
6. Add `@type: @id` for properties whose compact string values are node identifiers.
7. Add `@type: @vocab` only for controlled vocabulary values.
8. Add datatype, language, direction, or `@json` coercion only when it is semantically intended.
9. Choose containers from the permitted JSON-LD 1.1 combinations.
10. Use property-scoped or type-scoped contexts when the same local spelling requires a deliberately limited scope.
11. Protect contract-critical terms with `@protected`.
12. Keep `@import` acyclic and ensure the imported context does not contain another `@import`.
13. Publish a new immutable context IRI for a breaking mapping change.
14. Pin the exact context bytes and SHA-256 in the local registry.
15. Expand representative valid and invalid documents with the default processor.
16. Confirm every compact term expands to the intended absolute IRI.
17. Run compaction and semantic round-trip tests.
18. Review the change against Pydantic, JSON Schema, frames, and downstream graph consumers.

## Review questions

- Can a misspelled property silently expand under `@vocab`?
- Can a string be mistaken for a literal instead of a node reference?
- Can a later context override a critical mapping?
- Does a relative ID depend on retrieval location?
- Does a container alter cardinality or compact map shape?
- Will a type-scoped context propagate farther than intended?
- Does null context processing conflict with protected terms?
- Can every remote context be resolved offline and integrity checked?

## Deliverables

Produce:

1. A versioned context document.
2. A registry entry with exact IRI, local path, media type, and SHA-256.
3. Compact, expanded, and round-trip examples.
4. A change note listing every added, removed, or remapped term.
5. Regression tests for protected definitions, cycles, and unapproved loading.

Do not approve the context because the compact JSON looks readable. Approve it only after inspecting expanded identities and value forms.
