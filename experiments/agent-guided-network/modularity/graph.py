"""Canonical modules, graph-derived lowering, execution and bounded revisions."""
from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
from typing import Any

import numpy as np
from oak import (ACT, Act, Arrival, BindingValue, Call, Constant, ConstantValue, Emit, Interface,
                 LiteralValue, Node, NonEmpty, Process, Schema, Set, State, StateValue, ToolContract,
                 Trigger, ValueBinding, execute, parse, render, resolve, where)
from oak.resolve import ResolvedGraph

from operations import GROUPS, OPERATIONS, PROFILE, ROOMS, VOCAB, Program, canonical_bytes, decode_parameters, identity, invoke

SCHEMA_FILE = 'contracts.oak.md'
ROLES = {
    'encoder': 'How should these words be represented for both an observation and a question?',
    'attention': 'Which observed event is relevant to this question, taking report order into account?',
    'readout': 'Which location word is supported by the retrieved event and the question?',
    'memory': 'Which observations have actually been supplied in this episode?',
}
PORT_MEANINGS = {
    'TOKENS': 'integer token rows [N,12], host checks vocabulary bounds',
    'ENCODED': 'finite float64 representation [N,24], latent channels are not named concepts',
    'MEMORY': 'finite float64 observations [batch,events,24]',
    'QUERY': 'finite float64 questions [batch,24]',
    'MASK': 'integer validity flags [batch,events], at least one valid event per history',
    'CONTEXT': 'finite float64 retrieved evidence [batch,24], not ground truth',
    'PARAMETERS': 'one quantised parameter mapping belonging only to the owning module',
    'PROBABILITIES': 'finite normalised float64 class probabilities [batch,6]',
    'REPLIES': 'one numerically selected location word for each history',
}


def schema(names: tuple[str, ...]) -> Schema:
    return Schema(id='-'.join(names).lower().replace('_', '-'), name='Numerical Payload',
                  purpose='Carry one complete payload between numerical OAK modules.',
                  template='\n'.join(f'{name}: <{name}>' for name in names),
                  where=[where(name, NonEmpty(), description=PORT_MEANINGS.get(name, 'the closed host validates the complete value and capacity')) for name in names])


def target(names: tuple[str, ...]) -> str | None:
    return SCHEMA_FILE + '#schema.' + schema(names).id if names else None


def binding(name: str, source: Any) -> ValueBinding:
    return ValueBinding(placeholder=name, value=BindingValue(binding=source) if isinstance(source, str) else source)


def action(name: str, overrides: dict[str, Any] | None = None) -> Act:
    spec, sources = OPERATIONS[name], overrides or {}
    return ACT.tool(name, spec.instruction, input=target(spec.inputs), output=target(spec.outputs),
                    inputs=[binding(port, sources.get(port, port)) for port in spec.inputs], outputs=list(spec.outputs))


def call(process_target: str, inputs: dict[str, Any], outputs: tuple[str, ...] = ()) -> Call:
    return Call(process=process_target, inputs=[binding(name, source) for name, source in inputs.items()], outputs=list(outputs))


def process(identifier: str, name: str, inputs: tuple[str, ...], outputs: tuple[str, ...], steps: list[Any]) -> Process:
    return Process(id=identifier, name=name, input=target(inputs), output=target(outputs), steps=steps)


