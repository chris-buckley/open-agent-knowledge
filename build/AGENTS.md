<instructions>
This document owns generators, repository checks, freshness, the authoring prompt, generated reference, and the complete verification entry point.
Use package sources to generate outputs once.
Generate `outputs/oak.ebnf` from the vocabulary, surfaces, and fixed document arrangement.
Generate `outputs/docs` from model metadata, rules, surfaces, grammar, and canonical examples.
Generate `outputs/authoring.md` as one compact canonical OAK authoring prompt.
Keep the authoring prompt under its enforced 18,000-byte limit.
Use one complete example in the authoring prompt instead of one schema per Python model.
Use `python -m build.examples` as the complete repository verification entry point.
Verify vocabulary, metadata, surfaces, parsing, rendering, resolution, execution, examples, outputs, dependency direction, and obsolete paths.
Require every generated path and byte to equal a fresh build.
Remove stale generated pages during generation.
Treat EBNF as generated syntax documentation, not as the validator.
Discover every current repository-owned `AGENTS.md` and reject an unregistered path.
Require each repository-owned `AGENTS.md` to parse and reproduce its canonical XML OAK bytes.
Reject a repository-owned `AGENTS.md` longer than 500 lines.
Require the root `agents-router` to name every nested `AGENTS.md` exactly once.
Require one sole-ownership first authored instruction in every scoped `AGENTS.md`.
Reject duplicate normalized authored instructions across the scoped AGENTS graph.
Reject a child instruction that repeats an ancestor instruction.
Reject current architecture manuals, authoring guides, the removed PRD, and repository or docs README indexes.
Allow completed plans to retain historical references to removed architecture paths.
Inspect generated changes before committing them.
</instructions>