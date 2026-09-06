# Executable OAK modules and bounded learning

Recorded: 6 September 2026.
Baseline: `17a96a8be4f7ef1c0fdd4bb90884be94feb97d92`.
Status: Accepted design; measurements require source freeze and executable evidence.

## Question

Does OAK provide useful executable ownership, composition, reuse and bounded revision of numerical modules, rather than merely packaging one opaque Python model? Separately, can the teaching agent improve wording transfer by changing a selected module while leaving other modules byte-identical?

Agent participation is the intended learning mechanism. Neither a control match nor a negative transfer result invalidates participation. OAK is not credited for accuracy merely because it serialises weights. This study does not claim a new neural learning algorithm, general intelligence or conversation.

## Architecture and invariants

Decompose the verified 6,431-coefficient meaning network without initially changing its mathematics. Separate canonical OAK documents own the shared sentence encoder, attention retrieval, answer readout, observation memory, shared schemas and root composition. The same encoder process and weights serve observations and questions. Memory owns only observed event text. Parameters remain fixed within each run; accepted revisions create new documents.

Actual OAK CALL targets and named numerical actions define the computation. A restricted lowering adapter traverses the resolved processes to make an inference-only program; it must not ignore the graph and reconstruct an independently hard-coded network. Unsupported instructions, operations, control flow or malformed contracts fail export. OAK execution and lowered execution must agree. Python/NumPy still implement mathematical primitives; this is not a tensor-language extension or a universal OAK compiler.

A host-enforced update transaction names the baseline graph hash, permitted module paths, allowed parameter groups and candidate. Reject stale baselines, cross-module writes, nonparameter edits, invalid tensors and regression failures. Valid-looking JSON and a persuasive rationale are not acceptance evidence. Candidate evaluation occurs before promotion; rejected candidates remain recorded. Isolation means other module bytes remain unchanged, not that their outputs cannot change when an upstream module changes.

## Engineering tests

First prove decomposition equivalence using archived selected networks and new inputs. Test OAK resolution, canonical round trips, full numerical probabilities, state save/restore, isolated exports, missing dependencies, altered schema identity, unsupported operations, invalid matrix shape and semantic-boundary violations. Demonstrate that two consumers reuse one encoder owner and that a compatible module revision changes no neighbouring documents. Distinguish OAK-native checks from adapter-added tensor and edit-policy checks. Record source/compiled sizes, module coefficient counts and observed execution overhead; do not claim a productivity advantage without measuring one.

## Learning study

Keep the earlier four studies and their scientific sources unchanged. This is a new continuation study, not a replication of the old unseen-wording evaluation. That old failure is now known and may inform teaching. Start from the three archived selected meaning networks. Use fresh data seeds 503, 509 and 521, respectively paired with prior model seeds 401, 409 and 419. This is three numerical initialisations and one shared-context proposer, not three independent agents.

Use 1,024 new training histories, half ordinary and half five-to-six moves. Render the four already exposed sentence arrangements for teaching. Use 128 disjoint development histories per ordinary and medium regime. The next unseen arrangements are `the {o} from the {s} moved to the {d}` and `from the {s} to the {d} the {o} moved`; neither is used to select candidates. Final evaluation uses 256 disjoint histories per ordinary, new-combination and twelve-to-eighteen-move regime, plus both new arrangements. Split latent histories before wording and exclude archived training/development/final histories wherever recovered. Report source and destination questions separately, because the previous combination generator withholds destinations but not necessarily sources.

All fitting uses 300 Adam steps, learning rate 0.003, batch size 48, two wording views and the previous 0.3 agreement objective. Compare unchanged parameters, full-network ordinary-wording continuation, full-network varied-wording continuation and agent-selected module-restricted varied-wording teaching. Same examples and fitting steps do not imply equal compute or total cost; report trainable coefficients and unavailable conversation cost.

On the first new seed the assistant may make at most two proposals after inspecting development evidence. Permitted parameter owners are encoder, attention or readout, singly or explicitly named jointly. Acceptance requires at least 0.01 mean development accuracy gain with no regime dropping more than 0.03. The same chosen proposal methods may be numerically replayed on the other initialisations; label replay honestly. Freeze source, parameter baselines, data identities and settings after implementation-only seed-zero checks and before scored proposals. Close every selection before generating final cases. Do not reopen final tests to fix the chosen model.

## Evidence and finalisation

Retain observations, pre-evaluation proposals, candidate identities, changed-module lists, acceptance decisions, raw final predictions, labels and all failures. Update LEARNINGS.md with stable evidence-linked findings. Export selected OAK graphs to isolated numerical programs and check parameter identity, probability agreement, state reset and model-bound restoration without OAK, PyTorch, training code, simulator, credentials or network access. A transfer failure is a scientific result; an export mismatch blocks deployment equivalence.

The existing SMEAC record owns task state. All work stays on the experiment branch. No merge into main is authorised. Branch verification and compatibility with newer main are separate claims.

## Research connections

Andreas et al., Neural Module Networks (2015): https://arxiv.org/abs/1511.02799 . Reusable learned modules are an established idea; OAK ownership is not a novelty claim about modular networks.

Battaglia et al., Relational inductive biases, deep learning, and graph networks (2018): https://arxiv.org/abs/1806.01261 . Shared structured computation motivates reuse, not guaranteed generalisation.

Kim and Linzen, COGS (2020): https://aclanthology.org/2020.emnlp-main.731/ . Systematic held-out combinations motivate evaluation design. These results are not COGS scores.
