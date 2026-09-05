# Agent-guided network design delivery

Date: 2026-09-05.
Original scope: Experiment design and repository structure. The follow-on execution is recorded below; the original design account is retained as history.
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

## Authorised sequential-assistant execution

The user subsequently authorised a real small experiment, with the current assistant acting for all logical node roles. Commit `5a25878b5ee0a42252e92d4af549ac4149cde24f` updated EXPERIMENT.md as the next commit before implementation, as requested. No autonomous fleet or external paid model API was launched.

The container could not resolve github.com for cloning. Source snapshot workflow run 33965092932 produced artifact 9969158360 for commit `a825c588b699b453bb24703c68bb724b033b0797`. Its source.tar SHA256 was verified as `355ffff1de871510979b0f8ff675bf280fa3187cea8e13afd8e7b9631d2b4492` before extraction. The extracted repository's complete module verification entry point passed locally before implementation. Later numerical and OAK checks were real local execution, unlike the earlier design-only turn.

The [first-run report](../../../experiments/agent-guided-network/results/first-run/REPORT.md) records four actual assistant proposals on seed 7, one rejected and three accepted, and explicitly labelled numerical replay on two more seeds. All parameters remain inline in canonical OAK snapshots. A fresh numerical replay reproduced every recorded metric. The three selected deployment artifacts ran in isolated processes without OAK or agents and matched source outputs exactly on the tested cases.

Mean test accuracy was 99.9268% for the assistant-guided sequence and 99.9430% for numerical-only Adam. The engineering mechanism is demonstrated on this small synthetic task. Scientific superiority, hundred-node scaling, independent-agent effects, direct-edit comparisons, and semantic ablations are not established. Two broader plan tasks remain open instead of being marked complete without evidence.

The committed numerical source is identified by the code hashes in the run freeze. [Local verification](../../../experiments/agent-guided-network/results/first-run/verification.json) records actual commands, return codes, and package versions. The final publication/CI result belongs to the PR's current head and is not inferred from an older run. No merge into main is performed.
