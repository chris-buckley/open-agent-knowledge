# OAK execution architecture

This document owns one execution cycle, process scope, tools, state, emissions, and transaction behaviour.

## Execution input

The executor receives:

- one root node or resolved document graph;
- one arrival;
- one complete state mapping;
- an optional interpreter-native action handler;
- an exact tool registry.

The caller state mapping is not mutated.

## Arrival forms

One arrival is exactly one of:

```text
event text
receive interface plus complete values
```

An event arrival carries no values.

A receive arrival names one local `RECEIVES` interface and supplies one complete instance of its resolved schema.

The executor validates state and the arrival before trigger selection.

## Trigger selection

```text
arrival
  |
  +-- event -> source-less trigger with exact event text
  |
  +-- receive -> source-backed trigger with exact interface target
  |
  v
evaluate matching guards against state
  |
  +-- zero matches -> return without a process or emission
  +-- one match -> run its process
  +-- many matches -> fail as ambiguous
```

A source-backed trigger uses its event text as a semantic signpost. Machine selection uses the interface source, not the event text.

A guard runs after the event or source matches. Condition trees evaluate in authored order with short-circuiting.

## Initial process input

An event-backed trigger resolves its explicit seeds from literals, constants, and state.

A source-backed trigger uses the validated receive instance as the complete selected process input.

The executor validates the complete process input schema before creating the process frame.

## Process frames

A process frame contains immutable local bindings.

Input schema placeholders seed the first frame. Each action or call output becomes a new binding after validation.

A child branch, loop iteration, or called process receives a child scope. Child-only bindings do not leak into the parent unless a call explicitly promotes declared outputs.

State and staged emissions remain shared across called processes in one top-level transaction.

## Step execution

Steps run in authored order.

### ACT

Plain `ACT` delegates the instruction to the interpreter-native action handler.

`ACT TOOL` selects one exact tool registry entry. The supplied tool contract must match the authored placeholders, schemas, and parallel capability.

Action inputs validate before invocation. Returned outputs must match the declared names exactly and validate before they become bindings.

### SET

`SET` writes one local state target. The value validates through the state schema binding when one exists.

The write is staged and visible to later steps in the transaction.

### CALL

`CALL` invokes one local or resolved process synchronously.

The called process receives a fresh frame with validated call inputs. Its declared validated outputs are promoted into the caller frame in authored order.

`CALL` composes work inside one interpreter. It does not dispatch another agent.

### EMIT

`EMIT` targets one local `EMITS` interface.

An explicit emit maps each schema placeholder to one process value.

An inferred emit reads same-named visible bindings in interface schema order.

The complete instance validates before it is staged.

### Conditions and branches

Comparisons use strict JSON equality. Ordered comparison accepts two numbers or two strings. Booleans are not numbers.

`ALL`, `ANY`, and `NOT` form recursive condition trees.

`IF` executes only one branch. `ASSERT` fails a false condition. `FAIL` stops execution with its message.

### Iteration

`FOREACH` iterates one JSON list in index order. Each iteration has a fresh child scope.

`WHILE` tests before each iteration and has a positive hard limit. It fails when the condition remains true after the limit.

Staged state and emissions remain visible to later while iterations.

### Parallel work

`PAR` contains only exact named-tool actions.

The executor resolves and validates every child input before it launches any child. Each child receives the same immutable binding snapshot.

Outputs remain pending and invisible until the immediately following `JOIN`.

`JOIN` waits for all children. It promotes successful outputs in authored child order. If one child fails, no parallel output is promoted.

## Transaction

```text
start cycle
    |
    v
stage state writes and emissions
    |
    +-- any failure -> discard both
    |
    +-- success -> validate process output, then commit both
```

External tool effects are outside this transaction and cannot be rolled back by OAK.

## Execution result

A successful cycle returns:

- the selected process target or no selection;
- the committed complete state mapping;
- ordered committed emissions.

Processes can run without interfaces or triggers when the host invokes them through another controlled entry point. The standard cycle enters process work through triggers.
