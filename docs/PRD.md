---
title: OAK Product Requirements
status: draft
updated: 2026-08-24
owner: Christopher Buckley
defaults:
  render: OAK
  grouping: xml
  style: authored
open:
  - What fields does every entry share? Deferred on 2026-08-21 while the user reviews the PRD. The title field is out of the sketch until this is decided.
authoring:
  - These rules govern every line after the first `---` that follows the Purpose section; the Purpose prose above it is exempt.
  - This document is the complete ground truth for OAK; it evolves and is never partial.
  - Read it in full before any work.
  - One short sentence per line, one idea per sentence.
  - Write requirements as imperatives and definitions or rationale as declaratives.
  - Compress alternatives as (a|b|c).
  - Write only confirmed information.
  - Every line fights for its place; remove what loses.
  - Each line maps to (core schema: type|literal|discriminated union|nested model|min or max length|gt or lt|regex|strict|no extra fields|frozen|JSON parse from bytes|core serializer: dump|JSON dump|include or exclude|alias|context|Python engine rule: after validator|field validator|root graph check|exclude_if|field serializer|model serializer to text|JSON Schema|source lint|runtime check|purpose: intent|rationale); a line that maps to none is removed.
  - A line the engine can enforce is enforced in the models in the same pass, because pydantic-core runs the Rust items natively and dispatches the Python callbacks, so every such line is checked on every authoring.
  - Return the OAK render when no render, grouping, or style is named; every default is OAK.
  - Write no tests; the examples on every model and field validate the build, and tests add tokens and context for models.
  - Keep outputs and renders separate: the build uses the package to generate an output once; a render turns one knowledge tree into a format.
---

# OAK Product Requirements

## Purpose

