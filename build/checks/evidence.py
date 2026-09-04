"""Execute the implementer against recorded checks of exact immutable snapshots."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from pydantic import JsonValue

from examples.agents import implementer
from examples.schemas.verification import VERIFICATION_FIELDS
from oak.context import InterpreterContext
from oak.execute.executor import execute
from oak.execute.models import Arrival, ExecutionError, ExecutionResult, ToolContract
from oak.node.parts.processes.steps import Act
from oak.parse.document import parse

DRAFT = "def validate_title(value):\n    return value\n"
REVISED = (
    "def validate_title(value):\n"
    "    if not value.strip():\n"
    "        raise ValueError('A title is required')\n"
    "    return value\n"
)


class VerificationHost:
    """A deterministic test host with real checks and a simulated commit sink.

    Only the two fixed source fixtures above are executed. This is not a sandbox
    for arbitrary supplied code, and the commit identifier is a test fixture,
    not a claim that a Git commit was made.
    """

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.snapshots: dict[str, str] = {}
        self.records: dict[str, dict[str, JsonValue]] = {}
        self.commits: list[str] = []
        self.trace: list[str] = []
        self.override: dict[str, JsonValue] = {}
        self.blocked = False
        self.drift = False

    def interpret(self, context: InterpreterContext) -> Mapping[str, JsonValue]:
        action = parse(context.documents[context.invocation]).processes[0].steps[0]
        if not isinstance(action, Act):
            raise RuntimeError("expected one native action")
        self.trace.append(context.process)
        match tuple(action.outputs):
            case ("DRAFT_PLAN", "QUESTIONS"):
                return {"DRAFT_PLAN": "Reject blank titles.", "QUESTIONS": "None."}
            case ("PLAN",):
                return {"PLAN": "Reject blank titles."}
            case ("CHANGESET",):
                return {"CHANGESET": DRAFT}
            case ("FINDINGS",):
                return {"FINDINGS": "Whitespace-only titles must be rejected."}
            case ("REVISED_CHANGESET", "SUMMARY", "STATUS"):
                return {"REVISED_CHANGESET": REVISED, "SUMMARY": "Reject blank titles.",
                        "STATUS": "blocked" if self.blocked else "complete"}
        raise RuntimeError(f"unexpected native action outputs: {action.outputs}")

    def snapshot(self, _step: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        self.trace.append("snapshot")
        content = str(values["CHANGESET"])
        if content != REVISED:
            raise RuntimeError("the implementer snapshotted work before applying findings")
        revision = sha256(content.encode()).hexdigest()
        subject = f"snapshot:{revision}"
        self.snapshots[subject] = content
        return {"CANDIDATE": subject, "REVISION": revision}

    def verify(self, _step: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        self.trace.append("verify")
        subject = str(values["CANDIDATE"])
        content = self.snapshots[subject]
        if content not in (DRAFT, REVISED):
            raise RuntimeError("only fixed verification fixtures may be executed")
        namespace: dict[str, object] = {}
        exec(compile(content, "candidate.py", "exec"), namespace)
        validate_title = cast(Callable[[str], str], namespace["validate_title"])
        passed = validate_title("OAK") == "OAK"
        for value in ("", "   "):
            try:
                validate_title(value)
            except ValueError:
                continue
            passed = False
        revision = sha256(content.encode()).hexdigest()
        evidence = self.directory / f"{revision}.json"
        record = {
            "VERIFIED_SUBJECT": subject,
            "VERIFIED_REVISION": revision,
            "CHECK": "implementation-checks-v1",
            "PASSED": passed,
            "EVIDENCE": str(evidence),
        }
        evidence.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
        self.records[str(evidence)] = record
        return {**record, **self.override}

    def commit(self, _step: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        self.trace.append("commit")
        subject = str(values["CANDIDATE"])
        content = self.snapshots[subject] + ("# changed\n" if self.drift else "")
        actual = sha256(content.encode()).hexdigest()
        if actual != values["REVISION"]:
            raise ExecutionError("candidate_changed", "candidate changed before commit")
        evidence = str(values["EVIDENCE"])
        expected = {name: values[name] for name in VERIFICATION_FIELDS}
        if self.records.get(evidence) != expected or json.loads(Path(evidence).read_text()) != expected:
            raise ExecutionError("unrecorded_evidence", "evidence is not the recorded host result")
        self.commits.append(actual)
        return {"COMMIT": "c" * 40, "COMMITTED_REVISION": actual}

    def tools(self) -> dict[str, ToolContract]:
        return {
            "changes.snapshot": ToolContract(
                self.snapshot, frozenset({"CHANGESET"}), frozenset({"CANDIDATE", "REVISION"}),
                input=implementer.SCHEMA_CHANGESET, output=implementer.SCHEMA_CANDIDATE,
            ),
            "checks.verify-changeset": ToolContract(
                self.verify, frozenset({"CANDIDATE", "REVISION"}), frozenset(VERIFICATION_FIELDS),
                input=implementer.SCHEMA_CANDIDATE, output=implementer.SCHEMA_VERIFICATION,
            ),
            "changes.commit-verified": ToolContract(
                self.commit,
                frozenset({"CANDIDATE", "REVISION", *VERIFICATION_FIELDS, "COMMIT_CONVENTION"}),
                frozenset({"COMMIT", "COMMITTED_REVISION"}),
                input=implementer.SCHEMA_VERIFIED_CHANGESET, output=implementer.SCHEMA_COMMIT,
            ),
        }

    def run(self) -> ExecutionResult:
        return execute(
            implementer.implementer_node,
            Arrival(interface="interface.task-request-input", values={
                "TASK_BRIEF": "Reject blank titles.", "CONTEXT": "The fixed candidate.py fixture.",
            }),
            {}, source="examples/agents/implementer.oak.md", load=implementer.load_document,
            tools=self.tools(), interpreter=self.interpret,
        )


def validate_evidence() -> None:
    """Reject stale, wrong, failed, malformed, or unrecorded verification."""
    with TemporaryDirectory() as temporary:
        directory = Path(temporary)
        host = VerificationHost(directory)
        result = host.run()
        report = result.emissions[0].values
        revision = sha256(REVISED.encode()).hexdigest()
        if host.commits != [revision] or report["VERIFIED_REVISION"] != revision:
            raise RuntimeError("the accepted work differs from the verified revision")
        if host.trace.index("process.apply-findings") > host.trace.index("verify"):
            raise RuntimeError("verification ran before findings were applied")
        if report["VERIFIED_SUBJECT"] != report["CANDIDATE"] or report["PASSED"] is not True:
            raise RuntimeError("the report lost its verification subject or result")
        if json.loads(Path(str(report["EVIDENCE"])).read_text())["VERIFIED_REVISION"] != revision:
            raise RuntimeError("verification did not produce recorded evidence")

        rejected = (
            ({"VERIFIED_SUBJECT": "another-candidate"}, "assertion_failed"),
            ({"VERIFIED_REVISION": sha256(DRAFT.encode()).hexdigest()}, "assertion_failed"),
            ({"CHECK": "another-check-v1"}, "assertion_failed"),
            ({"PASSED": False}, "assertion_failed"),
            ({"PASSED": "true"}, "invalid_act_output"),
            ({"EVIDENCE": ""}, "invalid_act_output"),
            ({"EVIDENCE": "unrecorded-result.json"}, "unrecorded_evidence"),
        )
        for override, code in rejected:
            host = VerificationHost(directory)
            host.override = override
            try:
                host.run()
            except ExecutionError as error:
                if error.code != code:
                    raise RuntimeError(f"wrong verification rejection: {error}") from error
            else:
                raise RuntimeError(f"invalid evidence was accepted: {override}")
            if host.commits:
                raise RuntimeError("invalid evidence caused a commit")

        host = VerificationHost(directory)
        host.drift = True
        try:
            host.run()
        except ExecutionError as error:
            if error.code != "candidate_changed":
                raise
        else:
            raise RuntimeError("post-verification drift was accepted")
        if host.commits:
            raise RuntimeError("host failed to reject drift before its side effect")
        host = VerificationHost(directory)
        host.blocked = True
        blocked = host.run()
        if blocked.emissions[0].interface != "interface.escalation-output" or host.snapshots:
            raise RuntimeError("blocked work reached verification or commit")


__all__ = ["validate_evidence"]
