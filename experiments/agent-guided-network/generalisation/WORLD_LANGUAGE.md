# World and language generalisation

Recorded: 6 September 2026, Brisbane time.
Status: Proposed research direction; no world-language implementation, training run, or conversation result is claimed.
Intent: [EXPERIMENT.md](../EXPERIMENT.md).
Evidence index: [LEARNINGS.md](../LEARNINGS.md).
Implementation task history: [existing SMEAC record](../../../docs/plans/0011-agent-guided-network/plan.md).

## Question and boundaries

Can an agent deliberately shape a numerical network that reuses what it learns across unfamiliar situations, then talks about those situations without that agent? Participation is the mechanism; generalisation is the next capability; natural-language conversation is the ultimate aim. Beating an optimiser is not the definition of success. Controls still help identify whether measured behaviour comes from the network, the task generator, supplied rules, language examples, or an external model.

This is not a claim that English follows automatically from learning physics. Without a link between words and experience, renaming all objects leaves the same physical task unchanged: physics alone does not select English names or sentence conventions. Supply language examples and interactions. Count that teaching honestly. TinyStories demonstrates small-model language generation with supplied synthetic text, while grounded word-learning work connects words to objects and actions [G02, G05]. Neither establishes our proposed OAK route to conversation.

We should not wait for a general theory of matter or time before testing useful shared structure. An event changes relationships among persistent entities. That proposed common representation can support temporal ordering, containment, movement, transfer, and questions about evidence. Whether learned representations actually transfer is an empirical question. World understanding is a chosen grounding strategy, not a proven prerequisite or sufficient condition for language.

## One world, shared concepts

Start with a deterministic, deliberately limited world of named objects, containers, locations, and discrete events. It has explicit toy rules, not real-world physics. The first scope covers object identity, containment, movement, removal, and event order. Add counted transfers and simple interventions only after the corresponding rules and tests exist. Motion dynamics, heat, chemistry, and continuous physical quantities are later domains, not implied by this model.

| Concept | Example lesson | Proposed transfer test |
| --- | --- | --- |
| Identity | An object remains the same object when it moves or becomes hidden. | Previously unused names in known roles; increased object counts. |
| Relations and change | Moving a container changes the location of its contents under the declared rule. | Familiar moves combined with unseen contents and nested containers. |
| Time | Earlier and current states differ; event order determines the current answer. | Longer histories and reordered events with different correct answers. |
| Quantity | A closed-world transfer moves counted units without creating or destroying them. | New amounts and transfer chains within declared capacity. |
| Cause and alternatives | Removing a specified event can change a later outcome under the simulator's rules. | New interventions, with all other event assumptions stated. |
| Evidence and uncertainty | The last observation may not determine the current state. | Omitted events, ambiguous references, clarification, and abstention. |

Avoid a separate memoriser for each task. Use one shared numerical state-update model and reuse it across question types. Module names are responsibilities, not proof of interpretable internal concepts. Quantities obey conservation only where the simulator explicitly defines a closed system. Temporal ordering is not by itself causal understanding; intervention tests must change causes rather than merely reorder descriptions.

## Numerical architecture to investigate

```text
TRAINING
One assistant: examines failures, selects lessons, proposes parameter changes
                                  |
                      numerical fitting and evaluation
                                  |
                      versioned OAK-owned parameters

DEPLOYED, WITH NO ASSISTANT
observations + user words -> numerical encoder -> shared world/dialogue state
                                                   |
                               numerical prediction + word generation
                                                   |
                                               reply words
```

The simulator generates experiences and independent reference answers. It is not queried by the deployed network to answer questions. The first control may accept structured event inputs to isolate world-state learning. That control is not evidence that the network understood raw natural language.

A language-capable arm must read actual word or byte tokens through a declared numerical encoder and generate its own output tokens. A small sequence encoder/decoder with attention is a candidate, not an already implemented component. The existing retrieval attention profile cannot simply be relabelled a conversational model: input encoding, event updates, temporal representation, generation, and turn state still need implementation.

