"""Prepare and resume one synthetic review with instance-local indexed memory.

The host binds a separate instance root, serializes writers and persists returned
checkpoints. Native actions describe ordinary file work, not a supplied runtime.
Repository fixtures execute these contracts using disposable files and fixed inputs.
"""

from pathlib import Path

from oak import (
    ACT, Any, Assert, BindingValue, Call, Compare, Constant, ConstantValue, Emit, Interface,
    LiteralValue, Node, NonEmpty, OneOf, Process, Regex, Schema, Set, State, StateValue,
    Trigger, Type, Value, ValueBinding, parse, render, resolve, where,
)
from . import classifier, memory

CAPABILITY = "review-items/v1"
_IDENTIFIER = r"^[a-z0-9][a-z0-9\-]{0,63}$"

request_schema = Schema(
    id="review-request", purpose="Prepare one review for an explicitly selected owner and local instance.",
    template="Owner: <OWNER>\nInstance: <INSTANCE>\nRecord: <ID>\nText: <TEXT>\nPolicy: <POLICY_ID>\nRetention: <RETENTION>",
    where=[where(name, Type(of="string"), Regex(pattern=_IDENTIFIER)) for name in ("OWNER", "ID", "POLICY_ID")]
    + [where(name, Type(of="string"), NonEmpty()) for name in ("INSTANCE", "TEXT")]
    + [where("RETENTION", Type(of="string"), OneOf(values=["", "full", "summary"]),
             description="empty reuses a saved choice and requires a decision when none exists")],
)
resume_schema = Schema(
    id="resume-request", purpose="Publish only the pending review belonging to this owner and instance.",
    template="Owner: <OWNER>\nInstance: <INSTANCE>\nRecord: <ID>",
    where=[where(name, Type(of="string"), NonEmpty()) for name in ("OWNER", "INSTANCE", "ID")],
)
preparation_schema = Schema(
    id="preparation", purpose="Return inspected policy and the actual selected-input fingerprint.",
    template="Term: <TERM>\nRetention: <MODE>\nSnapshot: <SNAPSHOT>",
    where=[where("TERM", Type(of="string"), NonEmpty()),
           where("MODE", Type(of="string"), OneOf(values=["full", "summary"])),
           where("SNAPSHOT", Type(of="string"), NonEmpty())],
)
checkpoint_schema = Schema(
    id="checkpoint", purpose="Retain the exact pending work across host-driven arrivals.",
    template="Owner: <OWNER>\nInstance: <INSTANCE>\nPhase: <PHASE>\nRecord: <ID>\nText: <TEXT>\nPolicy: <POLICY_ID>\nCategory: <CATEGORY>\nRetention: <MODE>\nSnapshot: <SNAPSHOT>",
    where=[where(name, Type(of="string")) for name in ("OWNER", "INSTANCE", "ID", "TEXT", "POLICY_ID", "SNAPSHOT")]
    + [where("PHASE", Type(of="string"), OneOf(values=["idle", "prepared"])),
       where("CATEGORY", Type(of="string"), OneOf(values=["", "match", "other"])),
       where("MODE", Type(of="string"), OneOf(values=["", "full", "summary"]))],
)
receipt_schema = Schema(
    id="read-back", purpose="Report the actual file pair after reconciliation and read-back.",
    template="Reference: <REFERENCE>\nDigest: <SHA256>\nVerified: <VERIFIED>",
    where=[where("REFERENCE", Type(of="string"), NonEmpty()),
           where("SHA256", Type(of="string"), Regex(pattern="^[0-9a-f]{64}$")),
           where("VERIFIED", Type(of="boolean"))],
)
progress_schema = Schema(
    id="review-progress", purpose="Report preparation without claiming record publication.",
    template="Prepared: <ID>", where=[where("ID", Type(of="string"), NonEmpty())],
)
result_schema = Schema(
    id="review-result", purpose="Return a reviewed record only after successful file-pair verification.",
    template="Owner: <OWNER>\nRecord: <ID>\nCategory: <CATEGORY>\nReference: <REFERENCE>\nDigest: <SHA256>",
    where=[where(name, Type(of="string"), NonEmpty()) for name in ("OWNER", "ID", "REFERENCE")]
    + [where("CATEGORY", Type(of="string"), OneOf(values=["match", "other"])),
       where("SHA256", Type(of="string"), Regex(pattern="^[0-9a-f]{64}$"))],
)


