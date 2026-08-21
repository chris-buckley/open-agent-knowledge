# Build Info — Pydantic v2 Skill

## Pipeline

```csv
Phase,Status,Artifacts
1 — Discovery,Completed,"phase1-discovery/ (frontier, categorized-map, stats, raw-links)"
2 — Extraction,Completed,phase2-extraction/ (63 markdown files across 5 categories)
3 — Distillation,Completed,"phase3-distillation/ (10 topic directories, 19 files)"
4 — Assembly,Completed,phase4-assembly/SKILL.md + BUILD_INFO.md
```

## Source

- URL: https://docs.pydantic.dev/latest/
- Crawled: 200 pages (max-pages limit)
- Workers: 3 parallel browser sessions
- Exclude patterns: `blog`, `changelog`, `contributing`, `migration`, `version-policy`, `integrations`

## Categories Extracted

```csv
Category,Type,Pages,Notes
concepts,guide,19,Core documentation guides
api,reference,36,API reference pages
examples,example,6,Code examples
errors,guide,2,Error reference (validation + usage)
internals,reference,2,Architecture + annotation resolution
```

## Categories Excluded (versioned duplicates)

```csv
Category,Pages,Reason
dev,67,Version prefix duplicate of /latest/
2.12,8,Version prefix duplicate
"1.10, 2.0-2.11",1 each,Version landing pages
```

## Distillation Topics

```csv
Topic,Source Categories,distilled.md,pitfalls.md
models,"concepts, api",Yes,18 pitfalls
fields,"concepts, api",Yes,20 pitfalls
validators,"concepts, api",Yes,13 pitfalls
serialization,"concepts, api",Yes,17 pitfalls
types,"concepts, api",Yes,20 pitfalls
configuration,"concepts, api, settings",Yes,20 pitfalls
json-schema,"concepts, api",Yes,17 pitfalls
errors,errors,Yes,15 pitfalls
performance,"concepts, internals",Yes,12 pitfalls
api-reference,api (mechanical),Yes,—
```

Total pitfalls documented: 152

## Known Issues

1. Versioned URL duplication — Crawler consumed ~75 of 200 page budget on `/dev/` and versioned URL duplicates. Recommend `--url-prefix` flag for future crawls.
2. `_state.json` counters stale — Pipeline state file was not updated during agent-driven distillation phase. Actual artifact counts exceed what the state file reports.

## Build Date

2026-02-10
