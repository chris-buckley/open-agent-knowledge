---
title: OAK Product Requirements
status: draft
updated: 2026-08-30
owner: Christopher Buckley
defaults:
  render: OAK
  grouping: xml
  style: authored
authoring:
  - These rules govern every line after the first `---` that follows the Purpose section; the Purpose prose above it is exempt.
  - This document is the complete ground truth for OAK; it evolves and is never partial.
  - Read it in full before any work.
  - One short sentence per line, one idea per sentence.
  - Write requirements as imperatives and definitions or rationale as declaratives.
  - Compress alternatives as (a|b|c).
  - Write only confirmed information.
  - Every line fights for its place; remove what loses.
  - Each line maps to (core schema: type|literal|discriminated union|nested model|min or max length|gt or lt|regex|strict|no extra fields|frozen|JSON parse from bytes|core serializer: dump|JSON dump|include or exclude|alias|context|Python engine rule: after validator|field validator|document graph check|exclude_if|field serializer|model serializer to text|JSON Schema|source lint|runtime check|purpose: intent|rationale); a line that maps to none is removed.
  - A line the engine can enforce is enforced in the models in the same pass, because pydantic-core runs the Rust items natively and dispatches the Python callbacks, so every such line is checked on every authoring.
  - Return the OAK render when no render, grouping, or style is named; every default is OAK.
  - Write no tests; the examples on every model and field validate the build, and tests add tokens and context for models.
  - Keep outputs and renders separate: the build uses the package to generate an output once; a render turns one OAK document into a format.
---

# OAK Product Requirements

## Purpose

