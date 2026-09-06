"""Agent-free numerical dialogue primitives, direct execution and restored state."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray

PROFILE = 'oak-generated-dialogue-v1'
WIDTH, EMBED = 48, 24
MAX_INPUT, MAX_REPLY, MAX_MESSAGES = 256, 14, 24
OBJECTS = ('ball', 'cup', 'key', 'book')
ROOMS = ('kitchen', 'garden', 'office', 'hall')
VOCAB = ('<pad>', '<bos>', '<eos>', '<user>', '<assistant>', '<sep>', '<unk>',
         'the', 'a', 'is', 'in', 'was', 'it', 'now', 'before', 'where', 'moved', 'from', 'to',
         'went', 'travelled', 'did', 'come', 'can', 'you', 'tell', 'me', 'please', 'and',
         'i', 'do', 'not', 'know', 'then', 'actually', 'hello', 'hi', '.', '?') + OBJECTS + ROOMS
PAD, BOS, EOS, USER, ASSISTANT, SEP, UNK = range(7)
SHAPES = {
    'embedding': (len(VOCAB), EMBED), 'enc_wi': (3 * WIDTH, EMBED), 'enc_wh': (3 * WIDTH, WIDTH),
    'enc_bi': (3 * WIDTH,), 'enc_bh': (3 * WIDTH,), 'key': (WIDTH, WIDTH), 'query': (WIDTH, WIDTH),
    'dec_wi': (3 * WIDTH, EMBED + WIDTH), 'dec_wh': (3 * WIDTH, WIDTH),
    'dec_bi': (3 * WIDTH,), 'dec_bh': (3 * WIDTH,),
    'output': (len(VOCAB), 2 * WIDTH), 'output_bias': (len(VOCAB),),
}
GROUPS = {'encoder': ('embedding', 'enc_wi', 'enc_wh', 'enc_bi', 'enc_bh'),
          'attention': ('key', 'query'), 'decoder': ('dec_wi', 'dec_wh', 'dec_bi', 'dec_bh'),
          'readout': ('output', 'output_bias')}
Array = NDArray[np.float32]
Payload = dict[str, Any]  # Tensor or JSON values at validated operation boundaries.


def canonical_bytes(record: object) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def identity(record: object) -> str:
    return hashlib.sha256(canonical_bytes(record)).hexdigest()


def parameters(record: object, group: str | None = None) -> dict[str, Array]:
    if not isinstance(record, dict):
        raise ValueError('parameters must be an object')
    expected = SHAPES if group is None else GROUPS[group]
    if set(record) != set(expected):
        raise ValueError('parameter ownership differs')
    arrays = {}
    for name, raw in record.items():
        array = np.asarray(raw)
        if array.shape != SHAPES[name] or array.dtype.kind not in 'fiu' or not np.isfinite(array).all():
            raise ValueError('invalid tensor: ' + name)
        if np.abs(array).max() > 100:
            raise ValueError('parameter magnitude exceeds profile')
        arrays[name] = array.astype(np.float32)
        arrays[name].setflags(write=False)
    return arrays


def load_model(record: Payload) -> dict[str, Array]:
    if set(record) != {'profile', 'vocabulary', 'weights'} or record['profile'] != PROFILE or record['vocabulary'] != list(VOCAB):
        raise ValueError('invalid model profile or vocabulary')
    return parameters(record['weights'])


def token_ids(text: str) -> list[int]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError('nonempty text required')
    lexemes = re.findall(r"[a-z]+|[.?]|[^\s]", text.lower())
    return [VOCAB.index(word) if word in VOCAB else UNK for word in lexemes]


def encode_inputs(histories: list[list[dict[str, str]]], texts: list[str]) -> NDArray[np.int64]:
    if len(histories) != len(texts) or not texts:
        raise ValueError('one utterance per history required')
    rows = []
    for history, text in zip(histories, texts, strict=True):
        validate_history(history)
        tokens = []
        for message in history:
            tokens.extend([USER if message['role'] == 'user' else ASSISTANT, *token_ids(message['text']), SEP])
        tokens.extend([USER, *token_ids(text), SEP])
        if len(tokens) > MAX_INPUT:
            raise ValueError('dialogue token capacity exceeded')
        rows.append(tokens)
    encoded = np.zeros((len(rows), max(map(len, rows))), dtype=np.int64)
    for index, row in enumerate(rows):
        encoded[index, :len(row)] = row
    return encoded


def validate_history(history: object) -> None:
    if not isinstance(history, list) or len(history) > MAX_MESSAGES or len(history) % 2:
        raise ValueError('invalid dialogue history capacity or alternation')
    for index, message in enumerate(history):
        if not isinstance(message, dict) or set(message) != {'role', 'text'}:
            raise ValueError('invalid message')
        if message['role'] != ('user' if index % 2 == 0 else 'assistant'):
            raise ValueError('invalid message role')
        token_ids(message['text'])


def gru_step(inputs: Array, state: Array, weights: dict[str, Array], prefix: str) -> Array:
    xi = inputs @ weights[prefix + '_wi'].T + weights[prefix + '_bi']
    hh = state @ weights[prefix + '_wh'].T + weights[prefix + '_bh']
    xr, xz, xn = np.split(xi, 3, axis=-1)
    hr, hz, hn = np.split(hh, 3, axis=-1)
    reset = np.exp(-np.logaddexp(np.float32(0), -(xr + hr)))
    keep = np.exp(-np.logaddexp(np.float32(0), -(xz + hz)))
    return (1 - keep) * np.tanh(xn + reset * hn) + keep * state


def encode(weights: dict[str, Array], tokens: NDArray[np.int64]) -> tuple[Array, Array]:
    hidden = np.zeros((len(tokens), WIDTH), np.float32)
    memory = []
    for words in tokens.T:
        hidden = gru_step(weights['embedding'][words], hidden, weights, 'enc')
        memory.append(hidden)
    encoded = np.stack(memory, axis=1)
    last = encoded[np.arange(len(tokens)), (tokens != PAD).sum(axis=1) - 1]
    return encoded, last


def retrieve(weights: dict[str, Array], memory: Array, state: Array, mask: NDArray) -> Array:
    scores = ((memory @ weights['key']) * (state @ weights['query'])[:, None]).sum(-1) / np.float32(np.sqrt(WIDTH))
    scores = np.where(mask, scores, np.float32(-1e9))
    probabilities = np.exp(scores - scores.max(-1, keepdims=True))
    probabilities /= probabilities.sum(-1, keepdims=True)
    return np.sum(probabilities[..., None] * memory, axis=1)


def reply_text(tokens: list[int]) -> str:
    words = []
    for token in tokens:
        if token == EOS:
            break
        words.append(VOCAB[token])
    text = ' '.join(words).replace(' .', '.').replace(' ?', '?')
    return text[:1].upper() + text[1:] if text else '<empty>'


def predict(record: Payload, histories: list[list[dict[str, str]]], texts: list[str]) -> tuple[list[str], Array]:
    weights = load_model(record)
    tokens = encode_inputs(histories, texts)
    memory, state = encode(weights, tokens)
    previous = np.full(len(tokens), BOS, np.int64)
    tape, distributions = [], []
    for _ in range(MAX_REPLY):
        context = retrieve(weights, memory, state, tokens != PAD)
        inputs = np.concatenate((weights['embedding'][previous], context), axis=1)
        state = gru_step(inputs, state, weights, 'dec')
        logits = np.concatenate((state, context), axis=1) @ weights['output'].T + weights['output_bias']
        probs = np.exp(logits - logits.max(-1, keepdims=True))
        probs /= probs.sum(-1, keepdims=True)
        previous = probs.argmax(-1)
        tape.append(previous)
        distributions.append(probs)
    return [reply_text(row) for row in np.stack(tape, axis=1).tolist()], np.stack(distributions, axis=1)


class Session:
    """A frozen model plus explicit user/generated-reply history, without teacher access."""
    def __init__(self, record: Payload) -> None:
        load_model(record)
        self.record = copy.deepcopy(record)
        self.history: list[dict[str, str]] = []
        self.model_id = identity(record)

    def answer(self, text: str) -> str:
        if len(self.history) + 2 > MAX_MESSAGES:
            raise ValueError('dialogue message capacity exceeded')
        reply = predict(self.record, [self.history], [text])[0][0]
        self.history.extend([{'role': 'user', 'text': text}, {'role': 'assistant', 'text': reply}])
        return reply

    def snapshot(self) -> Payload:
        return {'model': self.model_id, 'history': copy.deepcopy(self.history)}

    def restore(self, snapshot: Payload) -> None:
        if set(snapshot) != {'model', 'history'} or snapshot['model'] != self.model_id:
            raise ValueError('state belongs to another model')
        validate_history(snapshot['history'])
        self.history = copy.deepcopy(snapshot['history'])


def _prepare(payload: Payload) -> Payload:
    tokens = encode_inputs(payload['HISTORIES'], payload['TEXTS'])
    return {'TOKENS': tokens, 'MASK': tokens != PAD}


def _encode(payload: Payload) -> Payload:
    memory, state = encode(parameters(payload['PARAMETERS'][0], 'encoder'), np.asarray(payload['TOKENS'], np.int64))
    count = len(memory)
    return {'MEMORY': memory, 'STATE': state, 'PREVIOUS': np.full(count, BOS), 'TAPE': [[] for _ in range(count)], 'EMBEDDING': np.asarray(payload['PARAMETERS'][0]['embedding'], np.float32)}


def _attend(payload: Payload) -> Payload:
    return {'CONTEXT': retrieve(parameters(payload['PARAMETERS'][0], 'attention'),
                               np.asarray(payload['MEMORY'], np.float32), np.asarray(payload['STATE'], np.float32),
                               np.asarray(payload['MASK'], bool))}


def _decode(payload: Payload) -> Payload:
    embedding = np.asarray(payload['EMBEDDING'], np.float32)
    inputs = np.concatenate((embedding[np.asarray(payload['PREVIOUS'], np.int64)], np.asarray(payload['CONTEXT'], np.float32)), axis=1)
    state = gru_step(inputs, np.asarray(payload['STATE'], np.float32), parameters(payload['PARAMETERS'][0], 'decoder'), 'dec')
    return {'NEWSTATE': state}


def _readout(payload: Payload) -> Payload:
    weights = parameters(payload['PARAMETERS'][0], 'readout')
    features = np.concatenate((np.asarray(payload['STATE'], np.float32), np.asarray(payload['CONTEXT'], np.float32)), axis=1)
    logits = features @ weights['output'].T + weights['output_bias']
    previous = logits.argmax(-1)
    return {'NEWPREVIOUS': previous, 'NEWTAPE': [row + [int(token)] for row, token in zip(payload['TAPE'], previous, strict=True)]}


def _finish(payload: Payload) -> Payload:
    return {'REPLIES': [reply_text(row) for row in payload['TAPE']]}


def _recall(payload: Payload) -> Payload:
    if not isinstance(payload['STORED'], list) or len(payload['STORED']) != 1:
        raise ValueError('one dialogue history required')
    validate_history(payload['STORED'][0])
    return {'HISTORIES': copy.deepcopy(payload['STORED'])}


def _commit(payload: Payload) -> Payload:
    histories = _recall({'STORED': payload['HISTORIES']})['HISTORIES']
    if len(payload['TEXTS']) != 1 or len(payload['REPLIES']) != 1 or len(histories[0]) + 2 > MAX_MESSAGES:
        raise ValueError('one bounded dialogue turn required')
    messages = [{'role': 'user', 'text': payload['TEXTS'][0]}, {'role': 'assistant', 'text': payload['REPLIES'][0]}]
    return {'STORED': [histories[0] + messages]}


@dataclass(frozen=True, slots=True)
class Operation:
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    function: Callable[[Payload], Payload]

    @property
    def instruction(self) -> str:
        names = ', '.join('<' + name + '>' for name in self.inputs + self.outputs)
        return 'Apply the registered numerical operation to ' + names + '.'


OPERATIONS = {
    'dialogue.prepare': Operation(('HISTORIES', 'TEXTS'), ('TOKENS', 'MASK'), _prepare),
    'dialogue.encode': Operation(('TOKENS', 'PARAMETERS'), ('MEMORY', 'STATE', 'PREVIOUS', 'TAPE', 'EMBEDDING'), _encode),
    'dialogue.attend': Operation(('MEMORY', 'STATE', 'MASK', 'PARAMETERS'), ('CONTEXT',), _attend),
    'dialogue.decode': Operation(('STATE', 'CONTEXT', 'PREVIOUS', 'EMBEDDING', 'PARAMETERS'), ('NEWSTATE',), _decode),
    'dialogue.readout': Operation(('STATE', 'CONTEXT', 'TAPE', 'PARAMETERS'), ('NEWPREVIOUS', 'NEWTAPE'), _readout),
    'dialogue.finish': Operation(('TAPE',), ('REPLIES',), _finish),
    'dialogue.recall': Operation(('STORED',), ('HISTORIES',), _recall),
    'dialogue.commit': Operation(('HISTORIES', 'TEXTS', 'REPLIES'), ('STORED',), _commit),
}


def invoke(operation: str, payload: Payload) -> Payload:
    spec = OPERATIONS[operation]
    if set(payload) != set(spec.inputs):
        raise ValueError('operation ports differ')
    return spec.function(payload)


class Program:
    """Execute a graph-lowered, model-bound numerical instruction list."""
    def __init__(self, program: Payload) -> None:
        self.program = copy.deepcopy(program)
        if program['profile'] != PROFILE or identity({k: v for k, v in program.items() if k != 'digest'}) != program['digest']:
            raise ValueError('invalid program identity')
        self.state = copy.deepcopy(program['initial_state'])

    def run(self, entry: str, inputs: Payload) -> Payload:
        slots: Payload = {}
        pending = copy.deepcopy(self.state)
        spec = self.program['entries'][entry]
        if set(inputs) != set(spec['inputs']):
            raise ValueError('entry ports differ')
        sources = {'input': inputs, 'constant': self.program['constants'], 'state': pending, 'slot': slots}
        def read(reference: list[str]) -> Any:
            return sources[reference[0]][reference[1]]
        for instruction in spec['instructions']:
            if instruction['kind'] == 'act':
                result = invoke(instruction['operation'], {k: read(v) for k, v in instruction['inputs'].items()})
                slots.update({slot: result[k] for k, slot in instruction['outputs'].items()})
            elif instruction['kind'] == 'set':
                pending[instruction['target']] = read(instruction['value'])
            elif instruction['kind'] != 'emit':
                raise ValueError('unsupported instruction')
        result = {k: read(v) for k, v in spec['outputs'].items()}
        self.state = pending
        return result

    def snapshot(self) -> Payload:
        return {'model': self.program['digest'], 'state': json.loads(json.dumps(self.state, default=lambda value: value.tolist()))}

    def restore(self, snapshot: Payload) -> None:
        if set(snapshot) != {'model', 'state'} or snapshot['model'] != self.program['digest'] or set(snapshot['state']) != set(self.state):
            raise ValueError('state belongs to another graph')
        for name, envelope in snapshot['state'].items():
            if name.endswith('#state.history'):
                _recall({'STORED': envelope})
            else:
                array = np.asarray(envelope)
                if array.dtype.kind not in 'fiu' or not np.isfinite(array).all():
                    raise ValueError('invalid generation state')
        self.state = copy.deepcopy(snapshot['state'])


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    args = parser.parse_args()
    record = json.loads(args.model.read_text())
    session = Session(record)
    print('Restricted learned dialogue. /reset clears history; /quit exits.')
    while True:
        try:
            utterance = input('You: ')
        except EOFError:
            break
        if utterance == '/quit':
            break
        if utterance == '/reset':
            session = Session(record)
            continue
        try:
            print('Model:', session.answer(utterance))
        except ValueError as error:
            print('Input error:', error)


if __name__ == '__main__':
    main()