OAK constants own each revision's parameters. OAK schemas express input/output and state shapes; processes sequence supported numerical work; interfaces carry events and utterances. Episode state contains remembered observations, referents, and conversation context. It is distinct from training history and from learned weights. Across scored turns, episode state may change but weights stay frozen. Across episodes, state resets. Use explicit bounded execution or state updates rather than illegal cyclic process calls. All required operators, tokenizer definitions, state initialisation, memory limits, and token decoding belong in the export.

No answer table, hand-written sentence renderer, external language model, hidden simulator state, or teacher correction may complete a scored reply in the language-generation arm. A deterministic token-to-text conversion is allowed; choosing the meaning and content must be the network's computation. Training sentences may be generated from templates, but template reuse and held-out language tests must be disclosed. A scripted language control can be useful, provided it is labelled as scripted rather than emerging language.

## Teaching and generalisation

Teach short world histories and their language descriptions together, rather than finish isolated numerical puzzles and bolt on a chatbot later. The same event history should support prediction, present and past questions, and brief explanations. Later dialogues should add pronouns, corrections, uncertainty, and requests for missing information. Do not require flawless physics before beginning the language component.

The executing assistant retains its sequential node responsibilities. It may place or tie weights directly, choose targeted numerical fitting, or propose teaching examples. Log these as distinct interventions. A gain from additional examples is not evidence for direct weight placement alone. A manually compiled relation rule is an explicit supplied prior, not a discovered physical law. Register lesson data and proposed updates before evaluation, retain failures, and disclose one shared-context proposer rather than claiming independent agents.

Generalisation must be demonstrated without new parameter edits on each test example. New random seeds alone are insufficient. Reserve complete combinations and structures from training, split by underlying world histories before rendering text, then hold out language forms independently. Include familiar words in unfamiliar roles, fresh object assignments, longer event chains, deeper containment, distracting facts, and paraphrases from separately authored forms. Test within architecture capacity and report out-of-capacity failures separately. Never equate unlimited extrapolation with success on a finite split.

Training on stories up to three moves and testing on six is one possible length contrast, not yet a frozen setting. Number of entities, dialogue turns, vocabulary, seeds, training examples, numerical steps, agent interventions, and resource budgets must be fixed in an OAK study before scored work. Maintain regression tasks so adding one skill does not silently erase earlier skills.

## Illustrative target dialogue, not an observed result

The declared world is fully observed; no unreported event occurs between the statements below.

```text
User: The ball is inside the box. The box is in the kitchen.
User: Move the box to the garden.
User: Where is the ball?
Network: In the garden.
User: Where was it before?
Network: In the kitchen.
User: Why did its location change?
Network: It was inside the box when the box moved.
User: Take the ball out. Move the box to the shed. Where is the ball now?
Network: In the garden.
```

The last question is important: the network must update its relation, not always answer with the box's location. Repeat with different entities and event combinations that were never paired during training. In partially observed variants, a missing observation must sometimes make the answer unknown; the network must not see the simulator's hidden answer. A follow-up such as "Which box?" is evaluated by whether it resolves a genuinely ambiguous reference, not by whether it sounds conversational.

## Evidence and falsification

| Question | Required evidence | Insufficient evidence |
| --- | --- | --- |
| Did the agent participate? | Pre-evaluation proposals, changed parameters, accepted/rejected records, and useful post-update behaviour. | A plausible rationale or automated replay called a new agent decision. |
| Does the network transfer? | Frozen-weight success on excluded compositions, longer histories, and name/role changes with per-split metrics. | New examples drawn from the same easy distribution alone. |
| Does state support answers? | Counterfactual event edits change answers appropriately; removing needed memory hurts the relevant tasks. | Fluent answers that ignore changed facts. |
| Does language come from the network? | Exported token generation on novel grounded dialogues, without response templates or a serving teacher. | A classifier's answer inserted into a hand-written sentence. |
| Is conversation coherent? | Consistency across follow-ups, reference tracking, corrections, and justified uncertainty. | Isolated question-answer accuracy or grammatical text alone. |
| Is it broadly conversational? | Transfer beyond the toy world to independently evaluated topics and interactions. | Passing only a small generated vocabulary and fixed question family. |

