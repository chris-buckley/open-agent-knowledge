"""Root-specific contract ownership checks, not general OAK language restrictions."""

from __future__ import annotations

from oak.node.model import Node
from oak.node.parts.processes.statements import Act, iter_statements
from oak.vocabulary.text.target_path import is_relative_target


ROOT_SCHEMAS = frozenset({
    "repository-task", "task-handle", "resume-request", "approval-decision",
    "task-checkpoint", "task-progress", "task-proposal", "revision-reading",
    "expected-revision", "change-receipt", "verification-receipt", "task-outcome",
    "repository-result", "change-description", "change-name", "branch-targets",
})


def validate_root_contracts(node: Node) -> None:
    """Require the repository root's contracts to be locally declared and connected.

    Descriptions must exist here because these boundaries have distinct authority
    and effects. Their adequacy still requires semantic review and behavior tests.
    This policy is deliberately outside Node and the cross-document resolver.
    """
    schemas = {"schema." + schema.id: schema for schema in node.schemas}
    if {schema.id for schema in node.schemas} != ROOT_SCHEMAS:
        raise RuntimeError("root must own all public, checkpoint, and receipt schemas")
    for schema in node.schemas:
        if schema.purpose is None:
            raise RuntimeError("root schema needs its information purpose: " + schema.id)
    for interface in node.interfaces:
        if interface.schema_id not in schemas:
            raise RuntimeError("root interface schema must be local: " + interface.id)
        if interface.description is None:
            raise RuntimeError("root boundary needs its distinct meaning: " + interface.id)
    for state in node.state:
        if state.schema_id != "schema.task-checkpoint" or state.placeholder is None:
            raise RuntimeError("root state needs the local checkpoint: " + state.id)
        schemas[state.schema_id].bind_value(state.placeholder, state.value)
    if {entry.placeholder for entry in node.state} != schemas["schema.task-checkpoint"].placeholders:
        raise RuntimeError("root state does not cover its complete checkpoint")
    processes = {"process." + process.id: process for process in node.processes}
    interfaces = {"interface." + interface.id: interface for interface in node.interfaces}
    for trigger in node.triggers:
        if trigger.source not in interfaces or trigger.process not in processes:
            raise RuntimeError("root arrivals must route to local entry processes")
        if interfaces[trigger.source].schema_id != processes[trigger.process].input:
            raise RuntimeError("root source and process schemas must have one local identity")
    for process in node.processes:
        targets = [process.input, process.output]
        for statement in iter_statements(process.body):
            if isinstance(statement, Act):
                targets.extend((statement.input, statement.output))
        if any(target is not None and (is_relative_target(target) or target not in schemas)
               for target in targets):
            raise RuntimeError("root process and action contracts must be local: " + process.id)
