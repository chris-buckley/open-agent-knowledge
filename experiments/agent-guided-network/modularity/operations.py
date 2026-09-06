"""Closed numerical operations and an OAK-lowered program; no training imports."""
from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray

PROFILE = 'oak-modular-meaning-v1'
WIDTH, MAX_WORDS, MAX_EVENTS = 24, 12, 32
OBJECTS = ('ball', 'cup', 'key', 'book', 'coin', 'ring')
ROOMS = ('kitchen', 'garden', 'office', 'hall', 'bedroom', 'shed')
VOCAB = ('<pad>',) + OBJECTS + ROOMS + ('the', 'moved', 'from', 'to', 'where', 'is', 'now', 'was', 'before')
SHAPES = {'embedding': (22, 16), 'gru_wi': (72, 16), 'gru_wh': (72, 24),
          'gru_bi': (72,), 'gru_bh': (72,), 'key': (24, 24), 'query': (24, 24), 'age': (1,),
          'hidden': (24, 72), 'hidden_bias': (24,), 'output': (6, 24), 'output_bias': (6,)}
GROUPS = {'encoder': ('embedding', 'gru_wi', 'gru_wh', 'gru_bi', 'gru_bh'),
          'attention': ('key', 'query', 'age'), 'readout': ('hidden', 'hidden_bias', 'output', 'output_bias')}
Payload = dict[str, Any]  # Validated JSON or tensor ports.
Array = NDArray[np.float64]


def canonical_bytes(record: object) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def identity(record: object) -> str:
    return hashlib.sha256(canonical_bytes(record)).hexdigest()


def decode_parameters(envelope: object, group: str) -> dict[str, Array]:
    if not isinstance(envelope, list) or len(envelope) != 1 or not isinstance(envelope[0], dict):
        raise ValueError('invalid parameter envelope')
    record = envelope[0]
    if set(record) != set(GROUPS[group]):
        raise ValueError('parameter ownership differs: ' + group)
    weights = {}
    for name, encoded in record.items():
        if not isinstance(encoded, dict) or set(encoded) != {'scale', 'values'}:
            raise ValueError('invalid parameter fields')
        scale, integers = encoded['scale'], np.asarray(encoded['values'])
        if type(scale) not in (int, float) or not np.isfinite(scale) or not 0 < scale <= 100:
            raise ValueError('invalid scale')
        if integers.dtype.kind not in 'iu' or integers.shape != SHAPES[name] or np.any(integers < -32767) or np.any(integers > 32767):
            raise ValueError('invalid parameter shape, dtype or range: ' + name)
        values = integers.astype(np.float64) * scale
        if not np.isfinite(values).all() or np.abs(values).max() > 100:
            raise ValueError('invalid parameter magnitude')
        values.setflags(write=False)
        weights[name] = values
    return weights


def numeric(raw: object, shape: tuple[int | None, ...], *, integer: bool = False) -> NDArray:
    values = np.asarray(raw)
    if values.dtype.kind not in ('iu' if integer else 'fiu') or values.ndim != len(shape):
        raise ValueError('invalid tensor rank or dtype')
    if any(size is not None and actual != size for actual, size in zip(values.shape, shape, strict=True)):
        raise ValueError('invalid tensor dimensions')
    if not np.isfinite(values).all():
        raise ValueError('nonfinite tensor')
    return values.astype(np.int64 if integer else np.float64, copy=False)


def words(text: str, vocabulary: list[str]) -> list[int]:
    if not isinstance(text, str):
        raise ValueError('utterance must be text')
    tokens = text.lower().strip().rstrip('.?').split()
    if not 1 <= len(tokens) <= MAX_WORDS or any(token not in vocabulary[1:] for token in tokens):
        raise ValueError('unknown word or utterance capacity')
    return [vocabulary.index(token) for token in tokens] + [0] * (MAX_WORDS - len(tokens))


def tokenise(payload: Payload) -> Payload:
    histories, questions, vocabulary = payload['HISTORIES'], payload['QUESTIONS'], payload['VOCABULARY']
    if vocabulary != list(VOCAB) or not isinstance(histories, list) or not histories:
        raise ValueError('invalid vocabulary or histories')
    if not isinstance(questions, list) or len(questions) != len(histories):
        raise ValueError('one question per history required')
    if any(not isinstance(history, list) or not 1 <= len(history) <= MAX_EVENTS for history in histories):
        raise ValueError('history capacity')
    count = max(map(len, histories))
    tokens = np.zeros((len(histories), count, MAX_WORDS), dtype=np.int64)
    for row, history in enumerate(histories):
        for index, text in enumerate(history):
            tokens[row, index] = words(text, vocabulary)
    return {'EVENT_TOKENS': tokens.reshape(-1, MAX_WORDS),
            'QUESTION_TOKENS': np.array([words(text, vocabulary) for text in questions]),
            'LAYOUT': [len(histories), count], 'MASK': tokens.any(axis=-1).astype(int)}


