"""PyTorch training; exported runtime and OAK execution do not import this module."""
from __future__ import annotations

import time
from typing import Any

import numpy as np
import torch
from torch import Tensor, nn
from torch.nn import functional as F

from runtime import BOS, EOS, MAX_REPLY, SHAPES, GROUPS, VOCAB, WIDTH, EMBED, PROFILE, encode_inputs, load_model, token_ids
from task import Episode, examples


def configure() -> None:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


class Network(nn.Module):
    def __init__(self, seed: int) -> None:
        super().__init__()
        torch.manual_seed(seed)
        self.weights = nn.ParameterDict()
        for name, shape in SHAPES.items():
            weight = torch.empty(shape)
            if len(shape) == 1:
                nn.init.zeros_(weight)
            else:
                nn.init.xavier_uniform_(weight)
            self.weights[name] = nn.Parameter(weight)
        self.encoder = nn.GRU(EMBED, WIDTH, batch_first=True)
        for suffix, name in [('weight_ih_l0', 'enc_wi'), ('weight_hh_l0', 'enc_wh'), ('bias_ih_l0', 'enc_bi'), ('bias_hh_l0', 'enc_bh')]:
            setattr(self.encoder, suffix, self.weights[name])

    def encode(self, tokens: Tensor) -> tuple[Tensor, Tensor]:
        weights = self.weights
        embedded = F.embedding(tokens, weights['embedding'])
        memory, _ = self.encoder(embedded)
        last = memory[torch.arange(len(tokens)), (tokens != 0).sum(1) - 1]
        return memory, last

    def forward(self, tokens: Tensor, targets: Tensor | None = None) -> Tensor:
        weights = self.weights
        memory, state = self.encode(tokens)
        keys = memory @ weights['key']
        previous = torch.full((len(tokens),), BOS, dtype=torch.long)
        outputs = []
        steps = MAX_REPLY if targets is None else targets.shape[1]
        for index in range(steps):
            scores = (keys * (state @ weights['query'])[:, None]).sum(-1) / np.sqrt(WIDTH)
            attention = scores.masked_fill(tokens == 0, -1e9).softmax(-1)
            context = (attention[..., None] * memory).sum(1)
            inputs = torch.cat((F.embedding(previous, weights['embedding']), context), dim=1)
            xi = F.linear(inputs, weights['dec_wi'], weights['dec_bi'])
            hh = F.linear(state, weights['dec_wh'], weights['dec_bh'])
            xr, xz, xn = xi.chunk(3, -1)
            hr, hz, hn = hh.chunk(3, -1)
            keep = (xz + hz).sigmoid()
            state = (1 - keep) * (xn + (xr + hr).sigmoid() * hn).tanh() + keep * state
            logits = F.linear(torch.cat((state, context), dim=1), weights['output'], weights['output_bias'])
            outputs.append(logits)
            previous = logits.argmax(-1) if targets is None else targets[:, index]
        return torch.stack(outputs, 1)


def model_record(network: Network) -> dict[str, Any]:
    return {'profile': PROFILE, 'vocabulary': list(VOCAB),
            'weights': {key: value.detach().numpy().tolist() for key, value in network.weights.items()}}


def from_record(record: dict[str, Any]) -> Network:
    arrays = load_model(record)
    network = Network(0)
    with torch.no_grad():
        for key, value in arrays.items():
            network.weights[key].copy_(torch.tensor(value.copy()))
    return network


def fit(record: dict[str, Any], episodes: list[Episode], *, seed: int, steps: int,
        groups: tuple[str, ...] = tuple(GROUPS), batch_size: int = 48) -> tuple[dict[str, Any], dict[str, Any]]:
    configure()
    network = from_record(record)
    permitted = {name for group in groups for name in GROUPS[group]}
    for name, weight in network.weights.items():
        weight.requires_grad_(name in permitted)
    optimiser = torch.optim.Adam([value for value in network.weights.values() if value.requires_grad], lr=0.003)
    pairs = examples(episodes)
    tokens = encode_inputs([pair['history'] for pair in pairs], [pair['text'] for pair in pairs])
    targets = np.zeros((len(pairs), MAX_REPLY), np.int64)
    for index, pair in enumerate(pairs):
        row = token_ids(pair['reply']) + [EOS]
        if len(row) > MAX_REPLY:
            raise ValueError('teaching reply exceeds capacity')
        targets[index, :len(row)] = row
    rng = np.random.default_rng(seed)
    start = time.perf_counter()
    for _ in range(steps):
        indices = rng.integers(0, len(pairs), size=batch_size)
        batch = tokens[indices]
        batch = batch[:, :(batch != 0).sum(1).max()]
        answer = torch.from_numpy(targets[indices])
        optimiser.zero_grad(set_to_none=True)
        logits = network(torch.from_numpy(batch), answer)
        loss = F.cross_entropy(logits.flatten(0, 1), answer.flatten(), ignore_index=0)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(network.parameters(), 1.0)
        optimiser.step()
    return model_record(network), {'steps': steps, 'batch': batch_size, 'examples': len(pairs),
        'trainable': sum(weight.numel() for weight in network.parameters() if weight.requires_grad),
        'groups': list(groups), 'seconds': time.perf_counter() - start, 'last_loss': float(loss.detach())}
