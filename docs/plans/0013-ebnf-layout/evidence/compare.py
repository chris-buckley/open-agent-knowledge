"""Reproduce the layout-only comparison against the committed planning baseline."""

from __future__ import annotations

from collections import defaultdict, deque
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from build.authoring import validator_module
from build.checks.ebnf import _productions, _TOKEN, validate_ebnf
from build.checks.ebnf_fixtures import GROUPING_FINGERPRINTS, HEADINGS
from build.ebnf import _source_productions, grammar

BASE = '7e002d5e8a3632f9f48026c22a5ad0bbec68e77d'
EVIDENCE = Path(__file__).resolve().parent
DELIVERIES = (
    'outputs/oak.ebnf', 'skills/oak-authoring/references/oak.ebnf',
    'skills/oak-authoring/references/00-structure.oak.md', 'outputs/oak-authoring.oak.md',
)
SOURCES = (
    'build/AGENTS.md', 'build/ebnf.py', 'build/_ebnf_layout.py',
    'build/checks/__init__.py', 'build/checks/ebnf.py', 'build/checks/ebnf_fixtures.py',
)


def _git(*arguments: str) -> str:
    return subprocess.check_output(['git', *arguments], cwd=ROOT, text=True)


def _baseline(path: str) -> str:
    return _git('show', BASE + ':' + path)


def _placements(text: str) -> list[dict[str, object]]:
    offsets: dict[tuple[str, ...], deque[int]] = defaultdict(deque)
    tokens: list[str] = []
    start = 0
    for match in _TOKEN.finditer(text):
        if match.lastgroup in ('comment', 'space'):
            continue
        if not tokens:
            start = match.start()
        tokens.append(match[0])
        if match[0] == ';':
            offsets[tuple(tokens)].append(start)
            tokens = []
    headings = [(text.index('(* ' + title), title) for title in HEADINGS]
    placements: list[dict[str, object]] = []
    for record in _source_productions(('xml', 'markdown')):
        token_record = _productions(record.text)[0]
        offset = offsets[token_record].popleft()
        section = max((position, title) for position, title in headings if position < offset)[1]
        placements.append({'source': record.source, 'section': section, 'line': text.count('\n', 0, offset) + 1})
    return placements


def _product_fingerprint() -> str:
    files = set(_git('ls-files', '--cached', '--others', '--exclude-standard').splitlines())
    digest = sha256()
    for name in sorted(files):
        if name.startswith('docs/plans/0013-ebnf-layout/') or name == '.github/workflows/ebnf-work.yml':
            continue
        path = ROOT / name
        if path.is_file():
            digest.update(name.encode() + b'\0' + path.read_bytes() + b'\0')
    return digest.hexdigest()


def compare() -> dict[str, object]:
    validate_ebnf()
    baseline = json.loads((EVIDENCE / 'baseline.json').read_text())
    sources = sorted((r.source, list(_productions(r.text)[0])) for r in _source_productions(('xml', 'markdown')))
    frozen = _productions((EVIDENCE / 'baseline.ebnf').read_text(encoding='utf-8'))
    observed = sorted((r['source'], list(frozen[r['index']])) for r in baseline['productions'])
    if sources != observed:
        raise RuntimeError('Source-qualified baseline comparison failed')
    old, current = _baseline('outputs/oak.ebnf'), grammar()
    if old != (EVIDENCE / 'baseline.ebnf').read_text():
        raise RuntimeError('Frozen baseline differs from committed grammar')
    for name in DELIVERIES[2:]:
        if _baseline(name).replace(old.rstrip('\n'), current.rstrip('\n'), 1) != (ROOT / name).read_text():
            raise RuntimeError('Non-grammar bytes changed: ' + name)
    _check_scope()
    validator = validator_module()
    if validator.package_digest(ROOT / 'oak') != validator.SOURCE_SHA256:
        raise RuntimeError('Validator package fingerprint changed')
    variants = _variants()
    return {
        'baseline_commit': BASE,
        'checkout_head': _git('rev-parse', 'HEAD').strip(),
        'subject': 'Working tree at the recorded checkout head; product fingerprint excludes this plan record.',
        'product_fingerprint': _product_fingerprint(),
        'source_occurrences': len(sources),
        'surface_occurrences': sum(source.startswith('surface.') for source, _ in sources),
        'source_content_preserved': True,
        'non_grammar_embedding_bytes_preserved': True,
        'unrelated_paths_unchanged': True,
        'validator_revision': validator.REVISION,
        'validator_source_sha256': validator.SOURCE_SHA256,
        'variants': variants,
        'deliveries': {name: {'bytes': len((ROOT / name).read_bytes()),
                              'sha256': sha256((ROOT / name).read_bytes()).hexdigest()} for name in DELIVERIES},
        'skill_entry_bytes': len((ROOT / 'skills/oak-authoring/SKILL.md').read_bytes()),
        'placement_inventory': _placements(current),
    }


def _check_scope() -> None:
    changed = set(_git('diff', BASE, '--name-only').splitlines())
    changed.update(_git('ls-files', '--others', '--exclude-standard').splitlines())
    unexpected = changed - set(SOURCES) - set(DELIVERIES)
    unexpected = {name for name in unexpected if not name.startswith('docs/plans/0013-ebnf-layout/')}
    if unexpected:
        raise RuntimeError('Unexpected changed paths: ' + ', '.join(sorted(unexpected)))


def _variants() -> list[dict[str, object]]:
    variants = []
    for grouping in GROUPING_FINGERPRINTS:
        text = grammar(grouping)
        variants.append({'groupings': grouping, 'sha256': sha256(text.encode()).hexdigest(),
                         'bytes': len(text.encode()), 'productions': len(_productions(text))})
    return variants


if __name__ == '__main__':
    print(json.dumps(compare(), indent=2) + '\n', end='')
