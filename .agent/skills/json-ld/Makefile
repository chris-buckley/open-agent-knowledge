.RECIPEPREFIX := >
.PHONY: test smoke examples verify-clean

test:
>pytest -q

smoke:
>python scripts/semantic_roundtrip.py examples/compact/system-bundle.jsonld --context examples/contexts/system-context.jsonld --engine profile
>python scripts/inspect_graph.py examples/compact/system-bundle.jsonld --engine profile

examples:
>python scripts/expand.py examples/compact/system-bundle.jsonld --engine profile --raw --output examples/expanded/system-bundle.expanded.json
>python scripts/flatten.py examples/compact/system-bundle.jsonld --engine profile --raw --output examples/flattened/system-bundle.flattened.json
>python scripts/frame.py examples/compact/system-bundle.jsonld --frame examples/framed/system.frame.jsonld --engine profile --raw --output examples/framed/domain-extension.framed.jsonld

verify-clean:
>python -c "from pathlib import Path; bad=[p for p in Path('.').rglob('*') if {'.venv','venv','node_modules'} & set(p.parts)]; assert not bad, bad"
