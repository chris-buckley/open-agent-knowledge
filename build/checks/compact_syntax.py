"""Compact syntax conformance: specimens, lexical errors, layout, and contracts."""

from __future__ import annotations

from itertools import permutations
import json
import random

from pydantic import ValidationError

from build.checks.compact_fixtures import SPECIMENS, binding, call, compare, literal, put, read, specimen_node
from build.checks.fixtures import normalized
from oak import (ACT, Act, All, Any, Assert, BindingValue, Call, Compare, ConstantValue,
                 Emit, Fail, If, LiteralValue, Node, Not, Set, Trigger, While, parse, render, resolve)
from oak.parse.errors import OakParseError, ParseError
from oak.parse.fragments import parse_fragment
from oak.render.oak.expressions import ListText, expression_lines
from oak.render.oak.processes import condition_text, step_lines
from oak.render.oak.styles import styled_node
from oak.render.oak.triggers import trigger_body
from oak.surface.syntax import CANONICAL_WIDTH


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejects(operation, *, code: str | None = None, line: int | None = None, path: str | None = None) -> None:
    """Reject only validation failures, not accidental implementation exceptions."""
    try:
        operation()
    except (ParseError, OakParseError) as error:
        failures = error.failures if isinstance(error, OakParseError) else (error.failure,)
        require(code is None or code in {item.code for item in failures}, f"wrong rejection: {error}")
        require(line is None or line in {item.line for item in failures}, f"wrong source line: {error}")
        require(path is None or any(path in item.path for item in failures), f"wrong source path: {error}")
    except ValidationError as error:
        require(line is None and path is None, f"lost source location: {error}")
        require(code is None or code in {item['type'] for item in error.errors()}, f"wrong model rejection: {error}")
    else:
        raise RuntimeError(f"invalid compact syntax was accepted (expected {code or 'a validation error'})")


def validate_compact_specimens() -> None:
    """S01-S12: exact reviewed spelling -> expected contracted Node, not just text."""
    for specimen in SPECIMENS:
        expected = specimen.node()
        parsed = parse(specimen.text())
        require(normalized(parsed) == normalized(expected), f"{specimen.identifier}: parsed meaning differs")
        resolve(parsed)
        for grouping in ("xml", "markdown"):
            for style in ("authored", "asd-ste100-9"):
                text = render(parsed, grouping=grouping, style=style)
                rebuilt = parse(text, grouping=grouping)
                require(normalized(rebuilt) == normalized(styled_node(expected, style)), f"{specimen.identifier}: {grouping}/{style} changed meaning")
                require(render(rebuilt, grouping=grouping, style=style) == text, f"{specimen.identifier}: noncanonical round trip")