Open Agent Knowledge (OAK) is a knowledge standard. OAK gives one standard vocabulary for knowledge by defining the smallest nodes of knowledge in a schema. Nodes compose into larger structures that OAK can compile into many different outputs. OAK is the next iteration of the [Agnostic Prompt Standard (APS)](https://github.com/chris-buckley/agnostic-prompt-standard).

Practical applications include, but are not limited to:
- Prompts for Agents (AI Models)
- Standard Operating Procedures (SOPs)
- Product Requirements Document
- React components
- Static information
- Entire projects
- Operating systems
- Knowledge base
- Library documentation
- Encoded file systems
- Conversations
- Shell simulations (bash, PowerShell) that run as state machines

Knowledge can also run: a tree whose state, triggers, and processes form a state machine is the machine itself, and an interpreter runs it continuously, reading state, matching triggers, and applying processes. Such a tree may declare no interfaces; it simply runs.

---

## Constraints

1. Reject an empty (SlugId|text) field.
2. Reject a process with no steps.
3. Reject unknown fields.
4. Reject an entry outside the seven parts (instructions|constants|schemas|state|triggers|processes|interfaces).
5. Require one root node.
6. Require each child of a node to be a node.
7. Reject a duplicate SlugId across nodes and entries.
8. Reject a (missing|wrong-type) reference target.
9. Omit unset optional fields from the Pydantic dump.
10. Reject a process value or emit step that conflicts with the interface direction.
11. Reject an act whose instruction placeholders differ from its inputs and outputs.
12. Reject a process that reads an unbound local binding.
13. Reject a process that redefines a visible local binding.
14. Reject an interface value whose placeholder is absent from the interface schema.
15. Reject an emit step whose bindings differ from the interface schema placeholders.
16. Reject a process call cycle.
17. Reject a statically dead process branch.
18. Fail one execution when multiple triggers match one cycle.
19. Reject a process name outside `ProcessName`.
20. Reject a trigger guard that reads no state value.
21. Reject a trigger guard that reads an (interface|local binding).
22. Reject equal trigger `when` values unless every guard pair is provably disjoint.

## Structure

- The name is OAK, short for Open Agent Knowledge.
- The name changed from UAOC, Universal Agent Operating Context, to OAK on 2026-08-21, because knowledge is broader than an operating context.
- OAK is a knowledge standard, not an information standard, because knowledge covers static information and executable instructions.
- The consumer of the knowledge is named the interpreter, confirmed over actor on 2026-08-21.
- OAK has four layers: the node, the render, the vocabulary, and the grouping.
- A node is one complete set of the seven parts.
- The parts are instructions, constants, schemas, state, triggers, processes, and interfaces.
- The set of parts is closed.
- Each part holds zero or more entries.
- An entry is one item in a part: one instruction, one constant, one schema, one state value, one trigger, one process, or one interface.
- Each entry belongs to exactly one part, so every entry validates at authoring time.
- A tree is nodes nested in nodes, and entries can reference each other.
- Knowledge is authored as a nested tree, because nesting gives one root, one parent, and no containment cycle structurally.
- Composition is the nesting of nodes, not an eighth part.
- The flat entry registry is derived from the tree during validation, not authored.
- Cross-references use typed fields, not a generic link field.
- Store only the target `SlugId` in each typed reference field.
- Require each (node|entry) ID to use `SlugId` independent of file placement.
- Do not prefix a `SlugId` with its part.
- A `SlugId` collision across parts is a duplicate ID.
- Every entry shares only `id`.
- Keep `name` and `purpose` part-specific.
- Discriminate the closed entry union on `part`.
- Author the tree root as `Root`.
- Author each nested node as `Node`.
- Root validation rejects duplicate IDs, overlapping trigger guards, missing reference targets, and wrong target types.
- Constants and state hold any JSON value.
- Validation is strict: no type coercion and no unknown fields.
- The PRD uses one short sentence per idea.
- Give every model and field a title, a description, and examples; the prompt and the documentation derive from them.
- Store the `Node` and `Root` example trees only in their model examples.
- Derive every `Node` and `Root` field example from validated model examples in the build.
- Validate every example against its model or field in the build, so the examples are the only tests.
- Parse one (xml|markdown) OAK document into `Root`, then run every model and graph check.
- Accept OAK as UTF-8 bytes or text.
- Infer the grouping from the first part delimiter when no grouping is named.
- Normalize (CRLF|CR) line endings to LF before parsing.
- Require each parsed node to contain the seven parts once in OAK order.
- Generate unique `SlugId` values for node and instruction ids because the OAK render loses them.
- Strip only exact built-in instruction lines before rebuilding authored instructions.
- Give each parse failure one code, one path, one optional line, and one message.
- Collect every parse failure before raising `OakParseError`.

## Instructions

- Instructions are rules the interpreter of the knowledge must follow.
- Instructions include interpretation rules.
- Instructions include rule following.
- Instructions include methods for how to go about something.
- Instructions include safety measures.
- Instructions include policy.
- Instructions MUST use one directive per line.
- Each line MUST be a single imperative or declarative that changes system behavior.
- Require each instruction body to use `NonBlankLine`.
- Instructions that interpretation references render first in the instructions part.
- Interpretation rules belong to instructions because they govern every entry.
- A node's interpretation instructions apply before a process reached through a trigger.

## Constants

- Constants are values that stay the same in every use of the knowledge.
- Give each constant one `form` selected from (inline|text|json|csv|yaml).
- Default each constant `form` to `inline`.
- Render an inline constant as one JSON value on one line.
- Render a block constant with one (`TEXT<<`|`JSON<<`|`CSV<<`|`YAML<<`) opening line and one `>>` closing line.
- Reject `>>` as a line inside a block body.
- Require each `TEXT` block value to be text.
- Parse each `JSON` block as one JSON value.
- Render each `JSON` block with two-space indentation.
- Parse each `CSV` block as one header and one or more data rows.
- Require every CSV row to use the same columns.
- Require every CSV cell to be a JSON scalar.
- Parse each `YAML` block with the safe YAML loader, then validate one JSON value.
- Render each `YAML` block with the safe YAML dumper in authored key order.

Example: multi-line TEXT constant using TEXT<< ... >>. Tree symbols mark each level.

```text
<constants>
repo-tree: TEXT<<
cb-agnostic-prompt-protocol
├── assets
│   ├── constants
│   │   └── constants-json-block-v1.0.0.example.md
│   └── formats
│       ├── format-code-map-v1.0.0.example.md
│       └── format-error-v1.0.0.example.md
└── SKILL.md
>>
</constants>
```

Example: multi-line JSON constant using JSON<< ... >>. The parser stores BODY as one JSON value.

```text
<constants>
default-tz: "Z"

api-config: JSON<<
{
  "api_base_path": "/v1",
  "default_time_zone": "Z",
  "retries": 3,
  "timeout_ms": 2000
}
>>
</constants>
```

Example: multi-line CSV constant using CSV<< ... >>. The parser stores each data row as one JSON object.

```text
<constants>
default-tz: "Z"

service-table: CSV<<
service,region,default_tz,enabled,note
billing,us-east-1,Z,true,"Primary billing region"
support,ap-southeast-2,"Australia/Brisbane",true,"Escalations use ""follow the sun"""
reporting,eu-west-1,Z,false,"EU, West"
>>
</constants>
```

Example: multi-line YAML constant using YAML<< ... >>. The parser stores BODY as one JSON value.

```text
<constants>
deployment-config: YAML<<
region: ap-southeast-2
replicas: 2
>>
</constants>
```

## Schemas

- Schemas define reusable information shapes.
- A schema is independent of boundary, direction, and process.
- Define each information shape once in schemas, so each use is (verifiable|stable|machine-checkable).
- Give each schema an optional `name`, an optional `purpose`, one `template`, and one `where` list.
- Store each template as one verbatim string.
- Keep `where` as an ordered list.
- Give each `Where` one `Placeholder`, one non-empty constraint list, optional examples, and an optional description.
- Author each `Where` with one `Placeholder` followed by its constraints.
- Represent each constraint as one discriminated union of (type|one of|regex|non-empty|max chars|lines|list of|at least|at most) on a required `kind`.
- Default each constraint `kind` in direct Pydantic authoring.
- Keep each constraint `kind` required in JSON Schema.
- Select each `type` value and each `list of` item from the vocabulary datatypes.
- Give each (at least|at most) a value that is (number|Placeholder).
- Extract each distinct `Placeholder` from the template.
- Reject a duplicate `Placeholder` in `where`.
- Reject a schema when its template `Placeholder` set and `where` `Placeholder` set differ.
- Reject an (at least|at most) whose `Placeholder` value is absent from the same schema.
- Reject examples on a `Where` with a `Placeholder` valued bound.
- Reject a `lines` constraint when (both bounds are absent|the minimum exceeds the maximum).
- Require each `lines` bound to be positive.
- Restrict authored regex patterns to anchors, atoms, character classes, escapes, and quantifiers.
- Reject a regex constraint that rust-regex cannot compile.
- Name each rejection with one error code, such as `placeholder_where_mismatch`.
- Apply every `Where` constraint to each value bound to its `Placeholder`.
- Resolve each `Placeholder` valued (at least|at most) within the same schema instance.
- Apply datatype validation before each bound comparison.
- Validate regex values with rust-regex.
- Accept placeholder bindings from the interpreter instead of recovering them from rendered text.
- Raise `SchemaBindingError` when a schema binding fails.
- Give each binding failure one code, one `Placeholder`, and one message.
- Collect every binding failure before raising.

## State

- State holds values that change while the interpreter uses the knowledge.

## Triggers

- Triggers route intent to the knowledge.
- A trigger records why the interpreter enters the knowledge.
- Require each trigger `when` value to use `NonBlankLine`.
- Give each trigger an optional `given` `Condition`.
- Treat an absent trigger `given` as true.
- Reject a trigger `given` without a state read with `trigger_guard_missing_state`.
- Reject a trigger `given` that reads an (interface|local binding) with `invalid_trigger_guard_value`.
- Require each trigger to reference one process.
- A trigger separates use with intent from use by discovery.
- Triggers are optional.
- A trigger's process reference must target a process entry.
- Multiple triggers can reference the same process or different processes.
- Match every trigger `when` before selecting a process.
- Match a trigger `when` by exact string equality.
- Evaluate a trigger `given` only after its `when` matches.
- Run the process when exactly one trigger matches its `when` and `given`.
- Run no process when no trigger matches both its `when` and `given`.
- Fail with `ambiguous_trigger_match` when multiple triggers match both their `when` and `given`.
- Reject equal trigger `when` values unless every guard pair is provably disjoint, with `overlapping_trigger_guards`.
- Prove guards disjoint when they compare the same state to unequal static values with `equals`.
- Prove guards disjoint when `equals` and `not_equals` compare the same state to the same static value.
- Treat every other equal-`when` guard pair as overlapping.
- The name trigger is confirmed over signal on 2026-08-21, because it names what makes an outsider enter.
- Triggers are optional in a node.

## Processes

- Processes are exact ways to do a task.
- Represent each process step as one discriminated union of (act|set|emit|if|call|fail) on a required `kind`.
- Represent each process value as one discriminated union of (literal|constant|state|interface|binding) on a required `source`.
- Give each value binding one `Placeholder` and one process value.
- Give each condition one left value, one operator, and one right value.
- Require each condition operator to be (equals|not_equals).
- Require each process to have one `ProcessName` and one or more steps.
- Author the first `ProcessName` word as the action and the second as its object.
- Give each act one `NonBlankLine` instruction, an input binding list, and an output `Placeholder` list.
- Require each act instruction placeholder to occur once in its inputs or outputs.
- Reject a duplicate act input or output.
- Reject an act placeholder used as both input and output.
- Require an act to return exactly its declared outputs.
- Store each act output as an immutable process-local JSON binding.
- Keep a binding created in an if branch inside that branch.
- Give each set step one state `SlugId` and one value.
- Resolve a state value from the current execution state.
- Apply a set step to the current execution state.
- Give each emit step one interface `SlugId` and one non-empty binding list.
- Require each emit interface to target an (out|inout) interface.
- Require each emit binding set to equal the interface schema placeholder set.
- Validate each emitted binding against the interface schema before emission.
- Give each if step one condition, one non-empty then list, and one optional otherwise list.
- Execute only the branch selected by the condition.
- Use (if|fail) steps for process preconditions.
- Do not give a process a `given` block.
- Give each call step one process `SlugId`.
- Require each call reference to target a process entry.
- Reject process call cycles with `process_call_cycle`.
- Run a called process synchronously in the current state and emission transaction.
- Give each fail step one `NonBlankLine` message.
- Stop the execution with `process_failed` when a fail step runs.
- Require each constant value reference to target a constant entry.
- Require each state value reference to target a state entry.
- Require each interface value reference to target an (in|inout) interface.
- Require each interface value placeholder to exist in the interface schema.
- Require each binding value to reference a visible prior binding.
- Commit state writes and interface emissions after successful top-level completion.
- Discard state writes and interface emissions after failure.
- Represent one arrival as one `when` value and zero or more input interface bindings.
- Validate each active input binding against its interface schema before trigger selection.
- Require the supplied state ids to equal the authored state ids.
- Execute one arrival cycle with `execute(root, arrival, state, act=...)`.
- Require an act handler only when an act step runs.
- Validate each act handler result against the declared output set.
- Return the selected process, committed state, and ordered emissions after success.
- Return no process and no emission when no trigger matches.
- Raise `ExecutionError` with one code and one message on runtime failure.
- Do not mutate the caller state mapping.
- Derive interface consumption and emission from typed process steps.
- Do not give a process separate `consumes` or `emits` lists.
- Use triggers for repetition instead of recursive process calls.
- Processes can run without interfaces.
- Processes do not have to be referenced by triggers.

## Interfaces

- An interface declares one information crossing at the tree boundary.
- An in interface carries information into the tree.
- An out interface carries information out of the tree.
- An inout interface carries information in both directions.
- Interfaces are optional.
- Require each interface `direction` to be (in|out|inout).
- Require each interface `schema` reference to use `SlugId`.
- Require each interface `schema` reference to target a schema entry.
- Give each interface an optional `NonBlankLine` description of the crossing.
- An interface description states boundary meaning that its schema does not state.
- Interfaces do not define information shapes.

## Vocabulary

- The vocabulary is how information is conveyed without ambiguity inside every render.
- The vocabulary holds the text shapes, the datatypes, the unit catalog, the time forms, and the display forms.
- The vocabulary is where the core schema and the Rust regex checks run.
- Every render uses the same vocabulary; OAK is the opinionated default render of it.
- Define `SlugId` as lower kebab case without a leading, trailing, or repeated hyphen.
- Define `NonBlankLine` as one line containing at least one non-whitespace character.
- Define `ProcessName` as two ASCII alphanumeric words with optional internal hyphens, separated by one U+0020 SPACE, with an uppercase first character.
- Define `Placeholder` as ASCII upper snake case without a leading, trailing, or repeated underscore.
- Define `DottedPath` as (`constant.SlugId`|`state.SlugId`|`process.SlugId`|`interface.SlugId`|`interface.SlugId.Placeholder`).
- Define `ValueReference` as `$` followed by (`constant.SlugId`|`state.SlugId`|`interface.SlugId.Placeholder`|`Placeholder`).
- `$` reads a value.
- The first `DottedPath` segment names the part.
- A bare `$Placeholder` reads one process-local act output.
- Use `DottedPath` without `$` for each (SET|CALL|EMIT) target.
- Use (`equals`|`does not equal`) for comparison.
- Use `=` only for assignment and value binding.
- Delimit each `Placeholder` with `<` and `>` in schema templates, `Where` lines, and act instructions.
- Render each process binding target and act output as a bare `Placeholder`.
- In a template, a line of one U+2026 HORIZONTAL ELLIPSIS tells the interpreter the pattern above it continues; the engine gives it no meaning.
- Represent each closed token catalog with a (literal|enum).
- Define `Datatype` as (string|integer|number|boolean|quantity|datetime|uri|path).
- Define `Unit` as (%|kg|°C|kg·m/s²).
- Represent a quantity as a nested model of a Decimal value and a unit enum; the serializer owns its display.
- Represent a datetime as a `DateTime` model with one `AwareDatetime` value and one optional `TimeZoneName` zone.
- Reject a naive datetime; never convert one to UTC.
- Use U+002E FULL STOP as the decimal separator.
- Use U+2009 THIN SPACE as the thousands separator.
- Render each quantity as a number, one U+0020 SPACE, and one unit.
- Render percent with U+0025 PERCENT SIGN as its unit.
- Render compound units with U+00B7 MIDDLE DOT.
- Select each unit from the shared unit catalog.
- Render temperature in °C.
- Render each datetime in ISO 8601 form.
- Render a zero UTC offset as `Z`.
- Require each local datetime to include a numeric UTC offset.
- Append an IANA time zone name as `[TimeZoneName]` when present.
- Keep number, quantity, and datetime display rules in separate display modules.

## Pydantic

- Pydantic v2 is the authoring form, not a render.
- Pydantic v2 is the description language for the vocabulary and the parts.
- Pydantic v2 is the authoring tool, and every render derives from the authored tree.
- Use the narrowest (type|literal|discriminated union|min length|max length|numeric bound|nested model) that states each rule.
- Use regex only when the complete value is the shape of one string.
- Anchor every regex pattern to the whole string.
- Use source lint for text conventions embedded in prose.
- Use a root graph check only for rules across (nodes|entries).
- Do not add a field only for a render token; validate the token in the renderer through a module-level `TypeAdapter`.
- Define each authored text syntax once in its own module under `oak/vocabulary/text/`.
- Define each OAK render text syntax once in `oak/render/oak/`.
- Build each regex pattern once at module import from its owning text syntax.
- Build each reusable string shape with `Annotated[str, StringConstraints(pattern=...)]`.
- Keep defaults and aliases at the field declaration and only constraints in the `Annotated` alias.
- Author the interface schema reference as `schema` through a field alias.
- Keep each token catalog at module scope, or annotate it `ClassVar` on a model.
- Set `regex_engine` to `rust-regex` on the shared OAK base model in `oak/base.py`.
- Pass each regex pattern as a string, because a compiled pattern forces `python-re`.
- Use `[0-9]` and `[A-Za-z]` for ASCII classes, because Rust regex treats `\d` and `\w` as Unicode.
- Validate every default value.
- Build each `TypeAdapter` once at module import.
- Emit the `Placeholder` pattern in JSON Schema.
- Emit each discriminated union as `oneOf` branches selected by its `kind`.
- Emit forbidden extra fields as `additionalProperties: false`.
- Restrict each regex pattern emitted in JSON Schema to syntax accepted by both rust-regex and ECMA-262.

## Render

- One knowledge tree can render to many formats.
- A render is a representation of one node or tree.
- The renders are OAK and JSON-LD.
- JSON-LD is the interchange render.
- The Pydantic dump is an internal authoring snapshot.
- Each projection defines what it preserves, what it loses, and how it orders content.

### OAK

- OAK is the default render.
- The text render is named OAK and is the default render, because it is the render an interpreter uses directly; APS was its predecessor.
- The OAK render is prose structured text which optimises for disambiguation for AI Models.
- OAK renders from the authored tree with a grouping and a style.
- These render choices do not change the authored tree.
- OAK rendering uses grouping and style outside the node, adding no part or field.
- The default OAK rendering is xml and authored.
- A grouping is the delimiters that group the parts: (xml tags|markdown fences).
- The groupings are xml and markdown.
- A grouping changes delimiters only.
- Each grouping defines how it escapes its delimiters.
- A renderer claims APS compatibility only when the tree and text meet APS rules.

#### Arrangement

- The OAK render has seven parts in this order: instructions, constants, schemas, state, triggers, processes, interfaces.
- The OAK render has one arrangement.
- OAK is the next iteration of APS; it uses the APS part order with interfaces in the input position.
- Each top-level part MUST appear at most once.
- Every part appears, empty when the node has no entry for it.
- Each part holds the node's own entries in authored order.
- Parts are siblings; no part nests inside another.
- Render each authored instruction as its text alone after the built-in instructions.
- When a process or guarded trigger exists, render `$ reads a value; a dotted path starts with its part; a bare $NAME is local to the running process; SET, CALL, and EMIT omit $.` before authored instructions.
- When constants has entries, render `Constants hold values that do not change while the knowledge runs.` before authored instructions.
- When schemas has entries, render `Each schema is one information shape: a template with <PLACEHOLDER> slots, and WHERE lines that constrain each slot.` before authored instructions.
- When state has entries, render `State holds values that persist and can change while processes run.` before authored instructions.
- When triggers has entries, render `Each trigger names one arrival reason, an optional state guard, and the process that runs when both match.` before authored instructions.
- When processes has entries, render `Each process is the exact way to do one task; follow its steps in order, top to bottom.` before authored instructions.
- When interfaces has entries, render `Each interface is one information crossing: in arrives, out is emitted, and inout does both.` before authored instructions.
- Inject no other built-in instruction text.
- Render each trigger as one self-closing `trigger` tag with one `id`, one optional `given`, one `when`, and one `process` attribute.
- Render each state entry and each inline constant as its id, `: `, and its value as JSON on one line.
- Render each block constant with its form opener, body, and closing line.
- Render each process with its id and name, then its typed steps one per line in authored order.
- Line order carries the step sequence; render no step numbers and no heading.
- Indent grouped lines by two spaces under their parent line.
- Render each process value as one of (JSON literal|`ValueReference`).
- Render each act with `ACT`, its instruction, optional `INPUTS:`, and optional `OUTPUTS:`.
- Render each act input and output name as a bare `Placeholder`.
- Render each set on one line with `SET`, its state `DottedPath`, ` = `, and its value.
- Render each emit with `EMIT`, its interface `DottedPath`, and one bare `Placeholder` binding per line.
- Render each if with `IF`, its condition, its indented then steps, and `ELSE:` with its indented otherwise steps when present.
- Render no (`GIVEN`|`THEN`) process keyword.
- Render each call on one line with `CALL` and its process `DottedPath`.
- Render each fail on one line with `FAIL` and its JSON string message.
- Render each interface with its id, direction, and schema reference, and its description as its body.
- Render each child node as one nested `node` block after the seven parts.
- Separate the parts and each nested `node` block with one blank line.
- Separate sibling (schema|process|interface) blocks with one blank line.
- Render each constant and state id with `SlugId`.
- A process renders with an inner structure.
- Render each process reference at the step or value that uses it.
- An interface renders with an inner structure.
- Render each schema template followed by one blank line and `WHERE:`.
- Preserve template whitespace in each text render.
- Render `Where` entries in authored order.
- Render each `Where` as one line: its delimited `Placeholder`, constraints joined by `; `, examples once in brackets as `(e.g. ...)`, then the description.
- The OAK render loses node and instruction ids and keeps every other entry id.

#### XML

```yaml
oak_parts:
  order: [instructions, constants, schemas, state, triggers, processes, interfaces]
  tags:
    - <instructions>…</instructions>
    - <constants>…</constants>
    - <schemas>…</schemas>
    - <state>…</state>
    - <triggers>…</triggers>
    - <processes>…</processes>
    - <interfaces>…</interfaces>
```

- The xml grouping uses XML-like tags as text delimiters.
- Render text between xml tags verbatim.
- Escape xml attribute values.
- Render trigger attributes in (`id`|`given`|`when`|`process`) order.
- Put each xml opening tag before its text on a separate line.
- Put each xml closing tag after its text on a separate line.
- The xml grouping uses OAK names and node structure.
- APS is not the canonical xml grouping, because OAK has its own parts and typed process model.
- Join built-in and authored instruction lines inside `<instructions>` with one U+000A LINE FEED.

#### Markdown

- The markdown grouping uses tilde fences as text delimiters.
- Open each part with `~~~~part` and close it with `~~~~`.
- Open each body entry with `~~~entry;attr="value"` and close it with `~~~`.
- Render a bodiless entry as one bare opening line.
- Keep each entry body byte-identical between the xml and markdown groupings.
- Encode each markdown attribute value as one JSON string.
- Use a node fence longer than every fence inside that node.
- Increase nested node fence lengths from five tildes as depth requires.

#### Styles

- Apply a style to natural language wording and display formatting only.
- Style is a render choice, not an interpretation instruction, because one tree must render in many styles.
- The authored style preserves the authored wording.
- A controlled style is a named and versioned renderer profile.
- A controlled style rewrites only instruction bodies, trigger text, act instructions, and fail messages.
- A controlled style preserves meaning, obligation, negation, conditions, and step order.
- A renderer fails when it cannot validate a requested controlled style.
- An ASD-STE100 style names its governing edition and validation rules.
- Name the implemented controlled style `asd-ste100-9`.
- The `asd-ste100-9` style targets ASD-STE100 Issue 9, January 2025.
- Rewrite (in order to|prior to|subsequent to|utilize|commence|terminate) and their implemented inflections with controlled alternatives.
- Reject controlled text with more than one line.
- Reject controlled text with more than one sentence.
- Reject controlled text with more than 20 words.
- Reject controlled text that still contains a replaced term.
- Do not claim full ASD-STE100 conformance.
- Apply the implemented line, sentence, word, and term checks through the named ASD-STE100 style.

### JSON-LD

- Render each node and entry `SlugId` as a relative `@id`.
- Render each typed reference target as a relative `@id`.
- Require the caller to supply a JSON-LD base IRI ending in `/`.
- Define `@base` as the caller base in the root context.
- Resolve each relative `@id` against `@base`.
- Render `Schema`, `Interface`, `Where`, each constraint kind, each process value source, and each process step kind as `@type`.
- Render each trigger `given` as `Condition`.
- Derive each `Where` `@id` as `{schema @id}/where/{Placeholder}`.
- Render `where`, `constraints`, and `examples` as `@list` containers.
- Render (interfaces|steps|inputs|outputs|bindings|then|otherwise) as `@list` containers.
- Define context terms for `template`, `where`, `placeholder`, `constraints`, `examples`, and each constraint field.
- Define context terms for (direction|schema|interfaces|steps|inputs|outputs|bindings|condition|given|left|operator|right|then|otherwise|instruction|message|constant|state|interface|binding).
- Render each `Placeholder` valued (at least|at most) value as the referenced `Where` `@id`.
- Require the caller to supply the JSON-LD vocabulary IRI.
- Define `oak` as the caller vocabulary prefix.
- Render OAK `@type` values as `oak` compact IRIs.
- Render one context with `@base` at the root of each JSON-LD document.

---

## Build

The build uses the package to generate the outputs once; a model writes OAK with the outputs; the models validate what it wrote.
- Validate text aliases, model examples, field examples, render defaults, both groupings, block constants, controlled style, parsing, execution, and display forms in `build/examples.py`.

### EBNF

- OAK when authoring the build of OAK emits a EBNF grammar for OAK itself, which is a meta-grammar for OAK.
- Emit one EBNF production for each named text alias.
- Generate each (Rust regex|JSON Schema pattern|EBNF production) from the same restricted text syntax of (literal|character class|sequence|choice|optional|repeat|named reference).
- Do not derive one output syntax from another output syntax.
- Do not use EBNF as a validator.
- Derive the OAK structural productions from the fixed part order.
- Write the grammar snapshot to `outputs/oak.ebnf`.

### Prompt

- Emit the authoring prompt as one markdown file of OAK generated from the models: instructions from the constraints, schemas from the models, one process to write OAK (with|without) the models, one trigger for a model that arrives to write OAK.
- Read the authoring instructions from the PRD Constraints section.
- Derive one prompt schema from each model title, description, and field description.
- Write the authoring prompt snapshot to `outputs/prompt.md`.

### Documentation

- Emit the documentation as a directory tree of markdown generated from the models, one file per model, built from every model and field (title|description|examples).
- Reject a model or field without a description.
- Derive a missing `Node` or `Root` field example from each validated model example.
- Remove stale generated model documents before rebuilding.
- Write one model document to `outputs/docs` for each model.

### Tree

- The tree below represents the build as the PRD above is written.
- The tree evolves with every line above it.
- A comment that starts with `*` marks a file the build generates.
- An entry `...` marks a group that grows as the PRD adds lines.

```t
oak
├── .agent  # skills the agent reads, not PRD driven
├── .gitignore
├── AGENTS.md  # repository rules
├── CLAUDE.md  # pointer to AGENTS.md
├── docs  # ground truth
│   ├── PRD.md
│   └── types.md  # Pydantic types the core schema validates
├── examples  # authored trees, one per file; the render sits next to its author
│   ├── incident_triage.py  # authors one agent-facing tree
│   ├── incident_triage.oak.md  # * the OAK render of incident_triage.py
│   ├── shell.py  # authors one shell state machine
│   └── shell.oak.md  # * the OAK render of shell.py
├── legacy-snapshot-aps  # APS reference, read only
├── oak  # the package, what the PRD builds
│   ├── __init__.py  # authoring API
│   ├── defaults.py  # render OAK, grouping xml, style authored
│   ├── base.py  # shared config, SlugId entries, rust-regex engine
│   ├── node  # layer 1, one complete set of the seven parts
│   │   ├── __init__.py
│   │   ├── model.py  # Node and Root: the seven parts, child nodes
│   │   ├── graph.py  # root graph checks
│   │   ├── dump.py  # Pydantic dump
│   │   └── parts  # one module per part, its entry model
│   │       ├── __init__.py  # the closed set, one discriminated union
│   │       ├── instructions.py  # Instruction
│   │       ├── constants.py  # Constant
│   │       ├── schemas.py  # Schema, Where, the constraint union, bind
│   │       ├── state.py  # State
│   │       ├── triggers.py  # Trigger and its optional state guard
│   │       ├── processes.py  # Process, values, conditions, and the closed step union
│   │       └── interfaces.py  # Interface, Direction
│   ├── vocabulary  # layer 3, how information is conveyed without ambiguity; one file provides one thing
│   │   ├── __init__.py
│   │   ├── syntax.py  # restricted text syntax tree; generates Rust regex, JSON Schema pattern, EBNF
│   │   ├── units.py  # the unit catalog, one enum
│   │   ├── text  # text shapes, one alias each
│   │   │   ├── __init__.py
│   │   │   ├── slug_id.py  # SlugId
│   │   │   ├── non_blank_line.py  # NonBlankLine
│   │   │   ├── process_name.py  # ProcessName
│   │   │   ├── placeholder.py  # Placeholder and template token extraction
│   │   │   ├── dotted_path.py  # DottedPath
│   │   │   ├── value_reference.py  # ValueReference
│   │   │   ├── regex_pattern.py  # RegexPattern, the portable authored subset
│   │   │   └── ...
│   │   ├── datatypes  # typed values, one model each
│   │   │   ├── __init__.py
│   │   │   ├── names.py  # Datatype, the name catalog, one validator each
│   │   │   ├── quantity.py  # Decimal value and unit enum
│   │   │   ├── datetime.py  # AwareDatetime and optional TimeZoneName
│   │   │   └── ...
│   │   └── display  # display forms, one rule set each
│   │       ├── __init__.py
│   │       ├── number.py  # decimal point, thousands separator
│   │       ├── quantity.py  # number, space, unit; percent; middle dot
│   │       ├── datetime.py  # ISO 8601, Z, offset, IANA name
│   │       └── ...
│   ├── parse.py  # OAK text to models
│   ├── execute.py  # one transactional trigger and process cycle
│   └── render  # layer 2, one module per render
│       ├── __init__.py  # render selection, defaults apply
│       ├── oak  # the default render
│       │   ├── __init__.py
│       │   ├── instructions.py  # built-in interpretation instructions
│       │   ├── syntax.py  # WHERE wording, constraints, paths, and process values
│       │   ├── arrangement.py  # seven parts, interfaces in the APS input position
│       │   ├── groupings.py  # layer 4, xml tags or markdown fences
│       │   └── styles.py  # authored, controlled ASD-STE100
│       └── json_ld.py  # @base, @id, @type, @list, the context
├── build  # uses the package to generate the outputs
│   ├── examples.py  # validate examples and each working product path
│   ├── ebnf.py
│   ├── prompt.py
│   └── docs.py
├── outputs  # snapshot of the oak build
│   ├── oak.ebnf  # * the OAK meta-grammar
│   ├── prompt.md  # * the authoring prompt, one markdown file of OAK
│   └── docs  # * markdown tree, one file per model
└── pyproject.toml
```
