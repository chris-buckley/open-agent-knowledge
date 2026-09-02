"""Author one coordinator that researches a question with three parallel workers, challenges their findings, and publishes a report."""

from __future__ import annotations

from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import (
    ACT,
    Arrival,
    BindingValue,
    Call,
    Emission,
    Emit,
    Instruction,
    Interface,
    InterfaceValue,
    Join,
    Lines,
    MaxChars,
    Node,
    NonEmpty,
    Par,
    Process,
    Schema,
    ToolContract,
    Trigger,
    Type,
    ValueBinding,
    execute,
    parse,
    render,
    resolve,
    where,
)
from examples.agents import docs_researcher, findings_challenger, github_researcher, web_researcher
from examples.agents.copilot import agent_text, frontmatter

SCHEMA_RESEARCH_REQUEST = "schema.research-request"
SCHEMA_SOURCE_FINDINGS = "schema.source-findings"
SCHEMA_REPORT_REQUEST = "schema.report-request"
SCHEMA_RESEARCH_REPORT = "schema.research-report"
SCHEMA_GITHUB_REQUEST = "github_researcher.oak.md#schema.research-request"
SCHEMA_GITHUB_RESULT = "github_researcher.oak.md#schema.repository-findings"
SCHEMA_WEB_REQUEST = "web_researcher.oak.md#schema.research-request"
SCHEMA_WEB_RESULT = "web_researcher.oak.md#schema.web-findings"
SCHEMA_DOCS_REQUEST = "docs_researcher.oak.md#schema.research-request"
SCHEMA_DOCS_RESULT = "docs_researcher.oak.md#schema.docs-findings"
SCHEMA_CHALLENGE_REQUEST = "findings_challenger.oak.md#schema.challenge-request"
SCHEMA_VERIFIED_FINDINGS = "findings_challenger.oak.md#schema.verified-findings"
PROCESS_FIND_SOURCE_FINDINGS = "process.find-source-findings"
PROCESS_VALIDATE_FINDINGS = "process.validate-findings"
PROCESS_WRITE_REPORT = "process.write-report"
PROCESS_PUBLISH_REPORT = "process.publish-report"
INTERFACE_RESEARCH_REQUEST_INPUT = "interface.research-request-input"
INTERFACE_RESEARCH_REPORT_OUTPUT = "interface.research-report-output"

TOOL_AGENT_GITHUB_RESEARCHER = "agent.github-researcher"
TOOL_AGENT_WEB_RESEARCHER = "agent.web-researcher"
TOOL_AGENT_DOCS_RESEARCHER = "agent.docs-researcher"
TOOL_AGENT_FINDINGS_CHALLENGER = "agent.findings-challenger"
EVENT_RESEARCH_REQUESTED = "Accelerator research is requested."

PLACEHOLDER_QUESTION = "QUESTION"
PLACEHOLDER_REPOSITORY_FINDINGS = "REPOSITORY_FINDINGS"
PLACEHOLDER_WEB_FINDINGS = "WEB_FINDINGS"
PLACEHOLDER_DOCS_FINDINGS = "DOCS_FINDINGS"
PLACEHOLDER_CONFIRMED_FINDINGS = "CONFIRMED_FINDINGS"
PLACEHOLDER_REFUTED_CLAIMS = "REFUTED_CLAIMS"
PLACEHOLDER_TLDR = "TLDR"
PLACEHOLDER_FINDINGS = "FINDINGS"
PLACEHOLDER_DROPPED_CLAIMS = "DROPPED_CLAIMS"

REQUEST_PLACEHOLDERS = (PLACEHOLDER_QUESTION,)
SOURCE_FINDINGS_PLACEHOLDERS = (PLACEHOLDER_REPOSITORY_FINDINGS, PLACEHOLDER_WEB_FINDINGS, PLACEHOLDER_DOCS_FINDINGS)
CHALLENGE_REQUEST_PLACEHOLDERS = (PLACEHOLDER_QUESTION, *SOURCE_FINDINGS_PLACEHOLDERS)
VERIFIED_FINDINGS_PLACEHOLDERS = (PLACEHOLDER_CONFIRMED_FINDINGS, PLACEHOLDER_REFUTED_CLAIMS)
REPORT_REQUEST_PLACEHOLDERS = (PLACEHOLDER_QUESTION, *VERIFIED_FINDINGS_PLACEHOLDERS)
RESEARCH_REPORT_PLACEHOLDERS = (PLACEHOLDER_TLDR, PLACEHOLDER_FINDINGS, PLACEHOLDER_DROPPED_CLAIMS)

