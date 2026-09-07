<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
repository-request: {"QUESTION": "Trace how a tool-backed ACT is authored, validated, resolved, and executed in OAK.\nIdentify its governing contracts, implementation owners, demonstrations, and\nverification gaps. Cite the inspected files. Change nothing.", "PATHS": "AGENTS.md\n.agents/rules/\noak/\nbuild/\nexamples/", "REVISION": "9956e6998869fcfbd84067eec0d6303273a54174"}

native-parent-request: TEXT<<
Use two oak-explorer instances in parallel on open-agent-knowledge at revision 9956e6998869fcfbd84067eec0d6303273a54174 within AGENTS.md, .agents/rules/, oak/, build/ and examples/. Give one action execution/dataflow and the other tool contracts/verification. Both must read complete applicable AGENTS at that revision before other inspection, change nothing, and return their full report. Wait for both; do not accept blocked, malformed or wrong-revision results as success. Reconcile findings, citations and gaps in one answer. This is a native-parent usage example, not a claim that Codex runs the Python OAK executor or that the illustrative agent.explore-* tools are Codex built-ins.
>>

fixture-request: {"QUESTION": "Explain fixture dispatch and contract checks.", "PATHS": "fixture/AGENTS.md\nfixture/runtime.txt\nfixture/contracts.txt", "REVISION": "fixture-sha256:d261737651ff7bf190221e9ae54fd3021fab6fcca85bdd959bdf545ec2835342"}

fixture-documents: JSON<<
{
  "fixture/AGENTS.md": "Inspect fixture data only. Change nothing. Do not run tests.\n",
  "fixture/runtime.txt": "ACT dispatches an exact registered tool.\nJOIN exposes the two independent reports.\n",
  "fixture/contracts.txt": "Validate input and output bindings.\nReject a failed branch before synthesis.\n"
}
>>

evidence-boundary: "The repository request and native-parent prompt are examples, not executed work. Repository fixtures inspect only the supplied in-memory fixture files, not OAK source or native clients. The two ToolContracts exist only in example.py. No live runtime or permission enforcement is delivered."
</constants>