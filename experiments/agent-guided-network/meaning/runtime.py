"""Closed numerical question-answering profile; no simulator or training imports."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

import numpy as np
from numpy.typing import NDArray

PROFILE = 'oak-word-meaning-v1'
OBJECTS = ('ball', 'cup', 'key', 'book', 'coin', 'ring')
ROOMS = ('kitchen', 'garden', 'office', 'hall', 'bedroom', 'shed')
VOCAB = ('<pad>',) + OBJECTS + ROOMS + ('the', 'moved', 'from', 'to', 'where', 'is', 'now', 'was', 'before')
WORD_IDS = {word: index for index, word in enumerate(VOCAB)}
WIDTH = 24
EMBED = 16
MAX_EVENTS = 32
MAX_WORDS = 12
SHAPES = {
    'embedding': (len(VOCAB), EMBED),
    'gru_wi': (3 * WIDTH, EMBED), 'gru_wh': (3 * WIDTH, WIDTH),
    'gru_bi': (3 * WIDTH,), 'gru_bh': (3 * WIDTH,),
    'key': (WIDTH, WIDTH), 'query': (WIDTH, WIDTH), 'age': (1,),
    'hidden': (WIDTH, 3 * WIDTH), 'hidden_bias': (WIDTH,),
    'output': (len(ROOMS), WIDTH), 'output_bias': (len(ROOMS),),
}
Array = NDArray[np.float64]
Weights = dict[str, Array]


def canonical_bytes(record: object) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def encode_words(text: str) -> list[int]:
    if not isinstance(text, str):
        raise ValueError('utterance must be text')
    words = text.lower().strip().rstrip('.?').split()
    if not 1 <= len(words) <= MAX_WORDS or any(word not in WORD_IDS for word in words):
        raise ValueError('unknown word or unsupported utterance length')
    return [WORD_IDS[word] for word in words] + [0] * (MAX_WORDS - len(words))


def encode_inputs(histories: list[list[str]], questions: list[str]) -> tuple[NDArray, NDArray]:
    if len(histories) != len(questions) or not histories:
        raise ValueError('one nonempty history per question required')
    if any(not 1 <= len(history) <= MAX_EVENTS for history in histories):
        raise ValueError('history outside profile capacity')
    count = max(map(len, histories))
    tokens = np.zeros((len(histories), count, MAX_WORDS), dtype=np.int64)
    for row, history in enumerate(histories):
        for event, text in enumerate(history):
            tokens[row, event] = encode_words(text)
    return tokens, np.array([encode_words(text) for text in questions], dtype=np.int64)


def validate_weights(weights: Mapping[str, object]) -> Weights:
    if set(weights) != set(SHAPES):
        raise ValueError('parameter names differ from profile')
    output = {}
    for name, shape in SHAPES.items():
        raw = np.asarray(weights[name])
        if raw.dtype.kind not in 'fiu' or raw.shape != shape:
            raise ValueError('invalid parameter shape or type: ' + name)
        matrix = np.array(raw, dtype=np.float64, copy=True)
        if not np.isfinite(matrix).all() or np.max(np.abs(matrix)) > 100:
            raise ValueError('invalid parameter magnitude: ' + name)
        matrix.setflags(write=False)
        output[name] = matrix
    return output


def model_record(weights: Mapping[str, object]) -> dict:
    encoded = {}
    for name, matrix in validate_weights(weights).items():
        scale = max(float(np.abs(matrix).max()) / 32767, 1e-12)
        encoded[name] = {'scale': scale, 'values': np.rint(matrix / scale).astype(int).tolist()}
    return {'profile': PROFILE, 'vocabulary': list(VOCAB), 'answers': list(ROOMS), 'weights': encoded}


def load_record(record: dict) -> Weights:
    if set(record) != {'profile', 'vocabulary', 'answers', 'weights'}:
        raise ValueError('unknown model fields')
    if record['profile'] != PROFILE or record['vocabulary'] != list(VOCAB) or record['answers'] != list(ROOMS):
        raise ValueError('unsupported profile or vocabulary')
    weights = {}
    for name, value in record['weights'].items():
        if set(value) != {'scale', 'values'} or isinstance(value['scale'], bool):
            raise ValueError('invalid quantised tensor')
        quantised = np.asarray(value['values'])
        scale = value['scale']
        if not isinstance(scale, (int, float)) or not np.isfinite(scale) or not 0 < scale <= 100:
            raise ValueError('invalid quantisation scale')
        if quantised.dtype.kind not in 'iu' or np.any(np.abs(quantised) > 32767):
            raise ValueError('invalid quantised coefficients')
        weights[name] = quantised.astype(np.float64) * scale
    return validate_weights(weights)


def sigmoid(values: Array) -> Array:
    return np.exp(-np.logaddexp(0, -values))


def encode_sentences(weights: Weights, tokens: NDArray) -> Array:
    if tokens.dtype.kind not in 'iu' or tokens.ndim != 2 or tokens.shape[1] != MAX_WORDS:
        raise ValueError('invalid token shape')
    if np.any(tokens < 0) or np.any(tokens >= len(VOCAB)):
        raise ValueError('token outside vocabulary')
    state = np.zeros((len(tokens), WIDTH))
    for word in tokens.T:
        x = weights['embedding'][word] @ weights['gru_wi'].T + weights['gru_bi']
        h = state @ weights['gru_wh'].T + weights['gru_bh']
        xr, xz, xn = np.split(x, 3, axis=1)
        hr, hz, hn = np.split(h, 3, axis=1)
        reset, keep = sigmoid(xr + hr), sigmoid(xz + hz)
        candidate = np.tanh(xn + reset * hn)
        updated = (1 - keep) * candidate + keep * state
        state = np.where((word != 0)[:, None], updated, state)
    return state


def forward(weights: Weights, events: NDArray, question: NDArray, *, uniform: bool = False) -> Array:
    if events.ndim != 3 or not 1 <= events.shape[1] <= MAX_EVENTS or len(events) != len(question):
        raise ValueError('invalid event tensor')
    batch, count, words = events.shape
    memory = encode_sentences(weights, events.reshape(-1, words)).reshape(batch, count, WIDTH)
    query = encode_sentences(weights, question)
    valid = np.any(events != 0, axis=-1)
    if not np.all(valid.any(axis=1)):
        raise ValueError('empty history')
    age = np.maximum(valid.sum(axis=1)[:, None] - 1 - np.arange(count), 0)
    scores = ((memory @ weights['key']) * (query @ weights['query'])[:, None]).sum(-1) / np.sqrt(WIDTH)
    scores -= np.logaddexp(0, weights['age'][0]) * age
    if uniform:
        scores[:] = 0
    scores = np.where(valid, scores, -1e30)
    attention = np.exp(scores - scores.max(axis=1, keepdims=True))
    attention /= attention.sum(axis=1, keepdims=True)
    context = (attention[..., None] * memory).sum(axis=1)
    features = np.concatenate((context, query, context * query), axis=1)
    hidden = np.tanh(features @ weights['hidden'].T + weights['hidden_bias'])
    logits = hidden @ weights['output'].T + weights['output_bias']
    probabilities = np.exp(logits - logits.max(axis=1, keepdims=True))
    return probabilities / probabilities.sum(axis=1, keepdims=True)


class Session:
    """Retain only supplied observations; never treat a generated answer as a fact."""

    def __init__(self, record: dict) -> None:
        self._weights = load_record(record)
        self._revision = hashlib.sha256(canonical_bytes(record)).hexdigest()
        self._events: list[str] = []

    def observe(self, utterance: str) -> None:
        encode_words(utterance)
        if len(self._events) >= MAX_EVENTS:
            raise ValueError('history capacity exceeded')
        self._events.append(utterance)

    def answer(self, question: str) -> str:
        events, query = encode_inputs([self._events], [question])
        return ROOMS[int(forward(self._weights, events, query)[0].argmax())]

    def snapshot(self) -> dict:
        return {'profile': PROFILE, 'revision': self._revision, 'events': list(self._events)}

    def restore(self, record: dict) -> None:
        if set(record) != {'profile', 'revision', 'events'}:
            raise ValueError('invalid state fields')
        if record['profile'] != PROFILE or record['revision'] != self._revision:
            raise ValueError('state belongs to a different model')
        if not isinstance(record['events'], list) or len(record['events']) > MAX_EVENTS:
            raise ValueError('invalid history')
        for text in record['events']:
            encode_words(text)
        self._events = list(record['events'])

    def reset(self) -> None:
        self._events.clear()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Agent-free numerical location answers')
    parser.add_argument('model', type=Path)
    parser.add_argument('request', type=Path, help='JSON with events and question')
    args = parser.parse_args()
    session = Session(json.loads(args.model.read_text()))
    request = json.loads(args.request.read_text())
    for text in request['events']:
        session.observe(text)
    print(session.answer(request['question']))
