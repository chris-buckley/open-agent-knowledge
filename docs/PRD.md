---
title: OAK Product Requirements
status: draft
updated: 2026-08-24
owner: Christopher Buckley
defaults:
  render: OAK
  variant: xml
  style: authored
open:
  - What fields does every entry share? Deferred on 2026-08-21 while the user reviews the PRD. The title field is out of the sketch until this is decided.
  - How does OAK resolve two triggers that match one arrival? Deferred on 2026-08-21 until trigger execution is defined.
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
  - Return the OAK render when no render, variant, or style is named; every default is OAK.
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

---

## Constraints

1. Reject an empty (ID|text) field.
2. Reject a process with no steps.
3. Reject unknown fields.
4. Reject an entry outside the seven parts (instructions|constants|schemas|state|triggers|processes|input).
5. Require one root node.
6. Require each child of a node to be a node.
7. Reject duplicate IDs across nodes and entries.
8. Reject a (missing|wrong-type) reference target.
9. Omit unset optional fields from the Pydantic dump.

## Structure

- The name is OAK, short for Open Agent Knowledge.
- The name changed from UAOC, Universal Agent Operating Context, to OAK on 2026-08-21, because knowledge is broader than an operating context.
- OAK is a knowledge standard, not an information standard, because knowledge covers static information and executable instructions.
- The consumer of the knowledge is named the interpreter, confirmed over actor on 2026-08-21.
- OAK has four layers: the node, the render, the vocabulary, and the variant.
- A node is one complete set of the seven parts.
- The parts are instructions, constants, schemas, state, triggers, processes, and input.
- The set of parts is closed.
- An entry is one item in a part: one instruction, one constant, one schema, one state value, one trigger, one process, or the input.
- Each entry belongs to exactly one part, so every entry validates at authoring time.
- A tree is nodes nested in nodes, and entries can reference each other.
- Knowledge is authored as a nested tree, because nesting gives one root, one parent, and no containment cycle structurally.
- Composition is the nesting of nodes, not an eighth part.
- The flat entry registry is derived from the tree during validation, not authored.
- Cross-references use typed fields, not a generic link field.
- Require each (node|entry) ID to use `IriId` independent of file placement.
- Every entry shares only `id`.
- Keep `name` and `purpose` part-specific.
- Discriminate the closed entry union on `part`.
- Author the tree root as `Root`.
- Author each nested node as `Node`.
- Root validation rejects duplicate IDs, missing reference targets, and wrong target types.
- Constants and state hold any JSON value.
- Validation is strict: no type coercion and no unknown fields.
- The PRD uses one short sentence per idea.
- Give every model and field a title, a description, and examples; the prompt and the documentation derive from them.
- Validate every example against its model or field in the build, so the examples are the only tests.
- Parse OAK text into the models, so OAK written without the models is validated afterwards.

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

Example: multi-line TEXT constant using TEXT<< ... >>. Tree symbols mark each level.

```text
<constants>
REPO_TREE: TEXT<<
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

Example: multi-line JSON constant using JSON<< ... >>. Engines parse BODY as JsonValue then compile it to canonical JSON (see json_spacing).

```text
<constants>
DEFAULT_TZ: "Z"

API_CONFIG: JSON<<
{
  "api_base_path": "/v1",
  "default_time_zone": DEFAULT_TZ,
  "retries": 3,
  "timeout_ms": 2000
}
>>
</constants>
```

Example: multi-line CSV constant using CSV<< ... >>. Engines parse BODY as CSV then compile it to canonical JSON rows (see 00 Structure / 02 Linting).

```text
<constants>
DEFAULT_TZ: "Z"

