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
    ("preserve-node", "keep-host-boundary"),
    ("map-schemas", "choose-schema-shape", "preserve-schema-shape", "separate-template-instance", "respect-schema-cardinality", "bind-values"),
    ("map-constants",),
    ("map-state", "separate-lifetimes", "keep-local-values"),
    ("map-interfaces", "emit-complete"),
    ("map-triggers", "route-receive", "declare-triggers"),
    ("map-processes", "name-process", "contract-work", "describe-action-roles", "distinguish-action-promises", "compose-work", "use-native-act", "use-exact-tool", "parallelize-tools", "delegate-document", "compose-conditions", "separate-layout"),
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
                         "populated-shapes fills these four schemas without wrappers or WHERE. "
                         "The one-row table has fixed cardinality; extend its template explicitly when justified."))]
    constants[2].append(Constant(id="forms", form="csv", value=[
        {"form": form, "use": use} for form, use in (
            ("JSON", "short fixed scalars, arrays, or objects"),
            ("TEXT", "verbatim fixed text"), ("CSV", "tabular fixed knowledge"),
            ("YAML", "readable structured fixed knowledge"),
        )
    ]))
    constants[3].append(owned_constant("oak/node/AGENTS.md", "value-lifetimes"))
    constants[4].append(Constant(id="boundaries", value="Reuse boundary schemas; never redefine their shapes inside interfaces or treat instances as mutable storage."))
    constants[5].append(Constant(id="routing", value="Sources identify receive interfaces with the same resolved schema as process input and no seeds. Guards require state reads, may compare literals or constants, and never read process bindings. Internal work uses CALL, not triggers."))
    constants[6].append(Constant(id="scopes", form="text", value=(
        "Bindings are immutable per frame. CALL promotes declared outputs; branches and iterations are local. "
        "IF promotes nothing: EMIT inside it or use process contracts, not invented state. "
        "Justify assertions, conditions, loops, and parallel work from the source.")))
    constants[7].append(Constant(id="last-decision", value="Do not author copies of the node-derived interpretation guidance."))
    examples = teaching_examples()
    constants[8] += [
        Constant(id="review", form="yaml", value=[
            "Check one idless node, unique ids, canonical part order, and justified parts.",
            "Check targets, complete bindings, lifetimes, and native versus named tools.",
            "Inspect populated output: layout, code fences, and cardinality, not just schemas.",
            "Grammar describes syntax; human review is not programmatic validation.",
            "Examples are inert teaching, not extra agents or arrivals to execute.",
        ]),
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
    constants[10] += [
        owned_constant("AGENTS.md", "part-authoring-priority"),
        Constant(id="reading", value=(
            "Load language references and practical guides in authoring order. Select scenarios via assets/examples/catalog.oak.md. "
            "The assembled agent has identical knowledge locally. Both forms author and interpret OAK without Python, installation, network, or validation.")),
        Constant(id="skill-template", form="json", value=TEMPLATE_ENTRY),
        Constant(id="template-use", value=(
            "For a new skill, copy _template/SKILL.md or materialize skill-template verbatim. "
            "Fill metadata markers as quoted YAML strings and PURPOSE_JSON as a JSON string. "
            "Replace each PART line with a justified OAK section and one blank-line separator, or remove the whole line. CONSTANT_ENTRIES adds fixed values or is empty. "
            "Remove all markers, unused parts and resources, and .gitkeep when adding content. "
            "The tree displays knowledge, not imports. Unfilled scaffolding is inert.")),
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
        "Apply <AUTHORING> and <STRUCTURE> to all <SOURCE> to define <SCOPE>. For a new skill, use <TEMPLATE> under <TEMPLATE_USE>; otherwise do not add scaffolding. Consult each guide's remaining knowledge as needed.",
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
        ACT("Review <DESIGN_7> against <REVIEW>, <GRAMMAR>, and complete <TEACHING> scenarios. Produce canonical <CANDIDATE>; do not claim a programmatic check.",
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
                ACT("Capture all supplied <SOURCE>; set <VALIDATE> true only for requested programmatic validation, otherwise false.",
                    output="schema.authoring-request", outputs=["SOURCE", "VALIDATE"]),
                Call(process="process.author-document", inputs=[local("SOURCE"), local("VALIDATE")]),
            ]),
            Process(id="author-document", name="Author document", input="schema.authoring-request", body=body),
            Process(id="validate-and-deliver", name="Check validator", input="schema.oak-candidate", body=[
                ACT("Apply <POLICY> with exact <HELPER> to <CANDIDATE> without --allow-install. Return actual <REPORT>; <INSTALL_REQUIRED> is true only for permission-required, not invalid OAK or unavailable execution.",
                    output="schema.validator-check", inputs=[knowledge("POLICY", 9, "validation-policy"), knowledge("HELPER", 9, "validator-script"), local("CANDIDATE")], outputs=["INSTALL_REQUIRED", "REPORT"]),
                If(condition=Compare(left=BindingValue(binding="INSTALL_REQUIRED"), operator="equals", right=LiteralValue(value=True)),
                   then=[
                       ACT("Ask permission to download <IDENTITY> and install its dependencies in an isolated retained environment. Set <APPROVED> true only after explicit installation approval, not merely a validation request.",
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
                ACT("Finalize <CANDIDATE> from <REPORT> under <POLICY>. Run exact <HELPER> with --allow-install only when <ALLOW_INSTALL> is true; otherwise never install or download. Repair errors and recheck changes under the same permission, not unchanged successes. Produce <OAK> and truthful <VALIDATION>.",
                    output="schema.authoring-result", inputs=[local("REPORT"), local("CANDIDATE"), local("ALLOW_INSTALL"), knowledge("POLICY", 9, "validation-policy"), knowledge("HELPER", 9, "validator-script")], outputs=["OAK", "VALIDATION"]),
                Emit(interface="interface.authored-document"),
            ]),
        ],
        interfaces=[Interface(id="authoring-input", flow="receives", schema="schema.authoring-request"),
                    Interface(id="authored-document", flow="emits", schema="schema.authoring-result")],
    )
