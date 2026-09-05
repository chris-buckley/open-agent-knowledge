# Agent-guided numerical networks

Prepared: 2026-09-05
Status: Design recorded; sequential single-agent implementation and execution authorised on 2026-09-05. No numerical result is claimed yet.
Baseline: OAK `cd1f8aed74b24f8515a3e176972e9f2cbcb53e5a`.
Branch: `experiment/agent-guided-network`.

## Intent

Build a numerical network whose computational modules are defined by OAK documents. During learning, an agent wraps each module, understands its intended responsibility, examines evidence about its behaviour, and participates in proposing updates to that module's matrices. The network's collective output is evaluated, feedback informs further proposals, and accepted changes become new versions of the node documents.

After learning, remove the agents completely. The remaining matrices, mathematical operations, connections, and input/output transformations must perform inference without language-model calls, conversational memory, natural-language interpretation, or agent judgement.

The user's defining idea is agents participating in the learning journey, not agents remaining responsible for the learned capability. The intended eventual scale is hundreds of connected OAK-defined modules. A small, inspectable experiment comes first to test the mechanism, not to replace that ambition.

The central requirement is that useful agent contributions become concrete numerical changes. A revised prompt, a persuasive explanation, or an agent correcting an answer is not a learned network update.

## Execution model: one running agent, many node responsibilities

The agent running this experiment acts on behalf of the logical node agents, including the proposed "100 agents". For the first execution, this is the assistant conducting the work in this conversation. It visits node responsibilities sequentially, examines numerical observations, proposes changes to the selected node's permitted matrices, and asks deterministic tools to fit and evaluate the proposed changes. No autonomous multi-agent framework, background agent fleet, or separate language-model instance per node is required.

"100 agents" describes logical learning responsibilities, not a claim that 100 independent agents have been launched. Report the actual number of numerical nodes, the actual proposer count of one, and the sequential scheduling policy. The initial runnable network may be smaller. Shared conversational context means this treatment is not an independent local-agent population and cannot establish an advantage of distributed agents over a central agent.

The assistant must actually inspect observations and record its chosen proposal and rationale before seeing the candidate's evaluation. A scripted optimiser replaying a recorded proposal is a reproducibility mechanism, not a new agent decision. Do not label hand-coded heuristics, numerical solvers, replay, or fabricated dialogue as autonomous agent activity.

Python performs every scored forward pass and computes the fixed evaluation metrics. The running assistant may choose a behavioural target, preservation examples, a bounded parameter change, or a numerical fitting method, but cannot supply answers during scored inference or rewrite the evaluator after seeing results. Accepted candidates become new immutable OAK node revisions; current constants remain fixed during each run.

The authorised next work is to implement and run a small real feasibility experiment on this same branch, compare initial, numerical-only, and agent-guided networks, and verify a standalone numerical export. Record observed improvements, ties, or regressions without assuming agent benefit. Keep final test examples outside the proposal loop, disclose privileged task knowledge and resource differences, and leave any unperformed broader ablation or scale study explicitly open. The user requested this clarification as the next commit before implementation, with progress updates during execution.

## Decisive architectural choice

Make the network numerical from the beginning. Do not first build an agent conversation graph and assume it can later be converted into matrices.

Every forward pass used to score a candidate already runs without agents. Agents participate between numerical runs by proposing changes. Unwrapping therefore removes training machinery; it does not substitute a different inference system.

```text
NUMERICAL COMPUTATION, DURING AND AFTER LEARNING

Input -> module A -> module B -> ... -> output
            |           |                 |
       observations and diagnostics        |
            |           |                 v
TEMPORARY LEARNING SUPPORT          fixed evaluator
                    |                     |
        one running assistant <------ feedback
        acting for node A, then node B, ...
                    |
        constrained update proposals
                    |
       numerical fitting and candidate tests
                    |
       accepted node revisions for the next run
```

Agent-free does not mean runtime-free. Ordinary numerical software still loads parameters and executes operations. The final artifact must contain every required encoder, numerical routing decision, state initialiser, and decoder, not just the weight matrices.

## Terms and scope

| Term | Meaning in this experiment |
| --- | --- |
| OAK node | The canonical knowledge unit described by one document. It remains idless; its document path supplies graph identity. |
| Computational module | A numerical transformation associated with an OAK node, not necessarily one scalar neuron. |
| Wrapper agent | Temporary learning responsibility for a module. In the initial execution, the same running assistant assumes each responsibility sequentially. It cannot contribute to scored forward computation. |
| Network | The explicit composition of numerical modules, connections, and complete input/output processing. |
| Node revision | An immutable candidate or accepted version of a module document and its parameters. |
| Network revision | One exact, compatible set of node revisions, topology, operation definitions, and preprocessing. |
| Evaluator | Host-controlled measurement and acceptance logic, separate from proposing agents. |
| Unwrapping | Removing agent dependencies and exporting the already-numerical inference graph. |

