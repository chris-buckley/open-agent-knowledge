# Shared memory, language, and finalisation

Status: Implementation and separate seed-zero pilot in progress. No scored outcome yet.
Baseline: `3275d25f98a9ed34f8e12ad87504f489c6476000`.

## Scaling decision

Use shared numerical operations across utterances, entities and attention reads. Do not add an OAK agent for each noun or rule. Model parameters and episode memory have different lifetimes. More observations may consume more memory and computation without requiring new learned parameters. The first implementation is an end-to-end learned memory question-answering network, not a manually compiled location solver.

This is a step toward the design in WORLD_LANGUAGE.md, not a complete implementation of all its future capabilities. It learns only from supplied short text/answer examples. It does not learn physical laws, control a body, handle arbitrary topics, or implement conserved quantities, heat, continuous motion, causal explanations or clarification. The simulator's location and containment rules appear only in data generation and independent scoring.

The reusable model has a word/position encoder, three shared recurrent attention reads over episode memory, and an autoregressive recurrent word decoder. Every output word is selected numerically. There is no serving answer table, sentence template, simulator lookup, pretrained language model or agent. Training sentences and target replies are templated and use a closed 42-token vocabulary, including six control tokens. Memorising their grammar is not open-domain conversation.

The memory stores tokenised messages supplied to the network and its own generated replies. It is an explicit episodic observation log, not an established learned symbolic world state. Queries re-encode that log and attend to it. More efficient recurrent state compression or indexed retrieval is a later scaling experiment, not an implemented property. This profile has 64 message slots, 20 tokens per message, 24 numerical channels, three attention reads and at most ten generated tokens per reply. Overflow is an explicit error, never silent truncation. New vocabulary and new physical domains need further training and evaluation.

## Research basis and boundaries

S01. Battaglia et al., Relational inductive biases, deep learning, and graph networks, https://arxiv.org/abs/1806.01261. Structured shared operations motivate compositional reuse. This is design guidance, not evidence that this implementation generalises.

S02. Sukhbaatar et al., End-To-End Memory Networks, https://arxiv.org/abs/1503.08895. Repeated learned attention over memory motivates the numerical profile. Our small autoregressive decoder and task differ from that study.

S03. Henaff et al., Tracking the World State with Recurrent Entity Networks, https://arxiv.org/abs/1612.03969. Learned dynamic state is a possible next architectural comparison. The implemented episodic log is not an EntNet replication.

S04. Kim and Linzen, COGS, https://aclanthology.org/2020.emnlp-main.731/. Separate novel wording and structures from random new examples. Our tests are not COGS scores.

S05. Eldan and Li, TinyStories, https://arxiv.org/abs/2305.07759. Small models can learn restricted text from supplied teaching corpora. This does not show that language follows from physics alone or establish dialogue competence.

S06. PyTorch saving and loading documentation, https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html. A checkpoint preserves parameters; an executable model also needs its architecture and inference configuration. Our final export uses explicit NumPy operations rather than Python object deserialisation.

Sources checked on 6 September 2026. None establishes universal scaling, general intelligence or agent superiority. Broad scaling would require diverse grounded and linguistic experience, open-vocabulary representations, memory management, repeated computation, regression testing and measured resource growth. Hand-editing every scalar is not the proposed scaling mechanism: the teaching agent can target whole shared transformations, lessons and numerical fitting procedures.

## Finalising a model

A model is finalised for one declared evaluation, not declared permanently intelligent. Freeze code, vocabulary, data rules, candidate budget and acceptance rule first. Choose a checkpoint using development examples only. Close all proposal selection, encode its parameters into canonical OAK documents, and record their content hashes. Test the already frozen model on untouched histories. An unsuccessful test is retained as a limitation; it does not silently reopen the same test set for training.

The export includes all learned parameters, vocabulary, position representation, recurrent gates, attention operations, token selection, memory limits, state reset and deterministic token-to-text conversion. Matrices are stored as signed eight-bit values with one scale per tensor and dequantised to float32. Quantisation happens before candidate scoring. Export equivalence compares against this quantised OAK source, not an unquantised training checkpoint.

Finalisation checks verify parameter identity, vocabulary identity, canonical parse/resolve, actual OAK execution, independent numerical execution, fresh-process replies, state reset, and refusal of changed profiles. The artifact has no training-agent history. Its own episode state starts empty and changes only with its inputs and generated replies. It contains no optimiser state or external model credentials.

A separate readiness gate requires at least 85% exact answers on each development regime. Failing that gate still permits a labelled research artifact, not an approved conversational deployment. Final-test failures are not hidden by calling export success conversational success. Production use or a broadly capable model is outside this pilot.

## Frozen scored settings

Numerical seeds are 41, 53 and 67. Each starts from 2,000 ordinary training episodes and four blocks of 300 Adam steps with batch size 64 and learning rate 0.003. Each block restarts optimiser state. Development has 96 episodes each of ordinary, five-to-six-event and separately worded probe histories. Select the initial or block checkpoint with the greatest mean exact-answer score; ties retain the earlier checkpoint. Score signed-int8 parameters after float32 dequantisation, including self-generated reply history.

One live assistant may make at most three proposals on seed 41. The fixed menu is query-key sharpening, temporal lessons, longer-history lessons, or fitting encoder/memory while freezing decoder/output parameters. Fitting proposals use 300 steps. Teaching proposals mix the original corpus with 2,000 additional episodes from their declared regime. Each proposal must precede its evaluation and improve mean development exact answers by at least 0.005 without dropping any regime by more than 0.02. Retain rejected candidates. Seeds 53 and 67 numerically replay the same methods, with their own acceptance outcomes; those are not fresh agent sessions.

An ordinary-data continuation control receives the same additional fitting-step count and development checkpoint selection. This matches numerical step count, not data diversity or total agent cost. Conversation cost is unknown. After selection closes, generate 192 untouched episodes per seed for each of seven regimes: ordinary, excluded direct object/room assignments, twelve-to-eighteen events, deeper containment, six objects, independently held-out wording and absent queried objects. Each episode has current, before-last-event and pronoun follow-up questions. Complete answer, location-word and whole-dialogue scores remain separate. Memory removal is a post-selection intervention without retraining. The deterministic simulator is a labelled rule control and is absent from exports.

Scored source and dataset identities are recorded before training in freeze.json. Final data are generated only after SELECTION_CLOSED.json exists. Selection may not be reopened using those tests. This is procedural separation, not an adversarial security boundary against the implementing assistant. The scored-source hashes, actual observations, proposals, decisions and all final replies must be preserved, including failures.