def _local(name: str) -> BindingValue:
    return BindingValue(binding=name)


def _state(name: str) -> StateValue:
    return StateValue(state="state." + name.lower().replace("_", "-"))


def _bindings(**values: Value) -> list[ValueBinding]:
    return [ValueBinding(placeholder=name, value=value) for name, value in values.items()]


def _equals(left: Value, right: Value) -> Compare:
    return Compare(left=left, operator="equals", right=right)


def review_node(classifier_path: str = "classifier.oak.md", memory_path: str = "memory.oak.md") -> Node:
    """Keep logical work identical while declaring the supplied dependency locations."""
    bind_action = ACT(
        "Bind <OWNER>/<CAPABILITY> to explicit <INSTANCE> under <MEMORY>. Reuse saved retention or require an actual first-use <RETENTION> choice. Verify actual Git exclusions and tracked status, read only <POLICY_ID> through its index, refuse a reused <ID>, and return <TERM>, <MODE> and observed <SNAPSHOT>. Never overwrite an existing instance or use the shared source path as its root.",
        output="schema.preparation", inputs=[
            *_bindings(**{name: _local(name) for name in ("OWNER", "INSTANCE", "ID", "POLICY_ID", "RETENTION")}),
            *_bindings(CAPABILITY=ConstantValue(constant="constant.capability"),
                       MEMORY=ConstantValue(constant=memory_path + "#constant.workflow")),
        ], outputs=["TERM", "MODE", "SNAPSHOT"],
    )
    classify_call = Call(
        process=classifier_path + "#process.classify", inputs=_bindings(TEXT=_local("TEXT"), TERM=_local("TERM")),
        outputs=["CATEGORY"],
    )
    retain = [Set(state="state." + name.lower().replace("_", "-"), value=_local(name))
              for name in ("OWNER", "INSTANCE", "ID", "TEXT", "POLICY_ID", "CATEGORY", "MODE", "SNAPSHOT")]
    prepare_process = Process(id="prepare-review", name="Prepare review", input="schema.review-request", body=[
        Assert(condition=_equals(_state("PHASE"), LiteralValue(value="idle")), message="A review is already pending."),
        *[Assert(condition=Any(conditions=[_equals(_state(name), LiteralValue(value="")),
                                         _equals(_state(name), _local(name))]),
                 message="The checkpoint belongs to another " + name.lower() + ".") for name in ("OWNER", "INSTANCE")],
        bind_action, classify_call, *retain,
        Set(state="state.phase", value=LiteralValue(value="prepared")),
        Emit(interface="interface.progress", bindings=_bindings(ID=_local("ID"))),
    ])
    publish_action = ACT(
        "Reconcile and publish pending <ID> for <OWNER>/<CAPABILITY> in <INSTANCE> under <MEMORY>. Check <SNAPSHOT>, one writer, <POLICY_ID> and saved <MODE>. Write the JSON record for <TEXT>/<CATEGORY> before its stable CSV index row; resume an exact orphan or verify an exact published pair without rewriting it. Preserve pending and tool-owned records. Return <REFERENCE>, computed <SHA256> and <VERIFIED> from actual read-back; an unknown conflict must fail.",
        output="schema.read-back", inputs=[
            *_bindings(**{name: _state(name) for name in ("OWNER", "INSTANCE", "ID", "TEXT", "POLICY_ID", "CATEGORY", "MODE", "SNAPSHOT")}),
            *_bindings(CAPABILITY=ConstantValue(constant="constant.capability"),
                       MEMORY=ConstantValue(constant=memory_path + "#constant.workflow")),
        ], outputs=["REFERENCE", "SHA256", "VERIFIED"],
    )
    publish_process = Process(id="publish-review", name="Publish review", input="schema.resume-request", body=[
        Assert(condition=_equals(_state("PHASE"), LiteralValue(value="prepared")), message="No prepared review can resume."),
        *[Assert(condition=_equals(_state(name), _local(name)), message="Resume targets a different " + name.lower() + ".")
          for name in ("OWNER", "INSTANCE", "ID")],
        publish_action,
        Assert(condition=_equals(_local("VERIFIED"), LiteralValue(value=True)), message="Record read-back did not pass."),
        Emit(interface="interface.result", bindings=[
            *_bindings(OWNER=_state("OWNER"), ID=_state("ID"), CATEGORY=_state("CATEGORY")),
            *_bindings(REFERENCE=_local("REFERENCE"), SHA256=_local("SHA256")),
        ]),
        Set(state="state.phase", value=LiteralValue(value="idle")),
        *[Set(state="state." + name.lower().replace("_", "-"), value=LiteralValue(value=""))
          for name in ("ID", "TEXT", "POLICY_ID", "CATEGORY", "MODE", "SNAPSHOT")],
    ])
    return Node(
        constants=[Constant(id="capability", value=CAPABILITY), Constant(id="host-boundary", value=(
            "The host serializes arrivals and writers, binds local instance roots, and durably stores only successful "
            "returned checkpoints. Shared OAK declarations are initial values, never rewritten after a run. "
            "Schema validity is not file or effect verification."))],
        schemas=[request_schema, resume_schema, preparation_schema, checkpoint_schema, receipt_schema, progress_schema, result_schema],
        state=[State(id=name.lower().replace("_", "-"), schema="schema.checkpoint", placeholder=name,
                     value="idle" if name == "PHASE" else "")
               for name in ("OWNER", "INSTANCE", "PHASE", "ID", "TEXT", "POLICY_ID", "CATEGORY", "MODE", "SNAPSHOT")],
        triggers=[
            Trigger(id="review-requested", event="A review is requested.", source="interface.request", process="process.prepare-review"),
            Trigger(id="review-resumed", event="A prepared review is resumed.", source="interface.resume", process="process.publish-review"),
        ], processes=[prepare_process, publish_process], interfaces=[
            Interface(id="request", flow="receives", schema="schema.review-request", description="Prepare only this owner and instance, without publishing a completed review."),
            Interface(id="resume", flow="receives", schema="schema.resume-request", description="Resume this exact pending review; completion is rejected if identity or inputs changed."),
            Interface(id="progress", flow="emits", schema="schema.review-progress", description="The host persists the returned checkpoint before acknowledging preparation."),
            Interface(id="result", flow="emits", schema="schema.review-result", description="Return a verified record reference; delivery and external effects remain host responsibilities."),
        ],
    )


TARGET = Path(__file__).with_suffix(".oak.md")


def sample() -> Node:
    return Node(constants=[
        Constant(id="request", value={"OWNER": "alpha", "INSTANCE": "instances/alpha", "ID": "item-1",
                                      "TEXT": "Urgent: review the synthetic item", "POLICY_ID": "priority", "RETENTION": "summary"}),
        Constant(id="expected", value={"category": "match", "reference": "state/history/records/item-1.json",
                                       "mode": "summary", "contains-source-text": False}),
        Constant(id="host", value="Repository fixtures use disposable instances and a deterministic normal-file adapter. No live model, user state, installation or external service is involved."),
    ])


def build() -> str:
    text = render(review_node())
    documents = {"example.oak.md": text, "classifier.oak.md": classifier.build(), "memory.oak.md": memory.build()}
    resolve(parse(text), source="example.oak.md", load=documents.get)
    if render(parse(text)) != text:
        raise RuntimeError("review workflow changed during rendering")
    return text


def write() -> Path:
    classifier.write()
    memory.write()
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    TARGET.parent.joinpath("sample.oak.md").write_text(render(sample()), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