OAK's node and host boundaries are defined by [the node owner](../../oak/node/AGENTS.md) and [the package owner](../../oak/AGENTS.md). This is an application of those boundaries, not a new definition of OAK.

## Questions the experiment must answer

H01, engineering: can agent-proposed updates produce useful numerical behaviour that persists after the wrappers are removed?

H02, learning value: does agent-guided numerical fitting outperform strong non-agent alternatives under declared resource budgets? No advantage is a valid result.

H03, meaning: do correct module descriptions and stable semantic interfaces improve proposals relative to missing or shuffled descriptions?

H04, organisation: do local node agents provide an advantage over one central agent with comparable information and budget? Sequential role-taking by one assistant does not answer this question.

H05, scale: does the approach remain useful as the number of modules grows toward hundreds? This is a later measurement target, not an established property.

Engineering success and scientific advantage are separate verdicts. A working export demonstrates the former, not automatically the latter. Modularity, parameter changes, and explanatory labels alone do not establish learning, causality, or interpretability.

## What each node owns

A basic numerical module may compute:

```text
h_i = activation_i(W_i x_i + b_i)
```

Other modules may compose relations, combine evidence, or apply numerical gates. Their exact operations must be declared and supported by the runtime. Matrices alone are insufficient to define a network: dimensions, axes, operations, connectivity, and numerical semantics must be explicit.

| OAK part | Responsibility in this application |
| --- | --- |
| Schemas | Reusable input/output shapes, parameter descriptions, observations, proposals, and evaluation records. |
| Constants | A revision's fixed matrices, biases, masks, axis meanings, and other fixed knowledge. |
| State | Training history or genuinely persistent runtime values when required, never undeclared replacement parameter storage. |
| Interfaces | Complete boundary payloads for requests, results, observations, or proposals. |
| Triggers | Outside arrivals that start work, not internal neuron firing or an implicit inter-node message bus. |
| Processes | Ordered numerical actions and explicit process composition; separately scoped learning work. |
| Instructions | Irreducible learning policy or explanation, not missing inference-time computation. |

