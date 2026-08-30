#!/usr/bin/env python3
from __future__ import annotations
import argparse
try:
    from jsonld_common import add_common_arguments, attach_parser, cli_main, emit_result, load_auxiliary_json, load_operation_context
except ImportError:
    from .jsonld_common import add_common_arguments, attach_parser, cli_main, emit_result, load_auxiliary_json, load_operation_context

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Frame JSON-LD into a stable application profile.")
    add_common_arguments(p)
    p.add_argument("--frame", required=True, help="Frame JSON-LD file")
    return p

def run(args: argparse.Namespace) -> None:
    document, provenance, registry, processor = load_operation_context(args)
    frame_doc, frame_provenance = load_auxiliary_json(args.frame, args, registry)
    result = processor.frame(document, frame_doc, base=args.base)
    emit_result(operation="frame", engine=args.engine, result=result, provenance=provenance, raw=args.raw, output=args.output, max_output_bytes=args.max_output_bytes, extra={"frame_source": frame_provenance})

attach_parser(run, parser)
if __name__ == "__main__":
    cli_main(run)
