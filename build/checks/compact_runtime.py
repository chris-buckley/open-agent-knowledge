"""Behaviour-preserving execution checks over the newly rendered syntax."""

from __future__ import annotations

from copy import deepcopy

from pydantic import ValidationError

from build.checks.compact_fixtures import SPECIMENS, binding, call, compare, literal, put, read, specimen_node, below_target
from oak import (ACT, Act, All, Any, Arrival, BindingValue, Call, Compare, Constant, ConstantValue,
                 Emit, ExecutionError, Fail, If, Interface, Node, Not, Process, Schema,
                 Set, ToolContract, Trigger, Type, While, execute, parse, render, resolve, where)
from oak.resolve.errors import ResolutionError


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def expect_error(operation, code: str) -> None:
    try:
        operation()
    except ExecutionError as error:
        require(error.code == code, f"expected {code}, got {error}")
    except ValidationError as error:
        require(code in {item['type'] for item in error.errors()}, f"expected {code}, got {error}")
    except ResolutionError as error:
        require(code in {item.code for item in error.failures}, f"expected {code}, got {error}")
    else:
        raise RuntimeError(f"expected {code}")


def initial_state(node: Node, **updates: object) -> dict:
    result = {"state." + entry.id: deepcopy(entry.value) for entry in node.state}
    result.update({"state." + key.replace('_', '-'): value for key, value in updates.items()})
    return result


def round_trip(node: Node) -> Node:
    return parse(render(node))


def validate_compact_short_circuit() -> None:
    """The skipped right operand would fail; eager evaluation is observable."""
    bad = compare('status', 1, 'less_than')
    cases = (
        (All(conditions=[compare('ready', False), bad]), 'reviewed'),
        (Any(conditions=[compare('ready'), bad]), 'published'),
        (Not(condition=All(conditions=[compare('ready', False), bad])), 'published'),
        (All(conditions=[Any(conditions=[compare('ready'), bad]), Not(condition=compare('blocked'))]), 'published'),
    )
    for condition, expected in cases:
        node = round_trip(specimen_node([If(condition=condition, then=[call('publish')], otherwise=[call('review')])]))
        state = initial_state(node)
        result = execute(node, Arrival(event='Run the specimen.'), state)
        require(result.state['state.result'] == expected and state['state.result'] == '', 'short-circuit or caller isolation changed')
    for condition in (All(conditions=[bad, compare('ready', False)]), Any(conditions=[bad, compare('ready')]), Not(condition=bad)):
        node = round_trip(specimen_node([If(condition=condition, then=[call('publish')])]))
        expect_error(lambda: execute(node, Arrival(event='Run the specimen.'), initial_state(node)), 'ordered_comparison_type_mismatch')
    for left, right, equal in ((True, 1, False), (1, 1.0, True), ([True], [1], False), ({'x': [1]}, {'x': [1.0]}, True)):
        condition = Compare(left=read('note'), operator='equals', right=literal(right))
        node = round_trip(specimen_node([If(condition=condition, then=[call('publish')], otherwise=[call('review')])]))
        result = execute(node, Arrival(event='Run the specimen.'), initial_state(node, note=left))
        require(result.state['state.result'] == ('published' if equal else 'reviewed'), 'strict JSON equality changed')


def validate_compact_loop_bounds() -> None:
    """Zero, early, exact-bound and exhausted loops retain state/emission behaviour."""
    for compound in (False, True):
        condition = All(conditions=[below_target(), Not(condition=compare('blocked'))]) if compound else below_target()
        for start, target, limit, expected in ((2, 2, 2, []), (0, 2, 3, [1, 2]), (0, 2, 2, [1, 2]), (0, 3, 2, None)):
            node = round_trip(specimen_node([While(condition=condition, limit=limit, steps=[call('grow-once')])], growth=True))
            state = initial_state(node, balance=start, reflection_target=target)
            untouched = deepcopy(state)
            effects: list[int] = []
            def grow(_step, values):
                effects.append(values['BALANCE'])
                return {'NEXT': values['BALANCE'] + 1}
            if expected is None:
                expect_error(lambda: execute(node, Arrival(event='Run the specimen.'), state, act=grow), 'while_limit_reached')
                require(effects == [0, 1], 'loop failed before its final allowed body or pretended to undo host effects')
            else:
                result = execute(node, Arrival(event='Run the specimen.'), state, act=grow)
                require([item.values['NEXT'] for item in result.emissions] == expected, 'iteration emission order changed')
                require(result.state['state.balance'] == target, 'loop did not terminate at the expected balance')
                require(effects == list(range(start, target)), 'iteration order or scope changed')
            require(state == untouched, 'a loop mutated the caller state, including on failure')