AGENT = ROOT / ".github" / "agents" / "accelerator-researcher.agent.md"
AGENT_FRONTMATTER = frontmatter(
    "accelerator-researcher",
    "Answers one question about Microsoft solution accelerators: sends it to the github-researcher, web-researcher, and docs-researcher agents at once, has the findings-challenger agent attack their findings, and returns a brief report that starts with a TLDR and links every finding.",
    ["agent"],
)


def local_bindings(placeholders: tuple[str, ...]) -> list[ValueBinding]:
    return [ValueBinding(placeholder=name, value=BindingValue(binding=name)) for name in placeholders]


accelerator_researcher_instructions = [
    Instruction(id=slug, body=body)
    for slug, body in (
        ("map-agent-tools", "Run a tool named agent.<name> as the custom agent <name> through the agent tool."),
        ("read-agent-message", "Treat a custom agent's final message as the outputs of its ACT line."),
        ("start-par-together", "Start every PAR child in one turn before you wait for any result."),
        ("separate-duties", "Do not research or verify claims yourself."),
        ("report-confirmed", "Report only claims that survived the challenge."),
        ("write-plainly", "Write the report in plain words."),
        ("expand-acronyms", "Expand each acronym the first time it appears."),
        ("keep-links", "End each finding with the link that proves it."),
        ("keep-brief", "Keep the report brief: one line per finding."),
    )
]

research_request_schema = Schema(
    id="research-request",
    name="Research Request",
    purpose="Carry one question to research.",
    template="Question: <QUESTION>",
    where=[where(PLACEHOLDER_QUESTION, Type(of="string"), NonEmpty(), description="the question the report must answer")],
)

source_findings_schema = Schema(
    id="source-findings",
    name="Source Findings",
    purpose="Carry the findings of the three researchers for one question.",
    template=(
        "Repository findings: <REPOSITORY_FINDINGS>\n"
        "Web findings: <WEB_FINDINGS>\n"
        "Docs findings: <DOCS_FINDINGS>"
    ),
    where=[
        where(PLACEHOLDER_REPOSITORY_FINDINGS, Type(of="string"), NonEmpty(), description="the cited repository findings"),
        where(PLACEHOLDER_WEB_FINDINGS, Type(of="string"), NonEmpty(), description="the cited web findings"),
        where(PLACEHOLDER_DOCS_FINDINGS, Type(of="string"), NonEmpty(), description="the cited documentation findings"),
    ],
)

report_request_schema = Schema(
    id="report-request",
    name="Report Request",
    purpose="Carry the question and the challenged findings the report is written from.",
    template=(
        "Question: <QUESTION>\n"
        "Confirmed findings: <CONFIRMED_FINDINGS>\n"
        "Refuted claims: <REFUTED_CLAIMS>"
    ),
    where=[
        where(PLACEHOLDER_QUESTION, Type(of="string"), NonEmpty(), description="the question the report must answer"),
        where(PLACEHOLDER_CONFIRMED_FINDINGS, Type(of="string"), description="the claims that survived the challenge, empty when none"),
        where(PLACEHOLDER_REFUTED_CLAIMS, Type(of="string"), description="the claims the challenge refuted, with reasons, empty when none"),
    ],
)

research_report_schema = Schema(
    id="research-report",
    name="Research Report",
    purpose="Carry one brief, challenged, and linked answer with the TLDR first.",
    template=(
        "TLDR: <TLDR>\n"
        "\n"
        "Findings:\n"
        "<FINDINGS>\n"
        "\n"
        "Dropped claims:\n"
        "<DROPPED_CLAIMS>"
    ),
    where=[
        where(PLACEHOLDER_TLDR, Type(of="string"), NonEmpty(), Lines(max=3), MaxChars(n=400), description="the answer in plain words"),
        where(PLACEHOLDER_FINDINGS, Type(of="string"), Lines(max=12), description="one confirmed finding per line, each ending with the link that proves it, empty when none"),
        where(PLACEHOLDER_DROPPED_CLAIMS, Type(of="string"), Lines(max=6), description="one refuted claim per line in plain words, empty when none"),
    ],
)

research_requested_trigger = Trigger(
    id="research-requested",
    event=EVENT_RESEARCH_REQUESTED,
    source=INTERFACE_RESEARCH_REQUEST_INPUT,
    process=PROCESS_PUBLISH_REPORT,
    seed=[
        ValueBinding(
            placeholder=PLACEHOLDER_QUESTION,
            value=InterfaceValue(interface=INTERFACE_RESEARCH_REQUEST_INPUT, placeholder=PLACEHOLDER_QUESTION),
        )
    ],
)

