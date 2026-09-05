<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Package boundaries, representation, derived interpreter context, authored syntax, parsing, rendering, vocabulary, surfaces, rules, and the public API."

host-boundary: CSV<<
owner,responsibility
OAK,"knowledge, internal contracts, canonical models, authored representations, explicit graph resolution, and execution semantics"
host,"model selection, credentials, transport, tool implementations, scheduling, persistence mechanism, delivery, and external side effects"
>>

representation-map: CSV<<
form,role
Node,canonical in-memory meaning
Pydantic,programmatic authoring and validation
OAK text,human and interpreter authoring
JSON-LD,interchange render
surface descriptor,single authored syntax definition shared by all syntax consumers
>>

package-dependencies: YAML<<
- Keep vocabulary independent of node models.
- Keep node models independent of parsing, rendering, resolution, and execution.
- Keep parsing and rendering independent of each other.
- Permit resolution to use parsing and node contracts without depending on execution.
- Permit execution to use resolved node meaning without making node models depend
  on execution.
>>

representation-contracts: YAML<<
- Default to XML-grouped authored-style OAK.
- Let grouping change delimiters only.
- Let controlled style change permitted natural-language wording without changing
  meaning, obligation, negation, contracts, targets, or step order.
- Use one surface descriptor for rendering, parsing, EBNF, authoring generation, and
  generated reference.
- Require canonical Node to OAK to Node to OAK equality.
- Keep exact model fields in Pydantic and exact authored tokens in surfaces and vocabulary.
- Derive interpreter context from canonical OAK meaning and render its knowledge as
  OAK documents rather than introducing task-specific YAML or another authored format.
>>

context-selection-contract: ["default to the complete resolved graph when prose dependencies are uncertain", "an explicit task process selects its whole owning document and transitive document dependencies", "retain additional host-known prose dependencies by exact document path", "never merge document identities or prune individual entries for a task view", "keep the complete execution graph authoritative"]
</constants>

<processes>
<process id="change-package" name="Change package">
ACT Use <BOUNDARY> to keep OAK meaning separate from host implementation. (
  BOUNDARY=$constant.host-boundary,
)
ACT Use <REPRESENTATIONS> to preserve one canonical meaning across every supported form. (
  REPRESENTATIONS=$constant.representation-map,
)
ACT Apply <DEPENDENCIES> before changing package imports or ownership. (
  DEPENDENCIES=$constant.package-dependencies,
)
ACT Apply <CONTRACTS> to each model, parser, renderer, vocabulary, surface, rule, and public export change. (
  CONTRACTS=$constant.representation-contracts,
)
ACT Apply <CONTEXT> when deriving interpreter task views. (
  CONTEXT=$constant.context-selection-contract,
)
ACT Read the matching specialist skill before changing Pydantic, JSON Schema, or JSON-LD behavior. ()
</process>
</processes>