<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
catalogue-version: "1"

artifact-kinds: YAML<<
- id: agent
  purpose: A role with defined behavior and execution context.
  structure: Define the role boundary and justified schemas, interfaces, triggers
    and processes; fixed knowledge alone need not be operational.
  state: Only for values retained across arrivals, with explicit host ownership.
  delivery: Canonical OAK body; requested native wrappers derive from the same body
    and known consumer context.
  questions:
  - Which role, boundaries and effects are actually required?
  - What consumer tools and permissions are known?
- id: single-shot-prompt
  purpose: Instructions for one bounded invocation.
  structure: Define one invocation, inputs and complete output; omit arrivals or orchestration
    without a demonstrated need.
  state: No persistent state by default.
  delivery: One OAK document; no installed service or invented runtime.
  questions:
  - What is the complete input and expected output for this invocation?
- id: compact-knowledge
  purpose: A concise definition of knowledge.
  structure: Use constants, schemas or irreducible instructions only as justified;
    do not invent triggers, tools or processes.
  state: Fixed knowledge, not persistent mutable state.
  delivery: One compact OAK document, preserving exact values and unresolved meaning.
  questions:
  - Which facts or reusable information shapes must be preserved?
- id: agents-md
  purpose: Repository or directory-scoped host knowledge.
  structure: One OAK body for the named AGENTS.md scope. Hierarchy is host scoping,
    never implicit OAK imports; do not copy root lifecycle without a request.
  state: No repository/session state invented from guidance.
  delivery: The named AGENTS.md body; file edits require actual scope and permission.
  questions:
  - Which directory and concern does this knowledge own?
- id: skill
  purpose: A reusable capability with supporting resources.
  structure: Populate the generic scaffold with justified parts and explicit resource/document
    closure; omit unused resources in the authored result, not the teaching template.
  state: No owned persistent state by default.
  delivery: Complete skill files with metadata and an entry; install name must match
    metadata. No automatic installation.
  questions:
  - What reusable task and supporting resources are necessary?
- id: stateful-skill
  purpose: A reusable capability retaining values across arrivals.
  structure: Specify initial state, retention/restoration ownership, arrivals, failure
    and commit behavior; resources remain explicit.
  state: Justified mutable values with a named host persistence boundary.
  delivery: Complete skill artifacts with lifecycle knowledge, never a persistence
    implementation.
  questions:
  - What persists, who restores it and when can it change?
  - What happens after a failed or repeated arrival?
>>
</constants>
