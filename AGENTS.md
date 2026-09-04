<instructions>

WHEN you start any work in this repository, you MUST:

- IMPORTANT: Read these instructions in full before your first action. They govern all work in this repository.
- Read `docs/architecture/overview.md` before you inspect or change implementation files.
- Use the documentation router in this file and read every document that matches the task.
- Read all matching documents when work crosses concerns.
- Read the `AGENTS.md` of each directory you work in.
- Treat every MUST in these files as a hard requirement.
- Stop and ask the user when a task conflicts with a rule.
- Obey these files over habit, convention, and inferred preference.

WHEN you update an `AGENTS.md` in this repository, you MUST:

- Keep only rules, one concepts CSV, one optional `<intent>` block, one `---` separator, and the enclosing `<instructions>` tags.
- Use ASD-STE100 Simplified Technical English.
- Use the shortest wording that preserves the complete meaning.
- Write each rule as `WHEN <condition>, you MUST [<shared-action>]:` followed by action bullets.
- Omit the shared action when each bullet is an action.
- Reuse an existing condition when it applies.
- Use `WHEN working in this repository` for repository-wide rules.
- Use `WHEN you work in this directory` for directory-wide rules.
- Keep rules about `AGENTS.md` files in this root file before the separator.
- Put repository-specific rules and content after the separator.
- Keep `WHEN you finish any task` as the last rule in this root file.
- Keep a nested `AGENTS.md` minimal: one pointer rule to this root file before its separator, then its concepts and directory rules.
- Do not repeat a rule an ancestor `AGENTS.md` states.

WHEN you define a repository concept, you MUST:

- Use the present tense and active voice.
- Add one row to the concepts CSV of the governing `AGENTS.md` in the form `name,meaning`.
- Quote a field that contains a comma.
- State what the concept is before you state its path.
- Define a concept before another definition uses it.
- Reuse an existing concept when possible.

WHEN you verify a better concept definition, you MUST:

- Replace the existing row.

WHEN a repository rule uses an undefined repository concept, you MUST:

- Add the concept to the concepts CSV.

---

WHEN you infer repository rules, you MUST know these concepts:

```csv
name,meaning
OAK,"Open Agent Knowledge, the portable knowledge standard this repository defines"
interpreter,"the human, agent, or program that interprets OAK knowledge before using it"
document,"one OAK file that contains exactly one node"
node,"one complete idless set of the seven OAK parts"
part,"one closed node section: instructions, constants, schemas, state, triggers, processes, or interfaces"
entry,"one identified item in a part"
schema,"one reusable information shape independent of boundary, flow, and process"
state,"one persistent mutable value in a document"
trigger,"one outside occurrence routed to one process"
process,"one ordered invocation-local way to do a task"
interface,"one identified one-way information crossing at a document boundary"
document graph,"OAK documents connected by target paths"
target path,"one local part-qualified entry path or one relative document path with a part-qualified fragment"
architecture document,"one current explanation of an OAK concern under `docs/architecture`"
documentation router,"the tree in this file that selects architecture documents for a task"
package,"the executable OAK models, parser, resolver, executor, surfaces, vocabulary, rules, and renderers in `oak`"
authoring surface,"the OAK text a human or interpreter writes; Pydantic is the programmatic authoring form"
surface descriptor,"one declarative authored text variant that drives rendering, parsing, EBNF, authoring generation, and generated reference"
render,"one representation of an OAK document: OAK or JSON-LD"
build,"the code in `build` that verifies the package and generates outputs"
output,"one generated artefact in `outputs`: the authoring prompt, EBNF, or model reference"
plan,"one accepted change record under `docs/plans`; a plan is history after completion"
```

WHEN you select repository documentation, you MUST:

- Use this documentation router:

```text
docs/
├── README.md                       documentation map and authority
├── architecture/
│   ├── overview.md                 every task
│   ├── document.md                 node, parts, values, schemas, triggers, processes, interfaces, examples
│   ├── graph.md                    target paths, loading, resolution, cross-document contracts
│   ├── validation.md               models, constraints, validators, errors, rejected forms
│   ├── execution.md                arrivals, state, triggers, calls, tools, loops, parallel work, emissions
│   ├── representation.md           authoring surfaces, parsing, rendering, grouping, styles, JSON-LD, EBNF
│   └── repository.md               package layout, dependencies, build, examples, outputs, repository-wide changes
├── guides/
│   └── authoring.md                authoring API, authoring prompt, OAK examples, knowledge-to-node design
└── plans/                          read only the plan named by the task
```

- Read `docs/architecture/overview.md` for every task.
- Read each matching route before implementation files.
- Read more than one route when the task crosses concerns.
- Read `docs/README.md` when documentation ownership, authority, or paths change.
- Read a plan only when the user or task names it.
- Do not use generated model pages as a substitute for architecture documents.

WHEN working in this repository, you MUST:

