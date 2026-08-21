---
name: json-ld
description: "Design, process, validate, secure, and integrate JSON-LD 1.1 graphs with typed Pydantic v2 application models."
license: MIT
version: "1.0.0"
metadata:
  author: "Christopher Buckley"
  spec_version: "1.0"
  framework_revision: "1.2.2"
  last_updated: "2026-08-05"
---

# JSON-LD

Use this skill to assign durable identities and typed relationships to JSON data, process JSON-LD 1.1 through governed contexts, frame graph data into stable application profiles, validate those profiles with Pydantic v2 and JSON Schema, and diagnose graph or security failures. Start with the mental model and context rules, use PyLD 3.1.0 as the default processor, keep remote loading offline and allowlisted, and use the bundled profile engine only for the included examples and smoke tests.

## References

1. [00 Source manifest](references/00-source-manifest.md)
2. [01 Data model, forms, identity, and relationships](references/01-data-model.md)
3. [02 Contexts](references/02-contexts.md)
4. [03 Keywords, object forms, and containers](references/03-keywords-and-object-forms.md)
5. [04 Processing algorithms](references/04-processing-algorithms.md)
6. [05 Framing and application profiles](references/05-framing.md)
7. [06 Pydantic v2 integration](references/06-pydantic-v2-integration.md)
8. [07 JSON Schema and RDF boundaries](references/07-json-schema-and-rdf-boundaries.md)
9. [08 Security and deterministic processing](references/08-security.md)
10. [09 Error catalog](references/09-error-catalog.md)
11. [10 Processor evaluation](references/10-processor-evaluation.md)
12. [11 Conformance and verification](references/11-conformance.md)

## Skill layout

- `SKILL.md` - Skill entrypoint and reference map.
- `references/` - Numbered standards, architecture, integration, security, and diagnostic authority.
- `guides/` - Task-focused procedures for context, identity, relationship, profile, and debugging work.
- `processes/` - APS workflows for ingesting, emitting, updating, and testing JSON-LD.
- `examples/` - Complete compact, expanded, flattened, framed, RDF, Pydantic, container, and invalid examples.
- `scripts/` - Safe command-line processors, graph checks, semantic comparison, and suite runner.
- `tests/` - Executable tests for examples, safety controls, models, schemas, CLIs, and packaging.
- `assets/` - Reusable APS constants and output format contracts.
- `build-report.md` - Sources, processor decision, tests, limitations, and conflicts.
- `SHA256SUMS` - SHA-256 manifest for delivered files.
