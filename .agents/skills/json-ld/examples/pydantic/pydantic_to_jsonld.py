#!/usr/bin/env python3
"""Pydantic application model -> aliased source dictionary -> compact JSON-LD."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))

from jsonld_common import (  # noqa: E402
    JsonLdSkillError,
    LocalDocumentRegistry,
    canonical_json_bytes,
    load_json_path,
    load_processor,
)
from models import ApplicationSystem, CONTEXT_IRI, application_to_source  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--context", default=str(ROOT / "examples" / "contexts" / "system-context.jsonld"))
    parser.add_argument("--registry", default=str(ROOT / "examples" / "contexts" / "registry.json"))
    parser.add_argument("--engine", choices=("pyld", "profile"), default="pyld")
    args = parser.parse_args()
    try:
        payload, provenance = load_json_path(args.input)
        application = ApplicationSystem.model_validate(payload)
        source = application_to_source(application)
        source_dict = source.model_dump(mode="json", by_alias=True, exclude_none=True)
        context_doc, context_provenance = load_json_path(args.context)
        context = context_doc.get("@context", context_doc)
        registry = LocalDocumentRegistry(args.registry)
        processor = load_processor(args.engine, registry)
        expanded = processor.expand(source_dict)
        compacted = processor.compact(expanded, CONTEXT_IRI)
        result = {
            "ok": True,
            "engine": args.engine,
            "source": provenance,
            "context_source": context_provenance,
            "jsonld": compacted,
        }
        sys.stdout.buffer.write(canonical_json_bytes(result))
    except (JsonLdSkillError, ValueError) as exc:
        payload = exc.as_dict() if isinstance(exc, JsonLdSkillError) else {"code": "pydantic_validation_error", "message": str(exc)}
        sys.stderr.buffer.write(canonical_json_bytes({"ok": False, "error": payload}))
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