def validate_compact_lexing() -> None:
    """C02-C03: punctuation belongs to its literal or enclosing list."""
    values = (
        'a equals b, (c)', 'a is less than b, (hold)', 'x=y: #tag; LIMIT 9:',
        'quote " here and backslash \\ there', '$state.ready', 'process.publish',
        'ALL(NOT(ANY(...)))', '</triggers>', '~~~', ["x,y", "(z)", {"ready": True}],
        {"items": ["x,y", "(z)"], "punctuation": "):=(,", "value": None},
    )
    for value in values:
        encoded = json.dumps(value, ensure_ascii=False)
        expected = Compare(left=literal(value), operator="equals", right=literal(value))
        parsed = parse_fragment(Compare, f"{encoded} equals {encoded}")
        require(parsed == expected, f"quoted operator or JSON punctuation changed {value!r}")
        for prefix, model in (("CALL process.accept", Call), ("ACT Inspect <VALUE>.", Act), ("EMIT interface.result", Emit)):
            parsed = parse_fragment(model, prefix + ' (\n  VALUE=' + encoded + ',\n)')
            actual = parsed.bindings if isinstance(parsed, Emit) else parsed.inputs
            require(actual == [binding("VALUE", literal(value))], f"binding literal changed: {prefix}")
        parsed_trigger = parse_fragment(Trigger, f'quoted(event="Quoted.", process=process.accept, seed=(VALUE={encoded},),)')
        require(parsed_trigger.seed == [binding("VALUE", literal(value))], "trigger seed changed JSON")
    for operator in ("equals", "does not equal", "is less than", "is at most", "is greater than", "is at least"):
        text = f'"a {operator} b" {operator} "c {operator} d"'
        condition = parse_fragment(Compare, text)
        require(condition.left.value == f"a {operator} b" and condition.right.value == f"c {operator} d", "operator split a quoted operand")

    for target in ("$state.ready", "$constant.approval", "$../shared.oak.md#constant.approval", "$TARGET"):
        value = parse_fragment(LiteralValue, target)
        require(not isinstance(value, LiteralValue), "typed read became literal")
        require(isinstance(parse_fragment(LiteralValue, json.dumps(target)), LiteralValue), "quoted reference was dereferenced")
    structured = parse_fragment(Call, 'CALL process.accept (VALUE={\n  "items": ["x,y", {"p": "(z)"}]\n},)')
    require(structured.inputs[0].value.value == {"items": ["x,y", {"p": "(z)"}]}, "nested JSON continuation failed")
    prose = 'ACT TOOL "tool,(x)=y": Preserve (notes), #tag, and <VALUE> in <RESULT>. (VALUE="literal ) (BAD=not syntax",) -> RESULT'
    action = parse_fragment(Act, prose)
    require(action.tool == 'tool,(x)=y' and action.instruction == 'Preserve (notes), #tag, and <VALUE> in <RESULT>.', "ACT tool or prose changed")
    require(action.inputs[0].value.value == 'literal ) (BAD=not syntax', "ACT selected a suffix inside a string")
    require(parse_fragment(Act, '\n'.join(step_lines(action))) == action, "ACT punctuation round trip failed")

    invalid_values = ('$', '$ state.ready', '$\nstate.ready', '"bad\\q"', '"unclosed', '[1,]', '{"a": 1,}',
                      '[1,,2]', '{"a": [1,2)}', "'single'", 'undefined', 'null trailing', '$interface.input.X',
                      '$../other.oak.md#state.ready', '$state.ready()', 'NaN', 'Infinity')
    for value in invalid_values:
        rejects(lambda value=value: parse_fragment(Call, f'CALL process.accept (VALUE={value})'))
    invalid_conditions = (
        'ALL()', 'ANY()', 'ALL($state.ready equals true)', 'ANY($state.ready equals true)',
        'NOT()', 'NOT($state.ready equals true, $state.approved equals true)',
        'ALL($state.ready equals true,, $state.approved equals true)',
        'ALL(, $state.ready equals true)', 'ALL($state.ready equals true, $state.approved equals true]',
        'NOT($state.ready equals true', '($state.ready equals true)', '$state.ready', 'true',
        '$state.ready and $state.approved', '$state.ready equals true or false',
        '$state.ready equals true equals false', '$state.ready equals true # comment',
        'all($state.ready equals true, $state.approved equals true)',
        '$state.ready equals true\n$state.approved equals true',
    )
    for text in invalid_conditions:
        rejects(lambda text=text: parse_fragment(Compare, text))
    for text in ('CALL process.accept (A=1,, B=2)', 'CALL process.accept (A=1, A=2)',
                 'CALL process.accept (1)', 'CALL process.accept (A=1) junk',
                 'CALL process.accept (A=1) -> A,', 'CALL process.accept (A=1) -> A -> B'):
        rejects(lambda text=text: parse_fragment(Call, text))
    # The diagnostic points to the original physical binding line and field.
    text = 'broken(\n  event="Broken.",\n  process=process.accept,\n  seed=(\n    VALUE="bad\\q",\n  ),\n)'
    rejects(lambda: parse_fragment(Trigger, text, line=20), code="invalid_json", line=24, path="broken.seed.VALUE")
    text = 'ACT Read <VALUE>. (\n  VALUE="bad\\q",\n)'
    rejects(lambda: parse_fragment(Act, text, path="processes.inspect", line=40), code="invalid_json", line=41, path="processes.inspect.inputs.VALUE")


