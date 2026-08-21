# Design JSON-LD identifiers

Use this guide to define stable identities for nodes, predicates, classes, relationship records, documents, and contexts. Read [01 Data model](../references/01-data-model.md) first.

## Procedure

1. Name the authority that owns each namespace.
2. Choose HTTPS absolute IRIs for canonical public identities.
3. Keep entity identity independent of the file containing its statements.
4. Keep schema and vocabulary identity independent of entity identity.
5. Give contexts and vocabulary releases versioned identifiers.
6. Decide whether document versions need distinct document IRIs.
7. Use human-readable slugs only when renaming does not silently change identity.
8. Define redirects or equivalence mappings for deliberate renames outside this skill's core contract.
9. Assign a stable relationship IRI when the relationship carries properties or provenance.
10. Avoid blank nodes for cross-document, governed, or long-lived records.
11. Define compact prefixes only after absolute namespace ownership is settled.
12. Test every compact IRI through the governed context.
13. Reject unresolved relative application identifiers after expansion.
14. Record original and canonical identifiers when a migration maps old identities to new ones.

## Example conventions

These are project conventions, not W3C requirements:

```text
system:orders
system:orders/database
relationship:orders-stores-in-orders-db
schema:System
term:stores_in
```

A context may map them to:

```text
https://example.org/system/orders
https://example.org/system/orders/database
https://example.org/relationship/orders-stores-in-orders-db
https://example.org/schema/System
https://example.org/term/stores_in
```

## Identity checklist

An identifier is suitable when:

- its namespace has an owner;
- its meaning survives file moves;
- its spelling is stable under ordinary label changes;
- it can be expanded without ambient network state;
- it does not collide after application normalization;
- it can be logged and compared exactly;
- its version policy is documented;
- its lifecycle does not depend on blank-node labels.

Do not derive identity from JSON object order, array position, filesystem path, or a display label unless the contract explicitly makes that value permanent.
