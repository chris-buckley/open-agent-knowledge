<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Practical OAK authoring, naming, decomposition, executable examples, and sibling render conventions."

authoring-method: ["identify the knowledge boundary", "place each fact in one justified structured part", "define reusable schemas before their consumers", "separate values by lifetime", "route outside occurrences through triggers", "keep work local to processes", "emit complete results", "apply the root part-authoring-priority"]

naming-rules: YAML<<
- Use the shortest unambiguous domain term.
- Reuse one noun across related schemas, state, processes, and interfaces.
- Name process ids with an action first and object second.
- Replace vague nouns and verbs with exact domain language.
- Preserve supplied tool names verbatim.
>>

python-authoring-rules: YAML<<
- Author through package Pydantic models.
- Hoist reused targets and placeholders into part-prefixed upper-snake constants.
- Define each multiline entry as one module value whose variable name ends with its
  part.
- List entry variables in each node so the node reads as a table of contents.
>>

evidence-authoring-rules: ["apply findings before freezing and verifying the final candidate", "have host tools compute immutable snapshot revisions and record observed check results", "gate acceptance on matching subject, revision, required check, and successful result", "require the effect-producing host to reject drift before the effect", "do not present schema-valid evidence as proof that a check ran", "label deterministic demonstration adapters and simulated effects honestly"]

schema-authoring-rules: ["apply the shape-selection guidance owned by oak/rules/guidance.py", "pair each demonstrated template with a complete populated instance", "use shaped schemas in working agents rather than only in the schema collection", "label fixed-cardinality examples and distinguish binding checks from presentation checks", "keep repetition sketches out of executable examples until their semantics are accepted"]

example-contract: ["render", "parse", "resolve when required", "round-trip", "write one canonical sibling .oak.md snapshot", "register in repository verification"]
</constants>

<processes>
<process id="author-example" name="Author example">
ACT Follow <METHOD> and omit every unjustified part or entry. (METHOD=$constant.authoring-method)
ACT Apply <NAMES> while decomposing multi-stage work into typed local processes. (NAMES=$constant.naming-rules)
ACT Apply <PYTHON> so the source remains flat, typed, readable, and reusable. (PYTHON=$constant.python-authoring-rules)
ACT Apply <SCHEMAS> when designing reusable information shapes and their populated examples. (SCHEMAS=$constant.schema-authoring-rules)
ACT Apply <EVIDENCE> to examples that verify and accept work. (EVIDENCE=$constant.evidence-authoring-rules)
ACT Complete <CONTRACT> before accepting the example. (CONTRACT=$constant.example-contract)
ACT Use outputs/oak.ebnf and outputs/docs only when exact syntax or model fields are required. ()
</process>
</processes>