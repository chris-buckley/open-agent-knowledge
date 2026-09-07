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
from build.ebnf import grammar
from build.agents import adaptor_node

ROOT = Path(__file__).resolve().parents[1]
GUIDES = (
    "references/00-structure.oak.md", "references/01-schemas.oak.md",
    "references/02-constants.oak.md", "references/03-state.oak.md",
    "references/04-interfaces.oak.md", "references/05-triggers.oak.md",
    "references/06-processes.oak.md", "references/07-instructions.oak.md",
    "guides/review.oak.md", "guides/validation.oak.md", "guides/authoring.oak.md",
    "guides/subagent-orchestration.oak.md", "platforms/codex/adaptor.oak.md",
)
# Each package authoring rule has one guide owner, not an instruction copy.
RULE_OWNERS = (
    ("preserve-node", "keep-host-boundary", "disclose-completeness"),
    ("map-schemas", "choose-schema-shape", "preserve-schema-shape", "separate-template-instance", "respect-schema-cardinality", "bind-values"),
    ("map-constants",),
    ("map-state", "separate-lifetimes", "keep-local-values"),
    ("map-interfaces", "emit-complete", "own-boundary-contracts", "explain-boundary-contracts"),
    ("map-triggers", "route-receive", "declare-triggers"),
    ("map-processes", "name-process", "contract-work", "describe-action-roles", "distinguish-action-promises", "compose-work", "compose-conditions", "separate-layout", "adapt-external-contracts"),
    ("map-instructions",),
    ("write-document",),
    ("validate-draft", "emit-document"),
    ("treat-context", "omit-unjustified", "avoid-invention", "reuse-domain"),
    ("use-native-act", "use-exact-tool", "parallelize-tools", "delegate-document"), (),
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
    constants[1].append(Constant(id="shape-source", value=(
        "In the teaching mapping, assets/examples/shape_gallery/example.oak.md pairs complete schemas with populated "
        "instances without definition wrappers or WHERE. Its table has one fixed row; extend the template explicitly if justified.")))
    constants[2].append(Constant(id="forms", form="csv", value=[
        {"form": form, "use": use} for form, use in (
            ("JSON", "short fixed scalars, arrays, or objects"),
            ("TEXT", "verbatim fixed text"), ("CSV", "tabular fixed knowledge"),
            ("YAML", "readable structured fixed knowledge"),
        )
    ]))
    constants[4].append(Constant(id="boundaries", value="Interface instances are not mutable storage."))
    constants[5].append(Constant(id="routing", value="Source triggers share receive/process schemas and omit seeds. Guards read state, may compare literals/constants, never process bindings. CALL sequences internal work."))
    constants[6].append(Constant(id="scopes", form="text", value=(
        "Bindings are immutable per frame; CALL promotes declared outputs. Branches/iterations are local. "
        "IF promotes nothing: use EMIT within it or process contracts, not invented state.")))
    constants[7].append(Constant(id="last-decision", value="Do not copy node-derived interpretation guidance."))
    examples = teaching_examples()
    constants[8] += [
        Constant(id="review", form="yaml", value=[
            "Check one idless node, unique ids, canonical order and justified parts;",
            "check targets, complete bindings, lifetimes and native/named tools.",
            "Review public promises against interface guidance and knowledge closure against structure guidance.",
            "Inspect output layout, fences and cardinality, not just schemas.",
            "Grammar describes syntax; review is not programmatic validation.",
            "Examples are inert teaching, not agents or arrivals to execute.",
        ]),
        # JSON strings preserve nested OAK block delimiters verbatim as inert data.
        Constant(id="teaching", form="json", value=examples),
    ]
    constants[9] += [
        Constant(id="identity", value={"version": version, "validator-revision": revision}),
        Constant(id="validation-policy", form="yaml", value=[
            "Validate only on request; authoring and interpretation need no installation, Python or network.",
            "Python 3.11+: reuse installed code, --source with optional --python, or retained cache. Match source and dependency fingerprints, never just name/version.",
            "Run skill scripts/validate.py; standalone users save validator-script verbatim as validate.py. Use its documented arguments and exit codes; --root permits only an explicitly allowed graph.",
            "Only permission-required prompts consent to download the identified revision and install declared dependencies in an isolated retained cache. Validation requests are not installation consent; explicit consent alone permits --allow-install.",
            "Reuse the cache; no published OAK package is needed. On declined installation or unavailable Python, network, dependencies or execution, continue authoring without installing and report the not-performed reason.",
            "Report actual checks, revision and errors outside OAK, not proof of execution or semantic correctness. Repair/recheck under the same permission; never silently change the validator revision.",
        ]),
        Constant(id="validator-script", form="text", value=script.rstrip("\n")),
    ]
    constants[10] += [
        owned_constant("AGENTS.md", "part-authoring-priority"),
        Constant(id="skill-template", form="json", value=TEMPLATE_ENTRY),
        Constant(id="template-use", value=(
            "For new skills use _template/SKILL.md or verbatim skill-template. "
            "Quote metadata as YAML strings, PURPOSE_JSON as a JSON string. "
            "Replace PART lines with justified OAK sections plus a blank line, or delete them. Fill CONSTANT_ENTRIES or leave empty. "
            "Remove markers, unused parts/resources, and .gitkeep when adding content. "
            "Unfilled scaffolding is inert.")),
    ]
    constants[11] += [Constant(id="orchestration", form="yaml", value=[
        "The coordinator owns splitting, dispatch, integration and final claims. Give each leaf a bounded independent task and mapped request/result schemas, not coordinator authority.",
        "Give workers one pinned revision, full applicable governing text, scope and evidence requirements. Restore truncation, preserve document scopes and report blocked work.",
        "CALL composes processes synchronously, not agents. ACT.tool constructs a tool action, not a capability or permission.",
        "PAR outputs stay isolated until immediate JOIN promotes them in authored order. Before synthesis reject blocked, failed, malformed or wrong-revision results; reconcile conflicts and retain gaps.",
        "Hosts own concurrency limits, deadlines, cancellation, cleanup and tool/sandbox enforcement. Fixture overlap proves no live subagent behavior.",
    ])]
    nodes = {name: Node(constants=items) for name, items in zip(GUIDES, constants, strict=True)}
    nodes[GUIDES[12]] = adaptor_node()
    return nodes


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
        "Apply <AUTHORING> and <STRUCTURE> to all <SOURCE> for <SCOPE>. Use <TEMPLATE> under <TEMPLATE_USE> only for new skills; consult needed guides.",
        inputs=[knowledge("AUTHORING", 10), knowledge("STRUCTURE", 0), local("SOURCE"),
                knowledge("TEMPLATE", 10, "skill-template"), knowledge("TEMPLATE_USE", 10, "template-use")], outputs=["SCOPE"],
    )]
    previous = "SCOPE"
    for index, (part, guide) in enumerate((("schemas", 1), ("constants", 2), ("state", 3), ("interfaces", 4), ("triggers", 5), ("processes", 6), ("instructions", 7))):
        result = f"DESIGN_{index + 1}"
        text = f"Design justified {part} as <{result}> from <SOURCE> and <{previous}> under <GUIDANCE>."
        bindings = [knowledge("GUIDANCE", guide), local(previous), local("SOURCE")]
        if guide == 1:
            text += " Preserve requested shapes using the complete schemas and populated instances in <TEACHING>."
            bindings.append(knowledge("TEACHING", 8, "teaching"))
        if guide == 6:
            text += " Apply <DELEGATION> and <ORCHESTRATION> to delegation, <CODEX> and <DEFAULTS> to native Codex artifacts."
            bindings.extend((knowledge("ORCHESTRATION", 11, "orchestration"), knowledge("DELEGATION", 11), knowledge("CODEX", 12, "mapping"), knowledge("DEFAULTS", 12, "native-defaults")))
        body.append(ACT(text, inputs=bindings, outputs=[result]))
        previous = result
    body += [
        ACT("Review <DESIGN_7> with <REVIEW>, <GRAMMAR> and <TEACHING> for canonical <CANDIDATE>, not programmatic validation. Use its catalogue to select complete scenarios.",
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
                ACT("Apply <POLICY> and exact <HELPER> to <CANDIDATE> without --allow-install. Return observed <REPORT>; <INSTALL_REQUIRED> means permission-required, not invalid OAK or unavailable execution.",
                    output="schema.validator-check", inputs=[knowledge("POLICY", 9, "validation-policy"), knowledge("HELPER", 9, "validator-script"), local("CANDIDATE")], outputs=["INSTALL_REQUIRED", "REPORT"]),
                If(condition=Compare(left=BindingValue(binding="INSTALL_REQUIRED"), operator="equals", right=LiteralValue(value=True)),
                   then=[
                       ACT("Request consent to download <IDENTITY> and install its dependencies in an isolated retained environment. <APPROVED> requires explicit installation consent, not a validation request.",
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
                ACT("Finalize <CANDIDATE> from <REPORT> under <POLICY> with exact <HELPER>. Only <ALLOW_INSTALL> true permits downloads/installation via --allow-install. Repair/recheck changes under the same permission, not unchanged successes. Return <OAK> and truthful <VALIDATION>.",
                    output="schema.authoring-result", inputs=[local("REPORT"), local("CANDIDATE"), local("ALLOW_INSTALL"), knowledge("POLICY", 9, "validation-policy"), knowledge("HELPER", 9, "validator-script")], outputs=["OAK", "VALIDATION"]),
                Emit(interface="interface.authored-document"),
            ]),
        ],
        interfaces=[Interface(id="authoring-input", flow="receives", schema="schema.authoring-request"),
                    Interface(id="authored-document", flow="emits", schema="schema.authoring-result")],
    )
