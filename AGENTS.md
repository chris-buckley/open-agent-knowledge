<instructions>
This document owns OAK product intent, repository-wide work rules, and the scoped AGENTS router.
Open Agent Knowledge (OAK) is a portable standard for expressing knowledge as one compact validated unit.
Read this file in full before any repository work.
Use this scoped AGENTS router to select every file that matches the task.
├── Read `oak/AGENTS.md` for package, representation, syntax, parsing, rendering, vocabulary, surfaces, and rules.
│   ├── Read `oak/node/AGENTS.md` for document, node, part, value, schema, and local-validation architecture.
│   ├── Read `oak/resolve/AGENTS.md` for target paths, loading, graph resolution, and cross-document contracts.
│   └── Read `oak/execute/AGENTS.md` for arrivals, processes, tools, state, emissions, and transactions.
├── Read `build/AGENTS.md` for generators, checks, freshness, and the authoring prompt.
├── Read `examples/AGENTS.md` for practical authoring, naming, and executable examples.
├── Read `outputs/AGENTS.md` for generated artifacts.
└── Read `docs/AGENTS.md` for plans and reports.
Read every applicable `AGENTS.md` from the repository root to each work path before you inspect or change implementation files.
Read additional routed `AGENTS.md` files when work crosses directory concerns.
Treat each scoped `AGENTS.md` as the sole current architecture owner for its stated concern.
Treat the `AGENTS.md` hierarchy as host scoping, not as implicit OAK document imports.
Follow every applicable instruction as a hard requirement.
Stop and ask the user when a task conflicts with an applicable instruction.
Keep every repository-owned `AGENTS.md` as one canonical XML-grouped OAK document.
Use only the instructions part in repository-owned `AGENTS.md` files.
Limit every repository-owned `AGENTS.md` to 500 lines.
Start each nested `AGENTS.md` with one instruction that states its sole owned concern.
Do not repeat or paraphrase architecture owned by another `AGENTS.md`.
Keep parent files as routers, not summaries of child architecture.
Update this router when a scoped `AGENTS.md` path or owner changes.
Use `.agents` as the only repository directory for agent support files.
Do not create or reference `.agent`.
Do not add README files as repository or directory indexes.
Apply the reduce principle: less is more.
Challenge every implementation line and documentation line.
Remove information that does not earn its place.
Update owned architecture, implementation, examples, and generated outputs together when one change affects them.
Do not stage product work into versions or deferred phases.
Show proposed architecture to the user before writing it unless the user approved it in the current task.
Read the matching `.agents/skills` material before work with Pydantic, JSON Schema, or JSON-LD.
Apply relevant skill references, guides, and examples to that work.
Treat Agnostic Prompt Standard material as legacy reference, not as content to copy into OAK.
Use `interpreter` for the consumer of OAK knowledge.
Use `render` for one representation of a document and `output` for one generated artifact.
Choose the simplest implementation that fully preserves the applicable architecture.
Keep components modular and concerns separate.
Use existing project dependencies before adding code or packages.
Check a library documentation and types before assuming that it lacks a capability.
Prefer an established maintained library when it reduces complexity or improves reliability.
Make architectural decisions for the long term, not as planned replacements.
Find every definition and repository-owned use of an obsolete name, path, format, or contract.
Delete replaced implementations and support material in the same task.
Do not add compatibility layers, shims, aliases, fallbacks, or migrations unless an owner or the user names the exact consumer.
Update the owning `AGENTS.md` before continuing after a durable correction to repository meaning or work rules.
Store product meaning in its scoped `AGENTS.md` and work rules in the nearest governing `AGENTS.md`.
Do not use platform memory as repository authority.
Write only confirmed information relevant to the owning concern.
Link to an exact owner instead of copying its types, syntax, or error catalog.
Use no em dash or asterisk emphasis in repository documentation.
Lead user communication with the answer or outcome.
Use short plain sentences and state uncertainty directly.
Use no jargon, filler, praise, or repetition in user communication.
Run `python -m build.examples` after an implementation or refactor.
Inspect the final diff instead of relying only on check results.
Search the final tree for every replaced identifier, path, format, and contract.
Delete a merged branch on the remote and locally in the same task.
Confirm every applicable instruction before you report completion.
</instructions>