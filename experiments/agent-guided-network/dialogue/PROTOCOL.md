# Generated dialogue and matched representations

Recorded: 7 September 2026, Brisbane time.
Baseline: `58c37dec3f71355eba18ee933e522e9d18f9acdd`.
Status: Protocol before implementation pilot and scored training. No result is implied.

## Questions

Can a small numerical model produce multiword, multi-turn replies about observed changes, including pronoun follow-ups, corrections and missing information, after its teaching agent is removed? Does OAK add measurable value over an equally safeguarded Python representation of the same model?

The first question is restricted grounded conversation, not open-domain conversation, a general world model or spontaneous English without teaching. The second separates representation from architecture and training. Identical weights and operations should not gain accuracy merely from an OAK wrapper. Comparative agent productivity requires independent proposer trials; one shared conversation cannot establish it.

## Architecture

Use a learned recurrent text encoder, numerical attention and an autoregressive recurrent decoder with a learned vocabulary output. Generate reply tokens, not one of several prepared sentences. OAK documents own encoder, attention, decoder, readout, episodic conversation memory, contracts and composition. Reuse the same weights at each decoding position. A bounded generation process is lowered from actual OAK calls; no unresolved language-model action is allowed. Ordinary Python composes the same operations directly. Both retain user words and their own generated replies, never simulator state, target replies or the teaching agent's context.

Freeze parameters during dialogue. Reset memory between episodes. Save and restore model-bound state. The simulator creates teaching and evaluation examples only. Language templates are permitted for training data, not serving replies. Vocabulary and finite context/reply limits are disclosed. Unsupported inputs and capacity errors must not silently consult another model.

## Study and selection

Implement and test with pilot seed 0 first. Record final numerical dimensions, corpus identities, code hashes, seeds, batch sizes, fitting budget, sampling, checkpoint selection and update acceptance in study.json before scored training. Use two scored numerical seeds and one shared-context assistant. Reserve complete latent episodes before language rendering. Include ordinary held-out episodes, new combinations, longer histories, new wording, missing information and connected pronoun/update turns. Final cases are generated only after all selections close.

One live development-informed teaching or scoped parameter-update proposal is allowed on the first seed. Replay that method on the second seed without calling it another agent trial. Record the proposal before scoring it. Retain rejected candidates. Compare baseline, ordinary continuation and the proposed update. Do not reopen final tests for model selection. Teach from generated natural-language examples; disclose that this is not direct manual placement of every weight.

## Matched OAK versus Python comparison

For every selected model, use identical tensors, tokenizer, inputs, autoregressive decoding, episode state and mathematical operations. Independently fit the same proposed update starting from OAK-loaded and Python-loaded parameters with the same batches and random seed. Check resulting weights and predictions, not just labels on the runs.

Compare actual OAK execution, graph-lowered inference and direct Python execution, including state restoration. Give the Python control equivalent shape, ownership, stale-revision and model-identity protections. Test deliberately invalid edits in both. Attribute OAK-native parsing/resolution checks separately from shared host-added numerical and update checks. Measure bytes and declared-fixture latency; do not claim agent effort, reliability or cost advantages from a scripted fault suite. Record one physical proposer and unavailable conversation costs.

## Evidence and delivery

Run preflight tests, retain train/development/final separation, audit saved predictions, verify isolated exports and show actual successful and failed conversations. Publish source, reproducible numerical records, selected models, comparisons and the evidence-linked LEARNINGS.md update on the existing branch. Prior studies remain unchanged. A failed capability test is publishable research, not an approved conversational deployment. No merge into main is authorised.

## Primary references

PyTorch, sequence-to-sequence attention tutorial: https://docs.pytorch.org/tutorials/intermediate/seq2seq_translation_tutorial.html . Supports the encoder/decoder implementation pattern, not this model's performance.

Eldan and Li, TinyStories: https://arxiv.org/abs/2305.07759 . Small-model language generation with supplied teaching text is a precedent, not evidence of dialogue competence or an OAK advantage.
