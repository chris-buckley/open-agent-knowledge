# Agent-guided training protocol

Status: Proposed; no training coordinator or agent integration is implemented.

## Roles

The node agent proposes changes using its module's declared responsibility and allowed observations. A numerical solver materialises permitted proposals. An independent evaluator measures their consequences. A coordinator controls snapshots, budgets, scheduling, and acceptance. The same model may serve multiple logical wrappers, but its contexts and proposals remain attributable to their respective modules.

No proposing agent can edit evaluator code, final-test data, acceptance thresholds, schemas, operation implementations, or topology in the initial treatment. Agents have no place in the scored forward path.

## One cycle

1. Freeze the incumbent network, dataset split identities, evaluator, and numerical environment. Compute their revision identities with host tools.
2. Run numerical computation on permitted training cases. Gather failure clusters and node-specific traces, activation summaries, sensitivity information, and gradients where available.
3. Supply selected wrappers with bounded diagnostic context. Supply only data permitted by the benchmark protocol. Record the information and any additional semantic supervision they receive.
4. Ask for a constrained proposal against the frozen revision. The primary form specifies correction examples, desired behaviour, preservation examples, and allowed parameters. Direct numerical edits form a separately recorded treatment.
5. Validate proposal targets and budgets. Materialise candidate parameters in an isolated copy using a numerical solver or permitted direct edit. Reject invalid shapes, non-finite values, forbidden writes, and exceeded bounds.
6. Measure the complete numerical network with those candidate parameters. Local concept tests are supporting diagnostics, not the acceptance authority.
7. Apply the frozen acceptance rule. Retest combinations of updates; do not infer compatibility from disjoint files. Re-evaluate proposals whose baseline has changed.
8. Immediately before acceptance, reject baseline drift. Atomically select the new compatible network snapshot or keep the incumbent, then record the decision and all measured costs.

Each cycle terminates within a predeclared proposal, numerical-step, evaluation, and resource budget. An unsuccessful proposal is evidence, not a reason to keep searching without accounting for additional cost.

## Candidate mechanisms

The primary treatment uses agent-selected behavioural constraints followed by numerical fitting. For the linear example in [EXPERIMENT.md](../EXPERIMENT.md), solve the stated regularised least-squares objective. For nonlinear modules, use an explicitly budgeted optimiser and report its settings.

Compare sparse direct edits, low-rank updates where appropriate, and numerical fitting with no agent. Record which component selected the target behaviour, which computed the parameter values, and what information each could access. Do not present solver improvements as evidence for semantic agent reasoning without the corresponding controls.

When desired local outputs are not supervised, label them as agent hypotheses. Downstream evaluation may reject them. Infeasible requests must produce a failed candidate or a recorded fitting residual, not fabricated target satisfaction.

## Coordination and credit

Initially accept one update at a time or a small jointly evaluated set. Candidate generation may be parallel; candidate commitment is revision-aware. A local gradient, counterfactual improvement, or confident explanation never authorises an untested combined update.

Track the accepted incumbent separately from exploratory snapshots. Exploration may tolerate bounded temporary regressions under its own budget, but only a candidate meeting the acceptance policy replaces the incumbent. Retain the last accepted snapshot for rollback.

## Stopping and failure

Stop a run on its fixed budget, its predeclared convergence condition, or an unrecoverable validity error. Record rejected, timed-out, stale, and non-improving proposals. Infrastructure failures and exhausted budgets are not successful training outcomes.

Do not expose the sealed test set to the coordinator's selection loop. The final evaluator runs only after candidate selection is frozen. No hidden conversational history, correction service, or wrapper-specific state may be needed to reproduce inference.

[Node contracts](../nodes/CONTRACT.md) define the records. [The benchmark](../evaluation/BENCHMARK.md) defines comparison and acceptance criteria. [Result status](../results/STATUS.md) distinguishes actual runs from this proposal.
