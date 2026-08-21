# Invalid fixtures

[`retail-lending.invalid.json`](retail-lending.invalid.json) adds an unknown root property named `debug`. The final retail contract rejects it through `unevaluatedProperties: false`.

[`retail-lending-node.invalid.json`](retail-lending-node.invalid.json) tags a child as `loan-product` but omits required `currency`. The tagged `oneOf` fails and exposes nested branch errors. Because the containing branch fails, a final `unevaluatedProperties` summary can also appear; diagnose the nested `/nodes/0/children/0` `required` error rather than treating the closure summary as the root cause.

Run with `--json` to preserve nested error context:

```bash
python scripts/validate_instance.py \
  examples/extension/schema/retail-lending.schema.json \
  examples/invalid/retail-lending-node.invalid.json \
  --registry examples/registry.json \
  --json
```