def validate_compact_routing() -> None:
    """Complete source forwarding, guards, exact events, seeds and one-arrival selection."""
    payload = {'SOURCE': 'A request, (quoted): x=y; #tag.', 'VALIDATE': True}
    for specimen in SPECIMENS[7:9]:
        node = round_trip(specimen.node())
        state = initial_state(node)
        forwarded = execute(node, Arrival(interface='interface.authoring-input', values=payload), state)
        require(forwarded.emissions[0].values == payload, 'source did not forward its complete instance')
        require(payload == {'SOURCE': 'A request, (quoted): x=y; #tag.', 'VALIDATE': True}, 'source values were mutated')
        idle = execute(node, Arrival(event=specimen.trigger.event), state)
        require(idle.process is None and not idle.emissions, 'source-backed event text was treated as another selector')
        expect_error(lambda: execute(node, Arrival(interface='interface.authoring-input', values={'SOURCE': 'incomplete'}), state), 'invalid_interface_binding')
    guarded = round_trip(SPECIMENS[8].node())
    idle = execute(guarded, Arrival(interface='interface.authoring-input', values=payload), initial_state(guarded, approved=False))
    require(idle.process is None and not idle.emissions, 'false guard executed')
    # A bad comparison is not evaluated before a matching occurrence exists.
    raw = SPECIMENS[7].node().model_dump(by_alias=True)
    raw['triggers'][0]['guard'] = compare('status', 1, 'less_than').model_dump()
    guarded = round_trip(Node.model_validate(raw))
    require(execute(guarded, Arrival(event='Not a matching source.'), initial_state(guarded)).process is None, 'unmatched guard evaluated')
    expect_error(lambda: execute(guarded, Arrival(interface='interface.authoring-input', values=payload), initial_state(guarded)), 'ordered_comparison_type_mismatch')

    message = round_trip(SPECIMENS[10].node())
    # S11 is lossless syntax, not permission to bypass the selected schema.
    # Existing NonEmpty accepts text/lists, not objects; preserve that rejection.
    expect_error(lambda: execute(message, Arrival(event=message.triggers[0].event), initial_state(message)), 'invalid_process_input')
    raw = message.model_dump(by_alias=True)
    raw['triggers'][0]['seed'][1]['value']['value'] = ['x,y', '(z)']
    accepted_message = round_trip(Node.model_validate(raw))
    result = execute(accepted_message, Arrival(event=accepted_message.triggers[0].event), initial_state(accepted_message))
    require(result.emissions[0].values == {'TEXT': 'a equals b, (c)', 'DATA': ['x,y', '(z)']}, 'event seeds changed literal values')
    for changed in ('Received "go, now" (draft): x=y; #tag', 'received "go, now" (draft): x=y; #tag.'):
        require(execute(message, Arrival(event=changed), initial_state(message)).process is None, 'event match stopped being exact')

    # A state update cannot turn an internal step into a second outside arrival.
    node = specimen_node([put('result', 'phase-two')])
    raw = node.model_dump(by_alias=True)
    raw['triggers'] = [trigger.model_dump() for trigger in (
        Trigger(id='first-arrival', event='Advance.', guard=compare('result', ''), process='process.run'),
        Trigger(id='next-arrival', event='Advance.', guard=compare('result', 'phase-two'), process='process.review'),
    )]
    node = round_trip(Node.model_validate(raw))
    first = execute(node, Arrival(event='Advance.'), initial_state(node))
    require(first.state['state.result'] == 'phase-two', 'an internal state write fired another trigger')
    second = execute(node, Arrival(event='Advance.'), first.state)
    require(second.state['state.result'] == 'reviewed', 'the next actual arrival did not recheck guards')
    raw['triggers'] = [trigger.model_dump() for trigger in (
        Trigger(id='any-route', event='Advance.', guard=Any(conditions=[compare('ready'), compare('approved')]), process='process.run'),
        Trigger(id='other-route', event='Advance.', guard=All(conditions=[compare('ready', False), compare('approved', False)]), process='process.review'),
    )]
    expect_error(lambda: Node.model_validate(raw), 'overlapping_trigger_guards')
    # Bypass construction deliberately to exercise the executor's defensive ambiguity guard.
    unsafe = node.model_copy(update={'triggers': [
        Trigger(id='unsafe-first', event='Ambiguous.', process='process.run'),
        Trigger(id='unsafe-second', event='Ambiguous.', process='process.review'),
    ]})
    expect_error(lambda: execute(unsafe, Arrival(event='Ambiguous.'), initial_state(unsafe)), 'ambiguous_trigger_match')


