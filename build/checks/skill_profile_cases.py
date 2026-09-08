"""Memory failure, retention and real Git-policy cases for the synthetic profile host."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess

from oak import Arrival
from build.checks.skill_profile_memory import IndexRow, index_bytes, json_bytes
from build.checks.skill_profiles import fixture, finish, initial_state, prepare, rejects, request, require, resume, run_cycle, state_files


def _interrupted_updates() -> None:
    for phase in ("record", "index"):
        with fixture() as (_, _, graph, host):
            checkpoint = prepare(graph, host)
            original = deepcopy(checkpoint)
            pending = (host.instances["alpha"] / "state/runs/pending.json").read_bytes()
            host.interrupt_at = phase
            rejects(lambda: run_cycle(graph, resume(host), checkpoint, act=host), "interrupted publication", match="fixture interruption")
            require(checkpoint == original and (host.instances["alpha"] / "state/runs/pending.json").read_bytes() == pending,
                    "failed publication discarded the pending checkpoint")
            record = host.instances["alpha"] / "state/history/records/item-1.json"
            before = record.read_bytes()
            finish(graph, host)
            require(record.read_bytes() == before and host.events.count("write-record") == 1
                    and host.events.count("write-index") == 1, "recovery repeated a completed file phase")
            require(("reconcile-orphan" if phase == "record" else "reconcile-pair") in host.events,
                    "recovery did not distinguish orphan and published pair")
            completed = state_files(host.instances["alpha"])
            rejects(lambda: finish(graph, host), "replayed completed arrival", match="No prepared review")
            require(state_files(host.instances["alpha"]) == completed, "replayed arrival changed completed state")

    with fixture() as (_, _, graph, host):
        checkpoint = prepare(graph, host)
        host.verified = False
        rejects(lambda: run_cycle(graph, resume(host), checkpoint, act=host), "failed verification", match="Record read-back did not pass")
        host.verified = True
        finish(graph, host)
        require(host.events.count("write-record") == 1 and host.events.count("write-index") == 1,
                "verification retry repeated the external file writes")


def _writer_and_input_conflicts() -> None:
    with fixture() as (_, _, graph, host):
        checkpoint = prepare(graph, host)
        root = host.instances["alpha"]
        retained = state_files(root)
        host.active_writer = "another-writer"
        rejects(lambda: run_cycle(graph, resume(host), checkpoint, act=host), "writer conflict", match="writer_conflict")
        require(state_files(root) == retained, "writer conflict changed files")
        host.active_writer = "agent"
        policy = root / "state/policy/priority.json"
        original_policy = policy.read_bytes()
        changed = json.loads(original_policy)
        changed["term"] = "changed"
        policy.write_bytes(json_bytes(changed))
        before = state_files(root)
        rejects(lambda: run_cycle(graph, resume(host), checkpoint, act=host), "changed prepared inputs", match="input_revision")
        require(state_files(root) == before, "input drift changed files")
        policy.write_bytes(original_policy)
        index = root / "state/history/index.csv"
        original_index = index.read_bytes()
        def change_index(instance: Path) -> None:
            (instance / "state/history/index.csv").write_bytes(original_index + b"\n")
        host.before_index = change_index
        rejects(lambda: run_cycle(graph, resume(host), checkpoint, act=host), "intervening edit", match="input_revision")
        require((root / "state/history/records/item-1.json").is_file(), "interrupted publication discarded its orphan")
        index.write_bytes(original_index)
        finish(graph, host)
        require("reconcile-orphan" in host.events, "explicit reconciliation did not reuse the orphan")


def _owner_and_configuration_failures() -> None:
    with fixture() as (directory, _, graph, host):
        root = host.instances["alpha"]
        rejects(lambda: run_cycle(graph, request(host, mode=""), initial_state(graph), act=host),
                "missing first-use decision", match="retention_choice")
        require(not (root / "state").exists(), "missing retention decision initialized state")
        wrong = dict(request(host).values)
        wrong["INSTANCE"] = (directory / "shared/review-items").as_posix()
        rejects(lambda: run_cycle(graph, Arrival(interface="interface.request", values=wrong), initial_state(graph), act=host),
                "source path used as instance", match="instance_owner")
        checkpoint = prepare(graph, host)
        before = state_files(root)
        for field, value in (("OWNER", "beta"), ("ID", "different-id"), ("INSTANCE", host.instances["beta"].as_posix())):
            values = {**resume(host).values, field: value}
            rejects(lambda: run_cycle(graph, Arrival(interface="interface.resume", values=values), checkpoint, act=host),
                    "wrong resume identity", match="Resume targets a different")
        rejects(lambda: run_cycle(graph, request(host, identifier="item-2"), checkpoint, act=host),
                "replacement of pending work", match="already pending")
        require(state_files(root) == before, "rejected arrivals modified pending work")
        settings = root / "state/configuration.json"
        original = settings.read_bytes()
        for field, value in (("version", 2), ("version", True), ("owner", "beta"), ("capability", "other/v1")):
            changed = json.loads(original)
            changed[field] = value
            settings.write_bytes(json_bytes(changed))
            retained = state_files(root)
            rejects(lambda: run_cycle(graph, resume(host), checkpoint, act=host), "unsupported or foreign settings")
            require(state_files(root) == retained, "invalid settings caused destructive recovery")
        settings.write_bytes(original)
        finish(graph, host)


def _index_and_record_failures() -> None:
    with fixture() as (_, _, graph, host):
        prepare(graph, host)
        finish(graph, host)
        root = host.instances["alpha"]
        index = root / "state/policy/index.csv"
        original = index.read_bytes()
        invalid = (
            (index_bytes([IndexRow("priority", "One", "priority.json"), IndexRow("priority", "Two", "priority.json")]), "index_identity"),
            (b"id,name\npriority,One\n", "index_shape"),
            (b"id,name,reference,extra\npriority,One,priority.json,bad\n", "index_shape"),
            (b'id,name,reference\npriority,"unfinished,priority.json\n', "index_shape"),
            (index_bytes([IndexRow("priority", "Missing", "absent.json")]), "record_reference"),
            (index_bytes([IndexRow("priority", "Escape", "../../../outside.json")]), "record_reference"),
            (index_bytes([IndexRow("priority", "Absolute", "C:/outside.json")]), "record_reference"),
        )
        for raw, expected in invalid:
            index.write_bytes(raw)
            before = state_files(root)
            rejects(lambda: prepare(graph, host, identifier="item-2"), "invalid index", match=expected)
            require(state_files(root) == before, "invalid index triggered a repair write")
        index.write_bytes(original)
        record = root / "state/policy/priority.json"
        original_record = record.read_bytes()
        for field, value in (("version", True), ("writer", "tool"), ("owner", "beta"), ("id", "other")):
            changed = json.loads(original_record)
            changed[field] = value
            record.write_bytes(json_bytes(changed))
            rejects(lambda: prepare(graph, host, identifier="item-2"), "foreign policy", match="policy_identity")
        record.write_bytes(original_record)
        alternate = root / "state/policy/alternate.json"
        alternate.write_bytes(original_record)
        index.write_bytes(index_bytes([IndexRow("priority", 'Quoted, "policy"', "alternate.json")]))
        prepare(graph, host, identifier="item-2")
        finish(graph, host, identifier="item-2")
        evidence = json.loads((root / "state/history/records/item-2.json").read_bytes())
        require(evidence["policy"] == "state/policy/alternate.json", "record invented its policy reference from an id")
        alias = root / "state/policy/alias.json"
        try:
            alias.symlink_to(alternate)
        except (OSError, NotImplementedError):
            pass
        else:
            index.write_bytes(index_bytes([IndexRow("priority", "Linked", "alias.json")]))
            rejects(lambda: prepare(graph, host, identifier="item-3"), "symbolic record reference", match="symbolic links")


def _retention_and_protected_records() -> None:
    with fixture() as (_, _, graph, host):
        prepare(graph, host, mode="full")
        root = host.instances["alpha"]
        pending = (root / "state/runs/pending.json").read_bytes()
        policy = (root / "state/policy/priority.json").read_bytes()
        settings = json.loads((root / "state/configuration.json").read_bytes())
        settings["retention"] = "summary"
        (root / "state/configuration.json").write_bytes(json_bytes(settings))
        require((root / "state/runs/pending.json").read_bytes() == pending, "future retention change rewrote pending input")
        receipt = root / "state/runs/tool-outcome.json"
        receipt.write_bytes(json_bytes({"writer": "tool", "outcome": "synthetic verified effect"}))
        saved_receipt = receipt.read_bytes()
        index = root / "state/runs/index.csv"
        _, rows = host.rows(root, index)
        rows.append(IndexRow("tool-outcome", "Protected outcome", "tool-outcome.json"))
        index.write_bytes(index_bytes(rows))
        finish(graph, host)
        first = (root / "state/history/records/item-1.json").read_bytes()
        require("source" in json.loads(first), "future retention choice changed an already prepared record")
        prepare(graph, host, identifier="item-2", mode="")
        finish(graph, host, identifier="item-2")
        require("source" not in json.loads((root / "state/history/records/item-2.json").read_bytes()), "saved summary choice was not applied")
        require((root / "state/history/records/item-1.json").read_bytes() == first
                and (root / "state/policy/priority.json").read_bytes() == policy and receipt.read_bytes() == saved_receipt,
                "retention or checkpoint update lost existing evidence")
        _, rows = host.rows(root, index)
        require(any(row.id == "tool-outcome" for row in rows), "checkpoint publication removed a protected run index entry")
        checkpoint = prepare(graph, host, identifier="item-3")
        protected = root / "state/history/records/item-3.json"
        protected.write_bytes(json_bytes({"writer": "tool", "id": "item-3"}))
        before = protected.read_bytes()
        rejects(lambda: run_cycle(graph, resume(host, identifier="item-3"), checkpoint, act=host), "protected record collision", match="record_conflict")
        require(protected.read_bytes() == before, "agent rewrote a tool-owned record")


def _bounded_loading_and_effect_reconciliation() -> None:
    with fixture() as (_, _, graph, host):
        prepare(graph, host)
        finish(graph, host)
        root = host.instances["alpha"]
        unselected = root / "state/history/records/unselected.json"
        unselected.write_bytes(b'{"synthetic":"unselected private content"}\n')
        index = root / "state/history/index.csv"
        index.write_bytes(index.read_bytes() + index_bytes([IndexRow("unselected", "Unread", "records/unselected.json")], header=False))
        host.reads.clear()
        checkpoint = prepare(graph, host, identifier="item-2")
        require("state/history/records/unselected.json" not in host.reads, "index-first loading read an unselected record")
        effects: list[str] = []
        def external_effect(instance: Path) -> None:
            effects.append("effect")
            (instance / "state/runs/effect.json").write_bytes(json_bytes({"writer": "tool", "outcome": "simulated"}))
        host.before_index = external_effect
        host.interrupt_at = "index"
        rejects(lambda: run_cycle(graph, resume(host, identifier="item-2"), checkpoint, act=host), "uncertain effect interruption", match="fixture interruption")
        receipt = (root / "state/runs/effect.json").read_bytes()
        finish(graph, host, identifier="item-2")
        require(effects == ["effect"] and (root / "state/runs/effect.json").read_bytes() == receipt,
                "recovery replayed or rewrote a simulated external effect")


def _git_policies() -> None:
    with fixture() as (_, _, graph, host):
        prepare(graph, host)
        finish(graph, host)
        root = host.instances["alpha"]
        subprocess.run(["git", "add", "-f", "--", "state/configuration.json"], cwd=root, check=True)
        before = state_files(root)
        rejects(lambda: prepare(graph, host, identifier="item-2"), "tracked private state", match="git_tracking")
        require(state_files(root) == before, "tracked-state conflict changed files")
    with fixture() as (repository, _, graph, host):
        prepare(graph, host)
        finish(graph, host)
        root = host.instances["alpha"]
        host.shared_paths["alpha"] = frozenset({"state/policy/index.csv", "state/policy/priority.json"})
        (root / ".gitignore").write_bytes(b"/state/*\n!/state/policy/\n/state/policy/*\n!/state/policy/index.csv\n!/state/policy/priority.json\n")
        prepare(graph, host, identifier="item-2")
        finish(graph, host, identifier="item-2")
        subprocess.run(["git", "add", "--", "state/policy/index.csv", "state/policy/priority.json"], cwd=root, check=True)
        prepare(graph, host, identifier="item-3")
        finish(graph, host, identifier="item-3")
        (repository / ".gitignore").write_bytes(b"/instances/alpha/\n")
        rejects(lambda: prepare(graph, host, identifier="item-4"), "inherited exclusion conflict", match="git_exclusion")


def validate_memory_cases() -> None:
    _interrupted_updates()
    _writer_and_input_conflicts()
    _owner_and_configuration_failures()
    _index_and_record_failures()
    _retention_and_protected_records()
    _bounded_loading_and_effect_reconciliation()
    _git_policies()
