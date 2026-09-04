<instructions>
This document owns package boundaries, canonical representation, authored syntax, parsing, rendering, vocabulary, surfaces, rules, and the public API.
The package in `oak` implements the exact executable OAK contract.
OAK owns knowledge and its internal contracts.
Leave model selection, credentials, network transport, tool implementations, server configuration, external persistence, scheduling, delivery, and external side effects to the host.
Permit OAK to name an exact tool contract without embedding its implementation or transport.
The `Node` model is the canonical in-memory meaning of one OAK document.
Use Pydantic as the programmatic authoring and validation form, not as a render.
Use OAK text as the human and interpreter authoring form.
Use JSON-LD as the interchange render.
Default rendering to OAK with XML grouping and authored style.
Let grouping change delimiters only.
Let style change only permitted natural-language wording and display formatting.
Require a controlled style to preserve meaning, obligation, negation, conditions, contracts, targets, and step order.
Define every concrete authored text variant once as a surface descriptor.
Use the same surface registry for rendering, parsing, EBNF, authoring generation, and generated model reference.
Keep reusable text shapes, datatypes, units, time forms, and display forms in `oak/vocabulary`.
Accept OAK as UTF-8 bytes or text and normalize line endings before parsing.
Infer grouping from the first present part delimiter when the caller does not name one.
Build one node through parsing and then run model and same-document validation.
Collect independent parse failures when structure permits and give each failure a stable code, path, optional line, and message.
Render only built-in interpretation instructions required by features present in the node.
Preserve every authored field in OAK text except instruction ids.
Require each canonical supported form to survive `Node -> OAK -> Node -> OAK` without text change.
Keep `oak/vocabulary` independent of node models.
Keep node models independent of parsing, rendering, resolution, and execution.
Keep parsing and rendering independent of each other.
Permit resolution to use parsing and node contracts without depending on execution.
Permit execution to use resolved node meaning without making node models depend on execution.
Expose the supported package API through explicit root exports.
Keep exact model fields and discriminated unions in their Pydantic models.
Keep exact authored tokens and shapes in `oak/surface` and `oak/vocabulary`.
Keep stable non-core rule text and codes in `oak/rules`.
Do not add a model field only to carry a render token.
Use the narrowest type, literal, bound, union, and nested model that expresses a contract.
Validate default values and reject unknown fields.
Build reusable adapters and regex-backed text shapes once at module import.
Prefer short typed authoring helpers with plain literal arguments over nested constructor keywords.
Prefer one discoverable dot-access namespace for each closed authoring set.
Keep render bytes unchanged when only the programmatic authoring surface changes.
</instructions>