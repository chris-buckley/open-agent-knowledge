# OAK Product Requirements

A reference sketch of the vocabulary as Pydantic v2 models is in [vocabulary_sketch.py](vocabulary_sketch.py).

## Purpose

- OAK is Open Agent Knowledge.
- OAK is a knowledge standard.
- OAK gives one standard vocabulary for knowledge.
- OAK defines the smallest nodes of knowledge in a schema.
- Nodes compose into larger structures.
- OAK tells the interpreter how to interpret the knowledge before the interpreter uses it.

### Representations

- One or many nodes can represent (agent|SOP|static information|project|operating system|knowledge base|library|encoded file system|conversation).

## Principles

1. Reduce, reduce, reduce: less is more.
2. Find the common denominator in each part of the tree.
3. Identify it, recognize it, and implement only it.
4. Do not repeat yourself.
5. Write the smallest amount of code that represents a vast amount of knowledge.
6. OAK has no comments: the knowledge documents itself, self-(describes|explains|documents)

## Constraints

1. Define one thing once.
2. Build every structure as a tree of nodes.
3. Leaves in the tree can reference each other.
4. The tree can represent an enormous range of knowledge types from the foundational vocabulary.
5. Each vocabulary element is mandatory or optional.
6. The vocabulary stays very small.
7. The vocabulary holds only the node types this PRD lists.
8. Pydantic v2 models describe the whole vocabulary.

## Outputs

- One knowledge tree can emit many output representations.
- The main outputs are Pydantic v2, OAK, JSON-LD, YAML-LD, a file system representation, relational tables in SQL, and CSV files placed in the file system.
- The file system representation is its own output, separate from CSV files placed in the file system.
- OAK generates an EBNF grammar of the OAK output as an output.
- Pydantic v2 is the driver.
- Pydantic v2 is the authoring form; JSON-LD, YAML-LD, and the file system representation are interchangeable once built.
- OAK is the default output.
- The OAK output is text.
- Each projection defines what it preserves, what it loses, and how it orders content.
- OAK renders from the authored tree with a variant and a style.
- These render choices do not change the authored tree or the vocabulary.
- The default OAK rendering is xml and authored.
- The OAK output has seven sections in this order: instructions, constants, schemas, state, triggers, processes, input.

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

- Each top-level section MUST appear at most once.
- Every section appears, empty when the composition has no node of its type.
- Each section holds the direct nodes of its type in authored order.
- Instructions that interpretation references render first in the instructions section.
- Sections are siblings; no section nests inside another.
- The variants are xml and markdown.
- A variant changes syntax only.
- The xml variant is well-formed XML.
- The markdown variant uses headings, lists, and fenced blocks.
- An instruction or trigger renders as its sentence alone.
- A schema or process renders with an inner structure.
- The OAK output loses node ids.
- Each variant defines how it escapes its delimiters.
- A style changes natural language wording only.
- The authored style preserves the authored wording.
- A controlled style is a named and versioned renderer profile.
- A controlled style rewrites only instruction bodies, trigger text, and process steps.
- A controlled style preserves meaning, obligation, negation, conditions, and step order.
- A renderer fails when it cannot validate a requested controlled style.

## Node types

The set of node types is closed.

### Instructions

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

### Constants

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

### Schemas

- Schemas are defined structures.
- Schemas include schemas, templates, and formats.

### State

- State holds values that change while the interpreter uses the knowledge.

### Triggers

- Triggers route intent to the knowledge.
- A trigger records why the interpreter enters the knowledge.
- A trigger can reference one process to follow when it matches.
- A trigger without a process remains a signpost.
- A trigger separates use with intent from use by discovery.
- A trigger is the knowledge's signpost to the outside.
- Anything searching or routing reads triggers before it enters the knowledge.
- A trigger signposts the composition that holds it.
- Triggers are optional.

### Processes

- Processes are exact ways to do a task.
- A process can use constants.
- A process can use schemas.
- A process can put constant values into schemas.
- A process can act on information inside the knowledge.

### Input

- Input is the contract for what the knowledge expects to receive.
- Input is defined before the knowledge is used.

## Vocabulary

### Numbers, units, and time

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

### Sentence, paragraph, and list limits

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

## Decisions

- The name is OAK, short for Open Agent Knowledge.
- The name changed from UAOC, Universal Agent Operating Context, to OAK on 2026-08-21, because knowledge is broader than an operating context.
- OAK is a knowledge standard, not an information standard, because knowledge covers static information and executable instructions.
- The set of node types is closed.
- The node types are instructions, constants, schemas, state, triggers, processes, and input.
- OAK is the next iteration of APS; it keeps the APS section order and uses its own names.
- Interpretation rules belong to instructions, because they govern every entry.
- A process reached through a trigger gives the ordered steps for that entry.
- A composition's interpretation instructions apply before a process reached through a trigger.
- A trigger can reference one process, and the reference must target a process node.
- Processes do not have to be referenced by triggers.
- Multiple triggers can reference the same process or different processes.
- The consumer of the knowledge is named the interpreter, confirmed over actor on 2026-08-21.
- The name trigger is confirmed over signal on 2026-08-21, because it names what makes an outsider enter.
- The unit of the vocabulary is named the node.
- A structure is a tree of nodes, and leaves can reference each other.
- Triggers are optional in a composition.
- Pydantic v2 is the description language for the vocabulary.
- The text output is named OAK and is the default output, because it is the output an interpreter uses directly.
- Pydantic v2 is the authoring tool, and every other representation derives from the authored tree.
- Knowledge is authored as a nested tree, because nesting gives one root, one parent, and no containment cycle structurally.
- The flat node registry is derived from the tree during validation, not authored.
- Each node has exactly one type from the closed set, so every node validates at authoring time.
- Cross-references use typed fields, not a generic link field.
- Node IDs are absolute IRI-shaped strings, independent of file placement.
- Root validation rejects duplicate IDs, missing reference targets, and wrong target types.
- Constants and state hold any JSON value.
- Validation is strict: no type coercion and no unknown fields.
- Composition is structure, not an eighth node type.
- OAK rendering uses variant and style outside the vocabulary, adding no node type or field.
- The OAK output has one arrangement, the seven sections in APS order, because OAK is the next iteration of APS.
- Style is an output choice, not an interpretation instruction, because one tree must render in many styles.
- An ASD-STE100 style names its governing edition and validation rules.
- The xml variant uses OAK names and composition structure.
- APS is not the canonical xml variant, because APS requires a process section and a process target that OAK does not.
- A renderer claims APS compatibility only when the tree and text meet APS rules.
- The PRD uses one short sentence per idea.

## Open questions

- What fields does every node share? Deferred on 2026-08-21 while the user reviews the PRD. The title field is out of the sketch until this is decided.
- How does OAK resolve two triggers that match one arrival? Deferred on 2026-08-21 until trigger execution is defined.