def build_nodes(record: dict[str, Any]) -> dict[str, Node]:
    if record['vocabulary'] != list(VOCAB) or record['answers'] != list(ROOMS):
        raise ValueError('reference vocabulary mismatch')
    nodes = {}
    entry_specs = {
        'encoder': ('encode', 'Encode words', ('TOKENS',), ('ENCODED',), 'modular.encode.v1'),
        'attention': ('retrieve', 'Retrieve evidence', ('MEMORY', 'QUERY', 'MASK'), ('CONTEXT',), 'modular.attend.v1'),
        'readout': ('classify', 'Select location', ('CONTEXT', 'QUERY'), ('PROBABILITIES', 'REPLIES'), 'modular.classify.v1'),
    }
    for group, (identifier, name, inputs, outputs, operation) in entry_specs.items():
        parameters = [{key: record['weights'][key] for key in GROUPS[group]}]
        decode_parameters(parameters, group)
        constants = [Constant(id='role', value=group), Constant(id='responsibility', value=ROLES[group]),
                     Constant(id='parameters', value=parameters)]
        overrides = {'PARAMETERS': ConstantValue(constant='constant.parameters')}
        if group == 'encoder':
            constants.append(Constant(id='vocabulary', value=list(VOCAB)))
        if group == 'readout':
            constants.append(Constant(id='answers', value=list(ROOMS)))
            overrides['ANSWERS'] = ConstantValue(constant='constant.answers')
        nodes[group + '.oak.md'] = Node(constants=constants,
            processes=[process(identifier, name, inputs, outputs, [action(operation, overrides)])])
    nodes['memory.oak.md'] = Node(constants=[Constant(id='role', value='memory'), Constant(id='responsibility', value=ROLES['memory'])],
        state=[State(id='history', schema=target(('STORED',)), placeholder='STORED', value=[[]])], processes=[
            process('remember', 'Remember observation', ('TEXT',), (), [
                action('modular.append.v1', {'HISTORY': StateValue(state='state.history')}),
                Set(state='state.history', value=BindingValue(binding='UPDATED'))]),
            process('read', 'Read history', (), ('HISTORIES',), [action('modular.recall.v1', {'STORED': StateValue(state='state.history')})])])
    outputs = ('PROBABILITIES', 'REPLIES')
    predict = process('predict', 'Predict locations', ('HISTORIES', 'QUESTIONS'), outputs, [
        action('modular.tokenise.v1', {'VOCABULARY': ConstantValue(constant='encoder.oak.md#constant.vocabulary')}),
        call('process.encode-events', {'TOKENS': 'EVENT_TOKENS', 'LAYOUT': 'LAYOUT'}, ('MEMORY',)),
        call('process.encode-question', {'TOKENS': 'QUESTION_TOKENS'}, ('QUERY',)),
        call('attention.oak.md#process.retrieve', {'MEMORY': 'MEMORY', 'QUERY': 'QUERY', 'MASK': 'MASK'}, ('CONTEXT',)),
        call('readout.oak.md#process.classify', {'CONTEXT': 'CONTEXT', 'QUERY': 'QUERY'}, outputs),
    ])
    entry_targets = {'observe': 'process.observe-event', 'answer': 'process.answer-questions', 'batch': 'process.answer-batch'}
    nodes['network.oak.md'] = Node(constants=[Constant(id='profile', value=PROFILE)], processes=[
        process('encode-events', 'Encode observations', ('TOKENS', 'LAYOUT'), ('MEMORY',), [
            call('encoder.oak.md#process.encode', {'TOKENS': 'TOKENS'}, ('ENCODED',)), action('modular.reshape.v1')]),
        process('encode-question', 'Encode question', ('TOKENS',), ('QUERY',), [
            call('encoder.oak.md#process.encode', {'TOKENS': 'TOKENS'}, ('ENCODED',)), action('modular.query.v1')]),
        predict,
        process('observe-event', 'Observe event', ('TEXT',), (), [call('memory.oak.md#process.remember', {'TEXT': 'TEXT'})]),
        process('answer-questions', 'Answer questions', ('QUESTIONS',), outputs, [
            call('memory.oak.md#process.read', {}, ('HISTORIES',)),
            call('process.predict', {'HISTORIES': 'HISTORIES', 'QUESTIONS': 'QUESTIONS'}, outputs), Emit(interface='interface.output')]),
        process('answer-batch', 'Answer batch', ('HISTORIES', 'QUESTIONS'), outputs, [
            call('process.predict', {'HISTORIES': 'HISTORIES', 'QUESTIONS': 'QUESTIONS'}, outputs), Emit(interface='interface.output')]),
    ], triggers=[Trigger(id=name + '-arrival', event='A modular ' + name + ' arrives.', source='interface.' + name, process=entry_target)
                 for name, entry_target in entry_targets.items()], interfaces=[
        Interface(id='observe', flow='receives', schema=target(('TEXT',))),
        Interface(id='answer', flow='receives', schema=target(('QUESTIONS',))),
        Interface(id='batch', flow='receives', schema=target(('HISTORIES', 'QUESTIONS'))),
        Interface(id='output', flow='emits', schema=target(outputs)),
    ])
    shapes = {}
    for spec in OPERATIONS.values():
        for ports in (spec.inputs, spec.outputs):
            shapes[schema(ports).id] = schema(ports)
    extra = [('TOKENS',), ('MEMORY', 'QUERY', 'MASK'), ('CONTEXT', 'QUERY'), ('TEXT',),
             ('HISTORIES',), ('TOKENS', 'LAYOUT'), ('HISTORIES', 'QUESTIONS'), ('QUESTIONS',)]
    for ports in extra:
        shapes[schema(ports).id] = schema(ports)
    nodes[SCHEMA_FILE] = Node(schemas=[shapes[key] for key in sorted(shapes)])
    return nodes


