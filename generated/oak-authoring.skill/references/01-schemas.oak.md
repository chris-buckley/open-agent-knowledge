<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
guidance: YAML<<
- Map reusable information shapes and contracts to schemas.
- 'Choose schema templates by information relationships: tables for comparison, outlines
  for hierarchy, sections for explanation, and fenced blocks for code; use lists only
  for list-shaped information.'
- Preserve requested layouts; the demonstrated shapes are examples, not a closed catalogue
  or a reason to force every schema into labelled fields.
- Keep templates and WHERE constraints in schema definitions; populated outputs fill
  its slots rather than copying the schema definition.
- A binding supplies one value per placeholder; repeated names reuse that value, and
  an ellipsis alone does not create independently typed rows or sections.
- Bind constants, state, processes, actions, and interfaces to schemas where values
  must validate; role names alone are not types.
>>

shape-source: "In the teaching mapping, assets/examples/shape_gallery/example.oak.md pairs complete schemas with populated instances without definition wrappers or WHERE. Its table has one fixed row; extend the template explicitly if justified."
</constants>
