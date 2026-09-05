"""Shared, part-ordered authoring knowledge and its native OAK workflow.

The same generated knowledge documents are loaded by the skill and consumed by
fusion. Package rules and working examples remain their original source owners.
"""

from pathlib import Path

from oak import (ACT, BindingValue, Call, Compare, Constant, ConstantValue, Emit,
                 If, Interface, LiteralValue, Node, NonEmpty, Process,
                 Schema, Trigger, Type, ValueBinding, parse, render, where)
from oak.rules import AUTHORING_GUIDANCE
from examples.catalog import teaching_examples
from examples.schemas.shape_gallery import EXPECTED_INSTANCES, SHAPES, shape_gallery_node
from build.ebnf import grammar

ROOT = Path(__file__).resolve().parents[1]
GUIDES = (
    "00-structure", "01-schemas", "02-constants", "03-state", "04-interfaces",
    "05-triggers", "06-processes", "07-instructions", "08-review", "09-validation",
)
# Each package authoring rule has one guide owner, not an instruction copy.
RULE_OWNERS = (
    ("treat-context", "omit-unjustified", "avoid-invention", "preserve-node", "reuse-domain", "keep-host-boundary"),
    ("map-schemas", "choose-schema-shape", "preserve-schema-shape", "separate-template-instance", "respect-schema-cardinality", "bind-values"),
    ("map-constants",),
    ("map-state", "separate-lifetimes", "keep-local-values"),
    ("map-interfaces", "emit-complete"),
    ("map-triggers", "route-receive", "declare-triggers"),
    ("map-processes", "name-process", "contract-work", "describe-action-roles", "distinguish-action-promises", "compose-work", "use-native-act", "use-exact-tool", "parallelize-tools", "delegate-document", "compose-conditions", "separate-layout"),
    ("map-instructions",),
    ("write-document",),
    ("validate-draft", "emit-document"),
)


def owned_constant(path: str, identifier: str) -> Constant:
    """Read an explicit repository owner; AGENTS scoping is not an OAK import."""
    node = parse((ROOT / path).read_text(encoding="utf-8"))
    return next(item for item in node.constants if item.id == identifier)


def populated_examples() -> str:
    """Keep table, hierarchy, sections, and code visible instead of YAML-escaped."""
    return "\n\n".join(f"{schema.name}\n{EXPECTED_INSTANCES[schema.id]}" for schema in SHAPES)


