# Model JSON-LD relationships

Use this guide to choose between a direct property, a reverse property, and a first-class relationship node. Read [01 Data model](../references/01-data-model.md) and [03 Keywords](../references/03-keywords-and-object-forms.md).

## Direct property

Use a direct property when the edge needs only its predicate and endpoints.

```json
{
  "@id": "sys:orders",
  "stores_in": {"@id": "sys:orders-db"}
}
```

Define `stores_in` with `@type: @id` when compact string values should become references.

## Reverse property

Use a reverse property when authors or consumers naturally start from the target.

```json
{
  "@id": "sys:orders-db",
  "@reverse": {
    "stores_in": {"@id": "sys:orders"}
  }
}
```

Verify by expansion that it produces the same forward predicate and endpoints.

## First-class relationship node

Use a relationship node when the edge needs its own identity or properties.

```json
{
  "@id": "rel:orders-storage",
  "@type": "schema:Relationship",
  "kind": {"@id": "term:stores_in"},
  "from": {"@id": "sys:orders"},
  "to": {"@id": "sys:orders-db"},
  "confidence": 0.98
}
```

Promote the relationship to a node when it needs one or more of:

- provenance;
- confidence;
- ownership;
- effective dates;
- evidence;
- constraints;
- an independent identifier;
- generator instructions;
- lifecycle or approval state.

## Procedure

1. Identify the intended directed predicate.
2. Define absolute identities for the predicate and both endpoints.
3. Decide whether the edge itself requires durable identity.
4. Choose direct, reverse, or first-class representation.
5. Define context coercion for every reference-valued property.
6. Keep endpoint objects as references unless the frame deliberately embeds them.
7. Validate the relationship shape with the application profile.
8. Build a node registry and verify every required target.
9. Reject duplicate relationship IDs and conflicting endpoint claims.
10. Preserve source and evidence provenance separately from compact authoring order.
11. Expand direct and reverse examples to confirm graph equivalence.
12. Round-trip the first-class node without losing its identifier or properties.

JSON-LD assigns graph meaning to the predicate and endpoints. It does not assign application behavior, execution order, ownership rules, or generator semantics unless the application contract defines them.
