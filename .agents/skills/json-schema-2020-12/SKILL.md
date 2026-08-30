---
name: json-schema-2020-12
description: "Design, generate, validate, compose, debug, and evolve portable JSON Schema Draft 2020-12 contracts."
license: MIT
version: "1.0.0"
metadata:
  author: "OpenAI"
  spec_version: "1.0"
  framework_revision: "1.2.2"
  last_updated: "2026-08-05"
  standard: "JSON Schema Draft 2020-12"
  python: ">=3.10"
---

# JSON Schema Draft 2020-12

Use this skill to author and review JSON Schema Draft 2020-12 contracts, resolve references without implicit network access, validate schemas and instances, compose extensible records, generate schemas from Pydantic v2, and project bounded schema fragments into OpenAPI 3.1. Read the numbered references for rules, use the guides for task procedures, run the APS processes for repeatable workflows, and execute the included scripts and fixtures before accepting a contract change.

## References

1. [00 Source manifest](references/00-source-manifest.md)
2. [01 Core and vocabularies](references/01-core-and-vocabularies.md)
3. [02 Identifiers and references](references/02-identifiers-and-references.md)
4. [03 Validation keywords](references/03-validation-keywords.md)
5. [04 Composition and extension](references/04-composition-and-extension.md)
6. [05 Pydantic v2 integration](references/05-pydantic-v2-integration.md)
7. [06 OpenAPI 3.1 interoperability](references/06-openapi-3-1-interoperability.md)
8. [07 Validation and diagnostics](references/07-validation-and-diagnostics.md)
9. [08 Error catalog](references/08-error-catalog.md)

## Skill layout

- `SKILL.md` - this skill entrypoint.
- `references/` - normative technical guidance and source provenance.
- `guides/` - concise procedures for common authoring and debugging tasks.
- `processes/` - APS workflows for generation, validation, and change review.
- `examples/` - runnable base, extension, recursive, invalid, and Pydantic fixtures.
- `scripts/` - deterministic offline validation and reference-checking tools.
- `tests/` - executable acceptance tests for all included claims.
- `assets/` - reserved APS constants and output-format assets.
- `requirements.txt` - verified Python dependency baseline.
- `BUILD_REPORT.md` - build decisions, verification evidence, and known limits.
- `SHA256SUMS.txt` - hashes for the skill files, excluding the manifest itself.
