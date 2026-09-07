# Implementation preflight: execution host required

Observed: 2026-09-07T03:41:19Z
Verdict: Blocked at Phase 1 provisioning; not implementation completion.
Plan: [Plan 0016](../plan.md)
Approved proposal/checkpoint: `612eeae81971c7b75d89d75171ba9a33de8b38d9`
Governing revision: `9956e6998869fcfbd84067eec0d6303273a54174`
Branch: `docs/plan-parallel-codex-exploration`

## Authorization and continuity

The user's message at 2026-09-07T03:38:25Z authorizes implementing the complete current plan and raising a PR when finished. It covers the native CLI/desktop, generated bundle, parallel exploration, adaptor, and SMEAC scope, not only an earlier proposal. Implementation and eventual completed-work PR approval remain valid for that unchanged scope; do not ask for those approvals again solely because work resumes.

The plan separately requires an explicit native installation destination/diff, dependency or tool installation consent, and a named model/provider, source-disclosure authorization, and total spend/token ceiling for live calls. Those concrete inputs have not been supplied. No live model call or installation was inferred from the continuation request.

The branch ref still pointed to the approved checkpoint when preflight began. The complete root and applicable governing text retained in the conversation are pinned to the governing revision. The mounted plan and research record were read in full and checked against their previously returned Git blob identities. No newer main instructions were substituted. P01.01 remains open because the affected-source/standards review for product edits is not complete.

| Restored artifact | Git blob SHA-1 | SHA-256 of exact bytes |
| --- | --- | --- |
| `plan.md` | `a07457a974f2ccf7a79b8aa913d469a1258bda0e` | `b35a0e3eacd2d1a8cb9dffafadfb1cf83c2f9c88694a96c740f39559ffc0b188` |
| `evidence/native-clients-research.md` | `78e578cb8a3e688ee2ff05c23123444ce127995e` | `7752417ae58e5832c4fcfed2c2df7fd9ee508a1ab4bf8c312f312930b7142a4c` |

These are restored input identities, not proof of implemented products or executed repository checks. This file records the preflight observation without changing the approved design, its acceptance specimens, or its checkboxes.

## Observed environment

These observations came from the available container, not the user's computer or a repository workstation. Package versions were read with `importlib.metadata`; no repository code was imported.

```text
System: Linux
Machine: x86_64
Python: 3.13.5
shutil.which("codex"): None
pydantic: 2.13.4
pydantic-settings: 2.14.1
pydantic-extra-types: 2.11.1
PyYAML: 6.0.3
mcp: not installed in this Python environment
```

The `codex` result establishes absence from this process's executable search path, not an exhaustive scan of every machine or filesystem. No absolute Codex binary path or authorized external execution host was supplied.

The pinned `pyproject.toml` requires `pydantic-settings>=2.15`. This container therefore does not satisfy the declared verification environment. The plan also requires an explicitly provisioned optional MCP SDK environment for the new host checks; its version range must be selected from compatibility evidence, not guessed or installed without consent.

A direct request for the approved source archive was attempted:

```text
curl --fail --location --connect-timeout 10 --max-time 30 \
  --output /mnt/data/oak-612eeae.tar.gz \
  https://codeload.github.com/chris-buckley/open-agent-knowledge/tar.gz/612eeae81971c7b75d89d75171ba9a33de8b38d9

Exit: 6
curl: (6) Could not resolve host: codeload.github.com
```

The separate download/web path did not deliver the archive either. No archive was extracted and no executable checkout was assembled. GitHub connector reads remain available, including the branch ref and exact plan blob; this is not a claim that the repository is inaccessible.

No desktop host is connected to the available execution tools. Plugin discovery found Remote Desktop Commander as an available, not installed connection option to a user-controlled filesystem/terminal, and it was suggested. A suggestion is not a connection, desktop UI control, Computer Use authorization, or evidence of native-client operation. No external execution host or human desktop evidence operator has been established.

## Gate assessment

| Gate | Observed status | Consequence |
| --- | --- | --- |
| P01.01 complete preparation | Partially restored; product-source/standards review not complete | Leave open; preserve approved scope and pinned governing text. |
| P01.02 installed backend/protocol | Blocked: no executable Codex runtime supplied | No generated protocol schema or effective runtime/tool inventory can be verified. |
| P01.03 strict-profile probes | Not executed | A source description, config flag, or invented tool registry cannot stand in for runtime denial evidence. |
| P01.04 authoring-size candidate | Not assembled or measured in this session | No size pass is claimed; the existing 10,000/64,000-byte limits are unchanged. |
| P01.05 native CLI/desktop foundation | Blocked: no supplied native clients, connected desktop host, or evidence operator | Native discovery, exact MCP naming, and wait/cancel behavior remain unverified. |
| Phase 2 transition | Not reached | Do not begin broad product implementation while the mandatory compatibility/size transition is unsatisfied. |

All 42 implementation checkboxes remain open. No product source, generated delivery, native TOML, installer, MCP server, or SMEAC schema was implemented in this preflight. No new workflow or remote publishing infrastructure was introduced to compensate for tool limitations.

The plan's missing-live-access contingency permits authorized offline work but does not establish a compatible host or erase the explicit Phase 1 transition. An offline-only reordering beyond the failed prerequisite needs a specific decision; it must not be silently treated as approval to bypass that prerequisite or reduce final native acceptance.

## Primary-source recheck

Current official documentation was revisited to distinguish an environment blocker from a disproved architecture:

- [App-server](https://learn.chatgpt.com/docs/app-server) documents version-specific `generate-json-schema` output and experimental dynamic-tool negotiation. Documentation is not a generated schema from a supplied installed binary.
- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) documents native TOML discovery and parent runtime overrides. A read-only default alone still does not establish the accepted restricted backend.
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) exposes separate shell, execution, plugin, and other controls, not a demonstrated universal tool allowlist for this environment.
- [Desktop product](https://help.openai.com/en/articles/20001276) retains a distinct Codex view. No native desktop view was operated here.

These checks do not show that Codex cannot satisfy the design. They show that the required installed-host evidence has not been obtained in the available environment.

## Exact recovery point

Resume Phase 1 against the approved proposal and this evidence checkpoint. Keep the governing revision pinned and retain the implementation/finished-PR authorization already granted. Do not replay any claimed completed product phase: none has completed.

Provide an authorized execution host with an actual checkout of this branch, an explicit installed Codex binary, and a Python environment satisfying the declared dependencies. Verify the host and restored bytes rather than assuming an existing checkout is current. Any missing tool/dependency installation needs the separate permission specified by the plan.

On that host, finish the no-model protocol/configuration/isolation inspection and strict-profile probes, then measure the complete authoring candidate under the unchanged limits. Establish actual Codex CLI and ChatGPT desktop / Codex / Local versions and an authorized desktop evidence operator. A terminal connection alone does not prove desktop UI access.

Only after the Phase 1 transition passes should Phase 2 begin. Before native installation or live acceptance, obtain the concrete destination/diff and named model/data/total budget approvals. Do not collect credentials into the chat or commit them.

No PR was opened: the requested PR is for completely finished work, and neither the implementation nor its required acceptance is complete. This is a recoverable blocked checkpoint, not a completed delivery or a promise of background work.
