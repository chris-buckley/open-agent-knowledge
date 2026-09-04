# OAK validation architecture

This document owns validation boundaries, check placement, and the failure contract.

## Principle

Validate each rule at the earliest boundary that has all required information.

Do not duplicate one check at several layers unless runtime data requires a second check.

OAK validation is strict. It rejects unknown fields and does not coerce authored values into another type.

## Validation layers

```text
1. Core model validation
2. Node validation
3. Document graph resolution
4. Runtime validation
```

### Core model validation

Pydantic models own one value or object shape.

This layer checks matters such as:

- literals and discriminated unions;
- required and optional fields;
- string shapes;
- non-empty lists;
- numeric bounds;
- schema template and local constraint coherence;
- default values;
- unknown fields.

### Node validation

Node validation owns relationships between entries in one document.

This layer checks matters such as:

- document-wide unique entry ids;
- local target existence and target type;
- trigger, process, action, call, and emit contracts;
- process binding visibility and redefinition;
- branch reachability;
- local process call cycles;
- interface flow use;
- local state and interface scope;
- statically knowable schema bindings.

### Document graph resolution

The resolver owns relationships that need another document.

This layer checks matters such as:

- exact document availability;
- fragment existence and type;
- resolved schema identity;
- cross-document process cycles;
- relative schema constraints;
- relative call and action contracts.

Local validation does not guess the result of a relative reference.

### Runtime validation

The executor owns values supplied or produced during one cycle.

This layer checks matters such as:

- caller state values;
- arrival shape and payload;
- trigger ambiguity;
- process inputs and outputs;
- action and tool results;
- loop conditions and limits;
- emitted schema instances;
- supplied tool contracts.

## Check ownership

| Rule kind | Owner |
|---|---|
| One text or value shape | `oak/vocabulary` or one model field |
| One model structure | Pydantic model |
| Same-document relationship | `oak/node/validation` |
| Cross-document relationship | `oak/resolve` |
| Supplied or produced runtime value | `oak/execute` |
| Stable authored rule text and code | `oak/rules` |
| Repository freshness | `build/checks` |

## Schema validation

A schema validates complete values in JSON form.

Datatype checks run before dependent constraints. Placeholder-valued bounds resolve within the same schema instance.

A constant or state binding validates its selected placeholder. A process, action, call, interface, arrival, or emission validates the complete schema instance at its boundary.

## Process scope validation

Each process input placeholder begins as a visible local binding.

A step can read only bindings visible before that step. A new binding cannot redefine a visible immutable binding.

Branch and loop child bindings stay in their child scope. Parallel outputs remain unavailable until `JOIN` promotes them.

Inferred emission is valid only when every target schema placeholder is visible at that exact step.

## Trigger validation

Event-backed triggers must provide exactly the selected process input through seeds.

Source-backed triggers have no seeds. Their receive interface and selected process input must resolve to the same schema entry.

A non-true guard reads state and never reads process bindings.

Triggers with the same event or source must have guards that the validator can prove disjoint. Unproved overlap is rejected.

## Failure contract

Parsing collects independent parse failures when possible and reports a stable code, path, optional line, and message.

Model and graph rules use stable rule codes. Runtime failures use `ExecutionError` with one code and message. Parallel execution can retain later child failures as suppressed diagnostics.

The exact code catalog belongs to `oak/rules`, parser errors, resolver errors, and execution code. Generated model pages under `outputs/docs` provide reference views.

## Repository verification

`python -m build.examples` runs the executable examples, model metadata checks, parser and renderer round trips, resolution and execution checks, generated output freshness, and repository architecture checks.