Measure answer truth against the episode, event-prediction accuracy, multi-turn consistency, invalid or unsupported claims, uncertainty behaviour, and performance on each held-out split. Score equivalent answers for meaning, not arbitrary wording alone; ReCOGS warns that incidental output-format choices can distort generalisation measurement [G04]. If generated language cannot be scored reliably, use blinded human review alongside executable structured checks. Do not let the teaching agent be the sole judge of its own results. Any limited response grammar used for scoring must be disclosed.

Include an untrained/initial network, a numerical-only trained network using the same examples, and a labelled rule-based world solver. A language-only control and a no-world-memory intervention test whether groundable information is actually used. These controls diagnose mechanisms and shortcuts; a non-agent tie does not invalidate the participation aim. Claims of added benefit still require matched information and resource accounting. Keep all test feedback out of the teaching loop.

Complete export verification must cover the language encoder, numerical episode memory, world update, token generator, and decoder. Test raw inputs through the complete artifact in a clean process. Verify repeatability, state reset, numerical agreement, and absence of hidden external calls. Compactness is measured for that complete artifact, including language representations and runtime; it must not be achieved by omitting a needed component.

## Research connections and limits

Primary-source abstracts and publication records checked on 6 September 2026. These sources motivate the design; this update does not replicate their experiments.

G01. Weston and colleagues, [Towards AI-Complete Question Answering: A Set of Prerequisite Toy Tasks](https://arxiv.org/abs/1502.05698), 2015. Synthetic questions separate skills such as chaining facts, deduction, and induction. Useful as diagnostic inspiration, not a claim that passing toy tasks supplies complete dialogue ability.

G02. Hill and colleagues, [Grounded Language Learning Fast and Slow](https://arxiv.org/abs/2009.01719), 2020. A simulated agent associates new words with objects and uses them with previously learned actions and lexical knowledge. Supports studying shared world/language representations and explicit episodic memory; does not establish free-form conversation or this OAK training method.

G03. Kim and Linzen, [COGS](https://aclanthology.org/2020.emnlp-main.731/), 2020. Evaluation withholds combinations of known words and structures rather than merely new random sentences. This motivates structural splits; its semantic-parsing task is not a dialogue benchmark.

G04. Wu, Manning, and Potts, [ReCOGS](https://arxiv.org/abs/2303.13716), 2023. Semantically irrelevant logical-form details can change apparent generalisation results. This motivates separating meaning from presentation in evaluation, not claiming perfect automated grading of conversation.

G05. Eldan and Li, [TinyStories](https://arxiv.org/abs/2305.07759), 2023. The authors report coherent story generation by small models trained on supplied synthetic stories. This supports investigating restricted language curricula, not expecting English from numerical tasks alone or treating story generation as multi-turn dialogue.

G06. Yi and colleagues, [CLEVRER](https://arxiv.org/abs/1910.01442), 2019 preprint. Temporal and causal video questions distinguish descriptions, explanations, predictions, and counterfactuals. Useful for separating kinds of reasoning; its simulated collisions do not establish fundamental laws or our proposed conversational transfer.

## Current outcome

The direction and success criteria are specified. No new world-state learner, language generator, training run, or measured generalisation gain is delivered by this document. The immediate proposed milestone is a small, auditable network that tracks a changing world and generates grounded follow-up answers on withheld combinations. Open-domain natural-language conversation remains the ultimate goal, not a promised automatic consequence of that milestone.
