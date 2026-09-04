<instructions>
This document owns practical OAK authoring, naming, decomposition, executable examples, and sibling render conventions.
Start authoring from what the document knows, what can enter, what can leave, and what work it can perform.
Place each source fact in exactly one justified part.
Omit every part and entry that the source does not justify.
Define complete reusable schemas before the interfaces, processes, actions, or calls that use them.
Apply the value lifetimes and part boundaries from `oak/node/AGENTS.md` instead of restating them here.
Select trigger forms, guards, and value lifetimes through the contracts in `oak/node/AGENTS.md`.
Select `ACT`, `ACT TOOL`, `CALL`, and delegated-agent forms through the runtime boundary in `oak/execute/AGENTS.md`.
Decompose multi-stage work into typed phase processes and keep the selected process as a short orchestrator.
Preserve every supplied tool name verbatim.
Keep repository agent delegation depth at one.
Use the shortest unambiguous domain term and reuse it across parts.
Name each process id with an action first and its object second.
Replace vague nouns and verbs with exact domain language.
Author every example through the package Pydantic models.
Hoist each reused target and placeholder into a part-prefixed upper-snake module constant.
Define each multi-line entry as one module value whose variable name ends with its part.
List entry variables in each node so the node reads as a table of contents.
Render, parse, resolve when required, and round-trip each example before writing its snapshot.
Keep one canonical sibling `.oak.md` render beside each Python example.
Register every executable example in the repository verification path.
Keep examples flat, dense, functional, and short.
Use `outputs/oak.ebnf` and `outputs/docs` when exact syntax or model fields are required.
</instructions>