def validate_compact_control() -> None:
    """C03-C04: nested expressions cannot steal suites or ELSE/MESSAGE metadata."""
    nested = SPECIMENS[5]
    with_blanks = nested.process_text.replace('\n  ELSE:', '\n\n  ELSE:').replace('\nELSE:', '\n\nELSE:')
    require(parse_fragment(If, with_blanks) == nested.steps[0], "blank lines changed ELSE association")
    loops = (
        'WHILE $state.note equals " LIMIT 99:" LIMIT 1:\n  CALL process.publish ()',
        'WHILE ALL(\n$state.ready equals true,\nNOT(\n$state.blocked equals true,\n),\n) LIMIT 10:\n  CALL process.publish ()',
    )
    for text in loops:
        step = parse_fragment(While, text)
        require(parse_fragment(While, '\n'.join(step_lines(step))) == step, "WHILE continuation did not round trip")
    assertion = 'ASSERT ALL(\n  $state.ready equals true,\n  NOT($state.blocked equals true,),\n)\n  MESSAGE "ready (now), LIMIT: true"'
    step = parse_fragment(Assert, assertion)
    require(step.message == "ready (now), LIMIT: true", "assertion metadata was treated as a suite")
    require(parse_fragment(Assert, '\n'.join(step_lines(step))) == step, "ASSERT did not round trip")

    # Explicit old-surface rejection fixtures are the only live tests of those tokens.
    invalid_steps = (
        'IF: $state.ready equals true\n  CALL process.publish ()',
        'IF:\n  ALL:\n    $state.ready equals true\n    $state.approved equals true\n  THEN:\n    CALL process.publish ()',
        'IF $state.ready equals true:\n  THEN:\n    CALL process.publish ()',
        'IF ALL:\n  $state.ready equals true\n  $state.approved equals true',
        'ELSE:\n  CALL process.publish ()', 'IF $state.ready equals true:',
        'IF $state.ready equals true:\n  CALL process.publish ()\nELSE:',
        'IF $state.ready equals true:\n CALL process.publish ()',
        'IF $state.ready equals true:\n    CALL process.publish ()',
        'IF $state.ready equals true:\n\tCALL process.publish ()',
        'IF $state.ready equals true:\n  CALL process.publish ()\n  ELSE:\n    CALL process.review ()',
        'IF $state.ready equals true:\n  CALL process.publish ()\nELSE:\n  CALL process.review ()\nELSE:\n  CALL process.review ()',
        'IF $state.ready equals true:\n  CALL process.publish ()\nCALL process.review ()\nELSE:\n  CALL process.review ()',
        'IF $state.ready equals true: CALL process.publish ()',
        'IF $state.ready equals true:\n  CALL process.publish ()\nELSE IF $state.approved equals true:\n  CALL process.review ()',
        'WHILE LIMIT 2:\n  ALL:\n    $state.ready equals true\n    $state.approved equals true\n  THEN:\n    CALL process.publish ()',
        'WHILE $state.ready equals true LIMIT 2:\n  CALL process.publish ()\nELSE:\n  CALL process.review ()',
        'ASSERT:\n  ALL:\n    $state.ready equals true\n    $state.approved equals true',
        'ASSERT $state.ready equals true\n  CALL process.publish ()',
        'ASSERT $state.ready equals true\nMESSAGE "wrong level"',
        'ASSERT $state.ready equals true\n    MESSAGE "wrong level"',
        'ASSERT $state.ready equals true\n  MESSAGE "first"\n  MESSAGE "second"',
        'IF ALL(\n\t$state.ready equals true, $state.approved equals true):\n  CALL process.publish ()',
    )
    for text in invalid_steps:
        rejects(lambda text=text: parse_fragment(If, text))
    for limit in ('', '0', '-1', '1.5', 'true', '$LIMIT', '"2"', '0x10', '+2', '２', '1e2'):
        rejects(lambda limit=limit: parse_fragment(While, f'WHILE $state.ready equals true LIMIT {limit}:\n  CALL process.publish ()'))
    rejects(lambda: parse_fragment(While, 'WHILE $state.ready equals true:\n  CALL process.publish ()'))

    # Deterministic trees exercise long recursive forms without normalizing the AST.
    randomizer = random.Random(6006)
    def condition(depth: int):
        if depth == 0 or randomizer.randrange(3) == 0:
            return compare(randomizer.choice(('ready', 'approved', 'blocked')), bool(randomizer.randrange(2)))
        model = randomizer.choice((All, Any, Not))
        if model is Not:
            return Not(condition=condition(depth - 1))
        return model(conditions=[condition(depth - 1) for _ in range(randomizer.randrange(2, 5))])
    for _ in range(80):
        expected = condition(5)
        text = condition_text(expected)
        require(parse_fragment(type(expected), text) == expected, "recursive condition tree changed")


