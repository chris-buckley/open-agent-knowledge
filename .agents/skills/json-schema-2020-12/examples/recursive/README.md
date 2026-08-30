# Recursive dynamic-reference example

[`tree.schema.json`](tree.schema.json) defines an extensible tree node with `$dynamicAnchor: "node"`. Its child items use `$dynamicRef: "#node"`.

[`strict-tree.schema.json`](strict-tree.schema.json) repeats the dynamic anchor, applies the base tree, requires `tag`, and closes the object. Dynamic scope causes descendants to require `tag` too.

[`strict-tree.valid.json`](strict-tree.valid.json) supplies tags at both levels. [`strict-tree.invalid.json`](strict-tree.invalid.json) omits the child tag and fails at `/children/0`.

Run:

```bash
python scripts/validate_instance.py \
  examples/recursive/strict-tree.schema.json \
  examples/recursive/strict-tree.valid.json \
  --registry examples/registry.json
```
