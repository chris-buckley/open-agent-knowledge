# Scripts

All scripts are local-only, deterministic command-line tools.

| Script | Purpose |
| --- | --- |
| `validate_schema.py` | Require Draft 2020-12 and validate a schema against its meta-schema |
| `check_references.py` | Resolve static references from an explicit local registry |
| `validate_instance.py` | Validate one instance and report exact instance and schema paths |
| `check_graph_targets.py` | Demonstrate a separate graph-wide target-existence rule |
| `_common.py` | Shared JSON, registry, format-policy, and diagnostic helpers |

Exit codes:

- `0` - requested check passed;
- `1` - instance or graph validation failed;
- `2` - JSON, usage, dialect, schema, resource, or tool failure.

Every script supports `--help`. Validation scripts support `--json` for deterministic machine-readable results.

The JSON loader rejects duplicate object keys. Registry manifests accept only absolute fragment-free URI keys and relative paths that remain beneath the manifest directory. Use repeated `--resource URI=PATH` arguments when a deliberate resource lives elsewhere.
