<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Practical OAK authoring, naming, decomposition, self-contained scenario sources, and sibling render conventions."

authoring-method: ["identify the knowledge boundary", "place each fact in one justified structured part", "define reusable schemas before their consumers", "separate values by lifetime", "route outside occurrences through triggers", "keep work local to processes", "emit complete results", "apply the root part-authoring-priority"]

naming-rules: YAML<<
- Use the shortest unambiguous domain term.
- Reuse one noun across related schemas, state, processes, and interfaces.
- Name process ids with an action first and object second.
- Replace vague nouns and verbs with exact domain language.
- Preserve supplied tool names verbatim.
- Apply the statement conventions owned by oak/rules/guidance.py; do not maintain
  a separate phrase dictionary here.
>>

python-authoring-rules: YAML<<
- Use package Pydantic models for OAK authoring; this does not prescribe Pydantic
  for unrelated Python code.
- Name meaningful OAK entries as module values ending in their part. Keep small single-use
  details inline when extraction adds only navigation.
- Use part-prefixed upper-snake constants for semantically reused targets and placeholders,
  not for every literal.
- Define reusable schemas before consumers. Derive reused local targets from their
  owning entry ids when dependency order permits; keep external and necessary forward
  targets explicit.
- Assemble named entries directly in each Node so it reads as a table of contents;
  omit single-use collection aliases that add no concept.
- Permit small typed helpers such as local_bindings when they remove construction
  ceremony without hiding schemas, bindings, scope, or effects.
- Distinguish Python dependency order from canonical OAK part order; keep rendered
  documents canonical.
>>

evidence-authoring-rules: ["apply findings before freezing and verifying the final candidate", "have host tools compute immutable snapshot revisions and record observed check results", "gate acceptance on matching subject, revision, required check, and successful result", "require the effect-producing host to reject drift before the effect", "do not present schema-valid evidence as proof that a check ran", "label deterministic demonstration adapters and simulated effects honestly"]

schema-authoring-rules: ["apply the shape-selection guidance owned by oak/rules/guidance.py", "pair each demonstrated template with a complete populated instance", "use shaped schemas in working agents rather than only in the schema collection", "label fixed-cardinality examples and distinguish binding checks from presentation checks", "keep repetition sketches out of executable examples until their semantics are accepted", "keep SMEAC phases compact with checkbox key tasks, plain labelled objective, success criteria, and transition trigger lines, and no internal blank lines"]

example-contract: ["render", "parse", "resolve when required", "round-trip", "write one canonical sibling .oak.md snapshot", "register in repository verification"]

scenario-contract: YAML<<
- Register each scenario once in examples/catalog.py. Keep stable snake_case directories,
  example.py and example.oak.md entries, and supporting document pairs in their scenario.
- Keep reusable schema definitions under examples/schemas. Generate local dependency
  documents and scenario bindings.py copies from their shared source owners; never
  edit delivery copies.
- Use the generated examples/catalog.oak.md for learning order, omitted parts, host
  disclosures, document paths, and regeneration or detached commands. Do not add directory
  README indexes.
- A self-contained OAK scenario contains its complete document graph and sample data.
  It does not vendor the OAK runtime. Distinguish repository-only Python regeneration
  from declared detached demonstrations.
- Retain collaborating operational documents as separate files; relocate only typed
  targets and explicit source identities, not literal payloads, templates, or tool
  names.
- Keep small fixtures in their owning Python source and derive sample.oak.md when
  teaching needs them. The selected four-stage core is fixed knowledge, shaped information,
  typed stateless work, and persistent state.
>>
</constants>

<processes>
<process id="author-example" name="Author example">
ACT Follow <METHOD> and omit every unjustified part or entry. (METHOD=$constant.authoring-method)
ACT Apply <NAMES> while decomposing multi-stage work into typed local processes. (
  NAMES=$constant.naming-rules,
)
ACT Apply <PYTHON> so the source remains flat, typed, readable, and reusable. (
  PYTHON=$constant.python-authoring-rules,
)
ACT Apply <SCHEMAS> when designing reusable information shapes and their populated examples. (
  SCHEMAS=$constant.schema-authoring-rules,
)
ACT Apply <EVIDENCE> to examples that verify and accept work. (
  EVIDENCE=$constant.evidence-authoring-rules,
)
ACT Complete <CONTRACT> before accepting the example. (CONTRACT=$constant.example-contract)
ACT Apply <SCENARIOS> when registering and delivering a scenario, then refresh all example-owned files with python -m examples.catalog. (
  SCENARIOS=$constant.scenario-contract,
)
ACT Use outputs/oak.ebnf and outputs/docs only when exact syntax or model fields are required. ()
</process>
</processes>