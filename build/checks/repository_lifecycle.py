"""Exercise the repository lifecycle with a deterministic host and serialized checkpoints."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import cast

from pydantic import JsonValue

from build.checks.fixtures import ROOT
from oak import parse, render, resolve
from oak.execute import Arrival, ExecutionResult, execute
from oak.node.parts.processes.statements import Act, iter_statements

_SOURCE = "repository/AGENTS.oak.md"
_MODULE = ".agents/rules/repository-change.oak.md"
_MODULE_SOURCE = "repository/" + _MODULE
_CONTRACTS = ".agents/rules/repository-task.oak.md"
_CONTRACT_SOURCE = "repository/" + _CONTRACTS
_READERS = frozenset({
    "read-scoped-knowledge", "read-python-standard", "read-specialist-skills",
    "select-knowledge-parts", "select-dependencies",
})
_GIT_ACTIONS = frozenset({"update-branch", "merge-change", "clean-merged-branch"})
_RULE_CONSTANTS = frozenset({
    "repository-rules", "communication-contract", "change-naming-rules", "commit-history-rules",
})
_State = dict[str, JsonValue]
_Inputs = Mapping[str, JsonValue]
_Outputs = dict[str, JsonValue]
_Handler = Callable[[_Inputs], _Outputs]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _documents() -> dict[str, str]:
    files = {_SOURCE: ROOT / "AGENTS.md", _MODULE_SOURCE: ROOT / _MODULE,
             _CONTRACT_SOURCE: ROOT / _CONTRACTS}
    if any(path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT.resolve())
           for path in files.values()):
        raise ValueError("repository lifecycle documents must be regular files")
    return {source: path.read_text(encoding="utf-8") for source, path in files.items()}


@dataclass
class _Host:
    actors: dict[str, str]
    revision: str = "workspace-0"
    calls: list[tuple[str, dict[str, JsonValue]]] = field(default_factory=list)
    edits: list[str] = field(default_factory=list)
    fail_on: str | None = None
    fail_after_effect: bool = False
    drift_after: str | None = None
    override: dict[str, _Outputs] = field(default_factory=dict)

    def act(self, step: Act, inputs: _Inputs) -> _Outputs:
        actor = self.actors[step.instruction]
        self.calls.append((actor, deepcopy(dict(inputs))))
        if actor == self.fail_on and not self.fail_after_effect:
            raise RuntimeError("simulated host failure before effects")
        outputs = self._handlers()[actor](inputs)
        if actor == self.drift_after:
            self.revision = "external-change"
        if actor == self.fail_on and self.fail_after_effect:
            raise RuntimeError("simulated host failure after effects")
        return {**outputs, **self.override.get(actor, {})}

    def _handlers(self) -> dict[str, _Handler]:
        return {
            **{actor: lambda _inputs: {} for actor in _READERS | _GIT_ACTIONS},
            "observe-revision": lambda _inputs: {"OBSERVED_REVISION": self.revision},
            "prepare-task": self._proposal,
            "implement-repository-task": self._implement,
            "refresh-repository-deliverables": self._refresh,
            "verify-repository-change": lambda _inputs: {
                "REVISION": self.revision, "EVIDENCE": "simulated verification at " + self.revision, "PASSED": True,
            },
            "produce-repository-result": lambda _inputs: {"OUTCOME": "Completed example task"},
            "name-change": self._name,
        }

    def _proposal(self, inputs: _Inputs) -> _Outputs:
        proposal = "Implement the supplied task without unrelated changes."
        content = json.dumps({"inputs": dict(inputs), "proposal": proposal}, sort_keys=True).encode()
        return {"PROPOSAL": proposal, "PROPOSAL_REVISION": sha256(content).hexdigest()}

    def _implement(self, _inputs: _Inputs) -> _Outputs:
        self.edits.append("implement")
        self.revision = "workspace-1"
        return {"REVISION": self.revision, "CHANGED_PATHS": "source.py"}

    def _refresh(self, inputs: _Inputs) -> _Outputs:
        _require(inputs["PRIOR_PATHS"] == "source.py", "refresh lost the implementation change set")
        self.edits.append("refresh")
        self.revision = "workspace-2"
        return {"REVISION": self.revision, "CHANGED_PATHS": "source.py, output.oak.md"}

    def _name(self, inputs: _Inputs) -> _Outputs:
        kind = cast(str, inputs["TYPE"])
        scope = "(" + cast(str, inputs["SCOPE"]) + ")" if inputs["SCOPE"] else ""
        summary = cast(str, inputs["SUMMARY"])
        marker = "!" if inputs["BREAKING"] else ""
        return {
            "BRANCH": kind + "/" + summary.replace(" ", "-"),
            "SUBJECT": kind + scope + marker + ": " + summary,
            "BODY": inputs["MIGRATION"] if inputs["BREAKING"] else "",
        }


class _Cycle:
    def __init__(self) -> None:
        self.documents = _documents()
        nodes = {source: parse(text) for source, text in self.documents.items()}
        self.host = _Host({
            step.instruction: process.id
            for node in nodes.values() for process in node.processes
            for step in iter_statements(process.body) if isinstance(step, Act)
        })
        self.state: _State = {
            "state." + entry.id: deepcopy(entry.value) for entry in nodes[_SOURCE].state
        }

    def arrive(self, interface: str, **values: JsonValue) -> ExecutionResult:
        before = deepcopy(self.state)
        node = parse(self.documents[_SOURCE])
        result = execute(
            node, Arrival(interface="interface." + interface, values=values), self.state,
            act=self.host.act, source=_SOURCE, root="repository", load=self.documents.get,
        )
        _require(self.state == before, "execution mutated the caller's checkpoint")
        saved = json.loads(json.dumps({"documents": self.documents, "state": result.state}))
        self.documents = saved["documents"]
        self.state = saved["state"]  # Restore the pinned graph and state for the next arrival.
        return result

    def start(self, task_id: str = "task-1") -> ExecutionResult:
        return self.arrive(
            "task-request", TASK_ID=task_id, TASK="Implement an example change",
            PATHS="source.py", CONSTRAINTS="Preserve unrelated work",
        )

    def resume(self, phase: str) -> ExecutionResult:
        return self.arrive("task-resume", TASK_ID=self.state["state.task-id"], PHASE=phase)

    def decide(self, approved: bool) -> ExecutionResult:
        return self.arrive(
            "task-approval", TASK_ID=self.state["state.task-id"],
            PROPOSAL_REVISION=self.state["state.proposal-revision"], APPROVED=approved,
        )

    def reach(self, phase: str) -> None:
        self.start()
        if phase == "prepare":
            return
        self.resume("prepare")
        if phase == "awaiting-approval":
            return
        self.decide(True)
        for checkpoint in ("implement", "refresh", "verify", "report"):
            if checkpoint == phase:
                return
            self.resume(checkpoint)
        _require(phase == "complete", "unknown fixture checkpoint")


def _reject(cycle: _Cycle, operation: Callable[[], object], reason: str) -> None:
    before = deepcopy(cycle.state)
    try:
        operation()
    except (RuntimeError, ValueError):
        _require(cycle.state == before, "rejected arrival changed its checkpoint: " + reason)
    else:
        raise RuntimeError("invalid lifecycle operation was accepted: " + reason)


def _check_documents() -> None:
    documents = _documents()
    root = parse(documents[_SOURCE])
    graph = resolve(root, source=_SOURCE, root="repository", load=documents.get)
    _require(set(graph.documents) == {_SOURCE, _MODULE_SOURCE, _CONTRACT_SOURCE}, "lifecycle document closure differs")
    _require(len(root.state) == 12 and not graph.documents[_MODULE_SOURCE].state
             and not graph.documents[_CONTRACT_SOURCE].state, "state ownership differs")
    _require(
        next(item.value for item in root.constants if item.id == "execution-source") == _SOURCE,
        "the documented execution source differs",
    )
    for source, node in graph.documents.items():
        _require(not (_RULE_CONSTANTS & {item.id for item in node.constants}), "procedural rules remain constants")
        _require(documents[source] == render(node), "lifecycle knowledge is noncanonical")
        for grouping in ("xml", "markdown"):
            text = render(node, grouping=grouping)
            _require(render(parse(text), grouping=grouping) == text, "lifecycle render changed meaning")
        for process in node.processes:
            actions = sum(isinstance(step, Act) for step in iter_statements(process.body))
            _require(actions <= 1, "a process owns multiple native actions: " + process.id)
    for source in (_MODULE_SOURCE, _CONTRACT_SOURCE):
        cycle = _Cycle()
        cycle.documents.pop(source)
        _reject(cycle, cycle.start, "missing explicit dependency")


def _check_success_and_replay() -> None:
    cycle = _Cycle()
    started = cycle.start()
    _require(cycle.state["state.phase"] == "prepare", "start did not retain the request")
    _require(started.emissions[0].values["TASK_ID"] == "task-1", "progress lost task identity")
    _reject(cycle, lambda: cycle.start("task-2"), "overlapping task")
    _reject(cycle, lambda: cycle.arrive("task-resume", TASK_ID="other", PHASE="prepare"), "wrong task")
    cycle.resume("prepare")
    _require(cycle.state["state.phase"] == "awaiting-approval", "preparation did not await approval")
    _require(not cycle.host.edits, "preparation mutated the repository")
    proposal_revision = cycle.state["state.proposal-revision"]
    _require(bool(proposal_revision), "proposal has no identity")
    _reject(cycle, lambda: cycle.resume("prepare"), "duplicate preparation")
    _reject(cycle, lambda: cycle.resume("implement"), "implementation without approval")
    _reject(
        cycle, lambda: cycle.arrive("task-approval", TASK_ID="task-1", PROPOSAL_REVISION="stale", APPROVED=True),
        "stale approval",
    )
    _reject(
        cycle, lambda: cycle.arrive("task-approval", TASK_ID="other", PROPOSAL_REVISION=proposal_revision, APPROVED=True),
        "approval for another task",
    )
    cycle.decide(True)
    _require(cycle.state["state.approved-revision"] == proposal_revision, "approval lost proposal identity")
    _reject(cycle, lambda: cycle.decide(True), "duplicate approval")
    for current, following in (("implement", "refresh"), ("refresh", "verify"), ("verify", "report")):
        cycle.resume(current)
        _require(cycle.state["state.phase"] == following, "resume advanced the wrong checkpoint")
        _reject(cycle, lambda: cycle.resume(current), "completed phase replay")
    completed = cycle.resume("report")
    _require(cycle.state["state.phase"] == "complete", "report did not complete the task")
    _require(cycle.host.edits == ["implement", "refresh"], "completed work was repeated")
    _require(len(completed.emissions) == 1, "completion emitted duplicate results")
    _require(completed.emissions[0].interface == "interface.task-result", "completion used the wrong interface")
    _require(completed.emissions[0].values == {
        "TASK_ID": "task-1", "OUTCOME": "Completed example task",
        "EVIDENCE": "simulated verification at workspace-2", "CHANGED_PATHS": "source.py, output.oak.md",
    }, "completion lost verified evidence or changed paths")
    _reject(cycle, lambda: cycle.resume("report"), "completed task replay")
    _reject(cycle, cycle.start, "reused task identifier")
    status = cycle.arrive("status-request", TASK_ID="task-1")
    _require(status.emissions[0].values["PHASE"] == "complete", "completed status differs")
    cycle.start("task-2")
    for key in ("proposal", "proposal-revision", "working-revision", "approved-revision",
                "verified-revision", "evidence", "changed-paths"):
        _require(cycle.state["state." + key] == "", "new task inherited a prior receipt")
    cycle.resume("prepare")
    _reject(
        cycle, lambda: cycle.arrive("task-approval", TASK_ID="task-2", PROPOSAL_REVISION=proposal_revision, APPROVED=True),
        "approval reused across tasks",
    )


def _check_cancellation() -> None:
    for phase in ("prepare", "awaiting-approval", "implement", "refresh", "verify", "report"):
        cycle = _Cycle()
        cycle.reach(phase)
        effects = list(cycle.host.edits)
        _reject(cycle, lambda: cycle.arrive("task-cancel", TASK_ID="other"), "wrong cancellation target")
        cycle.arrive("task-cancel", TASK_ID="task-1")
        _require(cycle.state["state.phase"] == "cancelled", "cancellation did not close the task")
        _require(cycle.state["state.approved-revision"] == "", "cancellation retained approval")
        _require(cycle.host.edits == effects, "cancellation claimed to undo external effects")
        _reject(cycle, lambda: cycle.resume("implement"), "resume after cancellation")
        _reject(cycle, lambda: cycle.arrive("task-cancel", TASK_ID="task-1"), "duplicate cancellation")
    cycle = _Cycle()
    cycle.reach("awaiting-approval")
    cycle.decide(False)
    _require(cycle.state["state.phase"] == "cancelled" and not cycle.host.edits, "declined proposal executed")
    cycle = _Cycle()
    cycle.reach("complete")
    _reject(cycle, lambda: cycle.arrive("task-cancel", TASK_ID="task-1"), "cancel completed task")


def _check_failures_and_drift() -> None:
    cycle = _Cycle()
    cycle.reach("prepare")
    cycle.host.drift_after = "prepare-task"
    _reject(cycle, lambda: cycle.resume("prepare"), "workspace drift during preparation")
    _require(cycle.state["state.proposal-revision"] == "", "drifting preparation published a proposal")
    for phase, actor in (
        ("prepare", "prepare-task"), ("implement", "implement-repository-task"),
        ("refresh", "refresh-repository-deliverables"), ("verify", "verify-repository-change"),
        ("report", "produce-repository-result"),
    ):
        cycle = _Cycle()
        cycle.reach(phase)
        cycle.host.fail_on = actor
        _reject(cycle, lambda: cycle.resume(phase), "native failure at " + phase)
        cycle.host.fail_on = None
        cycle.resume(phase)
        _require(cycle.state["state.phase"] != phase, "unchanged failed phase could not resume")
    for phase in ("awaiting-approval", "implement", "refresh", "verify", "report"):
        cycle = _Cycle()
        cycle.reach(phase)
        effects = list(cycle.host.edits)
        cycle.host.revision = "external-change"
        operation = (lambda: cycle.decide(True)) if phase == "awaiting-approval" else (lambda: cycle.resume(phase))
        _reject(cycle, operation, "workspace drift at " + phase)
        _require(cycle.host.edits == effects, "drift was checked after new effects")
    cycle = _Cycle()
    cycle.reach("implement")
    cycle.host.fail_on = "implement-repository-task"
    cycle.host.fail_after_effect = True
    _reject(cycle, lambda: cycle.resume("implement"), "failure after external effects")
    cycle.host.fail_on = None
    _reject(cycle, lambda: cycle.resume("implement"), "replay after partial external effects")
    _require(cycle.host.edits == ["implement"], "a partial external effect was repeated")
    for phase, actor in (("implement", "implement-repository-task"), ("verify", "verify-repository-change")):
        cycle = _Cycle()
        cycle.reach(phase)
        cycle.host.override[actor] = {"REVISION": "fabricated-revision"}
        _reject(cycle, lambda: cycle.resume(phase), "unobserved revision receipt")
    cycle = _Cycle()
    cycle.reach("verify")
    cycle.host.override["verify-repository-change"] = {"EVIDENCE": ""}
    _reject(cycle, lambda: cycle.resume("verify"), "empty verification evidence")
    cycle = _Cycle()
    cycle.reach("verify")
    cycle.host.override["verify-repository-change"] = {"PASSED": False, "EVIDENCE": "simulated check failure"}
    _reject(cycle, lambda: cycle.resume("verify"), "failed verification receipt")
    cycle = _Cycle()
    cycle.reach("report")
    cycle.host.drift_after = "produce-repository-result"
    _reject(cycle, lambda: cycle.resume("report"), "drift immediately before result emission")
    cycle = _Cycle()
    cycle.reach("report")
    cycle.state["state.verified-revision"] = ""
    _reject(cycle, lambda: cycle.resume("report"), "completion without matching verification")


def _check_boundaries_and_change_module() -> None:
    cycle = _Cycle()
    _reject(cycle, lambda: cycle.arrive("task-request", TASK="Legacy request", PATHS="source.py", CONSTRAINTS=""),
            "request without task identity")
    cycle.reach("awaiting-approval")
    _reject(cycle, lambda: cycle.arrive("task-approval", TASK_ID="task-1",
            PROPOSAL_REVISION=cycle.state["state.proposal-revision"], APPROVED="yes"), "non-boolean approval")
    cycle.state["state.phase"] = "unknown-phase"
    _reject(cycle, lambda: cycle.arrive("status-request", TASK_ID="task-1"), "invalid stored phase")
    cycle = _Cycle()
    named = cycle.arrive("name-request", TYPE="fix", SCOPE="agents", SUMMARY="add lifecycle", BREAKING=False, MIGRATION="")
    _require(named.emissions[0].values == {
        "BRANCH": "fix/add-lifecycle", "SUBJECT": "fix(agents): add lifecycle", "BODY": "",
    }, "name result did not cross the explicit module boundary")
    _reject(cycle, lambda: cycle.arrive("name-request", TYPE="platform", SCOPE="", SUMMARY="add lifecycle",
            BREAKING=False, MIGRATION=""), "unapproved change type")
    _reject(cycle, lambda: cycle.arrive("name-request", TYPE="feat", SCOPE="", SUMMARY="add lifecycle",
            BREAKING=True, MIGRATION=""), "breaking name without migration")
    broken = cycle.arrive("name-request", TYPE="feat", SCOPE="", SUMMARY="add lifecycle",
                          BREAKING=True, MIGRATION="Supply task identifiers and checkpoint state.")
    _require(broken.emissions[0].values["SUBJECT"] == "feat!: add lifecycle", "breaking marker was lost")
    for interface, actor in (("branch-update", "update-branch"), ("merge-request", "merge-change"),
                             ("merge-receipt", "clean-merged-branch")):
        before = deepcopy(cycle.state)
        cycle.arrive(interface, REMOTE="origin", SOURCE="feature", DESTINATION="main")
        _require(cycle.host.calls[-1] == (actor, {
            "REMOTE": "origin", "SOURCE": "feature", "DESTINATION": "main",
        }), "branch operation targets were lost")
        _require(cycle.state == before, "stateless change module altered lifecycle state")
    active = _Cycle()
    active.reach("implement")
    for interface in ("branch-update", "merge-request", "merge-receipt"):
        _reject(active, lambda: active.arrive(interface, REMOTE="origin", SOURCE="feature", DESTINATION="main"),
                "independent Git operation during an active task")
    _require(not any(actor in _GIT_ACTIONS for actor, _ in active.host.calls), "blocked Git work reached the host")


def validate_repository_lifecycle() -> None:
    """Verify typed arrivals, persisted phases, approval identity, failures and completion evidence."""
    _check_documents()
    _check_success_and_replay()
    _check_cancellation()
    _check_failures_and_drift()
    _check_boundaries_and_change_module()


__all__ = ["validate_repository_lifecycle"]
