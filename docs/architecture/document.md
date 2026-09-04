# OAK document architecture

This document owns the architecture of one OAK document, its node, its parts, and its value lifetimes.

## Document and node

One OAK file is one document. One document contains exactly one node.

The document path identifies the node. The node has no id and cannot contain another node.

The node contains seven closed parts in this order:

```text
instructions
constants
schemas
state
triggers
processes
interfaces
```

An empty part is absent from the OAK render. Part order does not change.

Every entry has one id. Entry ids are unique across all parts in one document.

## Part responsibilities

| Part | Owns | Lifetime | Does not own |
|---|---|---|---|
| instructions | Rules the interpreter follows | Whole use of the document | Data shapes or step order |
| constants | Fixed JSON values | Whole use of the document | Mutable values |
| schemas | Reusable information shapes | Definition lifetime | Boundary flow or process routing |
| state | Persistent mutable JSON values | Across arrivals | Invocation-local results |
| triggers | Outside routing to one process | One arrival decision | Internal process sequencing |
| processes | Ordered local work | One invocation | Outside transport |
| interfaces | Complete schema instances crossing the boundary | One receive or emission | Information shape definitions |

## Instructions

Instructions state required interpretation, policy, method, or safety behaviour.

Each instruction is one directive. Generated interpretation instructions appear before authored instructions in the OAK render.

Instructions apply before a process reached through a trigger.

## Constants

A constant is fixed while the knowledge is used.

A constant can hold one inline JSON value or one text, JSON, CSV, or YAML block.

A constant can bind to one schema placeholder when its value needs a reusable constraint.

## Schemas

A schema defines one reusable information shape.

The template shows the complete shape and names variable slots as placeholders. Each distinct placeholder has one ordered constraint entry.

A schema can type:

- a constant or state value;
- a process input or output;
- an action input or output;
- an interface crossing;
- a tool contract.

A schema does not become an interface or process because it is reused there.

## State

State stores values that must survive one execution cycle.

State values can use the same schema-placeholder binding as constants.

A process stages state writes. Later steps in the same transaction can see staged values. A failed top-level execution discards them.

## Triggers

A trigger signposts knowledge to the outside and selects one process.

A trigger always has event meaning. It can also have one receive source and one state guard.

There are two routing forms:

```text
event arrival -> exact event trigger -> explicit process seeds
receive arrival -> exact interface source -> complete process input
```

A source-backed trigger receives one complete interface schema instance. Its selected process uses the same resolved input schema and has no seeds.

An event-backed trigger can use explicit literal, constant, or state seeds for the selected process input.

A trigger guard reads state only. The guard runs after the event or source matches.

## Processes

A process is one named ordered way to do a task.

A process can declare input and output schemas. Input placeholders become initial local bindings. Required output placeholders must be visible after successful completion.

Processes compose internal work with `CALL`. Calls are synchronous and use fresh local binding scopes inside the same state and emission transaction.

An action is either interpreter-native work or one exact named tool invocation.

A process can branch, assert, fail, iterate, run a bounded loop, run exact named-tool actions in parallel, update state, call another process, and emit a result.

## Interfaces

An interface is one identified one-way crossing at the active document boundary.

```text
request RECEIVES schema.request
result EMITS schema.result
```

A receive interface accepts one complete instance of its schema.

An emit interface publishes one complete instance of its schema.

A duplex relationship uses two interfaces. An interface description adds only boundary meaning that the id and schema do not already state.

## Value lifetimes

OAK keeps four value lifetimes separate:

| Value | Meaning | Scope |
|---|---|---|
| constant | Fixed knowledge | Whole use |
| state | Persistent mutable knowledge | Document across arrivals |
| process binding | Local immutable value | One process frame or child scope |
| interface instance | Complete boundary payload | One receive or emission occurrence |

An interface instance is not ambient process storage. A receive occurrence becomes process input bindings before the process runs.

## Cross-part dataflow

```text
schema -> constant constraint
schema -> state constraint
schema -> process contract
schema -> interface contract

receive interface -> trigger -> process input bindings
state -> trigger guard
process -> state write
process -> CALL -> process
process bindings -> emit interface
```

The part boundaries prevent fixed, persistent, local, and boundary values from becoming one ambiguous value pool.
