#!/usr/bin/env python3
from __future__ import annotations
import argparse
try:
    from jsonld_common import add_common_arguments, attach_parser, cli_main, emit_result, load_auxiliary_json, load_operation_context
except ImportError:
    from .jsonld_common import add_common_arguments, attach_parser, cli_main, emit_result, load_auxiliary_json, load_operation_context

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Flatten JSON-LD into a deterministic node graph.")
    add_common_arguments(p)
    p.add_argument("--context", help="Optional context JSON file for compact flattened output")
    return p

def run(args: argparse.Namespace) -> None:
    document, provenance, registry, processor = load_operation_context(args)
    context = None
    extra = None
    if args.context:
        context_doc, context_provenance = load_auxiliary_json(args.context, args, registry)
        context = context_doc.get("@context", context_doc) if isinstance(context_doc, dict) else context_doc
        extra = {"context_source": context_provenance}
    result = processor.flatten(document, context, base=args.base)
    emit_result(operation="flatten", engine=args.engine, result=result, provenance=provenance, raw=args.raw, output=args.output, max_output_bytes=args.max_output_bytes, extra=extra)

attach_parser(run, parser)
if __name__ == "__main__":
    cli_main(run)
