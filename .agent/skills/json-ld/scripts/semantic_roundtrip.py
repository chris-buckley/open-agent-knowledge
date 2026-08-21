#!/usr/bin/env python3
"""Compare JSON-LD graph meaning across expand/compact/expand processing."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
from typing import Any

try:
    from jsonld_common import (
        JsonLdSkillError,
        add_common_arguments,
        canonical_json_bytes,
        emit_result,
        load_auxiliary_json,
        load_operation_context,
    )
except ImportError:
    from .jsonld_common import (
        JsonLdSkillError,
        add_common_arguments,
        canonical_json_bytes,
        emit_result,
        load_auxiliary_json,
        load_operation_context,
    )


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    add_common_arguments(p)
    p.add_argument("--context", required=True, help="Governed context document")
    p.add_argument(
        "--include-documents",
        action="store_true",
        help="Include compacted and re-expanded documents in the result",
    )
    return p


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> None:
    args = parser().parse_args()
    try:
        document, provenance, registry, processor = load_operation_context(args)
        context_doc, context_provenance = load_auxiliary_json(args.context, args, registry)
        context = context_doc.get("@context", context_doc) if isinstance(context_doc, dict) else context_doc
        expanded_before = processor.expand(document, base=args.base)
        compacted = processor.compact(expanded_before, context, base=args.base)
        expanded_after = processor.expand(compacted, base=args.base)
        normalized_before = processor.normalize(expanded_before, base=args.base)
        normalized_after = processor.normalize(expanded_after, base=args.base)
        equivalent = normalized_before == normalized_after
        result: dict[str, Any] = {
            "equivalent": equivalent,
            "comparison": "URDNA2015 canonical N-Quads" if args.engine == "pyld" else "bounded named-node semantic normal form",
            "before_sha256": _digest(normalized_before),
            "after_sha256": _digest(normalized_after),
            "textually_equal": canonical_json_bytes(document) == canonical_json_bytes(compacted),
            "note": "Text order and compact shape may change while the compared graph meaning remains equal.",
        }
        if args.include_documents:
            result.update(
                {
                    "compacted": compacted,
                    "expanded_before": expanded_before,
                    "expanded_after": expanded_after,
                }
            )
        emit_result(
            operation="semantic_roundtrip",
            engine=args.engine,
            result=result,
            provenance=provenance,
            raw=args.raw,
            output=args.output,
            max_output_bytes=args.max_output_bytes,
            extra={"context_source": context_provenance},
        )
        if not equivalent:
            raise SystemExit(1)
    except JsonLdSkillError as exc:
        sys.stderr.buffer.write(canonical_json_bytes({"ok": False, "error": exc.as_dict()}))
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
