# OAK Product Requirements

A reference sketch of the vocabulary as Pydantic v2 models is in [vocabulary_sketch.py](vocabulary_sketch.py).

## Purpose

- OAK is Open Agent Knowledge.
- OAK is a knowledge standard.
- OAK gives one standard vocabulary for knowledge.
- OAK defines the smallest nodes of knowledge in a schema.
- Nodes compose into larger structures.
- A composition of nodes can represent an agent.
- A composition of nodes can represent an SOP.
- A composition of nodes can represent static information.
- OAK tells the interpreter how to interpret the knowledge before the interpreter uses it.

## Principles

- Reduce, reduce, reduce: less is more.
- Find the common denominator in each part of the tree.
- Identify it, recognize it, and implement only it.
- Do not repeat yourself.
- Write the smallest amount of code that represents a vast amount of knowledge.

## Constraints

- Define one thing once.
- Build every structure as a tree of nodes.
- Leaves in the tree can reference each other.
- The tree can represent an enormous range of knowledge types from the foundational vocabulary.
- Each vocabulary element is mandatory or optional.
- The vocabulary stays very small.
- The vocabulary holds only the node types this PRD lists.
- Pydantic v2 models describe the whole vocabulary.

## Outputs

- One knowledge tree can emit many output representations.
- The main outputs are Pydantic v2, JSON-LD, YAML-LD, a file system representation, relational tables in SQL, and CSV files placed in the file system.
- The file system representation is its own output, separate from CSV files placed in the file system.
- Pydantic v2 is the driver and is implemented first.
- JSON-LD is implemented after the driver.
- YAML-LD is implemented after JSON-LD.
- The remaining outputs are implemented after YAML-LD.

## Node types

The set of node types is closed.

### Instructions

- Instructions are rules the interpreter of the knowledge must follow.
- Instructions include interpretation rules.
- Instructions include rule following.
- Instructions include methods for how to go about something.
- Instructions include safety measures.
- Instructions include policy.

### Constants

- Constants are values that stay the same in every use of the knowledge.

### Schemas

- Schemas are defined structures.
- Schemas include schemas, templates, and formats.

### Triggers

- Triggers route intent to the knowledge.
- A trigger records why the interpreter looks at the knowledge.
- A trigger separates use with intent from use by discovery.
- Triggers are optional.

### State

- State holds values that change while the interpreter uses the knowledge.

### Processes

- Processes are exact ways to do a task.
- A process can use constants.
- A process can use schemas.
- A process can put constant values into schemas.
- A process can act on information inside the knowledge.

### Input

- Input is the contract for what the knowledge expects to receive.
- Input is defined before the knowledge is used.

## Decisions

- The name is OAK, short for Open Agent Knowledge.
- The name changed from UAOC, Universal Agent Operating Context, to OAK on 2026-08-21, because knowledge is broader than an operating context.
- OAK is a knowledge standard, not an information standard, because knowledge covers static information and executable instructions.
- The set of node types is closed.
- The node types are instructions, constants, schemas, triggers, state, processes, and input.
- Interpretation belongs to the instructions node type, because it is a rule for how to interpret the knowledge.
- The consumer of the knowledge is named the interpreter.
- The unit of the vocabulary is named the node.
- A structure is a tree of nodes, and leaves can reference each other.
- Triggers are optional in a composition.
- Pydantic v2 is the description language for the vocabulary.
- The output order is Pydantic v2 as the driver, then JSON-LD, then YAML-LD.
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
- The PRD uses one short sentence per idea.

## Open questions

- What fields does every node share? Deferred on 2026-08-21 while the user reviews the PRD. The title field is out of the sketch until this is decided.