def write_graph(record: dict[str, Any], destination: Path) -> None:
    nodes = build_nodes(record)
    destination.mkdir(parents=True, exist_ok=False)
    for name, node in nodes.items():
        (destination / name).write_text(render(node), encoding='utf-8')
    compile_graph(destination)


def read_graph(directory: Path) -> ResolvedGraph:
    root = directory.resolve()

    def load(name: str) -> str:
        relative, path = PurePosixPath(name), directory / name
        if relative.is_absolute() or '..' in relative.parts or any(parent.is_symlink() for parent in [path, *path.parents]):
            raise ValueError('escaping or symlink document')
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError('missing or escaping dependency: ' + name)
        text = path.read_text(encoding='utf-8')
        node = parse(text)
        if render(node) != text or node.instructions:
            raise ValueError('noncanonical or unsupported authored instructions')
        return text

    return resolve(parse(load('network.oak.md')), source='network.oak.md', load=load)


def graph_hashes(directory: Path) -> dict[str, str]:
    graph = read_graph(directory)
    return {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in sorted(graph.documents)}


def join_parameters(directory: Path) -> dict[str, Any]:
    graph, weights = read_graph(directory), {}
    for group in GROUPS:
        _, constant = graph.entry(group + '.oak.md', 'constant.parameters', Constant)
        decode_parameters(constant.value, group)
        weights.update(constant.value[0])
    return {'profile': 'oak-word-meaning-v1', 'vocabulary': list(VOCAB), 'answers': list(ROOMS), 'weights': weights}


def compile_graph(directory: Path) -> dict[str, Any]:
    graph = read_graph(directory)
    constants, initial_state = {}, {}
    for document, node in graph.documents.items():
        if document != graph.root and node.triggers:
            raise ValueError('nested arrival routing outside this profile')
        for state in node.state:
            initial_state[document + '#state.' + state.id] = state.value
        for value in node.constants:
            constants[document + '#constant.' + value.id] = value.value
    for group in GROUPS:
        decode_parameters(constants[group + '.oak.md#constant.parameters'], group)
    counter, call_sites = 0, []

    def ports(document: str, contract: str | None) -> tuple[str, ...]:
        if contract is None:
            return ()
        _, resolved = graph.entry(document, contract, Schema)
        names = tuple(rule.placeholder for rule in resolved.where)
        if resolved != schema(names):
            raise ValueError('unsupported schema semantics')
        return names

    def lower(document: str, entry: Process, env: dict[str, list], instructions: list[dict]) -> dict[str, list]:
        nonlocal counter

        def value(source: Any) -> list:
            if isinstance(source, BindingValue):
                return env[source.binding]
            if isinstance(source, ConstantValue):
                owner, item = graph.entry(document, source.constant, Constant)
                return ['constant', owner + '#constant.' + item.id]
            if isinstance(source, StateValue):
                return ['state', document + '#' + source.state]
            if isinstance(source, LiteralValue):
                key = 'literal-' + identity(source.value)
                constants[key] = source.value
                return ['constant', key]
            raise ValueError('unsupported value source')

        if set(env) != set(ports(document, entry.input)):
            raise ValueError('process input contract differs')
        for step in entry.steps:
            if isinstance(step, Call):
                owner, child = graph.entry(document, step.process, Process)
                child_env = {item.placeholder: value(item.value) for item in step.inputs}
                call_sites.append({'caller': document + '#process.' + entry.id, 'target': owner + '#process.' + child.id})
                outputs = lower(owner, child, child_env, instructions)
                env.update({name: outputs[name] for name in step.outputs})
            elif isinstance(step, Act):
                if step.tool not in OPERATIONS:
                    raise ValueError('unsupported numerical operation')
                spec = OPERATIONS[step.tool]
                if (step.instruction != spec.instruction or ports(document, step.input) != spec.inputs
                        or ports(document, step.output) != spec.outputs):
                    raise ValueError('operation prose or schema contract differs')
                counter += 1
                outputs = {name: str(counter) + ':' + name for name in step.outputs}
                instructions.append({'kind': 'act', 'owner': document, 'operation': step.tool,
                                     'inputs': {item.placeholder: value(item.value) for item in step.inputs}, 'outputs': outputs})
                env.update({name: ['slot', slot] for name, slot in outputs.items()})
            elif isinstance(step, Set):
                _, declared = graph.entry(document, step.state, State)
                if ports(document, declared.schema_id) != ('STORED',):
                    raise ValueError('unsupported state contract')
                instructions.append({'kind': 'set', 'target': document + '#' + step.state, 'value': value(step.value)})
            elif isinstance(step, Emit):
                if step.bindings:
                    raise ValueError('explicit emissions outside this profile')
                _, interface = graph.entry(document, step.interface, Interface)
                instructions.append({'kind': 'emit', 'values': {name: env[name] for name in ports(document, interface.schema_id)}})
            else:
                raise ValueError('unsupported control flow')
        return {name: env[name] for name in ports(document, entry.output)}

    entries = {}
    for trigger in graph.documents[graph.root].triggers:
        if trigger.guard is not True or trigger.seed or trigger.source is None or trigger.source in entries:
            raise ValueError('unsupported or ambiguous trigger')
        owner, entry = graph.entry(graph.root, trigger.process, Process)
        inputs, instructions = ports(owner, entry.input), []
        outputs = lower(owner, entry, {name: ['input', name] for name in inputs}, instructions)
        entries[trigger.source] = {'inputs': inputs, 'outputs': outputs, 'instructions': instructions}
    record = {'profile': PROFILE, 'source': {'documents': graph_hashes(directory), 'call_sites': call_sites},
              'constants': constants, 'initial_state': initial_state, 'entries': entries}
    record['digest'] = identity(record)
    Program(record)
    return record