SERVICE_TABLE: CSV<<
service,region,default_tz,enabled,note
billing,us-east-1,DEFAULT_TZ,true,"Primary billing region"
support,ap-southeast-2,"Australia/Brisbane",true,"Escalations use ""follow the sun"""
reporting,eu-west-1,DEFAULT_TZ,false,"EU, West"
>>
</constants>
```

## Schemas

- Schemas hold every output contract an interpreter may render and every structure it may capture.
- Define each output contract once in schemas, so each output is (verifiable|stable|machine-checkable).
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
- Require each trigger to reference one process.
- A trigger separates use with intent from use by discovery.
- Triggers are optional.
- A trigger's process reference must target a process entry.
- Multiple triggers can reference the same process or different processes.
- The name trigger is confirmed over signal on 2026-08-21, because it names what makes an outsider enter.
- Triggers are optional in a node.

## Processes

- Processes are exact ways to do a task.
- Require each process step to use `NonBlankLine`.
- A process can use constants.
- A process can use schemas.
- A process can put constant values into schemas.
- A process can act on information inside the knowledge.
- A process reached through a trigger gives the ordered steps for that entry.
- Processes do not have to be referenced by triggers.

## Input

- Input is the contract for what the knowledge expects to receive.
- Input is defined before the knowledge is used.
- Give input one `NonBlankLine` body.

## Vocabulary

- The vocabulary is how information is conveyed without ambiguity inside every render.
- The vocabulary holds the text shapes, the datatypes, the unit catalog, the time forms, and the display forms.
- The vocabulary is where the core schema and the Rust regex checks run.
- Every render uses the same vocabulary; OAK is the opinionated default render of it.
- Define `IriId` as an ASCII scheme, a colon, and one or more non-whitespace characters.
- Define `NonBlankLine` as one line containing at least one non-whitespace character.
- Define `ConstantName` as ASCII upper snake case without a leading, trailing, or repeated underscore.
- Define `Placeholder` as `ConstantName`.
- Delimit each `Placeholder` with `<` and `>` in template text; any other `<` is literal.
- Represent each closed token catalog with a (literal|enum).
- Represent a quantity as a nested model of a Decimal value and a unit enum; the serializer owns its display.
- Represent a datetime as `AwareDatetime` with an optional `TimeZoneName`.
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
- Render an IANA time zone name separately when present.

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
- OAK renders from the authored tree with a variant and a style.
- These render choices do not change the authored tree.
- OAK rendering uses variant and style outside the node, adding no part or field.
- The default OAK rendering is xml and authored.
- A variant is the delimiters that group the parts: (xml tags|markdown fences).
- The variants are xml and markdown.
- A variant changes delimiters only.
- Each variant defines how it escapes its delimiters.
- A renderer claims APS compatibility only when the tree and text meet APS rules.

#### Arrangement

- The OAK render has seven parts in this order: instructions, constants, schemas, state, triggers, processes, input.
- The OAK render has one arrangement, the seven parts in APS order, because OAK is the next iteration of APS.
- OAK is the next iteration of APS; it keeps the APS part order and uses its own names.
- Each top-level part MUST appear at most once.
- Every part appears, empty when the node has no entry for it.
- Each part holds the node's own entries in authored order.
- Parts are siblings; no part nests inside another.
- Render each instruction or trigger as its text alone.
- Render each constant name with `ConstantName`.
- A process renders with an inner structure.
- Render each schema template followed by one blank line and `WHERE:`.
- Preserve template whitespace in each text render.
- Render `Where` entries in authored order.
- Render each `Where` as one `Placeholder` line followed by indented detail lines.
- Render each constraint, example, and description on its own detail line.
- The OAK render loses node ids and keeps schema entry ids.

#### XML

```yaml
oak_parts:
  order: [instructions, constants, schemas, state, triggers, processes, input]
  tags:
    - <instructions>…</instructions>
    - <constants>…</constants>
    - <schemas>…</schemas>
    - <state>…</state>
    - <triggers>…</triggers>
    - <processes>…</processes>
    - <input>…</input>
