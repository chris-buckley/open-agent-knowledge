"""Disposable normal-file host for profile acceptance, never a delivered state runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import csv
import hashlib
from io import StringIO
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

from pydantic import JsonValue
from oak import Act, Node, Schema, SchemaBindingError

_HEADER = ("id", "name", "reference")
_IDENTIFIER = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


@dataclass(frozen=True, slots=True)
class IndexRow:
    id: str
    name: str
    reference: str


def index_bytes(rows: list[IndexRow], *, header: bool = True) -> bytes:
    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    if header:
        writer.writerow(_HEADER)
    writer.writerows((row.id, row.name, row.reference) for row in rows)
    return stream.getvalue().encode("utf-8")


class MemoryFixture:
    """Supply only the three declared native actions in one synthetic fixture graph."""

    def __init__(self, instances: Mapping[str, Path], review: Node, classifier: Node, memory: Node) -> None:
        self.instances = {owner: path.resolve() for owner, path in instances.items()}
        self.configuration_schema: Schema = next(schema for schema in memory.schemas if schema.id == "configuration")
        self.policy_schema: Schema = next(schema for schema in memory.schemas if schema.id == "policy")
        prepare = next(process for process in review.processes if process.id == "prepare-review")
        publish = next(process for process in review.processes if process.id == "publish-review")
        operation = next(process for process in classifier.processes if process.id == "classify")
        self.handlers: dict[str, Callable[[Mapping[str, JsonValue]], Mapping[str, JsonValue]]] = {
            next(step.instruction for step in prepare.body if isinstance(step, Act)): self.bind,
            next(step.instruction for step in publish.body if isinstance(step, Act)): self.publish,
            next(step.instruction for step in operation.body if isinstance(step, Act)): self.classify,
        }
        self.reads: list[str] = []
        self.events: list[str] = []
        self.active_writer = "agent"
        self.interrupt_at: str | None = None
        self.before_index: Callable[[Path], None] | None = None
        self.verified = True
        self.shared_paths: dict[str, frozenset[str]] = {}

    def __call__(self, action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        handler = self.handlers.get(action.instruction)
        if handler is None:
            raise ValueError("the fixture cannot execute an undeclared action")
        return handler(values)

    def classify(self, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        self.events.append("classify")
        return {"CATEGORY": "match" if str(values["TERM"]).casefold() in str(values["TEXT"]).casefold() else "other"}

    def instance(self, values: Mapping[str, JsonValue]) -> Path:
        owner = str(values["OWNER"])
        declared = Path(str(values["INSTANCE"]))
        root = self.instances.get(owner)
        if root is None or declared.is_symlink() or declared.resolve() != root:
            raise ValueError("instance_owner: no matching explicitly bound local instance")
        if self.active_writer != "agent":
            raise ValueError("writer_conflict: another writer owns this fixture")
        return root

    def path(self, root: Path, relative: str, *, base: Path | None = None) -> Path:
        reference = PurePosixPath(relative)
        if not relative or reference.is_absolute() or set(relative).intersection("\\:\n\r\t"):
            raise ValueError("record_reference: expected a local relative path")
        lexical = (base or root) / relative
        target = lexical.resolve()
        if not target.is_relative_to(root):
            raise ValueError("record_reference: path escapes its instance")
        self._reject_links(root, lexical)
        return target

    def _reject_links(self, root: Path, lexical: Path) -> None:
        for candidate in (lexical, *lexical.parents):
            if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
                raise ValueError("record_reference: symbolic links are not permitted")
            if candidate == root:
                break

    def read(self, root: Path, path: Path) -> bytes:
        checked = self.path(root, path.relative_to(root).as_posix())
        self.reads.append(checked.relative_to(root).as_posix())
        return checked.read_bytes()

    def rows(self, root: Path, index: Path) -> tuple[bytes, list[IndexRow]]:
        raw = self.read(root, index)
        try:
            reader = csv.DictReader(StringIO(raw.decode("utf-8"), newline=""), strict=True)
            if tuple(reader.fieldnames or ()) != _HEADER:
                raise ValueError("index_shape: expected id,name,reference")
            result = []
            identifiers: set[str] = set()
            for fields in reader:
                row = self._index_row(root, index, fields)
                if row.id in identifiers:
                    raise ValueError("index_identity: invalid or duplicate record id")
                identifiers.add(row.id)
                result.append(row)
            return raw, result
        except (csv.Error, UnicodeDecodeError) as error:
            raise ValueError("index_shape: malformed CSV") from error

    def _index_row(self, root: Path, index: Path, fields: Mapping[str | None, object]) -> IndexRow:
        if set(fields) != set(_HEADER) or any(not isinstance(value, str) or not value for value in fields.values()):
            raise ValueError("index_shape: a row has missing or extra columns")
        row = IndexRow(str(fields["id"]), str(fields["name"]), str(fields["reference"]))
        if not _IDENTIFIER.fullmatch(row.id):
            raise ValueError("index_identity: invalid record id")
        if not self.path(root, row.reference, base=index.parent).is_file():
            raise ValueError("record_reference: dangling index entry")
        return row

    def settings(self, root: Path, values: Mapping[str, JsonValue]) -> dict[str, JsonValue]:
        settings = json.loads(self.read(root, root / "state/configuration.json"))
        if not isinstance(settings, dict) or set(settings) != {"version", "owner", "capability", "retention"}:
            raise ValueError("configuration_shape: unsupported instance settings")
        self.configuration_schema.bind({"VERSION": settings["version"], "OWNER": settings["owner"],
                                        "CAPABILITY": settings["capability"], "MODE": settings["retention"]})
        if settings["owner"] != values["OWNER"] or settings["capability"] != values["CAPABILITY"]:
            raise ValueError("instance_owner: settings belong to a different capability or owner")
        return settings

    def verify_git(self, root: Path, owner: str, prospective: tuple[str, ...] = ()) -> None:
        allowed = self.shared_paths.get(owner, frozenset())
        tracked = subprocess.run(["git", "ls-files", "--", "state"], cwd=root, capture_output=True, text=True, check=True)
        if set(tracked.stdout.splitlines()) - allowed:
            raise ValueError("git_tracking: private state is already tracked")
        paths = {path.relative_to(root).as_posix() for path in (root / "state").rglob("*") if path.is_file()}
        for relative in sorted(paths | set(prospective)):
            check = subprocess.run(["git", "check-ignore", "--no-index", "-q", "--", relative], cwd=root, check=False)
            expected = 1 if relative in allowed else 0
            if check.returncode != expected:
                raise ValueError("git_exclusion: actual rules differ from the explicitly selected paths")

    def initialize(self, root: Path, values: Mapping[str, JsonValue]) -> None:
        settings_path = self.path(root, "state/configuration.json")
        if settings_path.exists():
            return
        mode = values["RETENTION"]
        if mode not in {"full", "summary"}:
            raise ValueError("retention_choice: first use requires an actual retention decision")
        if (root / "state").exists() and any((root / "state").iterdir()):
            raise ValueError("instance_recovery: preserve and reconcile the existing incomplete instance")
        ignore = root / ".gitignore"
        if not ignore.exists():
            ignore.write_bytes(b"/state/\n")
        self.verify_git(root, str(values["OWNER"]), ("state/configuration.json", "state/history/index.csv"))
        for directory in ("state/policy", "state/history/records", "state/runs"):
            self.path(root, directory).mkdir(parents=True, exist_ok=True)
        settings_path.write_bytes(json_bytes({"version": 1, "owner": values["OWNER"],
                                             "capability": values["CAPABILITY"], "retention": mode}))
        (root / "state/policy/priority.json").write_bytes(json_bytes({"version": 1, "owner": values["OWNER"],
            "capability": values["CAPABILITY"], "id": "priority", "writer": "agent", "term": "urgent"}))
        (root / "state/policy/index.csv").write_bytes(index_bytes([IndexRow("priority", 'Priority, "urgent"', "priority.json")]))
        for area in ("history", "runs"):
            (root / f"state/{area}/index.csv").write_bytes(index_bytes([]))
        self.events.append("initialize")

    def policy(self, root: Path, values: Mapping[str, JsonValue]) -> tuple[bytes, bytes, dict[str, JsonValue], str]:
        index = root / "state/policy/index.csv"
        raw_index, rows = self.rows(root, index)
        selected = [row for row in rows if row.id == values["POLICY_ID"]]
        if len(selected) != 1:
            raise ValueError("policy_identity: selected policy is missing")
        reference = self.path(root, selected[0].reference, base=index.parent)
        raw_policy = self.read(root, reference)
        policy = self._policy_record(raw_policy, values)
        return raw_index, raw_policy, policy, reference.relative_to(root).as_posix()

    def _policy_record(self, raw: bytes, values: Mapping[str, JsonValue]) -> dict[str, JsonValue]:
        policy = json.loads(raw)
        if not isinstance(policy, dict) or set(policy) != {name.lower() for name in self.policy_schema.placeholders}:
            raise ValueError("policy_identity: expected one record object")
        try:
            self.policy_schema.bind({name.upper(): value for name, value in policy.items()})
        except SchemaBindingError as error:
            raise ValueError("policy_identity: invalid policy shape or writer") from error
        if (policy["id"] != values["POLICY_ID"] or policy["owner"] != values["OWNER"]
                or policy["capability"] != values["CAPABILITY"]):
            raise ValueError("policy_identity: wrong policy, owner or capability")
        return policy

    def snapshot(self, root: Path, values: Mapping[str, JsonValue], history: bytes) -> str:
        settings = self.settings(root, values)
        identity = {key: value for key, value in settings.items() if key != "retention"}
        index, record, _, _ = self.policy(root, values)
        return digest(json_bytes({"identity": digest(json_bytes(identity)), "policy_index": digest(index),
                                  "policy_record": digest(record), "history_index": digest(history)}))

    def bind(self, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        root = self.instance(values)
        self.initialize(root, values)
        settings = self.settings(root, values)
        self.verify_git(root, str(values["OWNER"]), (f"state/history/records/{values['ID']}.json",))
        _, _, policy, _ = self.policy(root, values)
        history, rows = self.rows(root, root / "state/history/index.csv")
        if any(row.id == values["ID"] for row in rows):
            raise ValueError("record_identity: this record id is already published")
        self.events.append("prepare")
        return {"TERM": policy["term"], "MODE": settings["retention"], "SNAPSHOT": self.snapshot(root, values, history)}

    def _record(self, root: Path, values: Mapping[str, JsonValue]) -> bytes:
        _, policy, _, policy_reference = self.policy(root, values)
        record = {"version": 1, "owner": values["OWNER"], "capability": values["CAPABILITY"], "id": values["ID"],
                  "writer": "agent", "category": values["CATEGORY"], "policy": policy_reference,
                  "policy_sha256": digest(policy), "source_sha256": digest(str(values["TEXT"]).encode("utf-8")),
                  "mode": values["MODE"]}
        if values["MODE"] == "full":
            record["source"] = values["TEXT"]
        return json_bytes(record)

    def _interrupt(self, phase: str) -> None:
        if self.interrupt_at == phase:
            self.interrupt_at = None
            self.events.append("interrupted-" + phase)
            raise ValueError("fixture interruption after " + phase)

    def publish(self, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        root = self.instance(values)
        identifier = str(values["ID"])
        if not _IDENTIFIER.fullmatch(identifier):
            raise ValueError("record_identity: unsafe record id")
        reference = f"state/history/records/{identifier}.json"
        self.verify_git(root, str(values["OWNER"]), (reference,))
        target = self.path(root, reference)
        expected_record = self._record(root, values)
        expected_row = IndexRow(identifier, f"Review {identifier}, {values['CATEGORY']}", f"records/{identifier}.json")
        row_bytes = index_bytes([expected_row], header=False)
        index = root / "state/history/index.csv"
        base_index, existing = self._publication_index(root, values, expected_row)
        self._publish_record(root, target, expected_record, indexed=existing)
        if not existing:
            self._publish_index(root, values, base_index, row_bytes)
        verified_record = self.read(root, target)
        _, verified_rows = self.rows(root, index)
        if verified_record != expected_record or [row for row in verified_rows if row.id == identifier] != [expected_row]:
            raise ValueError("read_back: record and index disagree")
        self.events.append("read-back")
        return {"REFERENCE": reference, "SHA256": digest(verified_record), "VERIFIED": self.verified}

    def _publication_index(
        self, root: Path, values: Mapping[str, JsonValue], expected_row: IndexRow,
    ) -> tuple[bytes, bool]:
        row_bytes = index_bytes([expected_row], header=False)
        index = root / "state/history/index.csv"
        raw_index, rows = self.rows(root, index)
        existing = [row for row in rows if row.id == expected_row.id]
        base_index = raw_index
        if existing:
            if existing != [expected_row] or not raw_index.endswith(row_bytes):
                raise ValueError("index_conflict: the pending row differs or moved")
            base_index = raw_index[:-len(row_bytes)]
        if self.snapshot(root, values, base_index) != values["SNAPSHOT"]:
            raise ValueError("input_revision: prepared memory inputs changed")
        return base_index, bool(existing)

    def _publish_record(self, root: Path, target: Path, expected_record: bytes, *, indexed: bool) -> None:
        if target.exists():
            stored = self.read(root, target)
            if stored != expected_record:
                raise ValueError("record_conflict: preserve the differing or protected existing record")
            self.events.append("reconcile-pair" if indexed else "reconcile-orphan")
        else:
            target.write_bytes(expected_record)
            self.events.append("write-record")
            self._interrupt("record")

    def _publish_index(self, root: Path, values: Mapping[str, JsonValue], base_index: bytes, row_bytes: bytes) -> None:
        if self.before_index is not None:
            self.before_index(root)
            self.before_index = None
        index = root / "state/history/index.csv"
        current, _ = self.rows(root, index)
        if self.snapshot(root, values, current) != values["SNAPSHOT"]:
            raise ValueError("input_revision: another edit intervened before index publication")
        index.write_bytes(base_index + row_bytes)
        self.events.append("write-index")
        self._interrupt("index")

    def save_checkpoint(self, owner: str, state: Mapping[str, JsonValue]) -> None:
        root = self.instances[owner]
        target = self.path(root, "state/runs/pending.json")
        if target.exists():
            existing = json.loads(self.read(root, target))
            if existing.get("writer") != "agent" or existing.get("owner") != owner:
                raise ValueError("checkpoint_owner: preserve the protected existing checkpoint")
        index = root / "state/runs/index.csv"
        _, rows = self.rows(root, index)
        pending = IndexRow("pending", "Current pending review", "pending.json")
        retained = [pending if row.id == "pending" else row for row in rows]
        if not any(row.id == "pending" for row in rows):
            retained.append(pending)
        target.write_bytes(json_bytes({"version": 1, "writer": "agent", "owner": owner, "state": dict(state)}))
        index.write_bytes(index_bytes(retained))

    def restore_checkpoint(self, owner: str) -> dict[str, JsonValue]:
        root = self.instances[owner]
        _, rows = self.rows(root, root / "state/runs/index.csv")
        row = next(row for row in rows if row.id == "pending")
        record = json.loads(self.read(root, self.path(root, row.reference, base=root / "state/runs")))
        if (type(record.get("version")) is not int or record["version"] != 1 or record.get("owner") != owner
                or record.get("writer") != "agent" or not isinstance(record.get("state"), dict)):
            raise ValueError("checkpoint_owner: wrong pending checkpoint")
        return record["state"]
