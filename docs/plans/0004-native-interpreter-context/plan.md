# Native OAK interpreter context and revision-linked evidence

## Accepted scope

Keep OAK as the only authored knowledge format. Derive interpreter requests from existing OAK models and canonical renders. Upgrade the implementer so verification belongs to the exact work accepted. Provide conservative task views without changing the language or execution graph.

## Completion checks

* [x] Preserve source policy scope, schema identity, document boundaries, and current state in interpreter context.
* [x] Produce detached, canonical OAK action invocations with literal inputs, without a task-specific YAML contract or new syntax.
* [x] Integrate an optional context interpreter with input/output validation while retaining the named direct callback and tool contracts.
* [x] Keep complete runtime context and make task selection explicit, whole-document, dependency-complete, and conservative about prose.
* [x] Add a reusable subject/revision/check/result/evidence schema using existing OAK authoring.
* [x] Apply findings before snapshotting and verifying the candidate; gate commit on matching successful evidence.
* [x] Require the effect-producing host to reject candidate drift before its effect.
* [x] Add executable OAK examples and regression checks to the existing verification entry point.
* [x] Regenerate affected examples and all reference outputs; verify repeated generation is byte-stable.
* [x] Run compilation, both local verification entry points, and whitespace checks.
* [x] Verify the final implementation tree on GitHub.

## Boundaries

The direct callback remains available for existing programmatic hosts. The new interpreter callback receives named OAK documents, not a second task language. Runtime context keeps the complete resolved graph; explicit task views retain whole documents and their reference closure. Source instructions are not transplanted into a synthetic document where local references would change meaning.

The verification schema validates the record, not its truth. Host tools own snapshot creation, actual checks, recorded evidence, and pre-effect drift rejection. Deterministic demonstration adapters are not live model integrations; the verification fixture uses real checks of fixed source examples and a simulated commit sink. No model credentials, vendor integration, network loader, implicit imports, or per-entry semantic pruning are added.
