# OAK document graph architecture

This document owns document identity, target paths, explicit loading, resolution, and cross-document scope.

## Composition

An OAK document graph is a set of OAK documents connected by typed target paths.

Composition is not an eighth node part. Each document remains one complete node with its own state and interfaces.

## Target paths

A local target names one entry in the active document:

```text
schema.request
process.review-request
state.review-status
interface.request
```

A relative target names one entry in another OAK document:

```text
workers/reviewer.oak.md#schema.review-request
```

The authored relative path is preserved for rendering and diagnostics.

## Allowed relative references

Schemas, constants, and processes can be referenced through relative document paths.

State reads, state writes, receive sources, and emissions stay in the active document.

This rule prevents one document from silently mutating another document or using another document as a shared boundary channel.

## Local validation and resolution

Local validation checks one node without loading other files.

A relative target is structurally valid during local validation when its path and required part are valid.

Explicit resolution checks the reachable graph when the caller supplies:

- the root document path;
- a document loader;
- the root node.

The resolver does not scan directories, guess filenames, use the working directory as a registry, or fetch the network.

## Resolution process

```text
root document
    |
    v
index local entries
    |
    v
find relative targets
    |
    v
load each exact relative document
    |
    v
parse and validate loaded node
    |
    v
verify fragment entry and expected type
    |
    v
continue through newly reachable targets
```

A loaded document is identified by its normalized resolved path. The resolver retains the authored path for the reference that caused the load.

## Resolved identity

Two schema targets are the same contract only when they resolve to the same document and schema id.

Equal placeholder names or equal-looking templates do not establish identity.

This rule is important for receive interfaces, process inputs, calls, actions, constants, state, and tool contracts.

## Graph checks

Resolution verifies:

- every reachable document is available;
- every fragment target exists;
- each target has the part required by its typed field;
- schema-bound values satisfy resolved placeholders;
- cross-document process calls have no cycle;
- source-backed trigger schemas match selected process inputs by resolved identity;
- relative action, process, and interface contracts remain coherent.

## Cycles

Document references can form a graph. Process call cycles cannot.

The local validator rejects local process call cycles. The resolver rejects cycles that appear only after relative process targets load.

A process uses triggers, `FOREACH`, and bounded `WHILE` for repetition instead of recursive calls.

## Host boundary

The host chooses how document paths map to storage. OAK requires only an explicit deterministic loader.

The same graph can be loaded from a file system, package, database, or another controlled source without changing OAK target syntax.
