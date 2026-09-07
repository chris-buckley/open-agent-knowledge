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
    "references/00-structure.oak.md", "references/01-schemas.oak.md",
    "references/02-constants.oak.md", "references/03-state.oak.md",
    "references/04-interfaces.oak.md", "references/05-triggers.oak.md",
    "references/06-processes.oak.md", "references/07-instructions.oak.md",
    "guides/review.oak.md", "guides/validation.oak.md", "guides/authoring.oak.md",
)
# Each package authoring rule has one guide owner, not an instruction copy.
RULE_OWNERS = (
    ("preserve-node", "keep-host-boundary", "disclose-completeness"),
    ("map-schemas", "choose-schema-shape", "preserve-schema-shape", "separate-template-instance", "respect-schema-cardinality", "bind-values"),
    ("map-constants",),
    ("map-state", "separate-lifetimes", "keep-local-values"),
    ("map-interfaces", "emit-complete", "own-boundary-contracts", "explain-boundary-contracts"),
    ("map-triggers", "route-receive", "declare-triggers"),
    ("map-processes", "name-process", "contract-work", "describe-action-roles", "distinguish-action-promises", "compose-work", "use-native-act", "use-exact-tool", "parallelize-tools", "delegate-document", "compose-conditions", "separate-layout", "adapt-external-contracts"),
    ("map-instructions",),
    ("write-document",),
    ("validate-draft", "emit-document"),
    ("treat-context", "omit-unjustified", "avoid-invention", "reuse-domain"),
)

