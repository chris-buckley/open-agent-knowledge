# Debug JSON-LD

Use this guide to locate failures without confusing syntax, context, graph, schema, and application layers. Read [09 Error catalog](../references/09-error-catalog.md).

## Procedure

1. Record the source path, bytes, SHA-256, processor, options, base, context registry, and frame.
2. Parse UTF-8 JSON with duplicate-key rejection.
3. Check source size and nesting depth.
4. Resolve each remote context through the exact local registry.
5. Verify every context digest and media type.
6. Detect context cycles and illegal imports.
7. Expand the document and save the expanded result.
8. Inspect every application-relevant property as an absolute IRI.
9. Classify values as references, node definitions, value objects, lists, or graph objects.
10. Find relative IDs, blank nodes, and duplicate named nodes.
11. Flatten and build a node registry.
12. Expand the frame and compare its match IRIs with the graph.
13. Frame one explicit root.
14. Validate the framed source with JSON Schema.
15. Validate the source and canonical Pydantic models.
16. Run missing-target and duplicate-identity checks.
17. Compact and re-expand the corrected output.
18. Compare semantic form rather than compact text.

## Fast symptom map

| Symptom | Inspect first |
|---|---|
| Property disappeared | Expanded output and term definition |
| String became `@value` | Missing `@type: @id` coercion |
| Unexpected array | Expanded cardinality and frame |
| Empty frame | Expanded frame and source type IRIs |
| Duplicate typed record | Flattened node map and normalization rule |
| Missing target | Local and external node registries |
| Different output order | Ordered option and application sorting |
| Changed blank-node label | Identity policy and canonical RDF comparison |
| Remote load attempt | Document loader and context registry |
| Model error after valid JSON-LD | Application profile, not context processing |

## Useful commands

```bash
python scripts/expand.py INPUT --registry REGISTRY --engine pyld --raw
python scripts/flatten.py INPUT --registry REGISTRY --engine pyld --raw
python scripts/frame.py INPUT --frame FRAME --registry REGISTRY --engine pyld --raw
python scripts/inspect_graph.py INPUT --registry REGISTRY --engine pyld
python scripts/semantic_roundtrip.py INPUT --context CONTEXT --registry REGISTRY --engine pyld
```

Use `--engine profile` only when reproducing the bundled examples without PyLD.

A correction is complete only when the failing layer passes and downstream layers still pass.