```

- The xml variant uses XML-like tags as text delimiters.
- Render text between xml tags verbatim.
- Escape xml attribute values.
- Put each xml opening tag before its text on a separate line.
- Put each xml closing tag after its text on a separate line.
- The xml variant uses OAK names and node structure.
- APS is not the canonical xml variant, because APS requires a process part and a process target that OAK does not.
- Join instruction bodies inside `<instructions>` with one U+000A LINE FEED.

#### Markdown

- The markdown variant uses headings, lists, and fenced blocks.
- Render process steps as a numbered list.

#### Styles

- Apply a style to natural language wording and display formatting only.
- Style is a render choice, not an interpretation instruction, because one tree must render in many styles.
- The authored style preserves the authored wording.
- A controlled style is a named and versioned renderer profile.
- A controlled style rewrites only instruction bodies, trigger text, and process steps.
- A controlled style preserves meaning, obligation, negation, conditions, and step order.
- A renderer fails when it cannot validate a requested controlled style.
- An ASD-STE100 style names its governing edition and validation rules.
- Apply sentence, paragraph, and list limits through the named ASD-STE100 style when it is defined.

### JSON-LD

- Render each schema id as `@id`.
- Render `Schema`, `Where`, and each constraint kind as `@type`.
- Derive each `Where` `@id` as `{schema @id}/where/{Placeholder}`.
- Render `where`, `constraints`, and `examples` as `@list` containers.
- Define context terms for `template`, `where`, `placeholder`, `constraints`, `examples`, and each constraint field.
- Render each `Placeholder` valued (at least|at most) value as the referenced `Where` `@id`.
- Require the caller to supply the JSON-LD vocabulary IRI.
- Define `oak` as the caller vocabulary prefix.
- Render OAK `@type` values as `oak` compact IRIs.
- Render one context at the root of each JSON-LD document.

---

## Build

The build uses the package to generate the outputs once; a model writes OAK with the outputs; the models validate what it wrote.

### EBNF

- OAK when authoring the build of OAK emits a EBNF grammar for OAK itself, which is a meta-grammar for OAK.
- Emit one EBNF production for each named text alias.
- Generate each (Rust regex|JSON Schema pattern|EBNF production) from the same restricted text syntax of (literal|character class|sequence|choice|optional|repeat|named reference).
- Do not derive one output syntax from another output syntax.
- Do not use EBNF as a validator.

### Prompt

- Emit the authoring prompt as one markdown file of OAK generated from the models: instructions from the constraints, schemas from the models, one process to write OAK (with|without) the models, one trigger for a model that arrives to write OAK.

### Documentation

- Emit the documentation as a directory tree of markdown generated from the models, one file per model, built from every model and field (title|description|examples).
- Reject a model or field without a description.

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
├── legacy-snapshot-aps  # APS reference, read only
├── oak  # the package, what the PRD builds
│   ├── __init__.py  # authoring API
│   ├── defaults.py  # render OAK, variant xml, style authored
│   ├── base.py  # shared config, references, rust-regex engine
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
│   │       ├── triggers.py  # Trigger
│   │       ├── processes.py  # Process
│   │       └── input.py  # Input
│   ├── vocabulary  # layer 3, how information is conveyed without ambiguity; one file provides one thing
│   │   ├── __init__.py
│   │   ├── syntax.py  # restricted text syntax tree; generates Rust regex, JSON Schema pattern, EBNF
│   │   ├── units.py  # the unit catalog, one enum
│   │   ├── text  # text shapes, one alias each
│   │   │   ├── __init__.py
│   │   │   ├── iri_id.py  # IriId
│   │   │   ├── non_blank_line.py  # NonBlankLine
│   │   │   ├── constant_name.py  # ConstantName
│   │   │   ├── placeholder.py  # Placeholder, template token extraction
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
│   └── render  # layer 2, one module per render
│       ├── __init__.py  # render selection, defaults apply
│       ├── oak  # the default render
│       │   ├── __init__.py
│       │   ├── syntax.py  # WHERE wording, constraint text
│       │   ├── arrangement.py  # seven parts in APS order
│       │   ├── variants.py  # layer 4, xml tags or markdown fences
│       │   └── styles.py  # authored, controlled ASD-STE100
│       └── json_ld.py  # @id, @type, @list, the context
├── build  # uses the package to generate the outputs
│   ├── examples.py  # validate every model and field example
│   ├── ebnf.py
│   ├── prompt.py
│   └── docs.py
├── outputs  # snapshot of the oak build
│   ├── oak.ebnf  # * the OAK meta-grammar
│   ├── prompt.md  # * the authoring prompt, one markdown file of OAK
│   └── docs  # * markdown tree, one file per model
└── pyproject.toml
```