TEMPLATE_DIRECTORIES = ("references", "assets/constants", "assets/schemas", "guides", "processes", "scripts")
TEMPLATE_ENTRY = '''---
name: "<SKILL_NAME>"
description: "<SKILL_DESCRIPTION>"
---

<INSTRUCTIONS_PART>
<constants>
purpose: <PURPOSE_JSON>

layout: TEXT<<
SKILL_TREE:
  SKILL.md→Skill entry point
  references/→Supporting knowledge
  assets/
    constants/→Reusable fixed values
    schemas/→Reusable information shapes
  processes/→OAK workflows
  guides/→Practical guidance
  scripts/→Executable helpers
>>

<CONSTANT_ENTRIES>
</constants>
<SCHEMAS_PART>
<STATE_PART>
<TRIGGERS_PART>
<PROCESSES_PART>
<INTERFACES_PART>
'''


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
        owned_constant("oak/node/AGENTS.md", "part-order"),
        owned_constant("oak/node/AGENTS.md", "part-responsibilities"),
        owned_constant("oak/AGENTS.md", "host-boundary"),
        Constant(id="oak-ebnf", form="text", value=grammar().rstrip("\n")),
    ]
    constants[1] += [Constant(id="populated-shapes", form="text", value=populated_examples()),
                     Constant(id="shape-notes", form="text", value=(
                         "populated-shapes fills these schemas without wrappers or WHERE. "
                         "The table has one fixed row; extend its template explicitly when justified."))]
    constants[2].append(Constant(id="forms", form="csv", value=[
        {"form": form, "use": use} for form, use in (
            ("JSON", "short fixed scalars, arrays, or objects"),
            ("TEXT", "verbatim fixed text"), ("CSV", "tabular fixed knowledge"),
            ("YAML", "readable structured fixed knowledge"),
        )
    ]))
    constants[3].append(owned_constant("oak/node/AGENTS.md", "value-lifetimes"))
    constants[4].append(Constant(id="boundaries", value="Interface instances are not mutable storage."))
    constants[5].append(Constant(id="routing", value="Source-backed triggers share the receive/process schema and omit seeds. Guards require state reads, may compare literals or constants, and cannot read process bindings. Sequence internal work with CALL."))
    constants[6].append(Constant(id="scopes", form="text", value=(
        "Keep bindings immutable per frame; CALL promotes declared outputs. Branches/iterations are local. "
        "IF promotes nothing; use EMIT within it or process contracts, not invented state. "
        "Justify assertions, conditions, loops, and parallel work from source.")))
    constants[7].append(Constant(id="last-decision", value="Do not copy node-derived interpretation guidance."))
    examples = teaching_examples()
    constants[8] += [
        Constant(id="review", form="yaml", value=[
            "Check one idless node, unique ids, canonical order, and justified parts.",
            "Check targets, complete bindings, lifetimes, and native/named tools.",
            "Apply interface guidance to public promises and structure guidance to claimed knowledge closure.",
            "Inspect populated output: layout, code fences, and cardinality, not just schemas.",
            "Grammar describes syntax, not validation; review is not a programmatic check.",
            "Examples are inert teaching, not extra agents or arrivals to execute.",
        ]),
        # JSON strings preserve nested OAK block delimiters verbatim as inert data.
        Constant(id="teaching", form="json", value=examples),
    ]
    constants[9] += [
        Constant(id="identity", value={"version": version, "validator-revision": revision}),
        Constant(id="validation-policy", form="yaml", value=[
            "Validate only when requested; authoring and interpretation need no installation.",
            "Use Python 3.11+. Reuse matching installed code, --source with optional --python, or retained cache. Match the source fingerprint, not name/version.",
            "Use the skill scripts/validate.py. For requested standalone validation, materialize validator-script verbatim as validate.py.",
            "Run python validate.py document.oak.md; --root permits larger explicitly allowed graphs.",
            "On permission-required, ask to download the identified OAK revision and install its declared dependencies in an isolated cache. Validation requests are not installation consent.",
            "After explicit approval, repeat with --allow-install. Reuse the retained installation; no published OAK package is needed.",
            "If installation is declined, do not install. Continue authoring and report: Programmatic validation was not performed (installation declined).",
            "If Python, network, dependencies, or execution are unavailable, continue authoring and report the actual not-performed reason.",
            "Exit 0: parse and resolution passed; 1: invalid; 2: not performed. Report checks, revision, and errors, never proof of execution or semantic correctness.",
            "Report validation outside OAK. Repair and recheck under the same permission; never silently switch validator revisions.",
        ]),
        Constant(id="validator-script", form="text", value=script.rstrip("\n")),
    ]
    constants[10] += [
        owned_constant("AGENTS.md", "part-authoring-priority"),
        Constant(id="reading", value=(
            "Load references and guides in authoring order; select scenarios via assets/examples/catalog.oak.md. "
            "Both skill and agent author and interpret without Python, installation, network, or validation.")),
        Constant(id="skill-template", form="json", value=TEMPLATE_ENTRY),
        Constant(id="template-use", value=(
            "For new skills, use _template/SKILL.md or verbatim skill-template. "
            "Quote metadata as YAML strings and PURPOSE_JSON as a JSON string. "
            "Replace PART lines with justified OAK sections and a blank line, or delete them. Fill CONSTANT_ENTRIES or leave empty. "
            "Remove markers and unused parts/resources; remove .gitkeep when adding content. "
            "Unfilled scaffolding is inert.")),
    ]
    return {name: Node(constants=items, schemas=list(SHAPES) if index == 1 else [])
            for index, (name, items) in enumerate(zip(GUIDES, constants, strict=True))}


def local(name: str) -> ValueBinding:
    return ValueBinding(placeholder=name, value=BindingValue(binding=name))


