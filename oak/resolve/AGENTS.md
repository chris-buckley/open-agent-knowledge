<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Document identity, target paths, explicit loading, graph traversal, resolved contracts, cross-document scope, and process-call cycle checks."

target-forms: CSV<<
form,shape,example
local,part-qualified entry path,schema.request
relative,relative POSIX .oak.md path plus part-qualified fragment,workers/reviewer.oak.md#process.review
>>

relative-target-parts: ["schema", "constant", "process"]

local-only-operations: ["state read", "state write", "receive source", "emission"]

resolution-order: ["index local entries", "find explicit relative targets", "load each exact document", "parse and validate the loaded node", "verify fragment and expected type", "continue through reachable targets", "validate resolved contracts and process-call cycles"]

graph-rules: YAML<<
- Require the caller to supply the root path, root node, and deterministic loader.
- Do not scan directories, guess filenames, use the working directory as a registry,
  or fetch the network.
- Identify loaded documents by normalized resolved path while preserving authored
  paths for rendering and diagnostics.
- Treat schema contracts as identical only when document and schema id both resolve
  identically.
- Permit document-reference cycles but reject process-call cycles.
>>
</constants>

<processes>
<process id="change-resolution" name="Change resolution">
ACT Use <TARGETS> to preserve local and relative target meaning. (TARGETS=$constant.target-forms)
ACT Keep <RELATIVE> as the only relative entry parts and <LOCAL> inside the active document. (
  RELATIVE=$constant.relative-target-parts,
  LOCAL=$constant.local-only-operations,
)
ACT Follow <ORDER> for deterministic reachable graph construction. (
  ORDER=$constant.resolution-order,
)
ACT Apply <RULES> to loading, identity, contract validation, and cycle detection. (
  RULES=$constant.graph-rules,
)
</process>
</processes>