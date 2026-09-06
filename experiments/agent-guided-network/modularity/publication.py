"""Publish audited modular evidence without changing the frozen scientific sources."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil

from reproduce import ARMS, DESTINATION, REGIMES, package
from run import EXPERIMENT, SEEDS, read, write

NAMES = {'baseline': 'Unchanged model', 'ordinary': 'Full-network ordinary continuation',
         'varied': 'Full-network varied wording', 'agent': 'Selected encoder-only sequence'}


def build_report(summary: dict, evidence: dict) -> str:
    rows = ['| Model | Familiar | New combinations | Long histories | New wording A | New wording B |',
            '| --- | ---: | ---: | ---: | ---: | ---: |']
    for arm in ARMS:
        scores = ' | '.join(f"{summary['means'][arm][regime]['accuracy'] * 100:.2f}%" for regime in REGIMES)
        rows.append(f'| {NAMES[arm]} | {scores} |')
    engineer = evidence['engineering']
    timing = engineer['timing_seconds_median']
    return f'''# Executable OAK modules: measured ownership and bounded learning

Recorded: 6 September 2026.
Scientific source: `0a6f38dbea5b67f8f911ce21b834fbf0b8b061fe`.
Protocol: `c4d808d5bd89265bc87ac108b67da373268617a2`.
Verdict: Executable modular ownership, reuse and bounded revision demonstrated. Generalisation remains mixed. This is not conversation, parameter compression or proof of an exclusive OAK advantage.

## What is different

The earlier 6,431-coefficient network lived inside one OAK parameter envelope and one Python inference call. This study divides the same initial mathematics into six canonical OAK documents. The encoder owns 3,376 coefficients, attention 1,153, and readout 1,902. Observation memory owns only the supplied history. Shared schemas and root composition complete the graph. The encoder process and parameter owner are reused by both observations and questions.

Actual OAK CALL targets, bindings, named operations and state writes determine execution. The restricted export adapter lowers those resolved processes rather than silently calling the original monolithic network. A preflight test changes compatible wiring and observes changed numerical output. Another verifies that two consumers use one encoder owner. This is a closed numerical profile, not a general compiler for arbitrary OAK.

The responsibility questions explain the intended modules to the teaching agent. They are not interpreted by a serving agent, and they do not make individual latent channels semantically meaningful. The memory remains an observed-event log, not an established learned global world state.

## Where the guarantees come from

OAK itself provides canonical parsing and rendering, explicit dependency and schema identities, binding flow, CALL scope and local state transactions. The numerical adapter adds exact tensor checks, a supported-operation list, graph lowering and parameter validation. The experiment coordinator adds revision hashes, allowed-module checks and performance acceptance. Those host-added controls must not be represented as native OAK guarantees.

A proposal identifies its baseline and permitted parameter owners. Changed neighbouring documents, nonparameter edits, stale baselines and invalid tensors are rejected. The unchanged documents are compared by content identity. This establishes structural isolation, not unchanged downstream outputs: the same frozen readout can behave differently when an upstream encoder changes. Whole-network evaluation therefore remains necessary.

## Actual learning intervention

One live proposal on seed 503 requested varied-wording teaching of the encoder only, using 300 numerical optimisation steps. Ordinary development accuracy stayed at 99.22%; reordered wording improved from 4.69% to 89.06%, and medium reordered histories from 6.25% to 91.41%. The candidate passed the frozen acceptance rule. Only `encoder.oak.md` changed; all five other documents stayed byte-identical. The observation, proposal and decision were committed in [live-session.json](live-session.json) before final evaluation.

The same method was replayed numerically on seeds 509 and 521. It passed on 509 and failed on 521, whose incumbent was retained. This is one physical assistant and one fresh decision, followed by two numerical replays, not three independent agents. It is an agent-selected module update materialised by fitting, not direct hand-placement of individual weights. The later CI reproduction makes zero fresh agent decisions.

## Data, controls and limits

Each new data seed starts from its corresponding archived selected meaning model. Training contains 1,024 new histories, half short and half five-to-six events. Teaching uses four already exposed sentence arrangements; the old failed arrangement is no longer an untouched test. Development has 128 disjoint histories per ordinary and medium regime. Five final groups each contain 256 new histories. Data are split by history before wording, with recovered earlier-study histories excluded.

All fits use 300 Adam steps, rate 0.003, batch 48, two views and agreement weight 0.3. Full-network ordinary and varied-wording continuations use the same histories. Step count and example presentations are matched, not total compute or conversation cost. The agent arm trains 3,376 coefficients; the full arms train 6,431. Control checkpoint selection uses mean development performance, while agent acceptance also enforces a per-regime regression cap. This difference limits causal comparisons of the training policies.

Selections close before new final cases are generated. No changes follow final scores. This remains a six-choice, one-word location task with 22 vocabulary tokens and a 32-event limit. The source location appears explicitly in the event sentence; a correct previous-location answer does not establish a general temporal model. New-combination questions withhold destinations but not necessarily sources, so both question types are reported separately in the raw results.

## Final results

Descriptive three-seed means, including the retained baseline on rejected seed 521. They are not independent-agent population estimates.

{chr(10).join(rows)}

New wording A is `the object from the source moved to the destination`. New wording B is `from the source to the destination the object moved`. Both use familiar words in withheld arrangements. Performance is highly arrangement-dependent. The bounded update improves B but does not preserve performance across every other test. Full-network varied teaching and the unchanged model each remain stronger on some measures. The experiment demonstrates participation and module ownership, not robust language understanding or an exclusive agent advantage.

## Verification and finalisation

The 22 modular preflight checks and 77 earlier experiment checks passed locally. Every saved final probability, prediction, label and score was audited against the original numerical implementation. Maximum observed probability difference was {evidence['maximum_probability_difference']}. Selected models passed {evidence['isolated_restored_predictions']:,} isolated predictions with model-bound state restoration and {evidence['oak_samples']} actual OAK execution samples. The isolated process excludes OAK, PyTorch, training and simulator modules, credentials and network access. These are sampled checks, not universal equivalence proofs.

The supplementary audit checks frozen sources, archived baseline identity, data separation, proposal chronology, selected identities, allowed-module boundaries and recomputed development acceptance. The replay must match committed local prediction hashes and scores. Raw records include rejected candidates, selected graphs, final cases, predictions, source identities and inference-only exports. Every member of [records.tar.xz](reproduced/records.tar.xz) is verified against its [manifest](reproduced/manifest.json). Consult [publication.json](publication.json) for the exact CI source and run; its completed job status is separate from numerical success.

## Costs and OAK's usefulness

Coefficient count remains {engineer['coefficient_count']:,}. The measured canonical source grows from {engineer['monolithic_oak_bytes']:,} to {engineer['modular_oak_bytes']:,} bytes; complete exports grow from {engineer['monolithic_export_bytes']:,} to {engineer['modular_export_bytes']:,} bytes. There is no compression claim.

For one 16-case fixture, median loaded monolithic NumPy execution was {timing['monolithic_numpy'] * 1000:.3f} ms, lowered execution {timing['lowered_numpy'] * 1000:.3f} ms, and the OAK path including load, resolution, validation and lowering {timing['oak_with_load_resolution_and_validation'] * 1000:.3f} ms. Five timed repetitions follow a warm-up. Compilation alone was {timing['compile_once'] * 1000:.3f} ms. This is not a pure dispatch comparison or a general speed benchmark. No productivity, peak-memory, energy or alternative-authoring-system study was conducted.

OAK is useful here as the explicit source of module boundaries, reusable computation and auditable edits. The additional machinery has measurable cost. Equivalent safeguards could be built in Python or another format; this study does not establish that OAK is uniquely necessary. The important distinction is between a module that can be replaced safely as an artifact and a replacement that preserves behaviour. OAK helps make the former inspectable; testing still decides the latter.

## Reproduce

Install repository dependencies and the existing meaning experiment requirements, then run:

```sh
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/modularity/run.py test
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/modularity/reproduce.py replay /tmp/oak-modularity-replay
```

Use a new output directory. The source commit and declared settings remain unchanged. Local whole-repository checks exceeded the available command window; the publishing workflow runs both complete entry points and generation freshness. Do not confuse branch verification with integration into newer main. No merge into main is authorised.
'''


def update_index() -> None:
    path = EXPERIMENT / 'LEARNINGS.md'
    text = path.read_text()
    if '| L025 |' in text:
        return
    rows = [
        ('L025', 'The numerical network can be decomposed into executable OAK modules without changing its initial mathematics.', 'Six documents and 6,431 coefficients; sampled numerical agreement, not a universal compiler.', 'what-is-different'),
        ('L026', 'The same encoder owner serves observations and questions, and resolved OAK wiring determines computation.', 'Reuse and a deliberate wiring intervention pass; metadata labels alone do not establish understanding.', 'what-is-different'),
        ('L027', 'A local encoder update can change only its permitted document while preserving all neighbouring document bytes.', 'One live proposal accepted and one replay rejected; structural isolation is not behavioural independence.', 'actual-learning-intervention'),
        ('L028', 'Improvement on a new sentence arrangement does not imply transfer across all held-out structures.', 'The encoder-only sequence improves wording B but harms other cases; every control remains visible.', 'final-results'),
        ('L029', 'Modular OAK has measured storage and execution overhead in this fixture.', 'Coefficient count unchanged; no productivity advantage or unique superiority over Python established.', 'costs-and-oaks-usefulness'),
        ('L030', 'OAK-native contracts, numerical-host validation and coordinator edit policies provide distinct guarantees.', 'Tensor validation and revision acceptance are adapter responsibilities, not newly added OAK semantics.', 'where-the-guarantees-come-from'),
    ]
    addition = ''.join(f'| {identifier} | {finding} | {limit} | [Modularity study](results/modularity-run/REPORT.md#{anchor}) |\n'
                       for identifier, finding, limit, anchor in rows)
    marker = '\n\n## How to extend this index'
    if marker not in text:
        raise ValueError('learning-index insertion marker missing')
    path.write_text(text.replace(marker, '\n' + addition + marker, 1))


def update_plan() -> None:
    path = EXPERIMENT.parents[1] / 'docs/plans/0011-agent-guided-network/plan.md'
    text = path.read_text()
    marker = '### Coordinating Instructions'
    phase = '''### Phase 10: Verify executable module ownership
Objective: Test real OAK composition, module-scoped learning and accountable evidence.
- [x] Key task: P10.01 Decompose the verified numerical model into shared canonical modules and verify graph-derived execution.
- [x] Key task: P10.02 Run the registered scoped-update study with preserved controls, rejected candidates and held-out tests.
- [x] Key task: P10.03 Audit and reproduce measurements, verify exports, publish evidence and update the learning index.
Success criteria: The modularity report links observed reuse, scope rejection, raw results and deployment-equivalence checks; no predictive advantage is attributed to serialisation.
Transition trigger: Numerical and module-boundary evidence is verified; broader language and comparison questions remain open.

'''
    if '### Phase 10: Verify executable module ownership' not in text:
        path.write_text(text.replace(marker, phase + marker, 1))
    report = path.with_name('report.md')
    text = report.read_text()
    if '## Executable modularity continuation' not in text:
        report.write_text(text + '\n\n## Executable modularity continuation\n\nThe [modularity report](../../../experiments/agent-guided-network/results/modularity-run/REPORT.md) records the frozen source, scoped update, rejection, complete measurements, runtime costs and evidence archive. All earlier scientific sources and results are preserved. Branch checks and integration with newer main remain distinct. No merge is authorised.\n')


def publish(directory: Path) -> None:
    summary, evidence = read(directory / 'summary.json'), read(directory / 'evidence.json')
    package(directory, DESTINATION / 'reproduced')
    (DESTINATION / 'REPORT.md').write_text(build_report(summary, evidence))
    write(DESTINATION / 'publication.json', {
        'scientific_source_commit': '0a6f38dbea5b67f8f911ce21b834fbf0b8b061fe',
        'protocol_commit': 'c4d808d5bd89265bc87ac108b67da373268617a2',
        'workflow_source_commit': os.environ.get('GITHUB_SHA', 'local-working-copy'),
        'workflow_run_id': os.environ.get('GITHUB_RUN_ID'),
        'kind': 'numerical reproduction of one recorded live module choice; zero new agent decisions in CI',
        'local_live_trace': 'live-session.json', 'final_job_status': 'consult workflow conclusion',
    })
    selected = read(directory / 'SELECTION_CLOSED.json')['selected'][str(SEEDS[0])]['agent']['folder']
    target = EXPERIMENT / 'nodes/modularity-learned'
    target.mkdir(exist_ok=False, parents=True)
    for path in (directory / str(SEEDS[0]) / selected).glob('*.oak.md'):
        shutil.copyfile(path, target / path.name)
    update_index()
    update_plan()
    path = EXPERIMENT / 'EXPERIMENT.md'
    text = path.read_text()
    if '## Executable module ownership' not in text:
        path.write_text(text + '\n\n## Executable module ownership\n\nThe [modularity study](modularity/PROTOCOL.md) makes the same initial network six connected OAK documents, reuses the encoder across two consumers and lowers actual resolved processes. The [measured report](results/modularity-run/REPORT.md) records module-scoped learning, rejected updates, mixed wording transfer, equivalence and runtime costs. OAK contributes inspectable composition and ownership, not intelligence by serialisation. Host tensor checks and edit policies are distinguished from native contracts. The coefficient count remains unchanged and this is not a conversational model.\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    publish(parser.parse_args().directory)