def knowledge(name: str, guide: int, identifier: str = "guidance") -> ValueBinding:
    return ValueBinding(placeholder=name, value=ConstantValue(constant=f"{GUIDES[guide]}#constant.{identifier}"))


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
    body = [ACT(
        "Apply <AUTHORING> and <STRUCTURE> to all <SOURCE> for <SCOPE>. Use <TEMPLATE> under <TEMPLATE_USE> only for new skills; consult other guide knowledge as needed.",
        inputs=[knowledge("AUTHORING", 10), knowledge("STRUCTURE", 0), local("SOURCE"),
                knowledge("TEMPLATE", 10, "skill-template"), knowledge("TEMPLATE_USE", 10, "template-use")], outputs=["SCOPE"],
    )]
    previous = "SCOPE"
    for index, (part, guide) in enumerate((("schemas", 1), ("constants", 2), ("state", 3), ("interfaces", 4), ("triggers", 5), ("processes", 6), ("instructions", 7))):
        result = f"DESIGN_{index + 1}"
        text = f"Apply <GUIDANCE> to <{previous}> and <SOURCE>; decide justified {part} as <{result}>."
        bindings = [knowledge("GUIDANCE", guide), local(previous), local("SOURCE")]
        if guide == 1:
            text += " Preserve the requested shape using the guide schemas and <POPULATED> instances."
            bindings.append(knowledge("POPULATED", 1, "populated-shapes"))
        body.append(ACT(text, inputs=bindings, outputs=[result]))
        previous = result
    body += [
        ACT("Review <DESIGN_7> with <REVIEW>, <GRAMMAR>, and complete <TEACHING>. Produce canonical <CANDIDATE>, not a claimed programmatic check.",
            inputs=[local("DESIGN_7"), knowledge("REVIEW", 8, "review"), knowledge("GRAMMAR", 0, "oak-ebnf"), knowledge("TEACHING", 8, "teaching")], outputs=["CANDIDATE"]),
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
            Process(id="capture-request", name="Capture request", body=[
                ACT("Capture all <SOURCE>; set <VALIDATE> true only for requested programmatic validation, otherwise false.",
                    output="schema.authoring-request", outputs=["SOURCE", "VALIDATE"]),
                Call(process="process.author-document", inputs=[local("SOURCE"), local("VALIDATE")]),
            ]),
            Process(id="author-document", name="Author document", input="schema.authoring-request", body=body),
            Process(id="validate-and-deliver", name="Check validator", input="schema.oak-candidate", body=[
                ACT("Apply <POLICY> and exact <HELPER> to <CANDIDATE> without --allow-install. Return actual <REPORT>; <INSTALL_REQUIRED> is true exactly for permission-required, never invalid OAK or unavailable execution.",
                    output="schema.validator-check", inputs=[knowledge("POLICY", 9, "validation-policy"), knowledge("HELPER", 9, "validator-script"), local("CANDIDATE")], outputs=["INSTALL_REQUIRED", "REPORT"]),
                If(condition=Compare(left=BindingValue(binding="INSTALL_REQUIRED"), operator="equals", right=LiteralValue(value=True)),
                   then=[
                       ACT("Ask to download <IDENTITY> and install its dependencies in an isolated retained environment. Set <APPROVED> true only for explicit installation consent, not a validation request.",
                           output="schema.installation-consent", inputs=[knowledge("IDENTITY", 9, "identity")], outputs=["APPROVED"]),
                       If(condition=Compare(left=BindingValue(binding="APPROVED"), operator="equals", right=LiteralValue(value=True)),
                          then=[finish_validation(True)],
                          otherwise=[Emit(interface="interface.authored-document", bindings=[
                              ValueBinding(placeholder="OAK", value=BindingValue(binding="CANDIDATE")),
                              ValueBinding(placeholder="VALIDATION", value=LiteralValue(value="Programmatic validation was not performed (installation declined).")),
                          ])]),
                   ], otherwise=[finish_validation(False)]),
            ]),
            Process(id="finalize-validation", name="Report validation", input="schema.validation-context", body=[
                ACT("Finalize <CANDIDATE> from <REPORT> under <POLICY> using exact <HELPER>. Only <ALLOW_INSTALL> true permits --allow-install, downloads, or installation. Repair and recheck changes under the same permission, not unchanged successes. Return <OAK> and truthful <VALIDATION>.",
                    output="schema.authoring-result", inputs=[local("REPORT"), local("CANDIDATE"), local("ALLOW_INSTALL"), knowledge("POLICY", 9, "validation-policy"), knowledge("HELPER", 9, "validator-script")], outputs=["OAK", "VALIDATION"]),
                Emit(interface="interface.authored-document"),
            ]),
        ],
        interfaces=[Interface(id="authoring-input", flow="receives", schema="schema.authoring-request"),
                    Interface(id="authored-document", flow="emits", schema="schema.authoring-result")],
    )
