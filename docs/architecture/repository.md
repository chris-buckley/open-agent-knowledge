# OAK repository architecture

This document owns implementation boundaries, source ownership, dependency direction, build flow, examples, and generated outputs.

## Repository map

```text
open-agent-knowledge/
├── AGENTS.md
├── docs/
│   ├── architecture/
│   ├── guides/
│   └── plans/
├── oak/
│   ├── node/
│   ├── vocabulary/
│   ├── surface/
│   ├── parse/
│   ├── render/
│   ├── resolve/
│   ├── execute/
│   └── rules/
├── build/
│   └── checks/
├── examples/
├── outputs/
└── pyproject.toml
```

## Source ownership

| Concern | Source owner |
|---|---|
| Product purpose and architecture | `docs/architecture` |
| Practical authoring method | `docs/guides/authoring.md` |
| Repository work rules and reading routes | `AGENTS.md` |
| Models and same-document meaning | `oak/node` |
| Text shapes, datatypes, units, and display | `oak/vocabulary` |
| Authored syntax variants | `oak/surface` |
| OAK text parsing | `oak/parse` |
| OAK and JSON-LD rendering | `oak/render` |
| Document graph loading and checks | `oak/resolve` |
| Runtime execution | `oak/execute` |
| Stable authoring and validation rules | `oak/rules` |
| Output generation and freshness | `build` |
| Executable use cases | `examples` |
| Generated reference | `outputs` |
| Change history | `docs/plans` |

The root `AGENTS.md` is the only documentation index and router.

No generated output defines source behaviour. No completed plan defines current architecture.

## Package boundaries

`oak/node` depends on the base model, vocabulary, and rule definitions. It does not depend on parsing, rendering, resolution, or execution.

`oak/vocabulary` does not depend on node models.

Parsing and rendering are separate. The parser does not import a renderer, and renderers do not import the parser.

Resolution can use parsing and node contracts. It does not depend on execution.

Execution uses resolved node meaning and runtime handlers. Node models do not depend on execution.

The package root exposes the supported public API through explicit literal exports.

## Build flow

```text
package sources
     |
     +-- build/ebnf.py ------> outputs/oak.ebnf
     +-- build/docs.py ------> outputs/docs/*.md
     +-- build/authoring.py -> outputs/authoring.md
     +-- examples/*.py -----> sibling *.oak.md
     |
     v
build/checks verify source and generated products
```

The build generates outputs once. A render converts one node into a representation during normal use.

## Examples

Each example is authored through the package and writes one canonical sibling OAK document.

Examples exercise working product paths, including parsing, rendering, resolution, execution, constraints, tools, loops, parallel work, interfaces, and schema-bound values.

Examples are executable verification, not alternative architecture documents.

## Generated outputs

- `outputs/authoring.md` is a compact OAK prompt that instructs an interpreter to author one valid OAK document.
- `outputs/oak.ebnf` is the generated grammar.
- `outputs/docs` contains one generated OAK reference document per authorable model.

Generated paths and contents must equal a fresh build. Stale pages are removed during generation.

## Verification

`python -m build.examples` is the complete repository verification entry point.

It checks:

- vocabulary and model examples;
- metadata and surface coverage;
- local and resolved contracts;
- execution behaviour;
- OAK and JSON-LD rendering;
- parsing and canonical round trips;
- controlled style behaviour;
- human example snapshots;
- generated output freshness;
- dependency direction and obsolete paths;
- documentation routing and current authority.

## Change discipline

When a change alters architecture, update the owning architecture document and implementation together.

When a change alters exact types or syntax, update the source model, vocabulary, or surface first, then regenerate outputs.

When a change invalidates examples, update and run them in the same task.

When a path or contract becomes obsolete, remove every current use. Do not leave compatibility paths unless the accepted architecture names an exact consumer.
