# Pydantic v2 example

[`model.py`](model.py) defines strict Pydantic v2 models for the retail lending example.

It demonstrates:

- `BaseModel.model_json_schema()`;
- `TypeAdapter.json_schema()` for the node union;
- `$defs` and a local reference template;
- external aliases for the JSON field `from`;
- tagged unions with `Field(discriminator="kind")`;
- recursive `ContainerNode` rebuilding;
- `json_schema_extra` for `$schema` and `$id`;
- explicit validation and serialization schema modes.

[`generated.schema.json`](generated.schema.json) is the committed validation-mode result for the complete model. [`node.generated.schema.json`](node.generated.schema.json) is the TypeAdapter result for the node union.

Regenerate deterministically:

```bash
python examples/pydantic/model.py generate /tmp/generated.schema.json --mode validation
python examples/pydantic/model.py generate-node /tmp/node.schema.json
```

The Pydantic schema corresponds to the hand-authored model but is intentionally not byte-for-byte identical. The hand-authored schema demonstrates parent composition and extension behavior that the Pydantic model does not generate automatically.