find_source_findings_process = Process(
    id="find-source-findings",
    name="Find source-findings",
    input=SCHEMA_RESEARCH_REQUEST,
    output=SCHEMA_SOURCE_FINDINGS,
    steps=[
        Par(
            steps=[
                ACT.tool(
                    TOOL_AGENT_GITHUB_RESEARCHER,
                    "Research GitHub repositories for <QUESTION> and produce <REPOSITORY_FINDINGS>.",
                    input=SCHEMA_GITHUB_REQUEST,
                    output=SCHEMA_GITHUB_RESULT,
                    inputs=local_bindings(REQUEST_PLACEHOLDERS),
                    outputs=[PLACEHOLDER_REPOSITORY_FINDINGS],
                ),
                ACT.tool(
                    TOOL_AGENT_WEB_RESEARCHER,
                    "Research the web for <QUESTION> and produce <WEB_FINDINGS>.",
                    input=SCHEMA_WEB_REQUEST,
                    output=SCHEMA_WEB_RESULT,
                    inputs=local_bindings(REQUEST_PLACEHOLDERS),
                    outputs=[PLACEHOLDER_WEB_FINDINGS],
                ),
                ACT.tool(
                    TOOL_AGENT_DOCS_RESEARCHER,
                    "Research Microsoft Learn for <QUESTION> and produce <DOCS_FINDINGS>.",
                    input=SCHEMA_DOCS_REQUEST,
                    output=SCHEMA_DOCS_RESULT,
                    inputs=local_bindings(REQUEST_PLACEHOLDERS),
                    outputs=[PLACEHOLDER_DOCS_FINDINGS],
                ),
            ]
        ),
        Join(),
    ],
)

validate_findings_process = Process(
    id="validate-findings",
    name="Validate findings",
    input=SCHEMA_CHALLENGE_REQUEST,
    output=SCHEMA_VERIFIED_FINDINGS,
    steps=[
        ACT.tool(
            TOOL_AGENT_FINDINGS_CHALLENGER,
            (
                "Attack <REPOSITORY_FINDINGS>, <WEB_FINDINGS>, and <DOCS_FINDINGS> against <QUESTION> "
                "and their cited sources, then produce <CONFIRMED_FINDINGS> and <REFUTED_CLAIMS>."
            ),
            input=SCHEMA_CHALLENGE_REQUEST,
            output=SCHEMA_VERIFIED_FINDINGS,
            inputs=local_bindings(CHALLENGE_REQUEST_PLACEHOLDERS),
            outputs=list(VERIFIED_FINDINGS_PLACEHOLDERS),
        )
    ],
)

write_report_process = Process(
    id="write-report",
    name="Write report",
    input=SCHEMA_REPORT_REQUEST,
    output=SCHEMA_RESEARCH_REPORT,
    steps=[
        ACT(
            "Write <TLDR>, <FINDINGS>, and <DROPPED_CLAIMS> that answer <QUESTION> from <CONFIRMED_FINDINGS> and <REFUTED_CLAIMS>.",
            inputs=local_bindings(REPORT_REQUEST_PLACEHOLDERS),
            outputs=list(RESEARCH_REPORT_PLACEHOLDERS),
        )
    ],
)

publish_report_process = Process(
    id="publish-report",
    name="Publish report",
    input=SCHEMA_RESEARCH_REQUEST,
    steps=[
        Call(
            process=PROCESS_FIND_SOURCE_FINDINGS,
            inputs=local_bindings(REQUEST_PLACEHOLDERS),
            outputs=list(SOURCE_FINDINGS_PLACEHOLDERS),
        ),
        Call(
            process=PROCESS_VALIDATE_FINDINGS,
            inputs=local_bindings(CHALLENGE_REQUEST_PLACEHOLDERS),
            outputs=list(VERIFIED_FINDINGS_PLACEHOLDERS),
        ),
        Call(
            process=PROCESS_WRITE_REPORT,
            inputs=local_bindings(REPORT_REQUEST_PLACEHOLDERS),
            outputs=list(RESEARCH_REPORT_PLACEHOLDERS),
        ),
        Emit(
            interface=INTERFACE_RESEARCH_REPORT_OUTPUT,
            bindings=local_bindings(RESEARCH_REPORT_PLACEHOLDERS),
        ),
    ],
)

research_request_input_interface = Interface(
    id="research-request-input",
    direction="in",
    schema=SCHEMA_RESEARCH_REQUEST,
    description="The question supplied by the caller.",
)

