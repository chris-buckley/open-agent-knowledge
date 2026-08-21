# UAOC Product Requirements

A reference sketch of the vocabulary as Pydantic v2 models is in [vocabulary_sketch.py](vocabulary_sketch.py).

## Purpose

- UAOC is the Universal Agent Operating Context.
- UAOC is a knowledge standard.
- UAOC gives one standard vocabulary for knowledge.
- UAOC defines the smallest building blocks of knowledge in a schema.
- Blocks compose into larger structures.
- A composition of blocks can represent an agent.
- A composition of blocks can represent an SOP.
- A composition of blocks can represent static information.
- UAOC tells the interpreter how to interpret the knowledge before the interpreter uses it.

## Constraints

- Define one thing once.
- Build every structure as a tree of nodes.
- Leaves in the tree can reference each other.
- The tree can represent an enormous range of knowledge types from the foundational vocabulary.
- Each vocabulary element is mandatory or optional.
- The vocabulary stays very small.
- The vocabulary holds only the block types this PRD lists.
- Pydantic v2 models describe the whole vocabulary.

## Block types

The set of block types is closed.

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

- The name is UAOC, short for Universal Agent Operating Context.
- UAOC is a knowledge standard, not an information standard, because knowledge covers static information and executable instructions.
- The set of block types is closed.
- The block types are instructions, constants, schemas, triggers, state, processes, and input.
- Interpretation belongs to the instructions block type.
- The consumer of the knowledge is named the interpreter.
- The unit of the vocabulary is named the node.
- A structure is a tree of nodes, and leaves can reference each other.
- Triggers are optional in a composition.
- Pydantic v2 is the description language for the vocabulary.
- The PRD uses one short sentence per idea.

## Open questions

- What fields does every block share? Deferred on 2026-08-21 because Chris reads the PRD first.