- Use `.agents` as the only repository directory for agent support files.
- Do not create or reference `.agent`.
- Apply the reduce principle: less is more.
- Attack every implementation and every documentation line.
- Make every bit of information fight for its place.
- Remove what does not win its place.
- Treat each architecture document as the current authority for its named concern.
- Treat the package as the exact executable contract for model fields, syntax, validation codes, and runtime behaviour.
- Treat outputs as generated reference, not source authority.
- Treat completed plans as history, not current architecture.
- Do not stage product work into versions or deferred phases.
- Update architecture, implementation, examples, and generated outputs in one pass when the concern requires them.
- Use no em dash or asterisk emphasis in repository documentation.

WHEN you change current architecture, you MUST:

- Update the one architecture document that owns each changed concern.
- Update every dependent implementation and generated output in the same task.
- Do not create a second authority for the same fact.
- Show the proposed architecture to the user before writing it unless the user already approved it in the current task.
- Update `docs/README.md` and the documentation router when a documentation path changes.

WHEN you work with JSON-LD, JSON Schema, or Pydantic, you MUST:

- Use the matching skill in `.agents/skills`.
- Read its `SKILL.md` before you start.
- Search its references, guides, and examples for material that applies.
- Apply that material when you plan and do the work.

WHEN you use APS material, you MUST:

- Treat APS as legacy reference, not a source to copy into OAK.
- Adopt an APS element only when an architecture document or the user adopts it.
- Keep OAK names and definitions.

WHEN you name the consumer of OAK knowledge, you MUST:

- Use interpreter.
- Do not use reader.

WHEN you name what OAK produces, you MUST:

- Use render for a representation of one OAK document.
- Use output for an artefact the build generates.

WHEN you design or extend the package authoring surface, you MUST:

- Prefer short helper functions with plain literal arguments over nested constructor keywords.
- Prefer one discoverable dot-access namespace per closed set over loose imports.
- Keep every helper typed and validate through the models.
- Keep the render byte-identical when only the programmatic authoring surface changes.
- Hoist each reused static value into one `UPPER_SNAKE` module constant.
- Prefix each entry-id constant with its part.
- Define each multi-line entry as one named module-level value.
- List only entry variable names inside the node so the node reads as a table of contents.
- Postfix each entry variable name with its part.

WHEN you write a document in this repository, you MUST:

- Include only information relevant to its stated concern.
- Include only confirmed information.
- Link to the exact owner instead of copying detailed types, syntax, or error catalogs.

WHEN you implement a change, you MUST:

- Choose the simplest implementation that fully meets the current architecture.
- Avoid speculative abstractions, configuration, and indirection.
- Keep components modular and concerns separate.

WHEN you change the package or an architecture document, you MUST:

- Update each example the change makes invalid.
- Run each affected example and keep its regenerated render next to it.
- Update every affected generated output.

WHEN a change makes a name, contract, format, location, or code path obsolete, you MUST:

- Find every definition and repository-owned use.
- Update every dependent file and generated output in the same task.
- Delete the replaced implementation and support material.
- Do not add compatibility layers, shims, wrappers, aliases, re-exports, fallbacks, or migrations.
- Add backward compatibility only when an architecture document or the user names the exact contract and consumer.

WHEN you add a capability, you MUST:

- Start from the smallest version that works end to end.
- Build on a product that already works.
- Do not trade a working product for unfinished complexity.

WHEN you need functionality, you MUST:

- Use existing project dependencies before you write an implementation or add a package.
- Check a library's documentation and types before you assume it lacks a capability.
- Prefer an established maintained library when it reduces complexity or improves reliability.
- Do not reimplement common functionality without a clear reason.

WHEN you make an architectural decision, you MUST:

- Decide for the long term.
- Do not accept a temporary design that is intended to be replaced.

WHEN the user corrects a durable repository assumption, you MUST:

- Update the owning architecture document or `AGENTS.md` before you continue.
- Prefer the architecture document for product meaning.
- Prefer the nearest `AGENTS.md` for work rules.
- Ask the user when ownership is unclear.

WHEN you store a durable lesson, preference, or decision, you MUST:

- Store product meaning in the owning architecture document.
- Store work rules in the affected `AGENTS.md`.
- Do not use platform memory as repository authority.

WHEN you communicate with the user, you MUST:

- Lead with the answer or outcome.
- Use short sentences and plain words.
- State uncertainty plainly.
- Do not use em dash, bold, italics, jargon, filler, praise, or repetition.
- Presume the routine answer to a routine question, act, and report it.

WHEN you finish an implementation or refactor, you MUST:

- Run `python -m build.examples`.
- Inspect the final diff, not only the check result.
- Search for every replaced identifier, path, format, and contract.
- Keep only the current implementation.

WHEN a branch is merged, you MUST:

- Delete it on the remote and locally in the same task.

WHEN you finish any task, you MUST:

- Confirm your work and reply followed every applicable rule before you report done.

</instructions>
