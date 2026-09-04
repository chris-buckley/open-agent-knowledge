<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "One OAK document, its node, seven parts, value lifetimes, schemas, cross-part dataflow, and same-document validation."

part-order: ["instructions", "constants", "schemas", "state", "triggers", "processes", "interfaces"]

part-responsibilities: CSV<<
part,owns,lifetime,excludes
instructions,irreducible interpreter policy,whole document use,"facts, reusable shapes, mutable values, routing, ordered work, and boundary payloads"
constants,fixed JSON knowledge,whole document use,mutable values
schemas,reusable information shapes,definition,boundary flow and process routing
state,persistent mutable JSON values,across arrivals,invocation-local results
triggers,outside occurrence routing,one arrival decision,internal sequencing
processes,ordered local work,one invocation,outside transport
interfaces,complete boundary schema instances,one receive or emission,information shape definitions
>>

value-lifetimes: CSV<<
value,scope
constant,fixed during document use
state,persistent across arrivals
process binding,immutable in one frame or child scope
interface instance,one complete boundary occurrence
>>

node-invariants: YAML<<
- One OAK file contains exactly one idless node.
- Every entry id is unique across all parts in one document.
- Empty parts are omitted without changing canonical part order.
- A source-backed trigger has no seeds and shares one resolved schema with its selected
  process input.
- An event-backed trigger can seed process input from literals, constants, and state.
- Trigger guards read state only.
- Interface instances never become ambient process storage.
- State and interface operations remain local to the active document.
>>

validation-ownership: CSV<<
boundary,owns
model,one field or object shape
node,"same-document ids, targets, contracts, binding flow, local cycles, and interface use"
resolver,facts that require another document
executor,supplied and produced runtime values
>>
</constants>

<processes>
<process id="change-node" name="Change node">
ACT Use <PARTS> and <LIFETIMES> to place each new fact in one semantic owner before considering instructions. (PARTS=$constant.part-responsibilities, LIFETIMES=$constant.value-lifetimes)
ACT Preserve <ORDER> and <INVARIANTS> across models, validation, authoring, parsing, rendering, and examples. (ORDER=$constant.part-order, INVARIANTS=$constant.node-invariants)
ACT Use <VALIDATION> to place each check at the earliest boundary with all required information. (VALIDATION=$constant.validation-ownership)
ACT Keep exact field, constraint, and error details in implementation and generated reference instead of restating them here. ()
</process>
</processes>