research_report_output_interface = Interface(
    id="research-report-output",
    direction="out",
    schema=SCHEMA_RESEARCH_REPORT,
    description="The challenged and linked report returned to the caller.",
)

accelerator_researcher_node = Node(
    instructions=accelerator_researcher_instructions,
    schemas=[research_request_schema, source_findings_schema, report_request_schema, research_report_schema],
    triggers=[research_requested_trigger],
    processes=[find_source_findings_process, validate_findings_process, write_report_process, publish_report_process],
    interfaces=[research_request_input_interface, research_report_output_interface],
)

TARGET = Path(__file__).with_suffix(".oak.md")
SOURCE = "examples/agents/accelerator_researcher.oak.md"
WORKER_DOCUMENTS = {
    "examples/agents/github_researcher.oak.md": github_researcher.github_researcher_node,
    "examples/agents/web_researcher.oak.md": web_researcher.web_researcher_node,
    "examples/agents/docs_researcher.oak.md": docs_researcher.docs_researcher_node,
    "examples/agents/findings_challenger.oak.md": findings_challenger.findings_challenger_node,
}

QUESTION_TEXT = "Which Microsoft solution accelerators help build a multi-agent customer service assistant on Azure?"
REPOSITORY_FINDING_TEXT = (
    "Multi-Agent Custom Automation Engine orchestrates a group of artificial intelligence (AI) agents on Azure Container Apps. "
    "https://github.com/microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator"
)
WEB_FINDING_TEXT = "The accelerator hub lists Customer Chatbot as actively maintained. https://accelerators.ms/#accelerators"
DOCS_FINDING_TEXT = (
    "Azure AI Foundry Agent Service documents connected agents for multi-agent orchestration. "
    "https://learn.microsoft.com/azure/ai-foundry/agents/how-to/connected-agents"
)
REFUTED_CLAIM_TEXT = "Customer Chatbot is actively maintained: the hub label is not commit evidence. https://accelerators.ms/#accelerators"
TLDR_TEXT = (
    "Start from the Multi-Agent Custom Automation Engine accelerator and add connected agents from the "
    "Foundry Agent Service for the customer service flow."
)
DROPPED_CLAIM_TEXT = "The hub calls Customer Chatbot actively maintained, but no commit history backs that. https://accelerators.ms/#accelerators"
WORKER_TEXTS = {
    PLACEHOLDER_REPOSITORY_FINDINGS: REPOSITORY_FINDING_TEXT + "\nGap: no catalogue entry names customer service as a use case.",
    PLACEHOLDER_WEB_FINDINGS: WEB_FINDING_TEXT,
    PLACEHOLDER_DOCS_FINDINGS: DOCS_FINDING_TEXT,
    PLACEHOLDER_CONFIRMED_FINDINGS: REPOSITORY_FINDING_TEXT + "\n" + DOCS_FINDING_TEXT,
    PLACEHOLDER_REFUTED_CLAIMS: REFUTED_CLAIM_TEXT,
}
RESEARCH_REQUEST_VALUES = {PLACEHOLDER_QUESTION: QUESTION_TEXT}
CHALLENGE_REQUEST_VALUES = {
    **RESEARCH_REQUEST_VALUES,
    **{name: WORKER_TEXTS[name] for name in SOURCE_FINDINGS_PLACEHOLDERS},
}
EXPECTED_REPORT = Emission(
    interface=INTERFACE_RESEARCH_REPORT_OUTPUT,
    values={
        PLACEHOLDER_TLDR: TLDR_TEXT,
        PLACEHOLDER_FINDINGS: WORKER_TEXTS[PLACEHOLDER_CONFIRMED_FINDINGS],
        PLACEHOLDER_DROPPED_CLAIMS: DROPPED_CLAIM_TEXT,
    },
)


def _worker_act(step, _values):
    return {name: WORKER_TEXTS[name] for name in step.outputs}


def _agent(node: Node, request_input: str, expected: dict[str, str], barrier: threading.Barrier | None = None):
    """Dispatch one worker: check its exact request, meet the other PAR children at the barrier, then run it."""

    def dispatch(_step, values):
        if dict(values) != expected:
            raise RuntimeError(f"{request_input} received an unexpected request")
        if barrier is not None:
            barrier.wait()
        completed = execute(
            node,
            Arrival(source=request_input, interfaces={request_input: dict(values)}),
            {},
            act=_worker_act,
        )
        return dict(completed.emissions[0].values)

    return dispatch