def knowledge_nodes(script: str, version: str, revision: str) -> dict[str, Node]:
    """Build focused OAK guides with no operational or authored policy scope."""
    rules = {item.id: item.instruction for item in AUTHORING_GUIDANCE}
    constants = [[Constant(id="guidance", form="yaml", value=[rules[key] for key in keys])] for keys in RULE_OWNERS]
    constants[0] += [
        owned_constant("AGENTS.md", "part-authoring-priority"),
        owned_constant("oak/node/AGENTS.md", "part-order"),
        owned_constant("oak/node/AGENTS.md", "part-responsibilities"),
        owned_constant("oak/AGENTS.md", "host-boundary"),
        Constant(id="reading", form="text", value=(
            "Load needed guides in authoring order, not render order. The entry routes work; "
            "supporting files supply fixed knowledge and reusable shapes. Omit empty parts. "
            "Select complete scenarios via references/examples/catalog.oak.md. The assembled agent "
            "has identical knowledge with local targets. Authoring and interpretation of either "
            "form need no Python, package, network, or validator.")),
    ]
    constants[1] += [Constant(id="populated-shapes", form="text", value=populated_examples()),
                     Constant(id="shape-notes", form="text", value=(
                         "populated-shapes shows filled instances of these four reusable schemas without WHERE "
                         "or schema wrappers. The one-row table is fixed-cardinality. Extend templates explicitly "
                         "when justified; apply the schema guidance above."))]
    constants[2].append(Constant(id="forms", form="csv", value=[
        {"form": form, "use": use} for form, use in (
            ("JSON", "short fixed scalars, arrays, or objects"),
            ("TEXT", "verbatim fixed text"), ("CSV", "tabular fixed knowledge"),
            ("YAML", "readable structured fixed knowledge"),
        )
    ]))
    constants[3] += [owned_constant("oak/node/AGENTS.md", "value-lifetimes"),
                     Constant(id="omission", value="A draft or pipeline intermediate is not state. Omit state unless a later arrival must observe a changed value.")]
    constants[4].append(Constant(id="boundaries", value="Reuse an existing schema at a boundary; do not redefine its shape inside the interface. Interface instances are not ambient mutable storage."))
    constants[5].append(Constant(id="routing", value="An event describes an outside occurrence. An optional source identifies one receiving interface; its schema must resolve identically to process input, with no seeds. A guard requires a state read and may compare literals or fixed constants; it cannot read process bindings. Internal work uses CALL, never triggers."))
    constants[6].append(Constant(id="scopes", form="text", value=(
        "Bindings are immutable per frame. CALL promotes declared outputs; branches and iterations "
        "have local scope. IF never promotes child outputs. EMIT in the branch or use process "
        "contracts, not invented state. Assertions, conditions, loops, and parallel steps need "
        "source-justified semantics.")))
    constants[7].append(Constant(id="last-decision", value="After the other six responsibilities are represented, ask what meaning remains. Keep only that irreducible policy in instructions. Generated interpretation guidance is derived from the node; do not author copies of it."))
    examples = teaching_examples()
    constants[8] += [
        Constant(id="review", form="yaml", value=[
            "Check one idless node, unique entry ids, canonical section order, and omission of unjustified parts.",
            "Check exact local and relative targets, complete schema bindings, data lifetimes, and native versus named tool work.",
            "Read populated output, not only the schema definition. Check actual layout, code fences, and cardinality.",
            "The grammar describes syntax. Human review is not a claim of programmatic validation.",
            "The examples are fixed teaching data, not additional agents or outside entry points to execute.",
        ]),
        Constant(id="oak-ebnf", form="text", value=grammar().rstrip("\n")),
        # JSON strings preserve nested OAK block delimiters verbatim as inert data.
        Constant(id="teaching", form="json", value=examples),
    ]
    constants[9] += [
        Constant(id="identity", value={"version": version, "validator-revision": revision}),
        Constant(id="validation-policy", form="yaml", value=[
            "Run programmatic validation only when the user requests it. Authoring and interpretation need no installation.",
            "The script uses Python 3.11 or newer. Reuse a matching installed validator, an explicit --source and optional --python, or its retained cache. The source fingerprint must match, not just the package name or version.",
            "Use scripts/validate.py from the skill. In the standalone agent, materialize validator-script exactly as a local validate.py only when validation is requested.",
            "First run: python validate.py document.oak.md. Use --root for a larger explicitly allowed document graph. In the skill directory the script path is scripts/validate.py.",
            "When the result says permission-required, ask permission to download the identified OAK revision and install its declared dependencies in an isolated cached environment. Requesting validation is not installation consent.",
            "Only after explicit approval, repeat the command with --allow-install. No published OAK package is needed. Keep the matching installation for future requests.",
            "When installation is declined, continue authoring and say: Programmatic validation was not performed (installation declined). Do not run the installer.",
            "When Python, network, dependencies, or execution are unavailable, continue authoring and state the actual reason validation was not performed.",
            "Exit 0 means parse and resolution checks passed, 1 means invalid, and 2 means not performed. Report the actual checks, revision, and errors; never imply execution or semantic correctness was proved.",
            "Keep validation status outside the authored OAK document. Repair reported authoring errors and recheck only under the same user permission. Do not silently switch validator revisions.",
        ]),
        Constant(id="validator-script", form="text", value=script.rstrip("\n")),
    ]
    return {f"references/{name}.oak.md": Node(constants=items, schemas=list(SHAPES) if index == 1 else [])
            for index, (name, items) in enumerate(zip(GUIDES, constants, strict=True))}


def local(name: str) -> ValueBinding:
    return ValueBinding(placeholder=name, value=BindingValue(binding=name))


def knowledge(name: str, guide: int, identifier: str = "guidance") -> ValueBinding:
    return ValueBinding(placeholder=name, value=ConstantValue(constant=f"references/{GUIDES[guide]}.oak.md#constant.{identifier}"))


def shape(identifier: str, fields: tuple[str, ...], *, boolean: str | None = None) -> Schema:
    return Schema(id=identifier, template="\n".join(f"{key}: <{key}>" for key in fields), where=[
        where(key, Type(of="boolean")) if key == boolean else where(key, Type(of="string"), NonEmpty()) for key in fields
    ])


def finish_validation(approved: bool) -> Call:
    return Call(process="process.finalize-validation", inputs=[
        local("CANDIDATE"), local("REPORT"),
        ValueBinding(placeholder="ALLOW_INSTALL", value=LiteralValue(value=approved)),
    ])


