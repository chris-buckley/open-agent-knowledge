# OAK documentation

This directory explains the current OAK architecture and how to author OAK documents.

Start with [architecture/overview.md](architecture/overview.md). Then read the documents that match the work.

## Documentation map

```text
docs/
├── README.md
├── architecture/
│   ├── overview.md
│   ├── document.md
│   ├── graph.md
│   ├── validation.md
│   ├── execution.md
│   ├── representation.md
│   └── repository.md
├── guides/
│   └── authoring.md
└── plans/
    ├── 0000-plan.md
    ├── 0000-report.md
    ├── 0001-plan.md
    ├── 0001-report.md
    ├── 0002-plan.md
    └── 0002-report.md
```

## Architecture

- [Overview](architecture/overview.md) explains OAK, its boundary, its invariants, and its lifecycle.
- [Document](architecture/document.md) explains one node, the seven parts, value lifetimes, and cross-part dataflow.
- [Graph](architecture/graph.md) explains target paths, document loading, resolution, scope, and cycles.
- [Validation](architecture/validation.md) explains where each check belongs and how failures cross boundaries.
- [Execution](architecture/execution.md) explains arrivals, trigger selection, process frames, tools, state, and emissions.
- [Representation](architecture/representation.md) explains Pydantic, OAK text, surfaces, parsing, groupings, renders, JSON-LD, and EBNF.
- [Repository](architecture/repository.md) explains source ownership, package layout, build flow, examples, outputs, and dependency direction.

## Guides

- [Authoring OAK](guides/authoring.md) gives the practical knowledge-to-node method and one complete example.

## Authority

OAK has no single product requirements document.

Each architecture document owns the meaning, boundary, and responsibility of its named concern.

The package owns exact executable contracts:

| Exact concern | Owner |
|---|---|
| Models and fields | `oak/node` |
| Text shapes and datatypes | `oak/vocabulary` |
| Authored syntax variants | `oak/surface` |
| Parse behaviour | `oak/parse` |
| Render behaviour | `oak/render` |
| Cross-document resolution | `oak/resolve` |
| Runtime execution | `oak/execute` |
| Named authoring and validation rules | `oak/rules` |

Generated outputs are reference, not source authority:

- `outputs/authoring.md` is the generated authoring prompt.
- `outputs/oak.ebnf` is the generated grammar.
- `outputs/docs` is the generated model and surface reference.

Completed plans and reports record how the repository changed. They do not define current architecture.
