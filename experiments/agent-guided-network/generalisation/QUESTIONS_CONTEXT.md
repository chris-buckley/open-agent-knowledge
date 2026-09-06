# Question-conditioned modules and shared context

Recorded: 6 September 2026, Brisbane time.
Status: Research proposal and continuation boundary. No new implementation or numerical result is claimed.
Inspected branch revision: `6fcc739aaca1516f698704c5d21c5443206af6de`.
Intent: [EXPERIMENT.md](../EXPERIMENT.md).
Related design: [WORLD_LANGUAGE.md](WORLD_LANGUAGE.md).
Existing protocol: [STUDY.md](STUDY.md).
Evidence index: [LEARNINGS.md](../LEARNINGS.md).

## User question and recommendation

The user asks whether matrices can be framed as questions about entities, time, change, or underlying structure, and whether a shared context matrix should carry the changing global context.

Investigate both ideas, with two distinctions. Give a computational module a testable question or prediction responsibility, not every individual matrix a presumed semantic meaning. Add shared numerical working memory inside the network, not an external reasoning agent above it. Fixed learned parameters determine how memory is read and updated; episode memory records what the model currently believes from its observations.

The intended mechanism remains agent participation during learning followed by agent-free numerical inference. Comparative superiority remains a separate question. Neither naming a matrix nor adding memory by itself establishes generalisation, interpretability, or conversation.

## Continuation boundary

At the inspected revision, the generalisation directory contains STUDY.md and WORLD_LANGUAGE.md. The existing protocol describes a learned encoder, attention over an episodic message log, and an autoregressive decoder. It does not provide a verified implementation or completed world-language run in that directory.

The preceding conversation mentioned local prototype checks and rejected teaching updates, but the current recovered files do not establish their implementation or results. Do not promote those statements into the empirical learning ledger, reconstruct measurements from prose, or assume an earlier local directory still exists. Recover and verify an exact source and evidence snapshot, or implement a new traceable baseline. A reconstruction is a new implementation, not recovery of the original experiment.

This note does not alter the existing protocol's frozen settings, reopen its proposed final tests, or claim that a proposed context architecture has been trained. A context or auxiliary-question comparison needs its own versioned protocol and fresh held-out histories before scoring. Implementation task state remains with the existing repository plan, not this research note.

## Questions as responsibilities, not labels on numbers

An OAK module could specify the question it is intended to answer, its numerical inputs and outputs, the required evidence, and the tests that would falsify the intended behaviour. The language description helps the training agent choose lessons and diagnose failures. The exported numerical operations must implement the behaviour without reading that prose through an external model.

| Concern | Example question | Evidence required |
| --- | --- | --- |
| Identity | Does this observation refer to the same entity as an earlier one? | Correct binding across aliases and changed attributes, including negative matches. |
| Current relations | Where is the queried entity now, according to the observations? | Correct updates after moves, containment, and removal, without reading simulator state. |
| Time | What was true before the last relevant event? | Earlier and current answers differ correctly; absolute event time and mention order are not confused. |
| Change | Which entity relationships should this observation change? | Relevant state changes and unrelated state is preserved. |
| Prediction | What is likely after this specified action and time interval? | Future observations under an explicit action and horizon; uncertainty where outcomes are not determined. |
| Evidence | Is the requested answer supported, missing, or contradicted? | Appropriate uncertainty on omitted or conflicting observations, not a confidence label alone. |

These are candidate training responsibilities, not a closed ontology or a claim to derive intelligence from fundamental physics. A time derivative is meaningful only after choosing a state variable, time scale, and units. For discrete stories, a before/after change is the more direct target. A prediction about an intervention is different from noticing temporal order and requires an explicit intervention model or corresponding evidence.

The same question family should apply to different entities. Prefer one shared relation-update mechanism and reusable question encoding over a matrix for each noun, object, or English question. New names need a declared numerical encoding and binding mechanism. Adding a memory slot alone does not teach a previously unknown word.

In attention, a learned query projection produces input-dependent query vectors. The fixed projection is not itself the current question, and queries do not have to correspond to English sentences. Several matrices normally cooperate to implement one useful operation [Q01]. Arbitrarily renaming a projection to time or matter changes no numerical behaviour.

