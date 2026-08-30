# Examples

All canonical schema identifiers use `https://example.org/`. The examples resolve those identifiers through [`registry.json`](registry.json); they do not require the identifiers to be network locations.

## Model

```text
BaseSystem
|-- nodes
|-- relationships
`-- metadata

RetailLendingSystem
|-- satisfies BaseSystem
|-- adds lending-specific node kinds
`-- adds lending-specific relationship kinds
```

## Fixture map

| Area | Schema or code | Claimed result |
| --- | --- | --- |
| Base system | `system/schema/system.schema.json` | Extensible parent contract |
| Closed base profile | `system/schema/system-closed.schema.json` | Rejects unknown root properties |
| Domain extension | `extension/schema/retail-lending.schema.json` | Composes with and satisfies BaseSystem |
| Tagged nodes | Base and retail `$defs/*Node` | Disjoint `kind` branches |
| Relationships | Base and retail `$defs/*Relationship` | First-class `kind`, `from`, and `to` objects |
| Recursive containment | `ContainerNode` | Child nodes recurse through the node union |
| Dynamic recursion | `recursive/*.schema.json` | Extension adds `tag` at every depth |
| Invalid closure | `invalid/retail-lending.invalid.json` | Fails root `unevaluatedProperties` |
| Invalid union | `invalid/retail-lending-node.invalid.json` | Fails the tagged node union because `currency` is missing |
| Pydantic | `pydantic/model.py` | Emits and validates a corresponding Draft 2020-12 schema |
| Semantic gap | `extension/retail-lending.missing-target.json` | Passes JSON Schema, fails graph target check |

## Run all evidence

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Validate the domain fixture

```bash
python scripts/validate_schema.py examples/extension/schema/retail-lending.schema.json
python scripts/check_references.py \
  examples/extension/schema/retail-lending.schema.json \
  --registry examples/registry.json
python scripts/validate_instance.py \
  examples/extension/schema/retail-lending.schema.json \
  examples/extension/retail-lending.valid.json \
  --registry examples/registry.json
```