def encode(payload: Payload) -> Payload:
    weights = decode_parameters(payload['PARAMETERS'], 'encoder')
    tokens = numeric(payload['TOKENS'], (None, MAX_WORDS), integer=True)
    if np.any(tokens < 0) or np.any(tokens >= len(VOCAB)):
        raise ValueError('token outside vocabulary')
    state = np.zeros((len(tokens), WIDTH))
    for word in tokens.T:
        x = weights['embedding'][word] @ weights['gru_wi'].T + weights['gru_bi']
        h = state @ weights['gru_wh'].T + weights['gru_bh']
        xr, xz, xn = np.split(x, 3, axis=1)
        hr, hz, hn = np.split(h, 3, axis=1)
        reset = np.exp(-np.logaddexp(0, -(xr + hr)))
        keep = np.exp(-np.logaddexp(0, -(xz + hz)))
        candidate = np.tanh(xn + reset * hn)
        updated = (1 - keep) * candidate + keep * state
        state = np.where((word != 0)[:, None], updated, state)
    return {'ENCODED': state}


def reshape_memory(payload: Payload) -> Payload:
    layout = numeric(payload['LAYOUT'], (2,), integer=True)
    if np.any(layout <= 0) or layout[1] > MAX_EVENTS:
        raise ValueError('invalid memory layout')
    encoded = numeric(payload['ENCODED'], (int(np.prod(layout)), WIDTH))
    return {'MEMORY': encoded.reshape(*layout, WIDTH)}


def query_view(payload: Payload) -> Payload:
    return {'QUERY': numeric(payload['ENCODED'], (None, WIDTH))}


def attend(payload: Payload) -> Payload:
    weights = decode_parameters(payload['PARAMETERS'], 'attention')
    memory = numeric(payload['MEMORY'], (None, None, WIDTH))
    batch, count, _ = memory.shape
    query = numeric(payload['QUERY'], (batch, WIDTH))
    valid = numeric(payload['MASK'], (batch, count), integer=True)
    if not 1 <= count <= MAX_EVENTS or not np.isin(valid, (0, 1)).all() or not valid.any(axis=1).all():
        raise ValueError('invalid memory mask')
    age = np.maximum(valid.sum(axis=1)[:, None] - 1 - np.arange(count), 0)
    scores = ((memory @ weights['key']) * (query @ weights['query'])[:, None]).sum(-1) / np.sqrt(WIDTH)
    scores -= np.logaddexp(0, weights['age'][0]) * age
    scores = np.where(valid != 0, scores, -1e30)
    attention = np.exp(scores - scores.max(axis=1, keepdims=True))
    attention /= attention.sum(axis=1, keepdims=True)
    return {'CONTEXT': (attention[..., None] * memory).sum(axis=1)}


def classify(payload: Payload) -> Payload:
    weights = decode_parameters(payload['PARAMETERS'], 'readout')
    context = numeric(payload['CONTEXT'], (None, WIDTH))
    query = numeric(payload['QUERY'], context.shape)
    if payload['ANSWERS'] != list(ROOMS):
        raise ValueError('answer vocabulary differs')
    features = np.concatenate((context, query, context * query), axis=1)
    hidden = np.tanh(features @ weights['hidden'].T + weights['hidden_bias'])
    logits = hidden @ weights['output'].T + weights['output_bias']
    probabilities = np.exp(logits - logits.max(axis=1, keepdims=True))
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    return {'PROBABILITIES': probabilities, 'REPLIES': [ROOMS[int(i)] for i in probabilities.argmax(-1)]}


def recall(payload: Payload) -> Payload:
    history = payload['STORED']
    if not isinstance(history, list) or len(history) != 1 or not isinstance(history[0], list):
        raise ValueError('invalid history envelope')
    if len(history[0]) > MAX_EVENTS:
        raise ValueError('history capacity')
    for text in history[0]:
        words(text, list(VOCAB))
    return {'HISTORIES': copy.deepcopy(history)}


