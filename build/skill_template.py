"""One inert skill foundation, its selected state extension, and package descriptions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
import posixpath
import re

import yaml
from oak import Constant, Node, parse, render


class Profile(StrEnum):
    STATELESS = "stateless"
    STATEFUL = "stateful"


class ResourceKind(StrEnum):
    SHARED = "shared"
    SCAFFOLD = "scaffold"
    GENERATED = "generated"
    DEPENDENCY = "dependency"


@dataclass(frozen=True, slots=True)
class Resource:
    path: str
    purpose: str
    when: str = ""
    kind: ResourceKind = ResourceKind.SHARED

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ResourceKind):
            raise ValueError("unknown resource kind")
        parts = _resource_parts(self.path, self.kind)
        if not self.purpose.strip() or set(self.purpose).intersection("\n\r→"):
            raise ValueError("resource needs a single-line purpose")
        _require_generated_marker(parts, self.kind)
        _require_loading_condition(self.kind, self.when)


def _resource_parts(raw: str, kind: ResourceKind) -> tuple[str, ...]:
    path = PurePosixPath(raw)
    if not path.parts or path.is_absolute() or posixpath.normpath(raw) != raw:
        raise ValueError("resource needs one normalized relative POSIX path")
    if set(raw).intersection("\\:\n\r\t"):
        raise ValueError("resource contains non-POSIX path characters")
    if kind != ResourceKind.DEPENDENCY and ".." in path.parts:
        raise ValueError("shared resources cannot escape their package")
    return path.parts


def _require_generated_marker(parts: tuple[str, ...], kind: ResourceKind) -> None:
    generated = kind == ResourceKind.GENERATED
    if parts.count("(...)") != int(generated) or generated and parts[-1] != "(...)":
        raise ValueError("only generated contents use one final (...) component")


def _require_loading_condition(kind: ResourceKind, when: str) -> None:
    if kind in {ResourceKind.SCAFFOLD, ResourceKind.GENERATED} and when:
        raise ValueError("instance contents cannot enter the shared discovery index")
    if kind == ResourceKind.DEPENDENCY and not when.strip():
        raise ValueError("a declared dependency needs its explicit loading condition")


TEMPLATE_DIRECTORIES = ("references", "assets/constants", "assets/schemas", "guides", "processes", "scripts")
ROLES = ("DEFINE", "ROUTE", "LOOP", "INDEX", "MAP", "ASSERT")
_BASE_TEMPLATE = '''---
name: "<SKILL_NAME>"
description: "<SKILL_DESCRIPTION>"
---

<INSTRUCTIONS_PART>
<constants>
title: <TITLE_JSON>

purpose: <PURPOSE_JSON>

principle: <PRINCIPLE_JSON>

roles: <ROLES_JSON>

index: <INDEX_JSON>

layout: TEXT<<
SKILL_TREE:
<RESOURCE_TREE>
>>

<CONSTANT_ENTRIES>
</constants>
<SCHEMAS_PART>
<STATE_PART>
<TRIGGERS_PART>
<PROCESSES_PART>
<INTERFACES_PART>
'''


def template(profile: Profile = Profile.STATELESS) -> str:
    """Select one state slot without maintaining a second common skeleton."""
    profile = Profile(profile)
    return _BASE_TEMPLATE if profile == Profile.STATEFUL else _BASE_TEMPLATE.replace("<STATE_PART>\n", "")


TEMPLATE_ENTRY = template()

MEMORY_RULES = (
    "Bind one stable owner and capability to an explicit local instance root, independently of shared source paths, script locations and exposed names. Reject another owner, unsupported format or changed required dependency before work.",
    "Use only justified state/policy, state/history, state/runs and state/runtime areas. Shared templates seed missing instances only; source updates never replace saved policy, evidence, pending work or tool-owned records.",
    "Ordinary memory needs normal file tools, not a state service. Use UTF-8 CSV with id,name,reference headers, stable unique ids and standard quoting. Resolve references from the containing index inside the permitted instance; reject malformed, dangling, escaping or symlink references.",
    "Load the requested index and selected records only after invocation. Keep mutable contents out of default context, shared INDEX/MAP and shared SKILL.md. An index reference neither grants access nor makes private records instructions.",
    "Reuse a saved retention decision. On first use ask only when no applicable decision exists. Full retains future source text; summary retains its digest, decision and evidence reference. Changing mode affects future records only; preserve existing evidence and pending work until an explicit compatible cleanup is approved.",
    "Loading, Git tracking, retention and backup are separate controls. Default to local state exclusions and verify actual git check-ignore plus tracked-file status. Explicit bounded opt-in needs its real ignore rules checked; configuration alone proves no exclusion. Inherited or already-tracked conflicts need reconciliation.",
    "Allow one active writer. Inspect inputs and identities, prepare the record, recheck for intervening edits, write the record before its index entry, then read both back. Resume by reconciling exact existing bytes and pending identity; preserve orphaned records and reject unknown writer conflicts. This is not an atomic multi-file transaction.",
    "Only the owning tool writes operational journals, locks, verified outcomes and protected datasets. Never fabricate a receipt. Reconcile uncertain effects through their owner before retry; failed OAK work discards staged values, not filesystem or external effects.",
)


def extension_node() -> Node:
    """Deliver stateful knowledge as constants, never an operational fusion scope."""
    return Node(constants=[
        Constant(id="profile", value=Profile.STATEFUL.value),
        Constant(id="selection", value=(
            "Populate the same _template/SKILL.md foundation. Insert the selected <STATE_PART> after schemas "
            "and before triggers; merge required schemas, constants and process entries into their existing parts. "
            "Retain only justified instance scaffolds. Do not concatenate operational documents.")),
        Constant(id="state-slot", value="<STATE_PART>"),
        Constant(id="memory", form="yaml", value=list(MEMORY_RULES)),
        Constant(id="boundary", value=(
            "This recipe and its examples are inert knowledge. They create no state for the authoring skill, "
            "supply no file tool or persistence service, and grant no installation or write authority.")),
    ])


def _selected_resources(profile: Profile, resources: Sequence[Resource]) -> tuple[Resource, ...]:
    selected = tuple(resources)
    _require_resource_names(selected)
    if profile == Profile.STATELESS and any(_instance_resource(resource) for resource in selected):
        raise ValueError("a stateless selection cannot contain instance resources")
    return selected


def _require_resource_names(resources: Sequence[Resource]) -> None:
    names = {resource.path for resource in resources}
    if len(names) != len(resources) or "SKILL.md" not in names:
        raise ValueError("a package needs one SKILL.md and unique resource paths")
    if any(PurePosixPath(name).name == ".gitkeep" for name in names):
        raise ValueError("remove empty template placeholders during population")
    for name in names:
        if any(parent.as_posix() in names for parent in PurePosixPath(name).parents):
            raise ValueError("a resource file cannot also be a directory")


def _instance_resource(resource: Resource) -> bool:
    return resource.kind in {ResourceKind.SCAFFOLD, ResourceKind.GENERATED} or PurePosixPath(resource.path).parts[0] == "state"


def resource_layout(resources: Sequence[Resource]) -> str:
    """Describe every selected leaf; generated names remain outside shared source."""
    lines = ["SKILL_TREE:"]
    directories: set[str] = set()
    for resource in sorted(resources, key=lambda item: (item.path != "SKILL.md", item.path)):
        if resource.kind == ResourceKind.DEPENDENCY:
            continue
        parts = PurePosixPath(resource.path).parts
        for depth in range(1, len(parts)):
            directory = "/".join(parts[:depth])
            if directory not in directories:
                lines.append("  " * depth + parts[depth - 1] + "/")
                directories.add(directory)
        lines.append("  " * len(parts) + parts[-1] + "→" + resource.purpose)
    return "\n".join(lines)


def _require_definition(name: str, description: str, *definition: str) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError("skill name must be a lowercase kebab-case identifier")
    if not all(value.strip() for value in (description, *definition)) or len(description) > 1024:
        raise ValueError("skill definition fields must be populated")
    slots = set(re.findall(r"<([A-Z_]+)>", _BASE_TEMPLATE))
    if slots.intersection(re.findall(r"<([A-Z_]+)>", "\n".join((description, *definition)))):
        raise ValueError("skill definition retains an unfilled scaffold marker")


def _require_roles(roles: Mapping[str, str]) -> None:
    required_roles = tuple(role for role in ROLES if role != "ROUTE" or role in roles)
    if tuple(roles) != required_roles or any(not target.strip() for target in roles.values()):
        raise ValueError("roles must follow DEFINE, optional ROUTE, LOOP, INDEX, MAP, ASSERT")


def _require_state(profile: Profile, work: Node) -> None:
    if profile == Profile.STATELESS and work.state:
        raise ValueError("stateless selection cannot own OAK state")
    if profile == Profile.STATEFUL and not work.state:
        raise ValueError("stateful selection needs its explicit owned state")


def populate(
    profile: Profile, work: Node, resources: Sequence[Resource], *,
    name: str, description: str, title: str, purpose: str, principle: str, roles: Mapping[str, str],
) -> str:
    """Assemble a selected skill in canonical parts with source-derived INDEX/MAP."""
    profile = Profile(profile)
    selected = _selected_resources(profile, resources)
    _require_definition(name, description, title, purpose, principle)
    _require_roles(roles)
    _require_state(profile, work)
    index = [{"when": resource.when, "reference": resource.path} for resource in selected if resource.when]
    common = [
        Constant(id="title", value=title),
        Constant(id="purpose", value=purpose),
        Constant(id="principle", value=principle),
        Constant(id="roles", value=dict(roles)),
        Constant(id="index", form="csv" if index else "inline", value=index),
        Constant(id="layout", form="text", value=resource_layout(selected)),
    ]
    parts = {part: list(getattr(work, part)) for part in Node.model_fields}
    parts["constants"] = [*common, *work.constants]
    node = Node(**parts)
    body = render(node)
    if parse(body) != node:
        raise RuntimeError("populated skill changed during canonical rendering")
    frontmatter = yaml.safe_dump({"name": name, "description": description}, sort_keys=False, allow_unicode=True)
    return "---\n" + frontmatter + "---\n\n" + body + "\n"