def validate_compact_triggers() -> None:
    """C06: field permutations do not change routing, seed order, or validation."""
    fields = ('event="Run."', 'source=interface.authoring-input', 'guard=$state.ready equals $constant.approval', 'process=process.author-document')
    canonical = None
    for order in permutations(fields):
        parsed = parse_fragment(Trigger, 'request(' + ', '.join(order) + ',)')
        node = specimen_node([put('result', 'unused')], parsed)
        resolve(node)
        text = trigger_body(parsed)
        canonical = text if canonical is None else canonical
        require(text == canonical, "outer field order affected canonical trigger")
    seeded = parse_fragment(Trigger, 'request(seed=(TEXT="process.publish", DATA={"x": [1,2]},), process=process.inspect, event="Inspect.")')
    require([item.placeholder for item in seeded.seed] == ['TEXT', 'DATA'], "seeds were sorted")
    require(isinstance(seeded.seed[0].value, LiteralValue), "quoted target became a reference")
    require(parse_fragment(Trigger, trigger_body(seeded)) == seeded, "seed canonical form changed meaning")
    require('guard=' not in trigger_body(seeded) and 'source=' not in trigger_body(seeded), "absent optionals were rendered")
    pair = Node(processes=[SPECIMENS[0].node().processes[1]], state=[SPECIMENS[0].node().state[-1]], triggers=[
        Trigger(id='first', event='First.', process='process.publish'), Trigger(id='second', event='Second.', process='process.publish'),
    ])
    text = render(pair)
    require(')\nsecond(' in text and ')\n\nsecond(' not in text, "trigger separator is not one newline")
    require(normalized(parse(text)) == normalized(pair), "adjacent declarations changed meaning")

    invalid = (
        't(event="Run.")', 't(process=process.run)', 't()',
        't("Run.", process=process.run)', 't(event="Run.", process=process.run, extra=1)',
        't(event="Run.", event="Again.", process=process.run)',
        't(event="Run.", process=process.run, process=process.run)',
        't(event="Run.", process=process.run, guard=true)',
        't(event="Run.", process=process.run, guard=false)',
        't(event="Run.", process=process.run, seed=())',
        't(event="Run.", source=interface.authoring-input, process=process.author-document, seed=())',
        't(event="Run.", source=interface.authoring-input, process=process.author-document, seed=(SOURCE="x"))',
        't(event="Run.", process=process.run, seed=(X=1, X=2))',
        't(event="Run.", process=process.run, seed=(X=$LOCAL))',
        't(event="Run.", process=process.run, guard=$LOCAL equals true)',
        't(event="Run.", process=process.run, guard=1 equals 1)',
        't(event="Run.", process=process.run, guard=$constant.approval equals true)',
        't(event="Run.", process="process.run")', 't(event="Run.", process=interface.authoring-input)',
        't(event="Run.", source="interface.authoring-input", process=process.run)',
        't(event="Run.", source=../other.oak.md#interface.input, process=process.run)',
        't(event="Run.", source=process.run, process=process.run)',
        't(event="", process=process.run)', 't(event="   ", process=process.run)',
        't(event="line\\nline", process=process.run)', 't(event="line\\rline", process=process.run)',
        't(event=1, process=process.run)', 't(event="Run.", process=process.run,,)',
        't(event="Run.", process=process.run', 't(event="Run.", process=process.run) trailing',
        'trigger.t.event := "Run."\ntrigger.t.process := process.run',
        '<trigger id="t">\nWHEN: Run.\nTHEN: process.run ()\n</trigger>',
        't(event="Run.", process=process.run)\nt(event="Again.", process=process.run)',
    )
    for text in invalid:
        rejects(lambda text=text: parse_fragment(Trigger, text))
    # Syntactically well-typed targets still need document-level contracts.
    for fields in (
        'event="Run.", source=interface.authored-output, process=process.author-document',
        'event="Run.", source=interface.authoring-input, process=process.grow-balance',
        'event="Run.", source=interface.authoring-input, process=process.publish',
        'event="Run.", process=process.grow-balance',
        'event="Run.", process=process.grow-balance, seed=(WRONG=2)',
        'event="Run.", process=process.publish, seed=(TARGET=2)',
        'event="Run.", process=process.unknown',
    ):
        trigger = parse_fragment(Trigger, 'bad(' + fields + ')')
        rejects(lambda trigger=trigger: specimen_node([put('result', 'unused')], trigger))
    # Unique entry IDs remain document-wide, not one namespace per section.
    rejects(lambda: specimen_node([put('result', 'unused')], Trigger(id='ready', event='Run.', process='process.publish')))


