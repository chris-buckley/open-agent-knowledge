# Wording versus meaning

Recorded: 6 September 2026, Brisbane time.
Baseline: a96de31abb234ee41c0843bab079b41bfdeae973.
Status: New implementation and experiment, not recovery of the earlier prototype.

## Evidence correction

The branch and the checksum-verified source artifact at the baseline contain the context study settings, not its implementation or final measurements. The current runtime contains the supplied archives but none of the previously claimed context run directories. The earlier claim that implementation commit 8c756a2461e77b3a4f6f9d968c9e7af1d8737286 was published is unsupported. Previously quoted context/world-language scores, proposals and parity failures are unverified and must not be treated as empirical findings. Do not fabricate missing files from those statements. Preserve the three earlier published studies unchanged. This study starts a new evidence trail.

## Question

Can an agent help teach one small numerical network to preserve answers across different descriptions of the same events, while changing answers when event direction or order changes? Participation is the mechanism. A comparative advantage is not a prerequisite. Reliable open conversation is not the claimed scope.

## Fixed architecture and task boundary

Use a shared learned word embedding and gated recurrent sentence encoder, attention over an ordered event log, and a numerical answer head. The answer is one location token from six choices, not unrestricted language generation. The network receives raw event sentences and a question, never hidden event records, source/destination labels or a simulator answer. There is no serving parser of event meaning or answer template. The OAK source owns all parameters. Episode state owns only supplied event text; learned parameters stay fixed during testing. No pretrained model or external model API is used.

Use six named objects and six rooms. An event reports a move from one room to another. Questions ask the current room or the room before the latest move of that object. Training histories contain two to four moves, including distractions and repeated entities. The same learned operators apply to all entities. The numerical profile rejects unknown tokens and histories beyond its stated capacity; it does not silently truncate them.

## Teaching comparisons

Begin with ordinary single-wording training. Compare equal-step continued single-wording teaching, multiple wordings with ordinary answer supervision, and multiple wordings with an additional agreement objective for matching descriptions. Every paired view has the same underlying history and answer. Paired opposite-direction examples must retain distinct labels rather than being forced to agree. Keep example presentations and numerical steps explicit. Additional teaching content, numerical fitting and direct weight edits are separate interventions.

After inspecting development evidence on the first seed, the running assistant may record at most two bounded teaching proposals before evaluating them. Permitted changes: reduce or increase the agreement weight, or mix longer histories while preserving ordinary examples. Fix the exact numerical settings, training budgets and source hashes in study.oak.md and freeze.json after a seed-zero implementation pilot and before scored training. The assistant must not edit inference rules after scored feedback. Later seeds replay the recorded methods; they are not independent agent sessions.

## Tests

Split by underlying histories before rendering wording variants. Do not place another rendering of a training history into development or final testing. Reserve selected object-room combinations from training. Use fresh final histories in familiar wording, new object-room combinations, longer histories, and an entirely held-out sentence arrangement made of familiar words. Evaluate matched pairs: same history in two wordings, identical-word-multiset moves with swapped source/destination, and changed event order. Pair success requires both answers correct; mere agreement or merely changing an answer is insufficient. Include a bag-of-words impossibility control for identical-word direction pairs and a labelled exact rule reference outside deployment.

Choose checkpoints using development cases only. An agent candidate must improve the preregistered development score and stay inside a fixed ordinary-task regression bound. Close all selections and record parameter identities before generating final sets. Do not reopen the final test to improve those candidates. Separate training seeds, data cases and physical proposer counts. Use case-paired uncertainty only with its correct scope.

## Finalisation and evidence

Freeze numerical weights, token vocabulary, operators, state reset and decoding. Check the exported numerical runtime against the training implementation and actual OAK execution. Save and restore state between observations and questions; uninterrupted and restored execution must agree. Test in a clean process without OAK, the teacher, simulator, credentials or network calls. Keep all source hashes, observed checks, selected checkpoints, rejected proposals and final predictions. A failed capability target remains a valid research outcome, but a failed equivalence test prevents a deployment-equivalence claim.

The learning index records only observed results. An implementation or export pass is not evidence of broad language understanding. No merge to main is authorised.

## Research motivation

Kim and Linzen (2020), COGS, motivates systematic gaps rather than random splits: https://aclanthology.org/2020.emnlp-main.731/ . This is not a COGS reproduction or score.
Sukhbaatar et al. (2015), End-To-End Memory Networks, motivates learned attention over observations: https://arxiv.org/abs/1503.08895 . This small profile is not a replication.
PyTorch documentation defines the GRU equations and checkpoint behaviour: https://docs.pytorch.org/docs/stable/generated/torch.nn.GRU.html and https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html . Record installed versions rather than assuming the current website matches the environment.
