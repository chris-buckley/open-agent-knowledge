# Agent-guided network design delivery

Date: 2026-09-05.
Scope: Experiment design and repository structure only.
Plan: [SMEAC execution record](plan.md).
Specification: [EXPERIMENT.md](../../../experiments/agent-guided-network/EXPERIMENT.md).
Original baseline: `cd1f8aed74b24f8515a3e176972e9f2cbcb53e5a`.
Integrated main revision: `4fd86cee4b85bb946a9c8ce7eab2c405e5568144`.
Branch: `experiment/agent-guided-network`.
Review: [Draft PR 14](https://github.com/chris-buckley/open-agent-knowledge/pull/14).

## Outcome

The design preserves the user's intent: agents help revise matrices owned by OAK nodes during learning, then are removed while the learned numerical network runs alone. The specification covers numerical-first execution, immutable revisions, meaningful modules, behavioural proposals and numerical fitting, credit assignment, coordinated acceptance, independent evaluation, export closure, research precedents, and risks.

The package separates node contracts, training, numerical export, benchmark design, primary sources, and evidence status. The plan keeps future implementation tasks open and explicitly gated. No runtime, training integration, benchmark result, trained weights, or export artifact is represented as implemented.

## Changed paths

Ten new documents belong to `experiments/` and `docs/plans/0009-agent-guided-network/`. Root `AGENTS.md` and `build/checks/agents.py` each gain one matching experiment-owner entry. No OAK grammar or execution semantics are changed.

The initial design commit is `ca70d3b65ae041efdb66ca45ad1406b4ab58eff5`. During publication, main advanced through PR 13 and allocated plan number 0008 to the self-contained examples change. This branch preserves that change and moves its own plan to 0009, repairing every experiment link. The original design baseline remains recorded as provenance, not as a claim that main did not advance.

## Verification evidence

The root and applicable scoped owners were read before repository changes. Updated root, build, and example owners were re-read when main advanced. Research titles, primary-source abstracts, and official export documentation were checked on 5 September 2026.

Local document checks passed for ten nonempty UTF-8 files, documentation conventions, forty relative Markdown links, five compact SMEAC phases, sixteen unique task identifiers, and open future implementation tasks. The eight published experiment blobs matched the locally checked drafts before the plan-link repair; the repaired drafts also passed the document checks.

Local repository cloning failed with `Could not resolve host: github.com`. These local draft checks are not execution of the repository. Draft PR 14 enables the existing repository verification workflow. The final observed CI result is recorded after the integrated candidate is checked, not assumed from the presence of a workflow.

## Experimental evidence

None. [Evidence status](../../../experiments/agent-guided-network/results/STATUS.md) explicitly records that training, benchmarking, and export have not been run. Repository validation, if successful, is not a scientific result.

## Verdict

Design package committed and under repository verification. Implementation and experimental verdicts remain open. No write or merge into main is authorised or performed by this experiment change.
