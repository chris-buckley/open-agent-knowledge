# OAK architecture overview

Read this document before every repository task.

## Purpose

Open Agent Knowledge (OAK) is a portable standard for expressing knowledge as one compact validated unit.

OAK gives instructions, fixed values, information shapes, persistent state, outside routing, ordered work, and boundary crossings consistent names and locations.

A human can read OAK. An interpreter can validate it, connect it to other OAK documents, render it, and execute it when it contains behaviour.

OAK succeeds the Agnostic Prompt Standard. APS remains legacy reference only.

## System boundary

OAK owns knowledge and its internal contracts.

OAK owns:

- the node and its seven parts;
- typed references between entries;
- reusable information shapes;
- routing from outside occurrences to processes;
- process-local binding scope;
- persistent state semantics;
- validated emissions;
- document graph composition;
- canonical representations.

The host owns:

- model selection;
- credentials;
- network transport;
- tool implementations;
- server configuration;
- external persistence;
- scheduling and delivery;
- external side effects.

OAK can name an exact tool contract. It does not embed the tool implementation or transport.

## Architectural concerns

OAK is implemented as cooperating concerns with one direction of meaning:

```text
vocabulary and surfaces
          |
          v
canonical node model
     |          |
     v          v
 parsing     rendering
     |          |
     +----+-----+
          |
          v
 document graph resolution
          |
          v
 execution
```

- The node is the canonical in-memory meaning.
- The vocabulary defines reusable text and value forms.
- Surface descriptors connect model fields to authored OAK syntax.
- The parser converts OAK text into a node.
- Renderers convert a node into OAK text or JSON-LD.
- The resolver loads and validates reachable document targets.
- The executor runs one arrival against one resolved graph.

## Core invariants

- One OAK document contains exactly one node.
- A node has no id and contains no node.
- A node has seven closed parts in one fixed order.
- Every entry belongs to one part and has one document-wide unique id.
- Schemas define information shapes without owning boundary flow or process routing.
- Constants are fixed during use.
- State persists across arrivals and changes only through process execution.
- Process bindings are immutable and local to one invocation scope.
- Interfaces are one-way crossings of complete schema instances.
- Triggers are the only outside entry to process execution.
- Processes own internal ordered work.
- State and interface operations stay in the active document.
- Relative references are explicit and resolve through a caller-supplied loader.
- Validation is strict and does not coerce authored values.
- OAK text has one canonical byte-stable form for each grouping and style.
- State writes and emissions commit only after successful top-level completion.
- External tool effects are not rolled back by OAK.

## Knowledge lifecycle

```text
source knowledge
      |
      v
author one Node
      |
      v
validate local structure and contracts
      |
      v
resolve reachable document targets when supplied
      |
      +----------------------+
      |                      |
      v                      v
render OAK or JSON-LD    execute one arrival
                              |
                              v
                    commit state and emissions
```

A document can contain only static knowledge. It can also contain a state machine. Interfaces and triggers are optional.

## Reading routes

- Read [document.md](document.md) for node and part semantics.
- Read [graph.md](graph.md) for composition and target resolution.
- Read [validation.md](validation.md) for check ownership and failures.
- Read [execution.md](execution.md) for runtime behaviour.
- Read [representation.md](representation.md) for authored and rendered forms.
- Read [repository.md](repository.md) for implementation ownership and build flow.
- Read [../guides/authoring.md](../guides/authoring.md) for practical authoring.
