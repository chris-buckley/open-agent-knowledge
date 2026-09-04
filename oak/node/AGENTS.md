<instructions>
This document owns one OAK document, its node, seven parts, value lifetimes, schemas, cross-part dataflow, and same-document validation.
One OAK file is one document and contains exactly one node.
Use the document path as node identity because a node has no id and contains no node.
Keep the closed parts in this order: instructions, constants, schemas, state, triggers, processes, interfaces.
Omit an empty part from OAK rendering without changing part order.
Permit one document to contain static knowledge or an executable state machine without requiring interfaces or triggers.
Give every entry one id that is unique across all parts in its document.
Use instructions for rules the interpreter follows during the whole use of a document.
Use constants for JSON values fixed during use.
Use schemas for reusable information shapes independent of boundary flow and process routing.
Use state for mutable JSON values that persist across arrivals.
Use triggers only for routing outside occurrences to one process.
Use processes for ordered invocation-local work.
Use interfaces for one-way boundary crossings of complete schema instances.
Permit one schema to type constants, state, process contracts, action contracts, interfaces, and tool contracts without changing its identity.
Require every schema template placeholder to have one matching ordered constraint entry.
Apply datatype checks before dependent schema constraints.
Permit constants and state to bind one value to one schema placeholder.
Keep fixed constants, persistent state, immutable process bindings, and boundary interface instances as separate value lifetimes.
Seed a process frame from its input schema placeholders.
Keep each process binding immutable and local to its frame or child scope.
Do not expose an interface instance as ambient process storage.
Require a source-backed trigger to have no seeds and to share one resolved schema with its selected process input.
Permit an event-backed trigger to seed process input from literals, constants, and state.
Restrict non-true trigger guards to state values.
Require every declared process output placeholder to be visible after successful completion.
Use `CALL` contracts to compose internal processes without sharing local frames.
Check document-wide ids, local target type, local contracts, binding visibility, branch reachability, local call cycles, and interface flow during node validation.
Validate each rule at the earliest same-document boundary that has all required information.
Reject type coercion and unknown fields in authored models.
Keep state reads, state writes, receive sources, and emissions local to the active document.
Defer only information that requires another document to `oak/resolve`.
Defer supplied or produced runtime values to `oak/execute`.
Keep exact field, constraint, and error details in the implementation and generated reference.
</instructions>