def validate_compact_layout() -> None:
    """C08: the formatter counts code points and the complete emitted header."""
    for total in (99, 100, 101):
        head = 'CALL process.accept '
        base = len(head + '(VALUE="") -> RESULT')
        step = Call(process='process.accept', inputs=[binding('VALUE', literal('é' * (total - base)))], outputs=['RESULT'])
        text = '\n'.join(step_lines(step))
        require(('\n' not in text) == (total <= CANONICAL_WIDTH), f"wrong width decision at {total}")
        require(parse_fragment(Call, text) == step, "width wrapping changed the step")
        if total <= CANONICAL_WIDTH:
            require(len(text) == total and len(text.encode()) > total, "width counted bytes instead of code points")
        else:
            require(text.endswith(',\n) -> RESULT'), "expanded list lost trailing comma or suffix")
    # Indentation and LIMIT/colon participate in the same width decision.
    for indent in (0, 2, 6):
        for suffix in (':', ' LIMIT 10:', ' -> RESULT'):
            item = 'x' * (100 - indent - len('IF G()') - len(suffix))
            flat = expression_lines(ListText('G', (item,)), indent, prefix='IF ', suffix=suffix)
            require(len(flat) == 1 and len(flat[0]) == 100, "complete header width was not counted")
            expanded = expression_lines(ListText('G', (item + 'x',)), indent, prefix='IF ', suffix=suffix)
            require(len(expanded) == 3 and expanded[-1] == ' ' * indent + ')' + suffix, "closer is not owner-aligned")
    nested = All(conditions=[compare('ready'), Not(condition=Any(conditions=[
        compare('note', 'long, atomic (text): ' * 10), compare('approved'),
    ]))])
    text = condition_text(nested)
    require('\n  NOT(\n    ANY(' in text and len(max(text.splitlines(), key=len)) > 100, "nested expansion or atomic exception failed")
    require(parse_fragment(All, text) == nested, "nested expansion changed tree")
    long_prose = ACT('Preserve ' + 'verbatim (text), ' * 15 + '<VALUE>.', inputs=[binding('VALUE', literal('x'))])
    actual = '\n'.join(step_lines(long_prose))
    require(parse_fragment(Act, actual) == long_prose and long_prose.instruction in actual, "formatter rewrote ACT prose")


__all__ = [
    'validate_compact_specimens', 'validate_compact_lexing', 'validate_compact_control',
    'validate_compact_triggers', 'validate_compact_layout',
]