def append_observation(payload: Payload) -> Payload:
    history = recall({'STORED': payload['HISTORY']})['HISTORIES']
    if len(history[0]) >= MAX_EVENTS:
        raise ValueError('history capacity')
    words(payload['TEXT'], list(VOCAB))
    return {'UPDATED': [[*history[0], payload['TEXT']]]}


@dataclass(frozen=True, slots=True)
class Operation:
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    function: Callable[[Payload], Payload]

    @property
    def instruction(self) -> str:
        inputs = ', '.join('<' + name + '>' for name in self.inputs)
        outputs = ', '.join('<' + name + '>' for name in self.outputs)
        return f'Transform {inputs} into {outputs} using the registered numerical contract.'


OPERATIONS = {
    'modular.tokenise.v1': Operation(('HISTORIES', 'QUESTIONS', 'VOCABULARY'), ('EVENT_TOKENS', 'QUESTION_TOKENS', 'LAYOUT', 'MASK'), tokenise),
    'modular.encode.v1': Operation(('TOKENS', 'PARAMETERS'), ('ENCODED',), encode),
    'modular.reshape.v1': Operation(('ENCODED', 'LAYOUT'), ('MEMORY',), reshape_memory),
    'modular.query.v1': Operation(('ENCODED',), ('QUERY',), query_view),
    'modular.attend.v1': Operation(('MEMORY', 'QUERY', 'MASK', 'PARAMETERS'), ('CONTEXT',), attend),
    'modular.classify.v1': Operation(('CONTEXT', 'QUERY', 'PARAMETERS', 'ANSWERS'), ('PROBABILITIES', 'REPLIES'), classify),
    'modular.append.v1': Operation(('HISTORY', 'TEXT'), ('UPDATED',), append_observation),
    'modular.recall.v1': Operation(('STORED',), ('HISTORIES',), recall),
}


def invoke(operation: str, payload: Payload) -> Payload:
    spec = OPERATIONS[operation]
    if set(payload) != set(spec.inputs):
        raise ValueError('operation input ports differ')
    result = spec.function(payload)
    if set(result) != set(spec.outputs):
        raise ValueError('operation output ports differ')
    return result


class Program:
    """Run a closed program lowered from OAK CALL and ACT dataflow."""

    def __init__(self, record: Payload) -> None:
        if set(record) != {'profile', 'source', 'constants', 'initial_state', 'entries', 'digest'}:
            raise ValueError('invalid program fields')
        digest = identity({key: value for key, value in record.items() if key != 'digest'})
        if record['profile'] != PROFILE or record['digest'] != digest:
            raise ValueError('program identity mismatch')
        self._record = copy.deepcopy(record)
        self._revision = digest
        self.reset()

    def run(self, entry: str, payload: Payload) -> Payload:
        plan = self._record['entries'][entry]
        if set(payload) != set(plan['inputs']):
            raise ValueError('entry payload differs')
        state, slots, emitted = copy.deepcopy(self._state), {}, {}

        def read(expression: list) -> Any:
            kind, key = expression
            return {'input': payload, 'slot': slots, 'state': state, 'constant': self._record['constants']}[kind][key]

        for instruction in plan['instructions']:
            match instruction['kind']:
                case 'act':
                    inputs = {key: read(expr) for key, expr in instruction['inputs'].items()}
                    outputs = invoke(instruction['operation'], inputs)
                    slots.update({slot: outputs[key] for key, slot in instruction['outputs'].items()})
                case 'set':
                    state[instruction['target']] = copy.deepcopy(read(instruction['value']))
                case 'emit':
                    emitted.update({key: read(expr) for key, expr in instruction['values'].items()})
                case _:
                    raise ValueError('unsupported program instruction')
        result = emitted or {key: read(expr) for key, expr in plan['outputs'].items()}
        self._state = state
        return result

    def snapshot(self) -> Payload:
        return {'revision': self._revision, 'state': copy.deepcopy(self._state)}

    def restore(self, snapshot: Payload) -> None:
        if set(snapshot) != {'revision', 'state'} or snapshot['revision'] != self._revision:
            raise ValueError('state belongs to another model')
        if not isinstance(snapshot['state'], dict) or set(snapshot['state']) != set(self._record['initial_state']):
            raise ValueError('state keys differ')
        for history in snapshot['state'].values():
            recall({'STORED': history})
        self._state = copy.deepcopy(snapshot['state'])

    def reset(self) -> None:
        self._state = copy.deepcopy(self._record['initial_state'])
        for history in self._state.values():
            recall({'STORED': history})
