---
title: OAK Product Requirements
status: draft
updated: 2026-08-22
owner: Christopher Buckley
defaults:
  output: OAK
  variant: xml
  style: authored
open:
  - What fields does every node share? Deferred on 2026-08-21 while the user reviews the PRD. The title field is out of the sketch until this is decided.
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
  - Return the OAK output when no output, variant, or style is named; every default is OAK.
  - Write no tests; the examples validate the build and tests add tokens and context for models.
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
4. Reject a node type other than (instruction|constant|schema|state|trigger|process|input).
5. Require one root composition.
6. Require each composition child to be a (node|composition).
7. Reject duplicate IDs across nodes and compositions.
8. Reject a (missing|wrong-type) reference target.
9. Omit unset optional fields from the Pydantic output.

## Structure

- The name is OAK, short for Open Agent Knowledge.
- The name changed from UAOC, Universal Agent Operating Context, to OAK on 2026-08-21, because knowledge is broader than an operating context.
- OAK is a knowledge standard, not an information standard, because knowledge covers static information and executable instructions.
- The consumer of the knowledge is named the interpreter, confirmed over actor on 2026-08-21.
- The unit of the vocabulary is named the node.
- The set of node types is closed.
- The node types are instructions, constants, schemas, state, triggers, processes, and input.
- Each node has exactly one type from the closed set, so every node validates at authoring time.
- A structure is a tree of nodes, and leaves can reference each other.
- Knowledge is authored as a nested tree, because nesting gives one root, one parent, and no containment cycle structurally.
- Composition is structure, not an eighth node type.
- The flat node registry is derived from the tree during validation, not authored.
- Cross-references use typed fields, not a generic link field.
- Node IDs are absolute IRI-shaped strings, independent of file placement.
- Root validation rejects duplicate IDs, missing reference targets, and wrong target types.
- Constants and state hold any JSON value.
- Validation is strict: no type coercion and no unknown fields.
- The PRD uses one short sentence per idea.

## Instructions

- Instructions are rules the interpreter of the knowledge must follow.
- Instructions include interpretation rules.
- Instructions include rule following.
- Instructions include methods for how to go about something.
- Instructions include safety measures.
- Instructions include policy.
- Instructions MUST use one directive per line.
- Each line MUST be a single imperative or declarative that changes system behavior.
- Multiple sentences per line are forbidden.
- Blank lines inside `<instructions>` are forbidden.
- Instructions that interpretation references render first in the instructions section.
- Interpretation rules belong to instructions because they govern every entry.
- A composition's interpretation instructions apply before a process reached through a trigger.

## Constants

- Constants are values that stay the same in every use of the knowledge.

Example: multi-line TEXT constant using TEXT<< ... >>. Tree symbols are not used because they cost extra tokens; use an indent instead.

