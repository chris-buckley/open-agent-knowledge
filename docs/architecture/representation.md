# OAK representation architecture

This document owns the relationship between the canonical model, authored text, parsing, rendering, groupings, styles, JSON-LD, and generated grammar.

## Canonical meaning

The `Node` model is the canonical in-memory meaning of one OAK document.

Pydantic is the programmatic authoring and validation form. It is not a render.

OAK text is the human and interpreter authoring form.

JSON-LD is the interchange render.

## Surface descriptors

Each concrete authored text variant has one surface descriptor.

A descriptor states:

- the model it represents;
- the authored shape;
- the model fields rendered by the shape;
- fixed, omitted, or generated fields;
- the condition that selects the variant.

The same descriptor registry drives:

```text
rendering
parsing
EBNF generation
authoring prompt generation
generated model reference
```

This prevents each consumer from inventing a separate syntax.

## OAK text

OAK text is structured prose optimized for interpreter disambiguation.

The seven parts render in fixed order. Entries retain authored order. Empty parts are omitted.

Natural-language text remains readable. Typed facts, targets, bindings, conditions, steps, and interface flows use closed canonical syntax.

The default render is OAK with XML grouping and authored style.

## Groupings

OAK supports XML-like tags and Markdown tilde fences.

A grouping changes delimiters only. It does not change the node or entry body meaning.

Schema and process entries use grouped body wrappers. Terse parts such as instructions, constants, state, trigger facts, and interfaces use their canonical line forms inside the part.

Interface part bodies are byte-identical between groupings.

## Parsing

The parser accepts UTF-8 bytes or text and normalizes line endings to LF.

It infers grouping from the first present part delimiter unless the caller supplies one.

The parser:

1. splits the fixed parts;
2. parses each part through its surface and vocabulary forms;
3. builds one `Node`;
4. runs model and node validation.

An empty document becomes one empty node. A missing part becomes an empty list.

## OAK rendering

The OAK renderer selects one surface for each model value and arranges non-empty parts.

Generated interpretation instructions appear only for features present in the node. Exact built-in lines are stripped when parsed so they do not become authored instructions.

The authored style preserves authored wording.

A controlled style can rewrite only permitted natural-language fields. It cannot change obligations, negation, conditions, contracts, targets, or step order.

The OAK render preserves all authored data except instruction ids, which are not present in OAK text.

## JSON-LD

JSON-LD renders one node under a caller-supplied absolute document IRI and vocabulary IRI.

Local entry targets become document fragments. Relative targets resolve against the document base.

Ordered OAK collections remain ordered JSON-LD lists. Literal JSON values use `@json`.

Context processing, structural validation, and graph target validation remain separate boundaries.

## EBNF

`outputs/oak.ebnf` is generated from the text vocabulary, surface descriptors, and fixed part order.

The grammar documents syntax. It is not the validator.

## Round-trip contract

For each canonical supported OAK form:

```text
Node -> OAK text -> Node -> OAK text
```

The final text must equal the first canonical text for the same grouping and style.

Generated checks also require each surface example, documentation page, and committed human example to round trip through the package.

## Exact reference

Use these generated outputs after reading the architecture:

- `outputs/oak.ebnf` for the exact grammar;
- `outputs/docs` for model and surface reference;
- `outputs/authoring.md` for the compact generated authoring prompt.
