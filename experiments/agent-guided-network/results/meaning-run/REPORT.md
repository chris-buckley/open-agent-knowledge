# Wording versus meaning: verified resumption

Recorded: 6 September 2026.
Verdict: Agent-selected teaching and agent-free execution demonstrated. Reliable transfer to unseen wording failed. This is not conversation or a general world model.
Scientific source: `7e2ef857f16978492d00a4790cb960e323b154ff`. [Protocol](../../meaning/PROTOCOL.md), [live evidence](live-session.json), [raw archive and summaries](reproduced/summary.json), [publication provenance](publication.json).

## Evidence boundary

The source archive was checksum-verified against the published GitHub Actions artifact. The earlier temporary run directories were absent. This is a new execution of the existing committed protocol, not recovery of the missing run or reproduction of its previously quoted percentages. Prior unverified aggregate scores were visible in the conversation. These results are therefore not an independent blinded trial. No final measurements from the missing context or world-language runs are reinstated.

All nine original scientific files remain byte-identical to the source commit. The added reproduction and publication scripts audit results; they do not change training, inference, datasets, acceptance rules or parameters. Selection closed before this execution generated final cases. No parameter edits followed its final scores. A 45-second local command limit interrupted closure; partial files were preserved, and the unchanged closure routine was restarted before final cases existed. Local recovery evidence is in live-session.json.

## What ran

One 6,431-coefficient network encodes event sentences and questions with shared learned recurrent weights, attends to the ordered observation log, and selects one of six location words. Its vocabulary has 22 tokens and its capacity is 32 events. The OAK node owns inline quantised parameter records and explicit event-history state. Parameter records use signed 16-bit-range integers plus scales and float64 inference; JSON storage is not a packed 16-bit deployment.

The task asks the current location or the source location in the object's most recent reported move. The source room is explicitly present in that sentence, so a correct past answer is not proof of a learned temporal world model. Questions name their subjects. This profile does not resolve pronouns, generate multiword replies, learn matter or physics, or sustain open conversation. It contains no serving simulator, answer template or external language-model call.

The registered seeds are 401, 409 and 419. Each receives 1,024 training histories, 128 short development histories, 128 medium histories and 512 final histories per regime. Training histories have two to four moves; medium histories have five to six; final long histories have twelve to eighteen. Splits are by underlying history before wording is rendered. One held-out arrangement is evaluated using familiar words. Testing that arrangement is not testing new vocabulary.

## Actual agent participation

One live proposal on seed 401 mixed 1,024 longer histories with the original examples, retaining the agreement strength of 0.3. The proposal and its rationale preceded evaluation. Medium-history development accuracy rose from 92.97% to 99.22%; ordinary accuracy rose from 97.66% to 99.22%. The frozen rule accepted the candidate, and no second proposal was made. The choice was replayed numerically on seeds 409 and 419 and accepted there too. Those are not new agent trials.

This is an agent-selected lesson implemented through 400 numerical optimisation steps, not direct hand-placement of individual weights. Each fit presents two views per batch, 48 histories per batch. Controls separate ordinary repetition, varied wording, an agreement objective, and ordinary-history continuation with the same added step count. Step count is matched, not information or total cost: the longer-lesson arm receives additional histories. Conversation tokens and monetary cost are unavailable.

The durable reproduced archive is a numerical re-execution of the recorded choice and makes zero fresh agent decisions. Its metrics are checked against the live execution. The live proposal, observation, decision, selected identity and local environment are retained separately in live-session.json. Three seeds and one shared-context proposer are not a population of independent agents.

## Final accuracy

Descriptive means over three numerical seeds; higher is better. Same histories recur across models and wording views, so those predictions are not independent samples.

| Treatment | Familiar wording | New object-room combinations | Longer histories | Unseen wording |
| --- | ---: | ---: | ---: | ---: |
| Initial ordinary teaching | 89.71% | 59.05% | 73.57% | 12.30% |
| Repeat ordinary teaching | 97.14% | 72.72% | 77.28% | 6.71% |
| Varied wording | 95.57% | 66.21% | 75.39% | 7.75% |
| Varied wording plus agreement | 95.51% | 58.98% | 75.46% | 10.74% |
| Agent-selected longer lessons | 99.35% | 71.74% | 83.59% | 8.07% |
| Matched-step ordinary continuation | 97.53% | 67.06% | 76.04% | 8.85% |

