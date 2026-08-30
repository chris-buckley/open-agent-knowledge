# Base system example

[`schema/system.schema.json`](schema/system.schema.json) defines an extensible `BaseSystem` resource at `https://example.org/schema/system`.

It contains:

- an application identifier shape;
- metadata;
- common node and relationship cores;
- closed known service, store, container, contains, and stores-in leaves;
- open extension branches for unknown node and relationship kinds;
- recursive container children;
- an open System root.

[`schema/system-closed.schema.json`](schema/system-closed.schema.json) applies the base and closes the complete root with `unevaluatedProperties: false`.

[`base-system.valid.json`](base-system.valid.json) passes both schemas. [`base-system-closed.invalid.json`](base-system-closed.invalid.json) adds `unexpected` and fails the closed profile.
