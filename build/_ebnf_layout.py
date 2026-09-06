"""Format outer OAK EBNF boundaries without interpreting opaque bodies."""

from __future__ import annotations

from collections.abc import Sequence
import re

_WIDTH = 100  # Reference layout, not authored OAK.
_QUOTED = re.compile(r'"(?:\\.|[^"\\])*"')
_BOUNDARY = re.compile(r'"(?:\\.|[^"\\])*"|[()\[\]{},|\"]')
_CLOSERS = {')': '(', ']': '[', '}': '{'}


def _outer_parts(expression: str, separator: str) -> list[str]:
    """Split only unquoted separators outside balanced grammar groups."""
    parts: list[str] = []
    stack: list[str] = []
    start = 0
    for match in _BOUNDARY.finditer(expression):
        token = match[0]
        _update_groups(stack, token)
        if token == separator and not stack:
            parts.append(expression[start:match.start()].strip())
            start = match.end()
    if stack:
        raise ValueError('EBNF group is not closed')
    parts.append(expression[start:].strip())
    return parts


def _update_groups(stack: list[str], token: str) -> None:
    if token == '"':
        raise ValueError('EBNF terminal is not closed')
    if token in '([{':
        stack.append(token)
    elif token in _CLOSERS:
        if not stack or stack.pop() != _CLOSERS[token]:
            raise ValueError('EBNF group delimiters do not match')


def _sequence_lines(parts: Sequence[str]) -> list[str]:
    """Pack indivisible outer components into bounded continuation lines."""
    lines: list[str] = []
    line = '    '
    for index, part in enumerate(parts):
        chunk = part + (',' if index + 1 < len(parts) else ' ;')
        candidate = line + (' ' if line.strip() else '') + chunk
        if line.strip() and len(candidate) > _WIDTH:
            lines.append(line)
            line = '    ' + chunk
        else:
            line = candidate
    lines.append(line)
    return lines


def _trigger_lines(expression: str) -> list[str]:
    parts = _outer_parts(expression, ',')
    if len(parts) != 7:
        raise ValueError('trigger layout requires seven outer components')
    return [
        '    ' + ', '.join(parts[:2]) + ',',
        '    ' + ', '.join(parts[2:5]) + ',',
        '    ' + ', '.join(parts[5:]) + ' ;',
    ]


def _field_columns(alternatives: Sequence[str]) -> list[str]:
    fields = [_outer_parts(alternative, ',') for alternative in alternatives]
    width = max(len(field[0]) for field in fields)
    return [field[0] + ',' + ' ' * (width - len(field[0]) + 1) + ', '.join(field[1:])
            for field in fields]


def _format_production(production: str, alignment: int = 0) -> str:
    """Preserve source tokens; only outer whitespace is presentational."""
    name, marker, body = production.partition(' = ')
    if not marker or not body.endswith(' ;'):
        raise ValueError('EBNF source needs a named production and final semicolon')
    prefix = name.ljust(alignment) + ' = '
    # Do not lex character classes or escaped-question-mark surface templates.
    if '?' in _QUOTED.sub('', body):
        return prefix + body
    expression = body[:-2].rstrip()
    if name == 'trigger_declaration':
        return name + ' =\n' + '\n'.join(_trigger_lines(expression))
    if len(prefix + body) <= _WIDTH:
        return prefix + body
    alternatives = _outer_parts(expression, '|')
    if len(alternatives) > 1:
        if name == 'trigger_field':
            alternatives = _field_columns(alternatives)
        lines = [('      ' if index == 0 else '    | ') + alternative
                 for index, alternative in enumerate(alternatives)]
        lines[-1] += ' ;'
    else:
        lines = _sequence_lines(_outer_parts(expression, ','))
    return name + ' =\n' + '\n'.join(lines)


def _format_group(productions: Sequence[str], alignment: int = 0) -> str:
    return '\n'.join(_format_production(production, alignment) for production in productions)
