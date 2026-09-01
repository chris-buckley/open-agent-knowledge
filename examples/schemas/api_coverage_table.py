"""Author the ported API coverage table format as one OAK schema document."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Node, NonEmpty, OneOf, Regex, Schema, Type, parse, render, resolve, where

api_coverage_table_schema = Schema(
    id="api-coverage-table",
    name="API Coverage Table",
    purpose="Report API operation coverage against a specification, one row per operation.",
    template=(
        "## <TABLE_NAME>\n"
        "| Operation | URI | SpecRef | Gap |\n"
        "| --- | --- | --- | --- |\n"
        "| <OPERATION> | <ENDPOINT_PATH> | <SPEC_REF> | <GAP> |"
    ),
    where=[
        where("TABLE_NAME", Type(of="string"), NonEmpty(), description="the title for the API coverage table"),
        where("OPERATION", Type(of="string"), OneOf(values=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]), description="the HTTP method"),
        where("ENDPOINT_PATH", Type(of="string"), Regex(pattern="^/.*$"), description="the absolute path of the API endpoint"),
        where("SPEC_REF", Type(of="string"), NonEmpty(), description="the reference in the form OpenAPI: target or Swagger: target"),
        where("GAP", Type(of="string"), OneOf(values=["OK", "MISSING_PATH", "MISSING_METHOD", "REQ_SCHEMA_MISMATCH", "RESP_SCHEMA_MISMATCH", "STATUS_CODE_MISSING"]), description="the coverage gap analysis code"),
    ],
)

api_coverage_table_node = Node(schemas=[api_coverage_table_schema])

TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    """Render, parse, resolve, and round-trip the authored API coverage table node."""
    rendered = render(api_coverage_table_node)
    parsed = parse(rendered)
    resolve(parsed)
    if render(parsed) != rendered:
        raise RuntimeError("API coverage table example changed during render and parse")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
