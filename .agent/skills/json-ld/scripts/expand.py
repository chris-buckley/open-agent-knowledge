#!/usr/bin/env python3
from __future__ import annotations
import argparse
try:
    from jsonld_common import add_common_arguments, attach_parser, cli_main, emit_result, load_operation_context
except ImportError:
    from .jsonld_common import add_common_arguments, attach_parser, cli_main, emit_result, load_operation_context

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Expand JSON-LD with safe offline document loading.")
    add_common_arguments(p)
    return p

def run(args: argparse.Namespace) -> None:
    document, provenance, _registry, processor = load_operation_context(args)
    result = processor.expand(document, base=args.base)
    emit_result(operation="expand", engine=args.engine, result=result, provenance=provenance, raw=args.raw, output=args.output, max_output_bytes=args.max_output_bytes)

attach_parser(run, parser)
if __name__ == "__main__":
    cli_main(run)
