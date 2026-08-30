# Retail lending extension example

[`schema/retail-lending.schema.json`](schema/retail-lending.schema.json) has canonical ID `https://example.org/schema/retail-lending`.

The adaptor:

- applies `https://example.org/schema/system` through `allOf`;
- adds `loan-product` and `repayment-structure` node kinds;
- replaces recursive container children with the retail node union;
- adds `offers` and `uses-repayment-structure` relationship kinds;
- closes complete leaves and the final root with `unevaluatedProperties: false`.

[`retail-lending.valid.json`](retail-lending.valid.json) validates against both the adaptor and the parent.

[`retail-lending.missing-target.json`](retail-lending.missing-target.json) also validates structurally because `to` is a valid identifier string. It then fails [`check_graph_targets.py`](../../scripts/check_graph_targets.py) because `node:missing` is absent.
