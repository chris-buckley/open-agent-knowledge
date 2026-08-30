#!/usr/bin/env python3
"""Safe JSON-LD -> frame -> Pydantic source model -> application model."""
from __future__ import annotations
import argparse
import json
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
    preflight_contexts,
)
from models import SystemProfileSource, source_to_application  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--frame", default=str(ROOT / "examples" / "framed" / "system.frame.jsonld"))
    parser.add_argument("--registry", default=str(ROOT / "examples" / "contexts" / "registry.json"))
    parser.add_argument("--engine", choices=("pyld", "profile"), default="pyld")
    parser.add_argument("--external-id", action="append", default=[])
    args = parser.parse_args()
    try:
        source, source_provenance = load_json_path(args.input)
        frame, frame_provenance = load_json_path(args.frame)
        registry = LocalDocumentRegistry(args.registry)
        preflight_contexts(source, registry)
        preflight_contexts(frame, registry)
        processor = load_processor(args.engine, registry)
        framed = processor.frame(source, frame)
        typed = SystemProfileSource.model_validate(
            framed,
            context={"external_ids": set(args.external_id)},
        )
        application = source_to_application(typed)
        result = {
            "ok": True,
            "engine": args.engine,
            "source": source_provenance,
            "frame_source": frame_provenance,
            "framed_profile": typed.model_dump(mode="json", by_alias=True, exclude_none=True),
            "application": application.model_dump(mode="json", exclude_none=True),
        }
        sys.stdout.buffer.write(canonical_json_bytes(result))
    except (JsonLdSkillError, ValueError) as exc:
        payload = exc.as_dict() if isinstance(exc, JsonLdSkillError) else {"code": "pydantic_validation_error", "message": str(exc)}
        sys.stderr.buffer.write(canonical_json_bytes({"ok": False, "error": payload}))
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