Question-shaped auxiliary training is a credible research direction: Dynamic Memory Networks condition memory processing on questions [Q02], and work on discovering useful predictive questions studies additional objectives that improve representations for another task [Q03]. Neither establishes that every matrix should have one human-readable meaning or that the proposed OAK approach already works.

A proposed objective can combine generated-reply error with selected state or prediction errors. Select its weights on a separate pilot and freeze them before scored runs. Report any extra supervision. A diagnostic head that can read a concept does not prove that the reply generator uses it. Intervention tests and end-to-end held-out performance are needed. Additional losses can conflict, so preserve the original reply objective and regression cases.

## Global context as changing numerical state

The existing design remembers what was said. The proposed extension also maintains an estimate of what those observations mean now. For example, a message log records that a box moved; an effective current-state representation would reflect the new locations of the box and its contents. The learner, not a hidden simulator call, must perform that update.

Use a context matrix G with rows representing learned memory slots and columns representing numerical features. Slots may bind to entities, events, or the current question. These interpretations are hypotheses until measured. Keep explicit source, time, validity, and episode boundaries where the application requires them rather than assuming they emerge in unnamed coordinates.

A candidate numerical arrangement is:

```text
observation words -> learned encoder -> gated context update
                                           |
                                    shared context G
                                           |
question words -> learned query -> attention read -> numerical reply decoder
```

Schematic functions, not an implemented API:

```text
z_t = encode_theta(observation_t)
G_t = update_theta(G_previous, z_t)
q_t = encode_question_theta(question_t)
r_t = attention(q_t, G_t)
reply_tokens = decode_theta(q_t, r_t, dialogue_state)
```

A gate chooses which slots to revise and which to retain. Gate parameters are learned weights; its outputs change with the input. No agent selects writes during scored inference. Questions may update dialogue focus without asserting new world facts. The model's generated claims must not silently become independent evidence for those same claims. Separate observed, inferred, hypothetical, and self-generated information in the declared policy and tests.

Use global to mean accessible across the network within one episode, not a shared mutable store across unrelated users or conversations. Reset episode memory and test isolation. A counterfactual evaluation uses a separate state branch and cannot overwrite the observed-world state. Updating current context must not imply that historical information is magically preserved: past questions need retained events, snapshots, or a separately tested historical representation.

The context is part of the neural system, not above it. Attention is one way to read it; a learned update mechanism writes it. The shared-workspace literature provides a close precedent for modules communicating through bounded shared memory [Q04]. Recurrent Entity Networks explicitly distinguish persistent learned transformations from changing entity memory [Q05]. Relational recurrent networks study attention among memory slots [Q06]. These precedents support trying the mechanism, not a claim of novelty or guaranteed generalisation.

For OAK, learned projections and write-rule parameters belong in constants for one model revision. Current context and dialogue values belong in state owned by an explicit document or in explicitly declared numerical runtime state. A proposed context.oak.md would expose typed update/read processes rather than allowing unrelated nodes to mutate its state implicitly. It is a proposed file, not an artifact delivered in this change. Use existing OAK boundaries and supported numerical operations; do not invent a context part.

## Scaling and limits

Use the same update and query operations for all compatible slots and all steps. This separates growth in represented entities or history from growth in learned parameters. Slot Attention provides evidence for exchangeable object representations on its studied perceptual tasks [Q07]; persistence, identity through time, and conversational grounding still require their own mechanisms and tests.

A bounded shared workspace should hold the active information needed for coordination, not every observation forever. Older evidence can remain in a declared event memory with numerical retrieval. Its storage, access policy, retrieval errors, and inference cost count as part of the system. Do not relabel a database or the training agent's history as a tiny learned model.

At fixed numerical precision, finite memory cannot preserve arbitrary unbounded histories exactly. Learned compression must lose some distinctions. Report capacity, overflow, forgetting, and conflicting-write behaviour. Sharing weights does not make memory, attention, computation, or language acquisition free.

Long-term neural memory combined with attention is also studied in Titans [Q08]. That work includes test-time learning and is not identical to the proposed frozen-parameter, changing-activation experiment. Do not introduce test-time parameter adaptation silently; the first comparison keeps model weights frozen while episode state changes.

