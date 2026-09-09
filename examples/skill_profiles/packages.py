"""Inert install-shaped package specimens from the shared template foundation."""

from pathlib import Path

from oak import BindingValue, Call, Constant, Emit, Interface, Node, Process, Trigger, ValueBinding, parse, render
from build.skill_template import Profile, Resource, ResourceKind, populate
from . import classifier, example, memory

CLASSIFY_RESOURCES = (
    Resource("SKILL.md", "Stateless entry, task index and complete package map"),
    Resource("processes/classify-item.oak.md", "Typed reusable classification",
             "Classify supplied text against the supplied term"),
)
REVIEW_RESOURCES = (
    Resource("SKILL.md", "Shared review entry, lifecycle and complete package map"),
    Resource("references/memory.oak.md", "Memory shapes, authority and interrupted-update practice",
             "Before binding or publishing one selected local instance"),
    Resource("../classify-item/processes/classify-item.oak.md", "Separate approved classifier",
             "Classify prepared text through its declared process contract", ResourceKind.DEPENDENCY),
    Resource(".gitignore", "Instance exclusions, verified separately from saved settings", kind=ResourceKind.SCAFFOLD),
    Resource("state/configuration.json", "Saved owner, capability and future-record retention", kind=ResourceKind.SCAFFOLD),
    Resource("state/policy/index.csv", "Policy lookup", kind=ResourceKind.SCAFFOLD),
    Resource("state/policy/priority.json", "Synthetic priority policy seed", kind=ResourceKind.SCAFFOLD),
    Resource("state/policy/(...)", "Generated learned policy records", kind=ResourceKind.GENERATED),
    Resource("state/history/index.csv", "Reviewed evidence lookup", kind=ResourceKind.SCAFFOLD),
    Resource("state/history/records/(...)", "Generated reviewed records", kind=ResourceKind.GENERATED),
    Resource("state/runs/index.csv", "Pending checkpoint lookup", kind=ResourceKind.SCAFFOLD),
    Resource("state/runs/(...)", "Generated checkpoints and protected host records", kind=ResourceKind.GENERATED),
)


def classify_entry() -> Node:
    request_process = Process(id="classify-item", name="Classify item", input="schema.item", body=[
        Call(process="processes/classify-item.oak.md#process.classify",
             inputs=[ValueBinding(placeholder=name, value=BindingValue(binding=name)) for name in ("TEXT", "TERM")],
             outputs=["CATEGORY"]),
        Emit(interface="interface.result"),
    ])
    return Node(
        schemas=[classifier.item_schema, classifier.category_schema], processes=[request_process],
        triggers=[Trigger(id="classification-requested", event="An item classification is requested.",
                          source="interface.request", process="process.classify-item")],
        interfaces=[
            Interface(id="request", flow="receives", schema="schema.item", description="Request a category from supplied text and policy without file access."),
            Interface(id="result", flow="emits", schema="schema.category", description="Return the validated category without external effects."),
        ],
    )


def package_files() -> dict[str, dict[str, str]]:
    """Return shared functional files only; the host separately creates instance scaffolds."""
    stateless = populate(
        Profile.STATELESS, classify_entry(), CLASSIFY_RESOURCES, name="classify-item",
        description="Classify supplied text against a supplied term without reading or changing files.",
        title="Classify an item", purpose="Return one category from explicit inputs.",
        principle="Classify only the supplied text and term.",
        roles={"DEFINE": "metadata, constant.title, constant.purpose and constant.principle", "LOOP": "process.classify-item",
               "INDEX": "constant.index", "MAP": "constant.layout", "ASSERT": "schema.category and interface.result"},
    )
    stateful = populate(
        Profile.STATEFUL, example.review_node("../classify-item/processes/classify-item.oak.md", "references/memory.oak.md"),
        REVIEW_RESOURCES, name="review-items",
        description="Prepare and resume synthetic item reviews with explicitly owned local indexed memory.",
        title="Review items", purpose="Publish reviewed evidence while preserving policy, pending work and shared source.",
        principle="Bind one owner, prepare once and reconcile before publishing.",
        roles={"DEFINE": "metadata, constant.title, constant.purpose, constant.principle and constant.capability",
               "ROUTE": "interface.request, interface.resume and the explicit classifier dependency",
               "LOOP": "process.prepare-review and process.publish-review", "INDEX": "constant.index",
               "MAP": "constant.layout", "ASSERT": "identity assertions, schema.read-back and interface.result"},
    )
    return {
        "classify-item": {"SKILL.md": stateless, "processes/classify-item.oak.md": classifier.build()},
        "review-items": {"SKILL.md": stateful, "references/memory.oak.md": memory.build()},
    }


TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    node = Node(constants=[
        Constant(id="packages", form="json", value=package_files()),
        Constant(id="boundary", value=(
            "These complete file mappings are inert specimens, never nested installed skills. The review package "
            "declares the separate classify-item export as its only operational dependency. Resolve both only "
            "inside the explicitly approved fixture root; do not copy the classifier into the review package. "
            "The host creates the MAP's fixed local scaffolds on first use; shared updates omit those paths.")),
    ])
    text = render(node)
    if render(parse(text)) != text:
        raise RuntimeError("package specimens changed during rendering")
    return text


def write() -> Path:
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET
