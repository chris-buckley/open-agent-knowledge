"""Synthetic teaching conversations and independently derived answers, never serving code."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import random

from runtime import OBJECTS, ROOMS, identity


@dataclass(frozen=True, slots=True)
class Episode:
    key: str
    users: tuple[str, ...]
    answers: tuple[str, ...]
    kinds: tuple[str, ...]


def _move(obj: str, source: str, destination: str, form: int) -> str:
    forms = (f'The {obj} moved from the {source} to the {destination}.',
             f'The {obj} went to the {destination} from the {source}.',
             f'From the {source} the {obj} moved to the {destination}.')
    return forms[form]


def generate(seed: int, count: int, *, regime: str = 'ordinary', excluded: set[str] | None = None) -> list[Episode]:
    rng = random.Random(seed)
    seen = set() if excluded is None else set(excluded)
    episodes = []
    while len(episodes) < count:
        subject = rng.randrange(len(OBJECTS))
        other = (subject + rng.randrange(1, len(OBJECTS))) % len(OBJECTS)
        moves = []
        positions = {index: rng.randrange(len(ROOMS)) for index in range(len(OBJECTS))}
        for index in range(rng.randint(8, 10) if regime == 'long' else rng.randint(1, 3)):
            obj = subject if index == 0 else rng.choice((subject, other))
            source = positions[obj]
            destination = rng.choice([room for room in range(len(ROOMS)) if room != source])
            if regime not in ('combination',) and destination == obj:
                destination = next(room for room in range(len(ROOMS)) if room != source and room != obj)
            positions[obj] = destination
            moves.append((obj, source, destination))
        if regime == 'combination':
            source = positions[subject]
            if source == subject:
                continue
            moves.append((subject, source, subject))
            positions[subject] = subject
        relevant = [event for event in moves if event[0] == subject][-1]
        source, destination = relevant[1:]
        next_room = rng.choice([room for room in range(len(ROOMS)) if room != destination])
        if regime != 'combination' and next_room == subject:
            next_room = next(room for room in range(len(ROOMS)) if room not in (destination, subject))
        missing = rng.random() < 0.35 or other not in {event[0] for event in moves}
        known_other = rng.choice([index for index in range(len(OBJECTS)) if index not in {event[0] for event in moves}]) if missing else other
        fingerprint = identity(moves)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        form = 2 if regime == 'wording' else (rng.randrange(2) if regime == 'varied' else 0)
        text = ' '.join(_move(OBJECTS[obj], ROOMS[src], ROOMS[dst], form) for obj, src, dst in moves)
        obj, source_name, destination_name = OBJECTS[subject], ROOMS[source], ROOMS[destination]
        next_name, other_name = ROOMS[next_room], OBJECTS[known_other]
        question = f'Where is the {obj} now?' if form != 2 else f'Can you tell me where the {obj} is now?'
        users = (text + ' ' + question,
                 'Where was it before?' if form != 2 else 'Where did it come from?',
                 f'Now the {obj} moved from the {destination_name} to the {next_name}. Where is it now?',
                 f'Where is the {other_name} now?')
        last = (f'I do not know where the {other_name} is.' if missing
                else f'The {other_name} is in the {ROOMS[positions[known_other]]}.')
        answers = (f'The {obj} is in the {destination_name}.', f'It was in the {source_name}.',
                   f'It is in the {next_name}.', last)
        episodes.append(Episode(fingerprint, users, answers, ('current', 'pronoun_past', 'update', 'missing' if missing else 'switch')))
    return episodes


def examples(episodes: list[Episode]) -> list[dict]:
    pairs = []
    for episode in episodes:
        history = []
        for text, reply in zip(episode.users, episode.answers, strict=True):
            pairs.append({'history': list(history), 'text': text, 'reply': reply})
            history.extend([{'role': 'user', 'text': text}, {'role': 'assistant', 'text': reply}])
    return pairs


def records(episodes: list[Episode]) -> list[dict]:
    return [asdict(episode) for episode in episodes]
