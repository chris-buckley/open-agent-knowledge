#!/usr/bin/env python3
from __future__ import annotations
import argparse
try:
    from jsonld_common import add_common_arguments, attach_parser, cli_main, emit_result, load_auxiliary_json, load_operation_context
except ImportError:
    from .jsonld_common import add_common_arguments, attach_parser, cli_main, emit_result, load_auxiliary_json, load_operation_context

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Compact JSON-LD using an explicit governed context.")
    add_common_arguments(p)
    p.add_argument("--context", required=True, help="Context JSON file or context document")
    return p

def run(args: argparse.Namespace) -> None:
    document, provenance, registry, processor = load_operation_context(args)
    context_doc, context_provenance = load_auxiliary_json(args.context, args, registry)
    context = context_doc.get("@context", context_doc) if isinstance(context_doc, dict) else context_doc
    result = processor.compact(document, context, base=args.base)
    emit_result(operation="compact", engine=args.engine, result=result, provenance=provenance, raw=args.raw, output=args.output, max_output_bytes=args.max_output_bytes, extra={"context_source": context_provenance})

attach_parser(run, parser)
if __name__ == "__main__":
    cli_main(run)
