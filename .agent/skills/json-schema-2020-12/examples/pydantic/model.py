#!/usr/bin/env python3
"""Pydantic v2 model and deterministic JSON Schema generator for the example system."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, TypeAdapter

DIALECT = "https://json-schema.org/draft/2020-12/schema"
IDENTIFIER_PATTERN = r"^[A-Za-z][A-Za-z0-9._:/-]*$"
Identifier = Annotated[
    str,
    Field(
        min_length=1,
        pattern=IDENTIFIER_PATTERN,
        description="An application identifier; target existence needs a graph-wide check.",
    ),
]


class ClosedModel(BaseModel):
    """Shared runtime policy for closed example records."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_by_alias=True,
        validate_by_name=True,
    )


class Metadata(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)

    owner: str = Field(min_length=1)
    version: str | None = Field(default=None, min_length=1)


class ServiceNode(ClosedModel):
    id: Identifier
    kind: Literal["service"]
    label: str = Field(min_length=1)
    endpoint: AnyUrl


class StoreNode(ClosedModel):
    id: Identifier
    kind: Literal["store"]
    label: str = Field(min_length=1)
    engine: str = Field(min_length=1)


class LoanProductNode(ClosedModel):
    id: Identifier
    kind: Literal["loan-product"]
    label: str = Field(min_length=1)
    currency: str = Field(pattern=r"^[A-Z]{3}$")


class RepaymentStructureNode(ClosedModel):
    id: Identifier
    kind: Literal["repayment-structure"]
    label: str = Field(min_length=1)
    frequency: Literal["weekly", "fortnightly", "monthly"]


class ContainerNode(ClosedModel):
    id: Identifier
    kind: Literal["container"]
    label: str = Field(min_length=1)
    children: list["Node"]


Node = Annotated[
    ServiceNode
    | StoreNode
    | ContainerNode
    | LoanProductNode
    | RepaymentStructureNode,
    Field(discriminator="kind"),
]


class RelationshipCore(ClosedModel):
    id: Identifier
    from_: Identifier = Field(alias="from")
    to: Identifier


class ContainsRelationship(RelationshipCore):
    kind: Literal["contains"]


class StoresInRelationship(RelationshipCore):
    kind: Literal["stores-in"]


class OffersRelationship(RelationshipCore):
    kind: Literal["offers"]


class UsesRepaymentStructureRelationship(RelationshipCore):
    kind: Literal["uses-repayment-structure"]


Relationship = Annotated[
    ContainsRelationship
    | StoresInRelationship
    | OffersRelationship
    | UsesRepaymentStructureRelationship,
    Field(discriminator="kind"),
]


class RetailLendingSystem(ClosedModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_by_alias=True,
        validate_by_name=True,
        json_schema_extra={
            "$id": "https://example.org/schema/retail-lending-pydantic",
            "$schema": DIALECT,
            "description": (
                "A Pydantic-generated portable shape corresponding to the hand-authored "
                "RetailLendingSystem example. It is not byte-for-byte identical."
            ),
        },
    )

    id: Identifier
    domain: Literal["retail-lending"]
    nodes: list[Node]
    relationships: list[Relationship]
    metadata: Metadata


ContainerNode.model_rebuild(_types_namespace={"Node": Node})
RetailLendingSystem.model_rebuild(
    _types_namespace={"Node": Node, "Relationship": Relationship}
)


def generated_schema(*, mode: Literal["validation", "serialization"] = "validation") -> dict:
    """Generate a stable Draft 2020-12 schema with external field aliases."""

    return RetailLendingSystem.model_json_schema(
        by_alias=True,
        mode=mode,
        ref_template="#/$defs/{model}",
    )


def generated_node_schema() -> dict:
    """Demonstrate TypeAdapter.json_schema() for a non-model union type."""

    schema = TypeAdapter(Node).json_schema(
        by_alias=True,
        mode="validation",
        ref_template="#/$defs/{model}",
    )
    schema["$schema"] = DIALECT
    schema["$id"] = "https://example.org/schema/node-pydantic"
    return schema


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate or use the Pydantic v2 RetailLendingSystem example."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="write a JSON Schema document")
    generate.add_argument("output", type=Path, help="output JSON path")
    generate.add_argument(
        "--mode",
        choices=("validation", "serialization"),
        default="validation",
        help="Pydantic JSON Schema generation mode",
    )

    node = subparsers.add_parser("generate-node", help="write the Node TypeAdapter schema")
    node.add_argument("output", type=Path, help="output JSON path")

    validate = subparsers.add_parser("validate", help="validate an instance with Pydantic")
    validate.add_argument("instance", type=Path, help="instance JSON path")
    return parser


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "generate":
        write_json(args.output, generated_schema(mode=args.mode))
        print(f"WROTE: {args.output.resolve()}")
        return 0
    if args.command == "generate-node":
        write_json(args.output, generated_node_schema())
        print(f"WROTE: {args.output.resolve()}")
        return 0

    raw = json.loads(args.instance.read_text(encoding="utf-8"))
    model = RetailLendingSystem.model_validate(raw)
    print(
        json.dumps(
            model.model_dump(mode="json", by_alias=True),
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
