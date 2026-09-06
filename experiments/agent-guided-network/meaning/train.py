"""Differentiable training implementation; inference export uses runtime.py only."""
from __future__ import annotations

import copy
import time
from typing import Mapping

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from runtime import EMBED, WIDTH, VOCAB, ROOMS, encode_inputs, load_record, model_record
from task import Case, render_case


def configure() -> None:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


class Network(nn.Module):
    """Shared GRU sentence encoding, temporal attention and one answer-token head."""

    def __init__(self, seed: int) -> None:
        super().__init__()
        torch.manual_seed(seed)
        self.embedding = nn.Embedding(len(VOCAB), EMBED, padding_idx=0)
        self.gru = nn.GRU(EMBED, WIDTH, batch_first=True)
        self.key = nn.Parameter(torch.randn(WIDTH, WIDTH) / np.sqrt(WIDTH))
        self.query = nn.Parameter(torch.randn(WIDTH, WIDTH) / np.sqrt(WIDTH))
        self.age = nn.Parameter(torch.zeros(1))
        self.hidden = nn.Linear(3 * WIDTH, WIDTH)
        self.output = nn.Linear(WIDTH, len(ROOMS))
        self.double()

    def encode(self, tokens: torch.Tensor) -> torch.Tensor:
        lengths = (tokens != 0).sum(1)
        sequence, _ = self.gru(self.embedding(tokens))
        last = sequence[torch.arange(len(tokens)), (lengths - 1).clamp(min=0)]
        return last * (lengths != 0)[:, None]

    def forward(self, events: torch.Tensor, question: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch, count, words = events.shape
        memory = self.encode(events.reshape(-1, words)).reshape(batch, count, WIDTH)
        query = self.encode(question)
        valid = (events != 0).any(-1)
        age = (valid.sum(1)[:, None] - 1 - torch.arange(count)).clamp(min=0)
        scores = ((memory @ self.key) * (query @ self.query)[:, None]).sum(-1) / np.sqrt(WIDTH)
        scores = scores - F.softplus(self.age) * age
        attention = torch.softmax(scores.masked_fill(~valid, -1e30), dim=1)
        context = (attention[..., None] * memory).sum(1)
        hidden = torch.tanh(self.hidden(torch.cat((context, query, context * query), dim=1)))
        return self.output(hidden), hidden


NAMES = {
    'embedding': 'embedding.weight', 'gru_wi': 'gru.weight_ih_l0', 'gru_wh': 'gru.weight_hh_l0',
    'gru_bi': 'gru.bias_ih_l0', 'gru_bh': 'gru.bias_hh_l0', 'key': 'key', 'query': 'query',
    'age': 'age', 'hidden': 'hidden.weight', 'hidden_bias': 'hidden.bias',
    'output': 'output.weight', 'output_bias': 'output.bias',
}


def record_network(network: Network) -> dict:
    state = network.state_dict()
    return model_record({name: state[key].detach().numpy() for name, key in NAMES.items()})


def restore_network(record: dict) -> Network:
    network = Network(0)
    weights = load_record(record)
    network.load_state_dict({NAMES[name]: torch.tensor(matrix.copy()) for name, matrix in weights.items()})
    return network


def encode_cases(cases: list[Case], form: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    rendered = [render_case(case, form) for case in cases]
    events, queries = encode_inputs([item[0] for item in rendered], [item[1] for item in rendered])
    return torch.from_numpy(events), torch.from_numpy(queries), torch.tensor([case.answer for case in cases])


@torch.no_grad()
def evaluate(record: dict, cases: list[Case], form: int) -> dict:
    network = restore_network(record).eval()
    events, queries, labels = encode_cases(cases, form)
    predictions, losses = [], []
    for start in range(0, len(cases), 128):
        logits, _ = network(events[start:start + 128], queries[start:start + 128])
        predictions.extend(logits.argmax(-1).tolist())
        losses.extend(F.cross_entropy(logits, labels[start:start + 128], reduction='none').tolist())
    return {'accuracy': float(np.mean(np.array(predictions) == labels.numpy())),
            'loss': float(np.mean(losses)), 'predictions': predictions, 'labels': labels.tolist()}


def fit(initial: dict, cases: list[Case], *, seed: int, steps: int, forms: tuple[int, ...],
        agreement: float = 0, rate: float = .003, batch: int = 48) -> tuple[dict, dict]:
    network = restore_network(initial).train()
    optimizer = torch.optim.Adam(network.parameters(), lr=rate)
    generator = np.random.default_rng(seed)
    encoded = {form: encode_cases(cases, form) for form in forms}
    losses = []
    started = time.monotonic()
    for _ in range(steps):
        indices = generator.integers(len(cases), size=batch)
        a, b = generator.choice(forms, size=2, replace=len(forms) == 1)
        xa, qa, target = (tensor[indices] for tensor in encoded[int(a)])
        xb, qb, _ = (tensor[indices] for tensor in encoded[int(b)])
        logits_a, features_a = network(xa, qa)
        logits_b, features_b = network(xb, qb)
        supervised = (F.cross_entropy(logits_a, target) + F.cross_entropy(logits_b, target)) / 2
        aligned = (F.normalize(features_a, dim=1) - F.normalize(features_b, dim=1)).square().sum(1).mean()
        loss = supervised + agreement * aligned
        optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(network.parameters(), 5)
        optimizer.step()
        losses.append(float(loss.detach()))
    return record_network(network), {'steps': steps, 'batch': batch, 'views_per_step': 2,
        'presentations': steps * batch * 2, 'agreement': agreement, 'forms': list(forms),
        'seconds': time.monotonic() - started, 'last_loss': float(np.mean(losses[-25:]))}
