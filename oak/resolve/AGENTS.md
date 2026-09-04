<instructions>
This document owns document identity, target paths, explicit loading, graph traversal, resolved contracts, cross-document scope, and process-call cycle checks.
Define a document graph as OAK documents connected by typed target paths.
Keep composition outside the seven node parts.
Use a part-qualified entry path for a local target.
Use a relative POSIX document path plus a part-qualified fragment for a relative target.
Permit relative targets for schemas, constants, and processes only.
Keep state and interface operations in the active document.
Validate one node locally without loading external targets.
Resolve a graph only when the caller supplies the root document path, root node, and exact document loader.
Do not scan directories, guess filenames, use the working directory as a registry, or fetch the network during resolution.
Identify each loaded document by its normalized resolved path.
Preserve each authored relative path for rendering and diagnostics.
Traverse only documents reachable through explicit targets.
Verify every loaded document, fragment, and expected entry type.
Treat two schema targets as one contract only when they resolve to the same document and schema id.
Do not infer contract identity from equal placeholders or equal-looking templates.
Validate resolved schema bindings, calls, actions, interfaces, and source-backed trigger handoffs.
Reject process-call cycles that appear after relative targets resolve.
Permit document-reference cycles when they do not create a process-call cycle.
Leave storage mapping to the host and require only a deterministic loader.
Keep runtime execution outside resolution.
</instructions>