Open Agent Knowledge (OAK) is a knowledge standard. OAK gives one standard vocabulary for knowledge by defining the smallest useful node of knowledge in a schema. One OAK document contains one node, and target paths compose documents into a document graph that OAK can compile into different outputs. OAK is the next iteration of the [Agnostic Prompt Standard (APS)](https://github.com/chris-buckley/agnostic-prompt-standard).

Practical applications include prompts for agents, standard operating procedures, product requirements, components, static information, projects, operating systems, knowledge bases, library documentation, encoded file systems, conversations, and shell simulations.

Knowledge can run: one document whose state, triggers, and processes form a state machine is the machine itself, and an interpreter runs it continuously by reading state, matching triggers, and applying processes. Such a document may declare no interfaces.

---

## Constraints

1. Reject an empty (SlugId|text) field.
2. Reject a process with no steps.
3. Reject unknown fields.
4. Reject an entry outside the seven parts (instructions|constants|schemas|state|triggers|processes|interfaces).
5. Require one node in each OAK document.
6. Reject a node id or contained node.
7. Reject a duplicate SlugId across entries in one document.
8. Reject a (missing|wrong-type) local reference target.
9. Omit unset optional fields from the Pydantic dump.
10. Reject a process value or emit step that conflicts with the interface direction.
11. Reject an act whose instruction placeholders differ from its inputs and outputs.
12. Reject a process that reads an unbound local binding.
13. Reject a process that redefines a visible local binding.
14. Reject an interface value whose placeholder is absent from the interface schema.
15. Reject an emit step whose bindings differ from the interface schema placeholders.
16. Reject a local or resolved process call cycle.
17. Reject a statically dead process branch or unreachable step.
18. Fail one execution when multiple triggers match one cycle.
19. Reject a process name outside `ProcessName`.
20. Reject a non-true trigger guard that reads no state value.
21. Reject a trigger guard that reads an (interface|local binding).
22. Reject equal trigger `when` values unless every guard pair is provably disjoint.
23. Reject an (ALL|ANY) condition with fewer than two children.
24. Reject an ordered comparison outside two numbers or two strings.
25. Reject an assertion that is statically (false|true).
26. Reject a foreach source that is statically not a list or a loop binding that is already visible.
27. Reject a par child that is not an exact named-tool act or that repeats an output binding.
28. Reject a par without one immediately following join or a join without one immediately preceding par.
29. Reject a relative state or interface operation.
30. Reject an unresolved relative target when explicit resolution is requested.
31. Reject an unknown tool or a named-tool act that conflicts with its supplied registry contract.
32. Reject a par tool whose supplied registry does not confirm parallel use.
33. Reject a trigger-selected process with an input schema.
34. Reject a process that cannot supply every output schema placeholder after successful completion.
35. Reject a call whose input set differs from the called process input schema or whose output set differs from its output schema.
36. Reject a while with no steps or a limit less than one.

## Structure

- The name is OAK, short for Open Agent Knowledge.
- OAK is a knowledge standard because knowledge covers static information and executable instructions.
- The consumer of OAK knowledge is the interpreter.
- OAK has four layers: the node, the render, the vocabulary, and the grouping.
- One OAK document contains exactly one node.
- A node is one complete set of the seven parts.
- A node has no id and contains no node.
- The document path identifies the node.
- The parts are instructions, constants, schemas, state, triggers, processes, and interfaces.
- The set of parts is closed.
- Each part holds zero or more entries.
- Each entry belongs to exactly one part.
- Every entry shares only `id`.
- Keep `name` and `purpose` part-specific.
- Discriminate the closed entry union on `part`.
- A document graph is OAK documents connected by target paths.
- Composition is target-path connection, not an eighth part.
- Derive each local entry registry from one node during validation.
- Cross-references use typed fields, not a generic link field.
- Define a local target as `part.SlugId`.
- Define a relative target as `relative/path.oak.md#part.SlugId`.
- Resolve each relative path from the referencing document directory.
- Keep the authored relative path for diagnostics.
- Allow relative targets for (schema|constant|process) references.
- Keep state reads, state writes, interface reads, and interface emissions in the active document.
- Require each entry id to use `SlugId` independent of file placement.
- Do not prefix an entry id with its part.
- A `SlugId` collision across parts is a duplicate id.
- Validate one document without loading an external target.
- Validate every reachable external target when the caller supplies an explicit source path and loader.
- Do not scan directories, guess filenames, use the working directory as a registry, or fetch the network during resolution.
- Pydantic v2 is the programmatic authoring and validation form.
- OAK text is the human and interpreter authoring surface.
- Constants and state hold any JSON value.
- Validation is strict: no type coercion and no unknown fields.
- Give every model and field a title, a description, and examples.
- Give every concrete authored text variant one surface descriptor.
- Give every non-core authoring rule one stable error code and instruction record.
- Parse one (xml|markdown) OAK document into `Node`, then run every model and standalone graph check.
- Accept OAK as UTF-8 bytes or text.
- Infer the grouping from the first part delimiter when no grouping is named.
- Normalize (CRLF|CR) line endings to LF before parsing.
- Require each parsed document to contain the seven parts once in OAK order.
- Generate unique instruction ids because the OAK render loses them.
- Strip exact built-in instruction lines and blank lines before rebuilding authored instructions.
- Give each parse failure one code, one path, one optional line, and one message.
- Collect every parse failure before raising `OakParseError`.

## Instructions

- Instructions are rules the interpreter of the knowledge must follow.
- Instructions include interpretation rules, methods, safety measures, and policy.
- Instructions MUST use one directive per line.
- Each line MUST be a single imperative or declarative that changes system behaviour.
- Require each instruction body to use `NonBlankLine`.
- Render built-in interpretation instructions before authored instructions.
- The interpretation preamble is the generated built-in instruction group.
- A node's instructions apply before a process reached through a trigger.

## Constants

- Constants are values that stay the same in every use of the knowledge.
- Give each constant one `form` selected from (inline|text|json|csv|yaml).
- Default each constant form to `inline`.
- Render an inline constant as one JSON value on one line.
- Render a block constant with one (`TEXT<<`|`JSON<<`|`CSV<<`|`YAML<<`) opening line and one `>>` closing line.
- Reject `>>` as a line inside a block body.
- Require each text block value to be text.
- Parse each JSON block as one JSON value.
- Render each JSON block with two-space indentation.
- Parse each CSV block as one header and one or more data rows.
- Require every CSV row to use the same columns.
- Require every CSV cell to be a JSON scalar.
- Parse each YAML block with the safe YAML loader, then validate one JSON value.
- Render each YAML block with the safe YAML dumper in authored key order.

## Schemas

- Schemas define reusable information shapes.
- A schema is independent of boundary, direction, and process.
- Give each schema an optional `name`, an optional `purpose`, one `template`, and one ordered `where` list.
- Store each template as one verbatim string.
- Give each `Where` one placeholder, one non-empty constraint list, optional examples, and an optional description.
- Represent each constraint as one discriminated union of (type|one of|regex|non-empty|max chars|lines|list of|at least|at most) on `kind`.
- Default each constraint kind in direct Pydantic authoring.
- Keep each constraint kind required in JSON Schema.
- Select each type and list item from the vocabulary datatypes.
- Give each (at least|at most) a value that is (number|Placeholder).
- Extract each distinct placeholder from the template.
- Reject a duplicate placeholder in `where`.
- Reject a schema when its template and `where` placeholder sets differ.
- Reject a placeholder-valued bound absent from the same schema.
- Reject examples on a `Where` with a placeholder-valued bound.
- Reject a lines constraint when both bounds are absent or the minimum exceeds the maximum.
- Require each lines bound to be positive.
- Restrict authored regex patterns to anchors, atoms, character classes, escapes, and quantifiers.
- Reject a regex constraint that rust-regex cannot compile.
- Apply every `Where` constraint to each bound value.
- Resolve placeholder-valued bounds within the same schema instance.
- Apply datatype validation before each bound comparison.
- Accept placeholder bindings from the interpreter instead of recovering them from rendered text.
- Raise `SchemaBindingError` with every binding failure.
- Give each binding failure one code, one placeholder, and one message.

## State

- State holds JSON values that change while the interpreter uses the knowledge.
- Keep authored state ids fixed for one document.
- Stage state writes until successful top-level process completion.

## Triggers

- Triggers route intent to knowledge.
- A trigger contains one `given`, one `when`, and one `then`.
- Give `given` either true or one recursive condition.
- Default direct Pydantic trigger authoring to `given=true`.
- Render `GIVEN` in every trigger.
- Require each `when` value to use `NonBlankLine`.
- Give `then` one local or relative process target.
- Match trigger `when` by exact string equality.
- Evaluate `given` only after `when` matches.
- Evaluate a condition tree in authored order with short-circuiting.
- Run no process when no trigger matches.
- Run the `then` process when exactly one trigger matches.
- Fail with `ambiguous_trigger_match` when multiple triggers match.
- Prove equal-when guards disjoint only from compatible state equality, exclusion, and range constraints.
- Treat every unproved equal-when guard pair as overlapping.
- Reject a non-true trigger guard without a state read with `trigger_guard_missing_state`.
- Reject a trigger guard that reads an interface or local binding with `invalid_trigger_guard_value`.
- Triggers are optional.

## Processes

- Processes are exact ordered ways to do a task.
- Represent each process step as one discriminated union of (act|set|emit|if|call|fail|assert|foreach|while|par|join) on `kind`.
- Represent each process value as one discriminated union of (literal|constant|state|interface|binding) on `source`.
- Give each value binding one placeholder and one process value.
- Give each process one `ProcessName`, optional input and output schema targets, and one or more steps.
- Use each input schema placeholder as one initial process-local binding.
- Require every output schema placeholder to be visible after successful process completion.
- Require each trigger-selected process to declare no input schema.
- Author the first process-name word as the action and the second as its object.
- Execute process steps in authored order.
- Give each act one instruction, one input binding list, one output placeholder list, and one optional exact tool name.
- Treat an act without a tool as interpreter-native work.
- Preserve a named tool string verbatim.
- Require each act instruction placeholder to occur once in its inputs or outputs.
- Reject a duplicate act input or output.
- Reject an act placeholder used as both input and output.
- Require an act to return exactly its declared outputs.
- Store each act output as an immutable process-local JSON binding.
- Give each condition one of (compare|all|any|not).
- Give each compare one left value, one operator, and one right value.
- Require each compare operator to be (equals|not equals|less than|at most|greater than|at least).
- Compare JSON equality structurally without coercion.
- Treat booleans as distinct from numbers.
- Order only two numbers or two strings.
- Compare strings by Unicode code-point order.
- Give each all or any at least two conditions.
- Give each not exactly one condition.
- Give each set one local state target and one value.
- Give each emit one local interface target and one non-empty binding list.
- Require each emit interface to target an (out|inout) interface.
- Require each emit binding set to equal the interface schema placeholder set.
- Validate each emitted binding before staging its emission.
- Give each if one condition, one non-empty then list, and one optional non-empty else list.
- Execute only the selected if branch.
- Keep a binding created in an if branch inside that branch.
- Give each call one local or relative process target, one input binding list, and one output placeholder list.
- Require each call input binding set to equal the called process input schema placeholder set.
- Require each call output set to equal the called process output schema placeholder set.
- Run a called process synchronously in the current state and emission transaction.
- Give each fail one `NonBlankLine` message.
- Stop execution with `process_failed` when fail runs.
- Give each assert one condition and one optional message.
- Stop execution with `assertion_failed` when assert is false.
- Give each foreach one loop binding, one list-valued process value, and one non-empty step list.
- Iterate foreach in list index order.
- Skip the foreach body for an empty list.
- Give each foreach iteration a fresh child binding scope.
- Keep each loop binding and iteration output inside its iteration.
- Give each while one recursive condition, one positive hard limit, and one non-empty step list.
- Test each while condition before every iteration.
- Skip the while body when its condition is false before the first iteration.
- Give each while iteration a fresh child binding scope.
- Keep each while iteration output inside its iteration.
- Keep staged state and emissions visible to later while iterations.
- Stop after no more than the authored while limit.
- Fail with `while_limit_reached` when the condition remains true after the authored limit.
- Give each par one or more exact named-tool acts.
- Resolve every par input before launching any child.
- Give every par child the same immutable visible-binding snapshot.
- Launch par children in authored order and permit completion in any order.
- Keep par outputs pending and invisible before join.
- Require join immediately after par.
- Wait for every par child at join.
- Promote successful par outputs in authored child order.
- Promote no par output when any child fails.
- Report the first par failure in authored order and retain later failures as suppressed diagnostics.
- Give a called process a fresh local binding scope.
- Seed a called process binding scope with its validated call inputs.
- Validate the called process outputs against its output schema before promotion.
- Promote each validated called process output as one immutable caller-local binding.
- Share state and emissions across called processes in one top-level transaction.
- Commit state writes and interface emissions after successful top-level completion.
- Discard state writes and interface emissions after failure.
- Do not claim rollback for external tool effects.
- Represent one arrival as one `when` value and zero or more input interface bindings.
- Validate each active input binding before trigger selection.
- Require the supplied state target set to equal the resolved authored state target set.
- Execute one cycle with `execute(document, arrival, state, act=..., tools=...)`.
- Require an interpreter-native act handler only when an unnamed act runs.
- Validate each act or tool result against its declared output set.
- Return the selected process target, committed state, and ordered emissions after success.
- Return no process and no emission when no trigger matches.
- Raise `ExecutionError` with one code and one message on runtime failure.
- Do not mutate the caller state mapping.
- Use triggers, foreach, and bounded while for repetition instead of recursive process calls.
- Processes can run without interfaces or triggers.
- Refuse (expression strings|try|recover|retry|timeout|with|capture|return|unset|tell|snap|milestone).

## Interfaces

- An interface declares one information crossing at the active document boundary.
- An in interface carries information into the document.
- An out interface carries information out of the document.
- An inout interface carries information in both directions.
- Require each interface direction to be (in|out|inout).
- Give each interface one local or relative schema target.
- Give each interface an optional `NonBlankLine` description.
- Use an interface description only for boundary meaning absent from its schema.
- Interfaces do not define information shapes.
- Interfaces are optional.

## Vocabulary

- The vocabulary conveys information without ambiguity inside every render.
- The vocabulary holds text shapes, datatypes, units, time forms, and display forms.
- Define `SlugId` as lower kebab case without a leading, trailing, or repeated hyphen.
- Define `NonBlankLine` as one line containing at least one non-whitespace character.
- Define `ProcessName` as two ASCII alphanumeric words with optional internal hyphens, separated by one U+0020 SPACE, with an uppercase first character.
- Define `Placeholder` as ASCII upper snake case without a leading, trailing, or repeated underscore.
- Define `EntryPath` as `part.SlugId` for one singular part name.
- Define `RelativeDocumentPath` as a relative POSIX path ending in `.oak.md` without a scheme, query, or fragment.
- Define `TargetPath` as (`EntryPath`|`RelativeDocumentPath#EntryPath`).
- Define `DottedPath` as one local (constant|schema|state|process|interface) target or one local interface placeholder path.
- Define `ValueReference` as `$` followed by one (constant target|local state target|local interface placeholder path|Placeholder).
- `$` reads a process value.
- Use `TargetPath` without `$` for each (SET|CALL|EMIT|THEN|schema) target.
- Delimit each placeholder with `<` and `>` in schema templates, `Where` lines, and act instructions.
- Render each binding target and act output as a bare placeholder.
- Define `Datatype` as (string|integer|number|boolean|quantity|datetime|uri|path).
- Define `Unit` as (%|kg|°C|kg·m/s²).
- Represent a quantity as one Decimal value and one unit enum.
- Represent a datetime as one aware datetime and one optional IANA time zone name.
- Reject a naive datetime and never convert one to UTC.
- Use U+002E FULL STOP as the decimal separator.
- Use U+2009 THIN SPACE as the thousands separator.
- Render each quantity as a number, one U+0020 SPACE, and one unit.
- Render each datetime in ISO 8601 form.
- Render a zero UTC offset as `Z`.
- Require each local datetime to include a numeric UTC offset.
- Append an IANA time zone name in brackets when present.

## Authoring

- Direct Python authoring validates through the existing Pydantic models.

### Entry IDs

- Do not require a minimum word count for an entry id.
- Use `<verb>-<object>[-<outcome-or-context>]` for process ids.
- Start each process id with an exact base-form action verb.
- Use `<verb>-<object>` for instruction ids.
- Use noun phrases for constant, schema, state, and interface ids.
- Use circumstance phrases for trigger ids.

#### Example AST

```text
NODE
├── INSTRUCTIONS
│   └── require-verification
├── CONSTANTS
│   └── completion-criteria
├── SCHEMAS
│   ├── candidate
│   ├── verification
│   └── verified-candidate
├── STATE
│   ├── candidate-goal
│   ├── verification-phase
│   ├── current-candidate
│   └── verification-feedback
├── TRIGGERS
│   ├── candidate-needed
│   └── verification-needed
├── PROCESSES
│   ├── produce-candidate
│   └── verify-candidate
└── INTERFACES
    └── verified-candidate-output
```

### Naming

- The process naming rules apply to processes.
- Name each reusable process for what it establishes, not how it works.
- Name each query process with matching `SlugId` and `ProcessName` forms that use the semantic structure `<query-action>_<object>` and a non-mutating action (is|has|find|read) (e.g. `find-document` and `Find document`).
- Name each command process with matching `SlugId` and `ProcessName` forms that use the semantic structure `<command-action>_<object>` and expose the state change (create|write|publish|delete) (e.g. `publish-report` and `Publish report`).
- Name each combined process with matching `SlugId` and two-word `ProcessName` forms that place its mutating action first and use the semantic structure `<command-action>_<object>[_if_<condition>]` (e.g. `create-folder-if-missing` and `Create folder-if-missing`).
- Name each verification process with matching `SlugId` and `ProcessName` forms that use the semantic structure `(test|validate|prove)_<object>[_<condition>][_<outcome>]` (e.g. `validate-candidate` and `Validate candidate`).
- Define each required log event as a reusable process with the semantic structure `log_<object>_<event>` (e.g. `log-artifact-published` and `Log artifact-published`).
- Perform interpreter-native logging with plain `ACT`.
- Use `ACT TOOL` only when one exact registered logging tool must perform the logging operation.
- Reuse a logging process from other processes with `CALL`.
- The value naming rules apply to constants, schemas, state, and process bindings.
- Name each value with the semantic structure `<role>_<object>_<kind-or-unit>` using a `SlugId` for a constant or state entry and a `Placeholder` for a schema or process binding (e.g. `source-document-file` and `SOURCE_DOCUMENT_FILE`).
- Name each collection with the semantic structure `<contents>_<shape>` (e.g. `report-names` as a `SlugId` or `REPORT_NAMES` as a `Placeholder`).
- Name each boolean as a positive condition or control (e.g. `is-ready` as a `SlugId` or `IS_READY` as a `Placeholder`).
- Name each quantity with the semantic structure `[<context>_]<quantity>_<unit>` (e.g. `poll-interval-seconds` as a `SlugId` or `POLL_INTERVAL_SECONDS` as a `Placeholder`).
- Name each identifier value with the semantic structure `<object>_id` (e.g. `document-id` as a `SlugId` or `DOCUMENT_ID` as a `Placeholder`).
- The mapping naming rule applies to constants, state, and process bindings.
- Name each mapping with the semantic structure `<key>_to_<value>` (e.g. `filename-to-document-id` as a `SlugId` or `FILENAME_TO_DOCUMENT_ID` as a `Placeholder`).
- The lifetime rule applies to constants, state, process bindings, and interfaces.
- Represent each variable-like value by its source and lifetime: `CONSTANT` for fixed values, `STATE` for mutable values, a process binding for local immutable values, and an `INTERFACE` binding for boundary values (e.g. `$constant.max-retries`, `$state.current-candidate`, or `$CANDIDATE`).
- The shared naming rules apply to every entry part.
- Use the shortest unambiguous name that states purpose or result and reuses one exact domain noun across every part, including verification processes (e.g. schema `candidate`, state `current-candidate`, process `validate-candidate`, and interface `verified-candidate-output`; do not rename `candidate` as `option` or `proposal`).
- Replace generic nouns and vague process verbs with exact domain terms that state purpose or action (e.g. replace (data|item|result|value|config|response|path) with (candidate|verification-step|verified-candidate|retry-limit|validation-rules|review-feedback|source-document-file), and replace (handle|process|manage|do) with (validate|publish|archive|verify)).

### Decomposition

- Decompose each multi-phase task into one process per phase.
- Give each phase process one input schema and one output schema.
- Name each contract schema as the information shape it carries.
- Keep each multi-phase trigger-selected process an orchestrator of calls and emits.
- Do not emit from a phase process.
- Keep pipeline values in call contracts; use state only for values that persist between arrivals.

### ACT

- Treat plain `ACT` as the default action form.
- Use plain `ACT` when the interpreter performs the instruction with its native capabilities.
- No `ACT.tool` means interpreter-native work.
- Use `ACT TOOL` only when one exact registered tool must perform the instruction.
- Omit `ACT TOOL` when the interpreter may choose how to perform the instruction.
- Copy each tool name from the supplied exact tool registry.
- Preserve each tool name verbatim.
- Do not invent, normalize, or infer a tool name.
- Use `CALL` to run another OAK process.
- Do not use `ACT TOOL` to run an OAK process.
- Keep tool implementations, handlers, transport, credentials, server configuration, and aliases outside the OAK document.
- Prefer `ACT TOOL` when stable tool selection, contract validation, auditability, or controlled side effects matter.
- An exact tool name fixes which registry entry is selected.
- An exact tool name does not guarantee deterministic output.
- Require the selected tool itself to provide deterministic behaviour when deterministic output is required.
- Expose plain `ACT` as `ACT(instruction, ...)` in direct Python authoring.
- Expose named `ACT TOOL` as `ACT.tool(name, instruction, ...)` in direct Python authoring.
- Make `ACT(...)` and `ACT.tool(...)` return the existing `Act` model.
- Keep `ACT(...)` and `ACT.tool(...)` as one `act` process step kind.
- Keep the rendered OAK syntax unchanged.
- Do not expose `ACT.infer`.
- Do not expose `ACT.use`.
- Add no second helper for interpreter-native work.

### Delegation

- Model each subagent as one worker OAK document with one in interface and one out interface.
- Treat the worker in interface schema as the request contract and the worker out interface schema as the result contract.
- Type each dispatch process with relative targets to the worker request and result schemas as its input and output schemas.
- Dispatch each worker inside its dispatch process with one exact tool name from the supplied registry.
- Prefer one registered portable `agent.<worker>` contract when the host permits registration.
- Use the native runner name verbatim when the host does not permit registration.
- Give each agent tool contract the worker request placeholders as inputs and the worker result placeholders as outputs.
- Keep agent invocation, model selection, and transport in the host registry, outside the OAK document.
- Treat the supplied registry as the worker allowlist.
- Run parallel workers as `PAR` children, one exact agent tool act per worker.
- Keep delegation depth at one: each worker returns its result to the coordinator and dispatches no workers.
- Do not dispatch a worker with `CALL`.
- `CALL` composes processes inside one interpreter and one transaction.
- Treat each dispatch as separate-interpreter host work, not as running an OAK process with `ACT TOOL`.
- Treat committed worker effects as external tool effects that the coordinator transaction cannot roll back.

## Pydantic

- Pydantic v2 is the programmatic authoring and executable validation form, not a render.
- Use the narrowest type, literal, discriminated union, bound, and nested model that states each rule.
- Use regex only when the complete value is one string shape.
- Anchor every regex pattern to the whole string.
- Use source lint for text conventions embedded in prose.
- Use a standalone document graph check only for rules across entries.
- Use the explicit resolver for rules across documents.
- Do not add a field only for a render token.
- Define each authored text syntax once under `oak/vocabulary/text`.
- Define each concrete authored render variant once in `oak/surface.py`.
- Classify every model field in each surface as (rendered|fixed|omitted|generated).
- Build rendering, parsing, EBNF, authoring generation, and documentation generation from the same surfaces.
- Keep each validator-backed authoring rule in `oak/rules.py` with its stable error code.
- Build each reusable string shape with `Annotated` and `StringConstraints` or one reusable after validator.
- Keep defaults and aliases at the field declaration.
- Set `regex_engine` to `rust-regex` on the shared OAK base model.
- Validate every default value.
- Build each `TypeAdapter` once at module import.
- Emit each discriminated union as tagged branches in JSON Schema.
- Emit forbidden extra fields as `additionalProperties: false`.
- Treat generated JSON Schema as a structural projection, not a replacement for Python or graph checks.

## Render

- One OAK document can render to many formats.
- The renders are OAK and JSON-LD.
- JSON-LD is the interchange render.
- The Pydantic dump is an internal programmatic snapshot.
- Each render defines what it preserves, loses, and orders.

### OAK

- OAK is the default render.
- OAK is prose structured text optimized for interpreter disambiguation.
- OAK renders from one node with one grouping and one style.
- Grouping and style do not change the node.
- The default OAK rendering is xml and authored.
- The groupings are (xml|markdown).
- A grouping changes delimiters only.
- Each grouping escapes its attributes.

#### Arrangement

- Render the seven parts in this order: instructions, constants, schemas, state, triggers, processes, interfaces.
- Render every part once, empty when it has no entry.
- Render entries in authored order.
- Keep parts as siblings.
- Render each authored instruction as its text after built-in instructions.
- Separate the interpretation preamble from authored instructions with one blank line.
- Generate built-in instructions only for authored features present in the node.
- Render each trigger as one body entry with `id`, `GIVEN`, `WHEN`, and `THEN`.
- Render each state and inline constant as its id, `: `, and one JSON value.
- Render each block constant with its form opener, body, and closing line.
- Render each process with its id, name, optional input and output schema targets, and typed steps.
- Let line order carry step sequence.
- Indent nested condition and step bodies by two spaces.
- Render each process value as one JSON literal or `ValueReference`.
- Render an unnamed act with `ACT` and a named act with `ACT TOOL` and one JSON string tool name.
- Render (SET|CALL|EMIT) targets as `TargetPath` without `$`.
- Render a call without bindings on one line.
- Render a call with bindings as `CALL target:`, an optional `INPUTS` block, and an optional `OUTPUTS` line.
- Render if with `IF`, its condition, `THEN`, and optional `ELSE`.
- Render assert with `ASSERT`, its condition, and optional `MESSAGE`.
- Render foreach with `FOREACH binding IN value` and its steps.
- Render a compare while with `WHILE condition LIMIT positive-integer:` and its steps.
- Render a recursive while with `WHILE LIMIT positive-integer:`, its condition, `THEN:`, and its steps.
- Render par with `PAR`, named-tool acts, and one following `JOIN`.
- Render fail with `FAIL` and one JSON string.
- Render each interface with id, direction, schema target, and optional description.
- Separate parts and sibling body entries with one blank line.
- Append exactly two LF characters between a schema template and `WHERE` so trailing template whitespace round-trips.
- Preserve schema template whitespace.
- Render `Where` entries in authored order.
- The OAK render loses instruction ids and loses no other authored field.

#### XML

- Use XML-like tags as text delimiters.
- Render text between tags verbatim.
- Escape attribute values.
- Put each opening and closing tag on its own line.
- Use OAK names and the single-node structure.

#### Markdown

- Use tilde fences as text delimiters.
- Open each part with `~~~~part` and close it with `~~~~`.
- Open each body entry with `~~~entry;attr="value"` and close it with `~~~`.
- Encode each attribute value as one JSON string.
- Keep each entry body byte-identical between groupings.

#### Styles

- Apply a style only to natural-language wording and display formatting.
- The authored style preserves authored wording.
- A controlled style is a named and versioned renderer profile.
- A controlled style rewrites only instruction bodies, trigger text, act instructions, and fail or assert messages.
- A controlled style preserves meaning, obligation, negation, conditions, and step order.
- Name the implemented controlled style `asd-ste100-9`.
- Target ASD-STE100 Issue 9, January 2025 without claiming full conformance.
- Reject controlled text with more than one line, one sentence, or 20 words.
- Reject controlled text that still contains an implemented prohibited term.

### JSON-LD

- Require the caller to supply one absolute document IRI without a fragment.
- Render the document IRI as the node `@id`.
- Render each local entry target as a fragment `@id`.
- Render each relative target against the document base.
- Require the caller to supply the JSON-LD vocabulary IRI.
- Define one root context with `@base` and the `oak` prefix.
- Render each entry, `Where`, constraint, condition, process value, and step kind as `@type`.
- Render `where`, `constraints`, `examples`, `steps`, `inputs`, `outputs`, `bindings`, `conditions`, `thenSteps`, and `otherwise` as ordered lists.
- Render trigger `then` as an id-valued process target.
- Render process input and output as id-valued schema targets.
- Render call process as an id-valued process target.
- Render if `thenSteps` and `otherwise` as ordered step lists.
- Render while `condition`, `limit`, and `steps` as one condition, one positive integer, and one ordered step list.
- Derive each `Where` id as `#schema.SlugId/where/Placeholder`.
- Render literal JSON values with `@type: @json`.
- Keep context processing, structural validation, and graph target checks as separate boundaries.

---

## Build

- The build uses the package to generate outputs once.
- A model writes OAK with the outputs, and the package validates what it writes.
- Keep one surface descriptor registry as the source of every authored text variant.
- Keep one validator rule registry as the source of every generated validator instruction.
- Keep one authoring guidance registry as the source of every generated authoring instruction.
- Validate text aliases, metadata examples, surfaces, renders, parsing, resolution, execution, JSON-LD, styles, display forms, and outputs in `build/examples.py`.

### EBNF

- Emit one EBNF grammar for OAK to `outputs/oak.ebnf`.
- Emit one production for each named text alias.
- Emit both grouping productions for every surface descriptor.
- Derive document structure from the fixed part order.
- Do not emit recursive node productions.
- Do not use EBNF as a validator.

### Authoring

- Emit one single-shot authoring document to `outputs/authoring.md` as xml-grouped OAK.
- Treat the complete host-supplied modality context as the source.
- Generate source-to-part instructions from one rule registry.
- Generate every Entry ID, Naming, Decomposition, ACT, and Delegation rule as one instruction entry.
- Include every authoring rule, every surface schema, the EBNF, one canonical OAK example, and one decomposed orchestrator example.
- Declare no universal input interface.
- Declare one OAK document schema, one out interface, one trigger, and one process.
- Derive a draft, validate it, and emit the valid OAK document as the sole response.

### Documentation

- Emit one markdown-grouped OAK document per authorable model under `outputs/docs`.
- Generate each page from the model metadata, matching authoring rules, surface descriptors, grammar productions, and canonical rendered examples.
- Represent each rendered example as an OAK constant, never as a JSON object dump.
- Project each surface render shape into one OAK schema.
- Project each rendered field into one `Where` line from its title and description.
- Remove stale generated pages before rebuilding.

### Examples

- Author each example with direct Python authoring.
- Hoist each reused target and placeholder into one part-prefixed `UPPER_SNAKE` module constant.
- Define each entry as one lower snake module value postfixed with its part, so the node reads as a table of contents.
- Render, parse, resolve, and round-trip each example before writing its sibling `.oak.md` snapshot.
- Grow one balance per bounded cycle and emit one reflection to the chat in `examples/compound_growth.py`.
- Exercise `ACT`, `ACT.tool`, bounded while, canonical OAK, parsing, resolution, and execution in `examples/compound_growth.py`.
- Encode the extracted implementer instructions in `examples/implementer.py`.
- Encode the extracted task reviewer instructions in `examples/task_reviewer.py`.
- Dispatch the task reviewer as one worker agent from `examples/delegation.py`.
- Keep each example flat, dense, functional, and short.

### Freshness

1. Require the authorable model set to equal the documented model set.
2. Require every concrete surface variant to select exactly one descriptor.
3. Require every rendered field to be covered exactly once by its descriptor.
4. Require every omitted, fixed, and generated field to be classified.
5. Require every validated model example to render through a descriptor.
6. Require every rendered example to parse back to the same preserved model data.
7. Require every documentation page to parse as one OAK document.
8. Require every parsed documentation page to reproduce its committed render.
9. Require authoring and documentation generation to share the same surface and rule objects.
10. Require the generated output path set and contents to equal the committed snapshot.

### Tree

```t
oak
├── .agents
├── .gitignore
├── AGENTS.md
├── CLAUDE.md
├── docs
│   └── PRD.md
├── examples
│   ├── __init__.py
│   ├── compound_growth.py
│   ├── compound_growth.oak.md
│   ├── delegation.py
│   ├── delegation.oak.md
│   ├── implementer.py
│   ├── implementer.oak.md
│   ├── task_reviewer.py
│   └── task_reviewer.oak.md
├── oak
│   ├── __init__.py
│   ├── authoring.py
│   ├── base.py
│   ├── defaults.py
│   ├── execute.py
│   ├── parse.py
│   ├── resolve.py
│   ├── rules.py
│   ├── surface.py
│   ├── node
│   │   ├── __init__.py
│   │   ├── dump.py
│   │   ├── graph.py
│   │   ├── model.py
│   │   └── parts
│   │       ├── __init__.py
│   │       ├── constants.py
│   │       ├── instructions.py
│   │       ├── interfaces.py
│   │       ├── processes.py
│   │       ├── schemas.py
│   │       ├── state.py
│   │       └── triggers.py
│   ├── render
│   │   ├── __init__.py
│   │   ├── json_ld.py
│   │   └── oak
│   │       ├── __init__.py
│   │       ├── arrangement.py
│   │       ├── groupings.py
│   │       ├── instructions.py
│   │       ├── styles.py
│   │       └── syntax.py
│   └── vocabulary
│       ├── __init__.py
│       ├── syntax.py
│       ├── units.py
│       ├── datatypes
│       │   └── ...
│       ├── display
│       │   └── ...
│       └── text
│           ├── __init__.py
│           ├── dotted_path.py
│           ├── non_blank_line.py
│           ├── placeholder.py
│           ├── process_name.py
│           ├── regex_pattern.py
│           ├── slug_id.py
│           ├── target_path.py
│           └── value_reference.py
├── build
│   ├── authoring.py
│   ├── docs.py
│   ├── ebnf.py
│   ├── examples.py
│   └── surfaces.py
├── outputs
│   ├── oak.ebnf
│   ├── authoring.md
│   └── docs
│       └── ...
└── pyproject.toml