def json_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {key: json_value(item) for key, item in value.items()}
    return value


def oak_run(directory: Path, arrivals: list[tuple[str, dict[str, Any]]]) -> tuple[list[dict], dict]:
    graph, program = read_graph(directory), compile_graph(directory)
    state = {graph.display_target(name.split('#')[0], 'state', name.split('state.')[1]): values
             for name, values in program['initial_state'].items()}
    tools = {}
    for name, spec in OPERATIONS.items():
        def handler(_step: object, payload: dict, operation: str = name) -> dict:
            return json_value(invoke(operation, payload))
        tools[name] = ToolContract(handler, frozenset(spec.inputs), frozenset(spec.outputs),
                                   input=target(spec.inputs), output=target(spec.outputs))
    emissions = []
    for interface, payload in arrivals:
        result = execute(graph.documents[graph.root], Arrival(interface=interface, values=payload), state,
                         tools=tools, source=graph.root, load=graph.documents.get)
        state = json.loads(canonical_bytes(result.state))
        emissions.extend(emission.values for emission in result.emissions)
    return emissions, state


@dataclass(frozen=True, slots=True)
class Proposal:
    baseline: str
    allowed_modules: tuple[str, ...]
    rationale: str


def validate_revision(incumbent: Path, candidate: Path, proposal: Proposal) -> dict[str, Any]:
    before, after = graph_hashes(incumbent), graph_hashes(candidate)
    if identity(before) != proposal.baseline:
        raise ValueError('stale baseline')
    if not proposal.allowed_modules or any(name not in GROUPS for name in proposal.allowed_modules):
        raise ValueError('invalid parameter owners')
    if set(before) != set(after):
        raise ValueError('document closure changed')
    changed = [name for name in before if before[name] != after[name]]
    if not changed or not set(changed) <= {name + '.oak.md' for name in proposal.allowed_modules}:
        raise ValueError('cross-module write or empty revision')
    old_graph, new_graph = read_graph(incumbent), read_graph(candidate)
    for name in changed:
        old_fields = old_graph.documents[name].model_dump(mode='json')
        new_fields = new_graph.documents[name].model_dump(mode='json')
        for fields in (old_fields, new_fields):
            for constant in fields['constants']:
                if constant['id'] == 'parameters':
                    constant['value'] = None
        if old_fields != new_fields:
            raise ValueError('nonparameter change')
    compiled = compile_graph(candidate)
    return {'changed': changed, 'unchanged': [name for name in before if name not in changed],
            'before': before, 'after': after, 'candidate': identity(after), 'program': compiled['digest']}


def export_graph(directory: Path, destination: Path) -> dict[str, Any]:
    program = compile_graph(directory)
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'program.json').write_bytes(canonical_bytes(program))
    shutil.copyfile(Path(__file__).with_name('operations.py'), destination / 'inference.py')
    manifest = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in destination.iterdir()}
    (destination / 'manifest.json').write_bytes(canonical_bytes(manifest))
    return {'files': manifest, 'bytes': sum(path.stat().st_size for path in destination.iterdir()), 'program': program['digest']}
