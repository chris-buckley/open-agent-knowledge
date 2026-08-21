# json-ld agent skill

This directory is a complete agent skill for JSON-LD 1.1 application work. It keeps five representations separate: authored JSON-LD, expanded JSON-LD, a flattened node graph, a framed application profile, and a typed Pydantic model.

## Install

Copy the `json-ld` directory into the host agent's skill directory, or extract the delivered archive there. Install the Python dependencies when the executable examples are required:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

PyLD 3.1.0 is the default standards processor. The explicit `--engine profile` mode is a bounded offline engine for the included examples and smoke tests. It MUST NOT be presented as a general conforming JSON-LD processor.

## Safe examples

All commands below use the pinned local context registry. They make no network requests.

```bash
python scripts/expand.py examples/compact/system-bundle.jsonld --engine profile --raw
python scripts/compact.py examples/expanded/system-bundle.expanded.json --context examples/contexts/system-context.jsonld --engine profile --raw
python scripts/flatten.py examples/compact/system-bundle.jsonld --engine profile --raw
python scripts/frame.py examples/compact/system-bundle.jsonld --frame examples/framed/system.frame.jsonld --engine profile --raw
python scripts/inspect_graph.py examples/compact/system-bundle.jsonld --engine profile
python scripts/semantic_roundtrip.py examples/compact/system-bundle.jsonld --context examples/contexts/system-context.jsonld --engine profile
```

Run the Pydantic bridge:

```bash
python examples/pydantic/jsonld_to_pydantic.py examples/compact/system-bundle.jsonld --engine profile --external-id sys:base
python examples/pydantic/pydantic_to_jsonld.py examples/pydantic/application-system.json --engine profile
```

## Verification

```bash
pytest -q
```

Use `scripts/run_official_subset.py` with a complete PyLD v3.1.0 checkout and its pinned test-suite submodules. The script never clones or downloads sources.

## Safety model

The scripts reject duplicate JSON keys, oversized inputs, excessive nesting, unpinned remote contexts, disallowed schemes, context cycles, integrity mismatches, and unexpected content types. The local registry maps exact HTTPS context IRIs to local files and SHA-256 digests. No script retrieves an arbitrary remote context by default.