These responsibilities follow [OAK's existing part contracts](../../oak/node/AGENTS.md). Empty parts remain omitted, and documents retain canonical part order. Connections must be represented explicitly; putting several documents in a directory does not connect them.

Small matrices, including 2D and 3D arrays, can be represented as nested JSON values in constants. The [current constant model](../../oak/node/parts/constants.py) permits JSON values; it does not alone establish tensor shape, dtype, arithmetic, or cross-node dimension compatibility. The proposed host adapter must enforce those additional contracts.

Parameters remain literally inside their owning OAK documents for the first experiment. An agent reads that canonical source and proposes its revision; it does not maintain a second authoritative weight store. Within a loaded revision, constants never mutate. An accepted update creates a new revision loaded for the next cycle. Transient candidate tensors are working values, not changes to the currently running document.

If large binary parameter bundles become necessary, their ownership and content identity require a separately evaluated packaging decision. They are not introduced here to quietly replace the inline-matrix requirement.

## How agents participate in learning

The preferred hypothesis is not that a language model can intuit arbitrary millions of floating-point values. It is that the agent can identify a useful behavioural correction and use numerical tools to realise it.

For example: a module mistakes contradictory evidence for additional support. Its agent identifies failing examples, requests a different response on them, and names already-correct behaviour that should be preserved. A solver materialises a candidate matrix update. The network evaluator, not the agent's confidence, determines whether that update survives.

For a linear module, let `W` have shape `[out, in]`, let the columns of `X` contain correction inputs, let `Y_target` contain desired outputs, and let the columns of `P` contain preservation inputs. A proposed fitting objective is:

```text
min_delta ||(W + delta) X - Y_target||_F^2
        + lambda ||delta P||_F^2
        + mu ||delta||_F^2
```

Here `lambda >= 0` weights preservation and `mu > 0` regularises the change. This is a regularised least-squares construction for the stated linear case. Nonlinear modules require an appropriate numerical optimisation procedure. Protected samples constrain observed behaviour only; they do not prove global preservation.

The preservation-versus-change idea has a precedent in model editing, but this objective and its use by local OAK agents are a proposed adaptation, not a reproduction of ROME or MEMIT. See [R03, R04, and R07](research/SOURCES.md).

The primary method combines agent-guided behavioural proposals, numerical fitting, and independent candidate acceptance. Direct sparse edits, small matrix edits, or low-rank updates remain comparison mechanisms where justified. Gradient information may assist an agent; banning gradients would test a different, unnecessarily restrictive hypothesis.

The first experiment fixes topology and numerical operators. Agents change permitted parameters, not evaluator code, network structure, schemas, operation implementations, or the definition of success. Later architecture search must be reported as a different treatment.

## Why meaningful modules matter

Assign agents coherent responsibilities, not arbitrary scalar neurons. Relation composition, evidence combination, and numerical routing are possible module roles. Give each agent its role, stable tensor-axis meanings, selected input/output traces, failure cases, activation and parameter summaries, and gradients when available.

A channel called `conflict` is not proven to detect conflict. Its semantics need supervision or intervention tests. [Concept bottleneck models, R08](research/SOURCES.md), motivate meaningful intermediate contracts, but their use of concept correction at test time does not satisfy our agent-free inference requirement.

Keep large numerical inspections in numerical tools rather than filling the language-model context with complete matrices. One shared language model may serve many logical wrappers. Separate ownership, evidence, and revision identity matter more than running hundreds of separately hosted models. The first execution uses the running assistant for all of those responsibilities, as specified above.

Agents need not act after every example. Invoke them for persistent failure clusters, stalled improvement, or predeclared review intervals while numerical optimisation performs routine fitting. Count the cost of both activities.

## Coordination and credit assignment

A final network score does not identify which module should change. Use end-to-end gradients where available, replacement tests against a frozen network, local concept checks, and selected counterfactual traces. Local measures diagnose; whole-network measures govern acceptance.

A minimal interference example is `y = w1 * w2` with target `1` and initial `w1 = w2 = 0.5`. Either agent can propose changing its own weight to `2`, which is perfect while the other weight remains `0.5`. Combining both individually successful proposals produces `4`.

Therefore every proposal names its exact baseline network revision. Acceptance initially proceeds sequentially. Future agents may propose in parallel, but combinations must be jointly evaluated. Re-evaluate stale proposals and combinations. Never merge local successes merely because their edited files differ.

Retain the best-known network separately from exploratory candidates. Coordinated improvements may require a bounded search branch, but an exploratory regression must not silently replace the accepted network. The full lifecycle and rejection rules are in [the training protocol](training/PROTOCOL.md).

## Numerical runtime and unwrapping

Use OAK for knowledge, contracts, ownership, and composition. Build a small host-side numerical adapter rather than a new OAK tensor language. [OAK execution](../../oak/execute/AGENTS.md) already distinguishes exact named-tool actions from interpreter-native actions. The adapter must explicitly implement supported numerical actions; existing tool dispatch is not itself a tensor compiler.

Keep tensors and derivatives in the numerical backend during computation. Do not serialise every internal activation through OAK text. A numerical graph built from validated documents remains accountable to their contracts and revisions.

Start with an acyclic graph. [OAK resolution](../../oak/resolve/AGENTS.md) rejects process-call cycles; arbitrary recurrent neural connections cannot be represented by ignoring that rule. Any later recurrence requires explicit state, scheduling, and supported numerical semantics.

Export is a checked property from the start. Every action reachable from inference must have a supported numerical meaning. Reject unresolved free-form actions, agent-dependent routing, unbundled encoders, and hidden external model calls. Never erase instructions that change behaviour merely to make export appear successful.

PyTorch and ONNX provide a possible route for a supported subset, not a universal exporter for OAK. Backend versions, operation coverage, and tolerances must be fixed during implementation. A clean process without credentials or training memory must load the artifact and reproduce reference outputs. See [the export contract](runtime/EXPORT.md) and [R09](research/SOURCES.md).

## First experiment and scientific controls

Begin with a small network, with about 16 meaningful modules as the initial design target, on a synthetic compositional-relation task with deterministic ground truth. The executing assistant may choose a smaller feasibility instance and must record its actual size before running comparisons. Inputs are numerical relation tables; output labels are calculated by an exact reference evaluator. Relation instances are data, not automatically learned parameters. The node matrices parameterise computation across examples.

A small permissions-style composition, such as a person's roles composed with role capabilities, is an understandable smoke test. It is not evidence that learned embeddings prove permissions or that the approach improves training. Real policy enforcement is outside this experiment.

Freeze the exact task, topology, operators, dataset split, acceptance criteria, and budget before scored comparisons. Use held-out entity assignments and relation combinations where meaningful, expose any extra rule knowledge given to agents, and do not let wrappers inspect the final test set.

Compare a strong numerical optimiser, budgeted non-agent proposal search, one central training agent, local agents with direct edits, and local agents with numerical fitting in the full study. Include matched numerical fitting without agents to separate the solver's contribution from the agent's. Test missing or shuffled descriptions and local-only versus whole-network acceptance. The first sequential-assistant run compares initial, numerical-only, and agent-guided networks; it does not claim that all full-study treatments have been run.

Measure held-out predictive performance, compute and language-model cost, candidate evaluation count, update acceptance, regressions, and exported equivalence across independent seeds. Reserve a final test set outside the adaptive improvement loop. Equal candidate count and equal total resource cost are different comparisons; report both rather than hiding the cost of the agents.

[The benchmark protocol](evaluation/BENCHMARK.md) owns detailed measurements and verdicts. No benchmark result exists at this stage.

## Research synthesis

| Evidence | Useful connection | Limit of the connection |
| --- | --- | --- |
| Tensor Logic, R01 | Logical relations and neural computation can use a tensor-based representation. | Does not establish distributed agent-guided matrix learning. |
| OPRO, R02 | Language models propose candidates using measured optimisation feedback. | Not evidence for efficiently writing large dense networks' weights. |
| ROME and MEMIT, R03/R04 | Specific behaviour can be changed through numerical weight edits. | Editing pretrained associations is not training this network from scratch. |
| AlphaEvolve, R05 | Agent proposals can be selected by external executable evaluation. | Its code evolution does not establish safe composition of local weight updates. |
| FunL2O, R06 | LLM-proposed feature programs are assessed through retraining and downstream evaluation. | Changes feature functions, not node-owned matrices through distributed wrappers. |
| Unified model editing, R07 | Formalises the tension between changing and preserving behaviour. | Does not validate our proposed agent/solver allocation of work. |
| Concept bottlenecks, R08 | Intermediate representations can be organised around meaningful concepts. | Labels alone do not supply meaning or guarantee agent-free inference. |
| PyTorch export, R09 | Supported numerical graphs can be exported and compared in ONNX Runtime. | Arbitrary OAK actions are not thereby exportable. |

[The source register](research/SOURCES.md) records primary sources, versions or publication dates, and what was checked. These are precedents for ingredients, not a novelty claim or proof that their combination will beat existing methods.

## Risks and design responses

| Risk | Response to test |
| --- | --- |
| Persuasive but incorrect agent diagnosis | Independent numerical evaluation and regression cases. |
| Local improvement damages other modules | Revision-pinned whole-network and joint-candidate evaluation. |
| Interface semantics drift | Fixed axes, schemas, and topology in the first treatment. |
| Agent knowledge leaks the answer | Record all extra supervision; equalise it or label the comparison. |
| Adaptive overfitting to evaluation data | Separate training, development, and sealed final testing. |
| Gains come only from the numerical solver | Matched solver-only and non-agent proposal baselines. |
| Explanation is mistaken for causal evidence | Counterfactual tests and explicit uncertainty. |
| Export depends on hidden reasoning or services | Static operation audit plus clean, offline execution tests. |
| Dense matrices overwhelm agent context or cost | Semantic modules, summaries, constrained edits, and measured budgets. |
| Parameter changes erase useful behaviour | Preservation cases, bounded updates, retained incumbent, and rollback. |
| Scaling fails beyond the small network | Report the measured limit; do not extrapolate to hundreds. |
| One assistant is mistaken for independent agents | Record one proposer, sequential node roles, shared context, and actual node count. |

## Directory structure and ownership

```text
experiments/
  AGENTS.md
  agent-guided-network/
    EXPERIMENT.md
    nodes/
      CONTRACT.md
    training/
      PROTOCOL.md
    runtime/
      EXPORT.md
    evaluation/
      BENCHMARK.md
    research/
      SOURCES.md
    results/
      STATUS.md

docs/plans/0009-agent-guided-network/
  plan.md
  report.md
```

This file is the complete conceptual synthesis and decision rationale. Supporting files own precise contracts, procedures, research attribution, and evidence status without creating a second architecture. The [SMEAC plan](../../docs/plans/0009-agent-guided-network/plan.md) owns implementation tasks and authorisation gates; the [report](../../docs/plans/0009-agent-guided-network/report.md) records delivery evidence.

During implementation, actual node `.oak.md` documents belong in `nodes/`, training code beside its protocol, numerical adapter/export code in `runtime/`, and the evaluator/tests beside the benchmark. Reusable schemas should be authored as OAK documents when implemented; this design does not introduce a second task-specific configuration language. A distributable training skill belongs in the repository's normal `skills/` product area only when it is genuinely implemented and packaged.

Create per-run result directories only when runs exist. Do not fill the structure with fake weights, sample success numbers, empty Python modules, or placeholder test suites.

## Current decision

Implement and run the numerical-first feasibility experiment with the current assistant serving all logical node-agent roles sequentially. Preserve immutable inline node parameters, behavioural proposals materialised by numerical tools, independent acceptance, and agent-free export.

The user authorised execution on 2026-09-05 after requesting this documentation change as the next commit. First establish the smallest working numerical path, then make and evaluate actual assistant proposals, and report measured results with limitations. This authorisation does not claim that implementation, training, or export has already succeeded, and does not authorise merging into main.