"""Latent-history splits and paired renderings; not imported by deployed inference."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Iterable

import numpy as np
from runtime import OBJECTS, ROOMS, canonical_bytes

FORMS = (
    'the {o} moved from the {s} to the {d}',
    'to the {d} from the {s} the {o} moved',
    'from the {s} the {o} moved to the {d}',
    'the {o} moved to the {d} from the {s}',
)


@dataclass(frozen=True, slots=True)
class Case:
    events: tuple[tuple[int, int, int], ...]
    subject: int
    before: bool

    @property
    def answer(self) -> int:
        latest = next(event for event in reversed(self.events) if event[0] == self.subject)
        return latest[1 if self.before else 2]

    @property
    def identity(self) -> str:
        return hashlib.sha256(canonical_bytes([self.events, self.subject, self.before])).hexdigest()

    @property
    def history_identity(self) -> str:
        return hashlib.sha256(canonical_bytes(self.events)).hexdigest()


def render_case(case: Case, form: int) -> tuple[list[str], str]:
    history = [FORMS[form].format(o=OBJECTS[o], s=ROOMS[s], d=ROOMS[d]) for o, s, d in case.events]
    tense = 'was' if case.before else 'is'
    when = 'before' if case.before else 'now'
    return history, f'where {tense} the {OBJECTS[case.subject]} {when}'


def generate_cases(seed: int, count: int, *, regime: str = 'ordinary', excluded: Iterable[str] = ()) -> list[Case]:
    rng = np.random.default_rng(seed)
    seen = set(excluded)
    cases: list[Case] = []
    attempts = 0
    while len(cases) < count:
        attempts += 1
        if attempts > count * 1000:
            raise RuntimeError('unable to construct disjoint histories')
        subject = int(rng.integers(6))
        low, high = {'long': (12, 19), 'medium': (5, 7)}.get(regime, (2, 5))
        length = int(rng.integers(low, high))
        current = [int(rng.choice([r for r in range(6) if r != o])) for o in range(6)]
        history = []
        for index in range(length):
            obj = subject if index == 0 else int(rng.integers(6))
            options = [r for r in range(6) if r != current[obj] and r != obj]
            dest = int(rng.choice(options))
            history.append((obj, current[obj], dest))
            current[obj] = dest
        if regime == 'combination':
            # Only the final queried destination uses a held-out object-room pair.
            index = max(i for i, event in enumerate(history) if event[0] == subject)
            history[index] = (subject, history[index][1], subject)
        case = Case(tuple(history), subject, bool(rng.integers(2)))
        if case.history_identity in seen:
            continue
        seen.add(case.history_identity)
        cases.append(case)
    return cases


def direction_pairs(seed: int, count: int, *, excluded: Iterable[str] = ()) -> list[tuple[Case, Case]]:
    rng = np.random.default_rng(seed)
    pairs = []
    seen = set(excluded)
    while len(pairs) < count:
        obj = int(rng.integers(6))
        source, dest = map(int, rng.choice(6, size=2, replace=False))
        other = (obj + int(rng.integers(1, 6))) % 6
        u, v = map(int, rng.choice(6, size=2, replace=False))
        a = Case(((obj, source, dest), (other, u, v)), obj, bool(rng.integers(2)))
        b = Case(((obj, dest, source), (other, u, v)), obj, a.before)
        if a.history_identity in seen or b.history_identity in seen:
            continue
        seen.update((a.history_identity, b.history_identity))
        pairs.append((a, b))
    return pairs


def order_pairs(seed: int, count: int, *, excluded: Iterable[str] = ()) -> list[tuple[Case, Case]]:
    rng = np.random.default_rng(seed)
    pairs = []
    seen = set(excluded)
    while len(pairs) < count:
        obj = int(rng.integers(6))
        a, b = map(int, rng.choice(6, size=2, replace=False))
        other = (obj + int(rng.integers(1, 6))) % 6
        x, y = map(int, rng.choice(6, size=2, replace=False))
        forward = Case(((obj, a, b), (other, x, y), (obj, b, a)), obj, bool(rng.integers(2)))
        reverse = Case(((obj, b, a), (other, x, y), (obj, a, b)), obj, forward.before)
        if forward.history_identity in seen or reverse.history_identity in seen:
            continue
        seen.update((forward.history_identity, reverse.history_identity))
        pairs.append((forward, reverse))
    return pairs