## Proposed comparisons and falsifiers

After a verified message-memory baseline exists, compare the same dialogue task with and without a learned context workspace, and with and without the selected auxiliary-question objectives. Keep the observation history available to all arms for the first comparison. Do not manufacture a memory benefit by giving one model the relevant fact while withholding it from another. Compare matched parameter and training budgets where feasible and report activation-memory and compute differences separately.

All arms use actual token inputs and generate output tokens. The simulator supplies training labels and independent scoring only. Hand-supplied entity slots or state labels constitute extra supervision and must have separately labelled controls. No sentence renderer, teacher answer, privileged state, or external language service may complete an evaluated reply.

The primary measurement is accurate, connected replies on held-out histories and combinations with frozen weights, not fluency alone. Include temporal questions, unseen entity assignments, longer histories, more objects within capacity, distracting events, and held-out wording. Keep unknown vocabulary and out-of-capacity failures separate from known-word compositional transfer. Do not label another random seed alone as a new kind of generalisation.

Test whether relevant state interventions change the answer as predicted, whether irrelevant writes leave it unchanged, whether memory reset prevents cross-episode leakage, and whether contradictory observations produce supported uncertainty. A readable probe is insufficient if the decoder ignores it. Memory scrambling and write-gate ablations are diagnostic interventions, not substitutes for retrained comparison arms.

A full comparison should separately count what the agent actually changed: parameter edits, teaching examples, objective selection, or architecture. Record each proposal before evaluation. A curriculum improvement does not demonstrate hand-placement alone. The programme can demonstrate participation without beating a non-agent control, while controls still explain what produced a measured capability.

## Finalisation

Freeze selected model weights, update/read equations, tokenizer, state dimensions, reset and overflow rules, and token-decoding policy. Initialise ordinary episode state explicitly rather than exporting a lucky populated test context. Include any learned initial memory in parameter accounting. Export the complete numerical system and check multi-turn state trajectories and replies after clean reload, without the training agent or evaluator.

Export correctness and language capability remain separate gates. Changing G during a conversation is normal inference under fixed learned rules. Further agent-driven changes to those rules create a new model revision. No new finalisation or conversational success is reported here.

## Primary research checked

Checked on 6 September 2026. Abstracts and the noted model sections support these design connections; no claim of an exhaustive literature review is made.

Q01. Vaswani et al., Attention Is All You Need (2017), model section 3.2: https://arxiv.org/html/1706.03762v7. Learned projections and input-dependent query/key/value vectors are distinct.

Q02. Kumar et al., Ask Me Anything: Dynamic Memory Networks for Natural Language Processing (2015 preprint), abstract: https://arxiv.org/abs/1506.07285. Questions condition iterative memory processing and answer generation.

Q03. Veeriah et al., Discovery of Useful Questions as Auxiliary Tasks (2019), abstract and method: https://arxiv.org/html/1909.04607v1. Predictive auxiliary questions can shape useful representations in the studied reinforcement-learning setting, not arbitrary English concepts per matrix.

Q04. Goyal et al., Coordination Among Neural Modules Through a Shared Global Workspace (2021 preprint), abstract: https://arxiv.org/abs/2103.01197. A bounded workspace coordinates specialist modules; this is not evidence of consciousness or universal memory.

Q05. Henaff et al., Tracking the World State with Recurrent Entity Networks (2017 revision), sections 1 to 3: https://arxiv.org/html/1612.03969v3. Shared learned updates operate on changing memory slots; explicitly tying slots to entities is a supplied prior.

Q06. Santoro et al., Relational recurrent neural networks (2018), abstract: https://arxiv.org/abs/1806.01822. Attention supports interactions among recurrent memories in the reported tasks.

Q07. Locatello et al., Object-Centric Learning with Slot Attention (2020), sections 1 and 2: https://arxiv.org/html/2006.15055v2. Shared exchangeable slots support object representations; temporal identity and open-ended language are not established by that result.

Q08. Behrouz et al., Titans: Learning to Memorize at Test Time (2025 paper identifier), abstract and memory architecture: https://arxiv.org/html/2501.00663v1. Attention and long-term neural memory can be combined; test-time parameter learning differs from the first proposed context comparison.