def entry_node() -> Node:
    """One operational scope for progressive loading and standalone assembly."""
    steps = [ACT(
        "Use <STRUCTURE> and the complete supplied <SOURCE> to establish <SCOPE>; consult the rest of that structure guide only as needed.",
        inputs=[knowledge("STRUCTURE", 0), local("SOURCE")], outputs=["SCOPE"],
    )]
    previous = "SCOPE"
    for index, (part, guide) in enumerate((("schemas", 1), ("constants", 2), ("state", 3), ("interfaces", 4), ("triggers", 5), ("processes", 6), ("instructions", 7))):
        result = f"DESIGN_{index + 1}"
        text = f"Apply <GUIDANCE> to <{previous}> and <SOURCE> to decide {part}; omit unjustified entries and produce <{result}>."
        bindings = [knowledge("GUIDANCE", guide), local(previous), local("SOURCE")]
        if guide == 1:
            text += " Use the supplied schema definitions and their <POPULATED> instances to preserve the requested information shape."
            bindings.append(knowledge("POPULATED", 1, "populated-shapes"))
        steps.append(ACT(text, inputs=bindings, outputs=[result]))
        previous = result
    steps += [
        ACT("Review <DESIGN_7> against <REVIEW>, <GRAMMAR>, and the complete scenarios in <TEACHING>. Produce <CANDIDATE> as one OAK node in canonical section order, without claiming a programmatic check.",
            inputs=[local("DESIGN_7"), knowledge("REVIEW", 8, "review"), knowledge("GRAMMAR", 8, "oak-ebnf"), knowledge("TEACHING", 8, "teaching")], outputs=["CANDIDATE"]),
        If(condition=Compare(left=BindingValue(binding="VALIDATE"), operator="equals", right=LiteralValue(value=True)),
           then=[Call(process="process.validate-and-deliver", inputs=[local("CANDIDATE")])],
           otherwise=[Emit(interface="interface.authored-document", bindings=[
               ValueBinding(placeholder="OAK", value=BindingValue(binding="CANDIDATE")),
               ValueBinding(placeholder="VALIDATION", value=LiteralValue(value="Programmatic validation was not performed (not requested).")),
           ])]),
    ]
    return Node(
        schemas=[shape("authoring-request", ("SOURCE", "VALIDATE"), boolean="VALIDATE"),
                 shape("oak-candidate", ("CANDIDATE",)), shape("authoring-result", ("OAK", "VALIDATION")),
                 shape("validator-check", ("INSTALL_REQUIRED", "REPORT"), boolean="INSTALL_REQUIRED"),
                 shape("installation-consent", ("APPROVED",), boolean="APPROVED"),
                 shape("validation-context", ("CANDIDATE", "REPORT", "ALLOW_INSTALL"), boolean="ALLOW_INSTALL")],
        triggers=[
            Trigger(id="authoring-requested", event="OAK authoring is requested for supplied source material.", process="process.capture-request"),
            Trigger(id="request-received", event="A complete OAK authoring request is received.", source="interface.authoring-input", process="process.author-document"),
        ],
        processes=[
            Process(id="capture-request", name="Capture request", steps=[
                ACT("Capture the complete supplied source as <SOURCE> and set <VALIDATE> true only when programmatic validation was requested; otherwise false.",
                    output="schema.authoring-request", outputs=["SOURCE", "VALIDATE"]),
                Call(process="process.author-document", inputs=[local("SOURCE"), local("VALIDATE")]),
            ]),
            Process(id="author-document", name="Author document", input="schema.authoring-request", steps=steps),
            Process(id="validate-and-deliver", name="Check validator", input="schema.oak-candidate", steps=[
                ACT("Apply <POLICY> to check <CANDIDATE> with the exact <HELPER> without --allow-install. Reuse matching code when available. Return the actual <REPORT> and set <INSTALL_REQUIRED> true only for permission-required, not for invalid OAK or an unavailable execution tool.",
                    output="schema.validator-check", inputs=[knowledge("POLICY", 9, "validation-policy"), knowledge("HELPER", 9, "validator-script"), local("CANDIDATE")], outputs=["INSTALL_REQUIRED", "REPORT"]),
                If(condition=Compare(left=BindingValue(binding="INSTALL_REQUIRED"), operator="equals", right=LiteralValue(value=True)),
                   then=[
                       ACT("Ask the user for permission to download the OAK revision in <IDENTITY> and install its dependencies in an isolated retained environment. Set <APPROVED> true only after explicit approval; a validation request alone is not approval.",
                           output="schema.installation-consent", inputs=[knowledge("IDENTITY", 9, "identity")], outputs=["APPROVED"]),
                       If(condition=Compare(left=BindingValue(binding="APPROVED"), operator="equals", right=LiteralValue(value=True)),
                          then=[finish_validation(True)],
                          otherwise=[Emit(interface="interface.authored-document", bindings=[
                              ValueBinding(placeholder="OAK", value=BindingValue(binding="CANDIDATE")),
                              ValueBinding(placeholder="VALIDATION", value=LiteralValue(value="Programmatic validation was not performed (installation declined).")),
                          ])]),
                   ], otherwise=[finish_validation(False)]),
            ]),
            Process(id="finalize-validation", name="Report validation", input="schema.validation-context", steps=[
                ACT("Use <REPORT> for <CANDIDATE> under <POLICY>. With <ALLOW_INSTALL> true, run the exact <HELPER> with --allow-install; otherwise never download or install. Repair reported authoring errors when possible and recheck changed documents under the same permission. Do not rerun an unchanged successful check. Produce <OAK> and truthful <VALIDATION>, including errors or why a check could not run.",
                    output="schema.authoring-result", inputs=[local("REPORT"), local("CANDIDATE"), local("ALLOW_INSTALL"), knowledge("POLICY", 9, "validation-policy"), knowledge("HELPER", 9, "validator-script")], outputs=["OAK", "VALIDATION"]),
                Emit(interface="interface.authored-document"),
            ]),
        ],
        interfaces=[Interface(id="authoring-input", flow="receives", schema="schema.authoring-request"),
                    Interface(id="authored-document", flow="emits", schema="schema.authoring-result")],
    )
