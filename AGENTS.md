<instructions>

WHEN you start any work in this repository, you MUST:

- IMPORTANT: Read these instructions in full before your first action. They govern ALL work in this repository, with NO exception.
- Read the `AGENTS.md` of each directory you work in. This root file governs every `AGENTS.md` in this repository.
- Treat every MUST in these files as a hard requirement, not guidance.
- NEVER act against a rule in these files. When a task conflicts with a rule, stop and ask the user.
- Obey these files over habit, convention, and inferred preference.

WHEN working in this repository, you MUST:

- Follow all rules in these files.
- Add a repository rule only after you verify it independently.
- Use no em dash or asterisk emphasis in `AGENTS.md` or other documentation to reduce token use.

WHEN you update an `AGENTS.md` in this repository, you MUST:

- Keep only rules, one `---` separator, and the enclosing `<instructions>` tags in the file.
- Use ASD-STE100 Simplified Technical English (STE).
- Use the shortest wording that preserves the complete meaning.
- Write each rule in this format:

```text
  WHEN <condition>, you MUST [<shared-action>]:

  - <action-or-object-1>
  - <action-or-object-2>
```

- Omit `<shared-action>` when the list items are actions.
- Reuse an existing condition when it applies.
- Use `WHEN working in this repository` for rules that apply throughout all work in this repository.
- Use `WHEN you work in this directory` for rules that apply throughout a nested directory.
- Keep rules about `AGENTS.md` files in this root file only, before the separator.
- Put repository-specific rules after the separator.
- Keep `WHEN you finish any task` as the last rule in this root file.
- Keep a nested `AGENTS.md` minimal: one pointer rule to this root file before its separator, then its own concepts and directory rules after its separator.
- Do not repeat a rule an ancestor `AGENTS.md` states.

WHEN you define a repository concept, you MUST:

- Use the present tense.
- Use the active voice.
- Add a row to the concepts CSV of the `AGENTS.md` that governs the concept's scope, in the format `name,meaning`.
- Quote a field that contains a comma.
- State what the concept is before you state its path.
- Define each repository-specific concept before another definition uses it.
- Reuse an existing concept when possible.

WHEN you verify a better concept definition, you MUST:

- Replace the existing row.

WHEN a repository rule uses an undefined concept, you MUST:

- Add the concept to the concepts CSV.

---

WHEN you infer repository rules, you MUST know these concepts:

```csv
name,meaning
operating context,"the complete information and rules supplied to an agent: instructions, constants, schemas, state, triggers, processes, input"
UAOC,"Universal Agent Operating Context, the universal language this repository defines to describe an agent's operating context"
interpreter,the agent that interprets UAOC knowledge and follows its instructions
```

WHEN working in this repository, you MUST:

- Read `docs/PRD.md` before any other work.

WHEN you work with JSON-LD, JSON Schema, or Pydantic, you MUST:

- Use the matching skill in `.agent/skills`.
- Read its `SKILL.md` before you start.
- Search its references, guides, and examples exhaustively for material that applies to the work.
- Apply that material when you plan and do the work.

WHEN you name the consumer of UAOC knowledge, you MUST:

- Use the concept interpreter.
- Do not use reader.

WHEN you write a document in this repository, you MUST:

- Include only information relevant to the document's purpose.
- Include only information the user confirmed.

WHEN you implement a change, you MUST:

- Choose the simplest implementation that fully meets the current requirements.
- Avoid speculative abstractions, configuration, and indirection.
- Keep components modular and concerns clearly separated.

WHEN a change makes a code path obsolete, you MUST:

- Remove the obsolete path.
- Do not add compatibility layers, fallbacks, or migrations.

WHEN you add a capability, you MUST:

- Start from the smallest version that works end to end.
- Build each new capability on a product that already works.
- Do not trade a working product for unfinished complexity.

WHEN you need functionality, you MUST:

- Use the dependencies already in the project before you write your own implementation or add a package.
- Check a library's documentation and types before you assume it lacks a capability.
- Prefer an established, well-maintained library when it reduces complexity or improves reliability.
- Do not reimplement common functionality without a clear reason.

WHEN you make an architectural decision, you MUST:

- Decide for the long term.
- Do not accept a stopgap that works only for now and is meant to be replaced later.

WHEN the user corrects or clarifies something you misinterpreted or got wrong, and the lesson benefits future work in this repository, you MUST:

- Update the affected `AGENTS.md` files before you continue the conversation or task.
- Prefer the nested `AGENTS.md` that governs the affected path or behaviour.
- Update the root `AGENTS.md` only when the correction applies to the whole repository.
- Update the only `AGENTS.md` when the repository has one.
- Ask the user before you proceed when the correct `AGENTS.md` is unclear.

WHEN you store a durable lesson, preference, or decision, you MUST:

- Understand that memory outside this repository is not read in future work, by you or by agents on other platforms. It is lost.
- Write it to the affected `AGENTS.md`. This is the only memory that persists.
- Do not write to platform memory or any store outside the repository. This is forbidden.

WHEN you communicate with the user, you MUST:

- Lead with the answer or outcome.
- Use short sentences and plain words.
- Write as one human talks to another, overly simple and concise.
- Use exact names, paths, and commands.
- State uncertainty plainly.
- Do not use em dashes, bold, or italics.
- Do not use jargon. Defined repository concepts are permitted as the concept list grows.
- Do not use filler, praise, or repetition.

WHEN you finish any task, you MUST:

- Confirm your work and your reply followed every rule in every applicable `AGENTS.md` before you report done.

</instructions>
