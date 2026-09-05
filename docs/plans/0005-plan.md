# Shape-first schema authoring

Status: Complete for the authoring and example scope below.
Baseline: main at 0d8d6d2eb0131da5c00a6572cf5a2688b4a98ce9.

## Accepted outcome

Help interpreters choose useful information arrangements instead of defaulting to
labelled records. Keep one OAK schema concept, the existing seven parts, and the
current grammar. Do not introduce task-specific YAML or a separate format system.

## Implementation checks

- [x] Record the durable authoring correction in the owning AGENTS document.
- [x] Add shape-selection, layout-preservation, and definition/instance guidance.
- [x] Put comparison, decision, outline, and code schemas with populated examples
  into the generated authoring prompt without raising its 18,000-byte limit.
- [x] Add canonical Python/OAK examples and a real typed process pipeline that uses
  all four shapes across explicit document references.
- [x] Label the fixture host and text substitution helper as demonstrations rather
  than live inference or a production presentation engine.
- [x] Replace the existing title-review record template with a sectioned result.
- [x] Correct the process-execution table delimiter and its fixed-row description.
- [x] Check bindings and populated presentations, including malformed fixtures,
  both OAK groupings, and runtime output rejection.
- [x] Regenerate affected outputs and examples, run both repository entry points,
  inspect the diff, and verify repeated generation leaves the same bytes.

## Repetition: design sketch only

This section is not an accepted grammar or an implemented capability.

The focused extension should bind an ordered collection of complete instances of
one reusable schema. Each item needs its own placeholder scope and validation;
repeating a placeholder name must not silently become a second value. One generic
repeated-block mechanism should serve table rows, report sections, and file blocks.
A containing template must distinguish content rendered once from the repeated
block. Schema selection should preserve existing resolved document/schema identity.

Before implementation, decide cardinality bounds, empty-collection presentation,
separators, nesting and recursion limits, binding paths, cross-field constraints,
and canonical XML/Markdown round trips. The same semantics must cover received
values, native/tool action outputs, calls, and emissions. Presentation escaping
and fence collisions also need explicit host or language ownership. Do not reserve
new tokens or teach an ellipsis as machine-validated repetition in the meantime.
