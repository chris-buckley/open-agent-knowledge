# Agent-guided network design delivery

Date: 2026-09-05.
Scope: Experiment design and repository structure only.
Plan: [SMEAC execution record](plan.md).
Specification: [EXPERIMENT.md](../../../experiments/agent-guided-network/EXPERIMENT.md).
Original baseline: `cd1f8aed74b24f8515a3e176972e9f2cbcb53e5a`.
Integrated main revision: `4fd86cee4b85bb946a9c8ce7eab2c405e5568144`.
Verified design revision: `efce833e3ad4d47c090987ff60f72c622294d936`.
Branch: `experiment/agent-guided-network`.
Review: [Draft PR 14](https://github.com/chris-buckley/open-agent-knowledge/pull/14).

## Outcome

The design preserves the user's intent: agents help revise matrices owned by OAK nodes during learning, then are removed while the learned numerical network runs alone. The specification covers numerical-first execution, immutable revisions, meaningful modules, behavioural proposals and numerical fitting, credit assignment, coordinated acceptance, independent evaluation, export closure, research precedents, and risks.

The package separates node contracts, training, numerical export, benchmark design, primary sources, and evidence status. The plan marks design delivery complete and keeps all twelve future implementation, training, evaluation, and export tasks open. No runtime, benchmark result, trained weights, or numerical export artifact is represented as implemented.

## Changed paths

Ten new documents belong to `experiments/` and `docs/plans/0009-agent-guided-network/`. Root `AGENTS.md` and `build/checks/agents.py` each gain one matching experiment-owner entry. No OAK grammar, execution semantics, runtime dependency, or verification assertion is changed.

The initial design commit is `ca70d3b65ae041efdb66ca45ad1406b4ab58eff5`. During publication, main advanced through PR 13 and allocated plan number 0008 to the self-contained examples change. This branch preserves that change and uses 0009 for its own plan, repairing every experiment link. The original design baseline remains recorded as provenance, not as a claim that main did not advance.

## Verification evidence

The root and applicable scoped owners were read before repository changes. Updated root, build, and example owners were re-read when main advanced. Research titles, primary-source abstracts, and official export documentation were checked on 5 September 2026.

Local document checks passed for ten nonempty UTF-8 files, documentation conventions, forty relative Markdown links, five compact SMEAC phases, sixteen unique task identifiers, and open future implementation tasks. The eight published experiment blobs matched the locally checked drafts before the plan-link repair; the repaired drafts also passed those checks.

Local repository cloning failed with `Could not resolve host: github.com`. Local draft checks were not execution of the repository. Repository-wide execution was performed by the existing GitHub Actions workflow through draft PR 14.

[Run 33964324673](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33964324673) failed on design revision `3f88ee12542548843302ec803ee5bac58ad09c05` with `RuntimeError: experiments/AGENTS.md is not canonical XML-grouped OAK`. Inspection of the existing renderer established that four action binding lists exceeded the canonical width of 100 Unicode code points. Commit `efce833e3ad4d47c090987ff60f72c622294d936` applied the required expanded layout without changing meaning or weakening checks.

[Run 33964429242](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/33964429242), named Verify OAK, completed with conclusion `success` for that corrected design revision. The workflow covers compilation, example catalogue generation, EBNF/reference/authoring generation, both complete verification entry points, repeated generation with a clean diff, and the approved detached bootstrap/cache check. This is observed GitHub Actions evidence, not a claim of local repository execution.

This report's CI evidence is pinned to the verified design revision above. The final record update changes only this report and the design-delivery checkbox; its own CI status remains separately visible on PR 14 rather than being inferred from an earlier run.

## Experimental evidence

None. [Evidence status](../../../experiments/agent-guided-network/results/STATUS.md) explicitly records that training, benchmarking, and numerical export have not been run. Passing repository validation is not a scientific result.

## Verdict

The requested design package is committed, its repository verification passed, and Phase 1 is complete. Implementation and experimental verdicts remain open. No write or merge into main was performed by this experiment change.