def validate_compact_frames() -> None:
    """Typed calls, exact tool identity, child scopes, staged writes and emissions."""
    # Construct the child output contract before validating its caller.
    raw = specimen_node([put('result', 'unused')]).model_dump(by_alias=True)
    raw['processes'][0]['steps'] = [step.model_dump() for step in (
        Call(process='process.grow-once', outputs=['NEXT']),
        Set(state='state.result', value=BindingValue(binding='NEXT')),
        Emit(interface='interface.progress-output'),
    )]
    raw['processes'][4]['output'] = 'schema.progress'
    raw['processes'][5]['steps'][0]['steps'][0]['outputs'] = ['NEXT']
    raw['processes'][4]['steps'][0]['tool'] = 'counter,(next)=exact'
    node = round_trip(Node.model_validate(raw))
    effects = []
    def tool(step, values):
        effects.append((step.tool, step.instruction, deepcopy(values)))
        return {'NEXT': values['BALANCE'] + 1}
    registry = {'counter,(next)=exact': ToolContract(tool, frozenset({'BALANCE'}), frozenset({'NEXT'}))}
    result = execute(node, Arrival(event='Run the specimen.'), initial_state(node), tools=registry)
    require(result.state['state.result'] == 1 and [item.values['NEXT'] for item in result.emissions] == [1, 1], 'CALL promotion or emission order changed')
    require(effects == [('counter,(next)=exact', 'Grow <BALANCE> into <NEXT>.', {'BALANCE': 0})], 'tool name, prose, or input changed')
    bad_registry = {'counter,(next)=exact': ToolContract(lambda *_: {'NEXT': 'not a number'}, frozenset({'BALANCE'}), frozenset({'NEXT'}))}
    expect_error(lambda: execute(node, Arrival(event='Run the specimen.'), initial_state(node), tools=bad_registry), 'invalid_emission')
    # A branch-local result cannot escape just because its source uses fewer indents.
    def invalid_scope():
        return specimen_node([
            If(condition=compare('ready'), then=[ACT('Produce <LOCAL>.', outputs=['LOCAL'])]),
            Set(state='state.result', value=BindingValue(binding='LOCAL')),
        ])
    expect_error(invalid_scope, 'unbound_process_binding')
    failed = round_trip(specimen_node([
        put('result', 'staged'), Emit(interface='interface.progress-output', bindings=[binding('NEXT', literal(5))]),
        Fail(message='Stop after staging.'),
    ]))
    state = initial_state(failed)
    expect_error(lambda: execute(failed, Arrival(event='Run the specimen.'), state), 'process_failed')
    require(state == initial_state(failed), 'failure committed staged state')


def validate_compact_relative_targets() -> None:
    """Relative calls return declared values; the caller emits at its local boundary."""
    shared = Node(constants=[Constant(id='request', value='shared.oak.md#process.not-a-reference')], schemas=[
        Schema(id='value', template='<VALUE>', where=[where('VALUE', Type(of='string'))]),
    ])
    worker = Node(processes=[Process(id='run', name='Run worker',
        input='../shared.oak.md#schema.value', output='../shared.oak.md#schema.value', steps=[
            ACT('Inspect <VALUE>.', inputs=[binding('VALUE', BindingValue(binding='VALUE'))]),
        ])])
    seed = binding('VALUE', ConstantValue(constant='shared.oak.md#constant.request'))
    root = Node(triggers=[Trigger(id='requested', event='Run.', process='process.dispatch')],
        processes=[Process(id='dispatch', name='Dispatch worker', steps=[
            Call(process='workers/run.oak.md#process.run', inputs=[seed], outputs=['VALUE']),
            Emit(interface='interface.out'),
        ])], interfaces=[Interface(id='out', flow='emits', schema='shared.oak.md#schema.value')])
    documents = {'entry.oak.md': render(root), 'shared.oak.md': render(shared), 'workers/run.oak.md': render(worker)}
    root = parse(documents['entry.oak.md'])
    graph = resolve(root, source='entry.oak.md', load=documents.get)
    require(set(graph.documents) == set(documents), 'relative graph changed')
    result = execute(root, Arrival(event='Run.'), {}, source='entry.oak.md', load=documents.get, act=lambda *_: {})
    require(result.process == 'process.dispatch', 'root process target changed')
    require(result.emissions[0].interface == 'interface.out', 'emission escaped its active document')
    require(result.emissions[0].values == {'VALUE': shared.constants[0].value}, 'target-like literal was rewritten')
    direct = Node(triggers=[Trigger(id='requested', event='Run.', process='workers/run.oak.md#process.run', seed=[seed])])
    result = execute(round_trip(direct), Arrival(event='Run.'), {}, source='entry.oak.md', load=documents.get, act=lambda *_: {})
    require(result.process == 'workers/run.oak.md#process.run' and not result.emissions, 'relative trigger process target changed')


__all__ = [
    'validate_compact_short_circuit', 'validate_compact_loop_bounds', 'validate_compact_routing',
    'validate_compact_frames', 'validate_compact_relative_targets',
]