```text
<constants>
REPO_TREE: TEXT<<
cb-agnostic-prompt-protocol
  assets
    constants
      constants-json-block-v1.0.0.example.md
    formats
      format-code-map-v1.0.0.example.md
      format-error-v1.0.0.example.md
  SKILL.md
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

- Schemas are defined structures.
- Schemas include schemas, templates, and formats.

## State

- State holds values that change while the interpreter uses the knowledge.

## Triggers

- Triggers route intent to the knowledge.
- A trigger records why the interpreter enters the knowledge.
- A trigger can optionally reference one process to follow when it matches.
- A trigger without a process remains a signpost.
- A trigger separates use with intent from use by discovery.
- Triggers are optional.
- A trigger can optionally reference one process.
- A trigger's process reference must target a process node.
- Multiple triggers can reference the same process or different processes.
- The name trigger is confirmed over signal on 2026-08-21, because it names what makes an outsider enter.
- Triggers are optional in a composition.

## Processes

- Processes are exact ways to do a task.
- A process can use constants.
- A process can use schemas.
- A process can put constant values into schemas.
- A process can act on information inside the knowledge.
- A process reached through a trigger gives the ordered steps for that entry.
- Processes do not have to be referenced by triggers.

## Input

- Input is the contract for what the knowledge expects to receive.
- Input is defined before the knowledge is used.

## Outputs

- One knowledge tree can emit many output representations.
- The main outputs are Pydantic v2, OAK, JSON-LD, YAML-LD, a file system representation, relational tables in SQL, and CSV files placed in the file system.
- Pydantic v2 is the authoring form; JSON-LD, YAML-LD, and file system representation are interchangeable once built.
- Each projection defines what it preserves, what it loses, and how it orders content.

### OAK

- OAK is the default output.
- The text output is named OAK and is the default output, because it is the output an interpreter uses directly.
- The OAK output is prose structured text which optimises for disambiguation for AI Models.
- OAK renders from the authored tree with a variant and a style.
- These render choices do not change the authored tree or the vocabulary.
- OAK rendering uses variant and style outside the vocabulary, adding no node type or field.
- The default OAK rendering is xml and authored.
- The variants are xml and markdown.
- A variant changes syntax only.
- Each variant defines how it escapes its delimiters.
- A renderer claims APS compatibility only when the tree and text meet APS rules.

#### Arrangement

- The OAK output has seven sections in this order: instructions, constants, schemas, state, triggers, processes, input.
- The OAK output has one arrangement, the seven sections in APS order, because OAK is the next iteration of APS.
- OAK is the next iteration of APS; it keeps the APS section order and uses its own names.
- Each top-level section MUST appear at most once.
- Every section appears, empty when the composition has no node of its type.
- Each section holds the direct nodes of its type in authored order.
- Sections are siblings; no section nests inside another.
- An instruction or trigger renders as its sentence alone.
- A schema or process renders with an inner structure.
- The OAK output loses node ids.

#### XML

```yaml
oak_sections:
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

- The xml variant is well-formed XML.
- The xml variant uses OAK names and composition structure.
- APS is not the canonical xml variant, because APS requires a process section and a process target that OAK does not.

#### Markdown

- The markdown variant uses headings, lists, and fenced blocks.

#### Styles

- A style changes natural language wording only.
- Style is an output choice, not an interpretation instruction, because one tree must render in many styles.
- The authored style preserves the authored wording.
- A controlled style is a named and versioned renderer profile.
- A controlled style rewrites only instruction bodies, trigger text, and process steps.
- A controlled style preserves meaning, obligation, negation, conditions, and step order.
- A renderer fails when it cannot validate a requested controlled style.
- An ASD-STE100 style names its governing edition and validation rules.

```yaml
numbers_units_time:
  numbers:
    decimals: "."
    thousands: "U+2009 (thin space)"

  units:
    format: "<number><space><unit>"
    percent: "50 %"
    temperature: "60 °C"
    symbols: middle_dot_between_compounds # U+00B7
    catalog: units.json (project)

  time:
    iso8601: true
    default_tz: "Z"
    local_times_require_offset_or_iana: true
```

```yaml
sentence_limits:
  procedures: 20
  descriptions: 25

paragraph_limits:
  sentences_max: 6
  one_topic: true

lists:
  steps_numbered: true
  supportive_bullets: true
```

### Pydantic

- Pydantic v2 is the description language for the vocabulary.
- Pydantic v2 is the authoring tool, and every other representation derives from the authored tree.

### JSON-LD

### YAML-LD

### File system

### SQL

### CSV

### EBNF

- OAK when authoring the build of OAK emits a EBNF grammar for OAK itself, which is a meta-grammar for OAK.

---

## Build

The tree below is a representation of the build as the PRD above is written; it evolves with every line above it.

```text
oak
  .agent  skills the agent reads, not PRD driven
  .gitignore
  AGENTS.md  repository rules
  CLAUDE.md  pointer to AGENTS.md
  docs  ground truth
    PRD.md
    types.md  Pydantic types the core schema validates
  examples  executable compositions, they validate the build
    agent.py
    sop.py
    static.py
  legacy-snapshot-aps  APS reference, read only
  oak  the package
    __init__.py  authoring and output API
    models.py  shared config, references, the seven node models, one discriminated union
    composition.py  composition model and root graph checks
    outputs  one module per output
      __init__.py  output selection, defaults to OAK xml authored
      oak.py  xml and markdown variants, styles
      pydantic.py
      json_ld.py
      yaml_ld.py
      filesystem.py
      sql.py
      csv.py
      ebnf.py  OAK meta-grammar
  pyproject.toml
```
