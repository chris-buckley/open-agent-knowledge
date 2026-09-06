"""Score complete generated conversations without gold reply feedback."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

from runtime import predict
from task import Episode


def evaluate(record: dict[str, Any], episodes: list[Episode], *, erase_history: bool = False) -> dict[str, Any]:
    histories: list[list[dict[str, str]]] = [[] for _ in episodes]
    replies: list[list[str]] = [[] for _ in episodes]
    kinds: dict[str, list[bool]] = defaultdict(list)
    terminated = 0
    for turn in range(4):
        texts = [episode.users[turn] for episode in episodes]
        predictions = []
        for start in range(0, len(episodes), 32):
            selected_histories = histories[start:start + 32]
            if erase_history:
                selected_histories = [[] for _ in selected_histories]
            batch, distributions = predict(record, selected_histories, texts[start:start + 32])
            predictions.extend(batch)
            terminated += int((distributions.argmax(-1) == 2).any(-1).sum())
        for index, (episode, reply) in enumerate(zip(episodes, predictions, strict=True)):
            replies[index].append(reply)
            kinds[episode.kinds[turn]].append(reply == episode.answers[turn])
            histories[index].extend([{'role': 'user', 'text': texts[index]}, {'role': 'assistant', 'text': reply}])
    correct = [all(reply == expected for reply, expected in zip(row, episode.answers, strict=True))
               for episode, row in zip(episodes, replies, strict=True)]
    return {'reply_accuracy': sum(sum(values) for values in kinds.values()) / (4 * len(episodes)),
            'dialogue_accuracy': sum(correct) / len(episodes), 'terminated_fraction': terminated / (4 * len(episodes)),
            'per_kind': {name: {'correct': sum(values), 'count': len(values)} for name, values in kinds.items()},
            'dialogues': [{'key': episode.key, 'users': episode.users, 'expected': episode.answers, 'replies': row,
                          'kinds': episode.kinds} for episode, row in zip(episodes, replies, strict=True)]}


def score_summary(scores: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in scores.items() if key != 'dialogues'}