def _write_report_act(_step, values):
    if (
        values[PLACEHOLDER_QUESTION] != QUESTION_TEXT
        or values[PLACEHOLDER_CONFIRMED_FINDINGS] != WORKER_TEXTS[PLACEHOLDER_CONFIRMED_FINDINGS]
        or values[PLACEHOLDER_REFUTED_CLAIMS] != REFUTED_CLAIM_TEXT
    ):
        raise RuntimeError("the report request does not carry the challenged findings")
    return {
        PLACEHOLDER_TLDR: TLDR_TEXT,
        PLACEHOLDER_FINDINGS: values[PLACEHOLDER_CONFIRMED_FINDINGS],
        PLACEHOLDER_DROPPED_CLAIMS: DROPPED_CLAIM_TEXT,
    }


def _load_worker(path: str) -> Node | None:
    return WORKER_DOCUMENTS.get(path)


def _tool_registry() -> dict[str, ToolContract]:
    """Register the four workers; the three researchers must all be running before any one proceeds."""
    barrier = threading.Barrier(3, timeout=10)
    return {
        TOOL_AGENT_GITHUB_RESEARCHER: ToolContract(
            _agent(github_researcher.github_researcher_node, github_researcher.INTERFACE_RESEARCH_REQUEST_INPUT, RESEARCH_REQUEST_VALUES, barrier),
            frozenset(REQUEST_PLACEHOLDERS),
            frozenset({PLACEHOLDER_REPOSITORY_FINDINGS}),
            True,
            input=SCHEMA_GITHUB_REQUEST,
            output=SCHEMA_GITHUB_RESULT,
        ),
        TOOL_AGENT_WEB_RESEARCHER: ToolContract(
            _agent(web_researcher.web_researcher_node, web_researcher.INTERFACE_RESEARCH_REQUEST_INPUT, RESEARCH_REQUEST_VALUES, barrier),
            frozenset(REQUEST_PLACEHOLDERS),
            frozenset({PLACEHOLDER_WEB_FINDINGS}),
            True,
            input=SCHEMA_WEB_REQUEST,
            output=SCHEMA_WEB_RESULT,
        ),
        TOOL_AGENT_DOCS_RESEARCHER: ToolContract(
            _agent(docs_researcher.docs_researcher_node, docs_researcher.INTERFACE_RESEARCH_REQUEST_INPUT, RESEARCH_REQUEST_VALUES, barrier),
            frozenset(REQUEST_PLACEHOLDERS),
            frozenset({PLACEHOLDER_DOCS_FINDINGS}),
            True,
            input=SCHEMA_DOCS_REQUEST,
            output=SCHEMA_DOCS_RESULT,
        ),
        TOOL_AGENT_FINDINGS_CHALLENGER: ToolContract(
            _agent(findings_challenger.findings_challenger_node, findings_challenger.INTERFACE_CHALLENGE_REQUEST_INPUT, CHALLENGE_REQUEST_VALUES),
            frozenset(CHALLENGE_REQUEST_PLACEHOLDERS),
            frozenset(VERIFIED_FINDINGS_PLACEHOLDERS),
            input=SCHEMA_CHALLENGE_REQUEST,
            output=SCHEMA_VERIFIED_FINDINGS,
        ),
    }


def build() -> str:
    """Render, parse, resolve across the four workers, run one research cycle, and round-trip."""
    rendered = render(accelerator_researcher_node)
    parsed = parse(rendered)
    resolve(parsed, source=SOURCE, load=_load_worker)
    if render(parsed) != rendered:
        raise RuntimeError("accelerator researcher changed during render and parse")
    completed = execute(
        parsed,
        Arrival(
            source=INTERFACE_RESEARCH_REQUEST_INPUT,
            interfaces={INTERFACE_RESEARCH_REQUEST_INPUT: dict(RESEARCH_REQUEST_VALUES)},
        ),
        {},
        act=_write_report_act,
        tools=_tool_registry(),
        source=SOURCE,
        load=_load_worker,
    )
    if completed.emissions != [EXPECTED_REPORT]:
        raise RuntimeError("accelerator researcher did not publish one challenged report")
    return rendered


def write() -> Path:
    """Write the canonical sibling OAK snapshot and the Copilot CLI agent file."""
    rendered = build()
    TARGET.write_text(rendered, encoding="utf-8", newline="\n")
    AGENT.parent.mkdir(parents=True, exist_ok=True)
    AGENT.write_text(agent_text(AGENT_FRONTMATTER, rendered), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
