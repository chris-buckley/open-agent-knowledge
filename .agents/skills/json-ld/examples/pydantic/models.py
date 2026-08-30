"""Stable framed JSON-LD source models and canonical application models."""
from __future__ import annotations

from datetime import date
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator

CONTEXT_IRI = "https://example.org/context/system-v1.jsonld"


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_by_alias=True,
        validate_by_name=True,
    )


class NodeRef(StrictModel):
    id: str = Field(alias="@id", serialization_alias="@id")


class ServiceNode(StrictModel):
    id: str = Field(alias="@id", serialization_alias="@id")
    type: Literal["Service"] = Field(alias="@type", serialization_alias="@type")
    label: str


class StoreNode(StrictModel):
    id: str = Field(alias="@id", serialization_alias="@id")
    type: Literal["Store"] = Field(alias="@type", serialization_alias="@type")
    label: str


class AdaptorNode(StrictModel):
    id: str = Field(alias="@id", serialization_alias="@id")
    type: Literal["Adaptor"] = Field(alias="@type", serialization_alias="@type")
    label: str
    links_to: str


Node = Annotated[ServiceNode | StoreNode | AdaptorNode, Field(discriminator="type")]


class RelationshipSource(StrictModel):
    id: str = Field(alias="@id", serialization_alias="@id")
    type: Literal["Relationship"] = Field(alias="@type", serialization_alias="@type")
    kind: str
    from_id: str = Field(alias="from", serialization_alias="from")
    to_id: str = Field(alias="to", serialization_alias="to")
    confidence: float = 1.0
    effective_from: date | None = None
    source_document: str | None = None


class SystemProfileSource(StrictModel):
    context: str = Field(alias="@context", serialization_alias="@context")
    id: str = Field(alias="@id", serialization_alias="@id")
    type: Literal["System"] = Field(alias="@type", serialization_alias="@type")
    label: str
    extends: str | None = None
    nodes: list[Node]
    relationships: list[RelationshipSource] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_graph_targets(self, info: ValidationInfo) -> "SystemProfileSource":
        external_ids = set()
        if info.context and isinstance(info.context.get("external_ids"), (set, list, tuple)):
            external_ids = {str(item) for item in info.context["external_ids"]}
        identifiers = [self.id]
        identifiers.extend(node.id for node in self.nodes)
        identifiers.extend(edge.id for edge in self.relationships)
        duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
        if duplicates:
            raise ValueError(f"duplicate application identities: {duplicates}")
        available = set(identifiers) | external_ids
        missing: list[dict[str, str]] = []
        if self.extends and self.extends not in available:
            missing.append({"path": "$.extends", "target": self.extends})
        for index, node in enumerate(self.nodes):
            if isinstance(node, AdaptorNode) and node.links_to not in available:
                missing.append({"path": f"$.nodes[{index}].links_to", "target": node.links_to})
        for index, edge in enumerate(self.relationships):
            if edge.from_id not in available:
                missing.append({"path": f"$.relationships[{index}].from", "target": edge.from_id})
            if edge.to_id not in available:
                missing.append({"path": f"$.relationships[{index}].to", "target": edge.to_id})
        if missing:
            raise ValueError(f"graph reference targets are absent: {missing}")
        return self


class ApplicationNode(StrictModel):
    id: str
    kind: Literal["Service", "Store", "Adaptor"]
    label: str
    links_to: str | None = None


class ApplicationRelationship(StrictModel):
    id: str
    kind: str
    from_id: str
    to_id: str
    confidence: float = 1.0
    effective_from: date | None = None
    source_document: str | None = None


class ApplicationSystem(StrictModel):
    id: str
    label: str
    extends: str | None = None
    nodes: list[ApplicationNode]
    relationships: list[ApplicationRelationship] = Field(default_factory=list)


def source_to_application(source: SystemProfileSource) -> ApplicationSystem:
    return ApplicationSystem(
        id=source.id,
        label=source.label,
        extends=source.extends,
        nodes=[
            ApplicationNode(
                id=node.id,
                kind=node.type,
                label=node.label,
                links_to=node.links_to if isinstance(node, AdaptorNode) else None,
            )
            for node in source.nodes
        ],
        relationships=[
            ApplicationRelationship(
                id=edge.id,
                kind=edge.kind,
                from_id=edge.from_id,
                to_id=edge.to_id,
                confidence=edge.confidence,
                effective_from=edge.effective_from,
                source_document=edge.source_document,
            )
            for edge in source.relationships
        ],
    )


def application_to_source(application: ApplicationSystem) -> SystemProfileSource:
    nodes: list[Node] = []
    for node in application.nodes:
        if node.kind == "Service":
            nodes.append(ServiceNode(id=node.id, type="Service", label=node.label))
        elif node.kind == "Store":
            nodes.append(StoreNode(id=node.id, type="Store", label=node.label))
        else:
            if node.links_to is None:
                raise ValueError(f"Adaptor {node.id} requires links_to")
            nodes.append(
                AdaptorNode(
                    id=node.id,
                    type="Adaptor",
                    label=node.label,
                    links_to=node.links_to,
                )
            )
    relationships = [
        RelationshipSource(
            id=edge.id,
            type="Relationship",
            kind=edge.kind,
            from_id=edge.from_id,
            to_id=edge.to_id,
            confidence=edge.confidence,
            effective_from=edge.effective_from,
            source_document=edge.source_document,
        )
        for edge in application.relationships
    ]
    return SystemProfileSource.model_validate(
        {
            "@context": CONTEXT_IRI,
            "@id": application.id,
            "@type": "System",
            "label": application.label,
            "extends": application.extends,
            "nodes": [node.model_dump(mode="json", by_alias=True, exclude_none=True) for node in nodes],
            "relationships": [edge.model_dump(mode="json", by_alias=True, exclude_none=True) for edge in relationships],
        },
        context={"external_ids": {application.extends} if application.extends else set()},
    )