The combination set changes the final queried destination to an object-room pairing absent from training. Current-location questions therefore require the withheld destination; before-location questions still ask a previously allowed source. They must not be treated as equivalent tests. The summary retains exact correct/count breakdowns for both question types by seed.

## Paired meaning tests

Both answers must be correct. Mere agreement, or simply changing the answer, does not pass.

| Treatment | Same event, changed wording | Reversed move direction | Reordered events |
| --- | ---: | ---: | ---: |
| Initial ordinary teaching | 10.87% | 80.60% | 58.85% |
| Repeat ordinary teaching | 6.38% | 91.41% | 85.29% |
| Varied wording | 7.42% | 89.45% | 80.73% |
| Varied wording plus agreement | 10.22% | 82.68% | 74.74% |
| Agent-selected longer lessons | 8.01% | 87.76% | 81.51% |
| Matched-step ordinary continuation | 8.79% | 87.11% | 82.81% |

Direction pairs have identical word multisets but different correct answers. A deterministic bag-of-words answer function cannot answer both correctly. That is an analytical control, not a trained bag-of-words benchmark. Order pairs contain the same events in different orders. The selected network handles many such contrasts in familiar wording, but fails the held-out arrangement of the same meaning.

## Error analysis and interpretation

On unseen wording, 1340 of 1536 selected-network answers (87.24%) give the other endpoint of the queried move: source instead of destination, or destination instead of source. This post-selection diagnostic identifies a systematic role-confusion pattern on these cases, not a universal causal explanation of its hidden representation. No training followed this analysis.

The longer-history lesson improves long-history performance relative to the matched-step continuation, but does not solve wording transfer. The repeat control is stronger on some paired direction/order tests. Neither more varied wording nor the agreement objective is an across-the-board improvement here. Participation has been demonstrated; robust reusable meaning has not.

The next research question is how to teach stable source/destination roles across sentence positions. Any new lesson or architecture must use a newly declared study with fresh held-out forms. The current held-out wording must not be silently reopened as evidence of untouched generalisation.

## Verification and finalisation

All saved labels, predictions, losses, paired metrics and aggregate scores were independently recomputed with the NumPy inference implementation. Training/development/final history separation and selected-model identities were checked. All original source hashes match the freeze. Eighteen meaning preflight checks and the 59 prior-study checks pass, alongside the two complete branch verification entry points and generation freshness.

The twelve selected-model export checks cover 6,144 predictions in clean processes with model-bound state restoration after observations and questions. They exclude OAK, PyTorch, simulator imports, credentials and network use. Actual OAK execution with serialised state is checked on 96 samples. Maximum observed PyTorch/NumPy probability difference is 9.16e-15; all tested decisions agree. These are sampled checks, not universal proofs.

The complete raw archive contains candidate and selected parameters, observations, proposals, decisions, selection closure, cases, predictions, canonical OAK nodes and standalone exports. Every archived member is SHA-256 checked against the manifest. The selected exports require Python and NumPy, not the teaching agent. Successful export does not make the model conversationally ready.

Local pydantic-settings 2.14.1 is below the repository's declared minimum 2.15; that environment discrepancy is retained. The evidence workflow installs declared repository dependencies and pins the study's numerical versions. Its exact environment is recorded in the reproduced freeze. Branch checks and PR integration are distinct: the draft PR's pre-existing conflicts with newer main are not resolved by this experiment, and no merge into main is authorised.

## Reproduce

Install repository dependencies and meaning/requirements.txt, then run from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/meaning/run.py test
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/meaning/reproduce.py replay /tmp/oak-meaning-replay
```

Replay starts a new output directory, preserves the committed settings, performs no new agent reasoning, and fails on inconsistent evidence or export behaviour. The raw archive is `reproduced/records.tar.xz`; its manifest and archive hash sit beside it.
