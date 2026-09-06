"""Explicit OAK dialogue composition; scoped edits are enforced equally in the Python control."""
from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

import numpy as np
from oak import (ACT, Act, Arrival, BindingValue, Call, Constant, ConstantValue, Emit, Interface,
                 LiteralValue, Node, NonEmpty, Process, Schema, Set, State, StateValue, ToolContract,
                 Trigger, execute, parse, render, resolve, where, ValueBinding)
from oak.resolve import ResolvedGraph
from runtime import GROUPS, OPERATIONS, PROFILE, VOCAB, MAX_REPLY, Program, canonical_bytes, identity, invoke, parameters

SCHEMA_FILE = 'contracts.oak.md'


def schema(names: tuple[str, ...]) -> Schema:
    return Schema(id='-'.join(names).lower(), name='Dialogue Payload', purpose='Carry a complete bounded numerical payload.',
        template='\n'.join(name + ': <' + name + '>' for name in names),
        where=[where(name, NonEmpty(), description='the numerical host validates the exact tensor or message contract') for name in names])


def target(names: tuple[str, ...]) -> str | None:
    return SCHEMA_FILE + '#schema.' + schema(names).id if names else None


def binding(name: str, source: Any) -> ValueBinding:
    return ValueBinding(placeholder=name, value=BindingValue(binding=source) if isinstance(source, str) else source)


def action(name: str, overrides: dict[str, Any] | None = None) -> Act:
    spec, sources = OPERATIONS[name], overrides or {}
    return ACT.tool(name, spec.instruction, input=target(spec.inputs), output=target(spec.outputs),
        inputs=[binding(port, sources.get(port, port)) for port in spec.inputs], outputs=list(spec.outputs))


def call(name: str, ports: tuple[str, ...], outputs: tuple[str, ...]) -> Call:
    return Call(process=name, inputs=[binding(port, port) for port in ports], outputs=list(outputs))


def process(identifier: str, inputs: tuple[str, ...], outputs: tuple[str, ...], steps: list[Any]) -> Process:
    return Process(id=identifier, name=(identifier.replace('-', ' ').capitalize() if '-' in identifier else identifier.capitalize() + ' dialogue'), input=target(inputs), output=target(outputs), steps=steps)


def build_nodes(record: dict[str, Any]) -> dict[str, Node]:
    from runtime import load_model
    load_model(record)
    nodes = {}
    roles = {'encoder': 'Represent the supplied dialogue words in order.',
             'attention': 'Retrieve dialogue evidence for the next generated word.',
             'decoder': 'Update numerical generation state using previous word and retrieved evidence.',
             'readout': 'Select the next word from the numerical generation state.'}
    names = {'encoder': 'encode', 'attention': 'attend', 'decoder': 'decode', 'readout': 'readout'}
    for group, names_in_group in GROUPS.items():
        operation = 'dialogue.' + names[group]
        spec = OPERATIONS[operation]
        constants = [Constant(id='parameters', value=[{k: record['weights'][k] for k in names_in_group}]),
                     Constant(id='responsibility', value=roles[group])]
        overrides: dict[str, Any] = {'PARAMETERS': ConstantValue(constant='constant.parameters')}
        inputs = tuple(name for name in spec.inputs if name != 'PARAMETERS')
        nodes[group + '.oak.md'] = Node(constants=constants,
            processes=[process(names[group], inputs, spec.outputs, [action(operation, overrides)])])
    nodes['memory.oak.md'] = Node(state=[State(id='history', schema=target(('STORED',)), placeholder='STORED', value=[[]])], processes=[
        process('recall', (), ('HISTORIES',), [action('dialogue.recall', {'STORED': StateValue(state='state.history')})]),
        process('commit', ('HISTORIES', 'TEXTS', 'REPLIES'), (), [action('dialogue.commit'), Set(state='state.history', value=BindingValue(binding='STORED'))])])
    generation_states = [State(id='hidden', schema=target(('HIDDEN',)), placeholder='HIDDEN', value=[[0.0] * 48]),
        State(id='previous', schema=target(('TOKEN',)), placeholder='TOKEN', value=[1]),
        State(id='tape', schema=target(('TAPE',)), placeholder='TAPE', value=[[]])]
    def mapped_call(name: str, inputs: dict[str, Any], outputs: tuple[str, ...]) -> Call:
        return Call(process=name, inputs=[binding(key, value) for key, value in inputs.items()], outputs=list(outputs))
    generation_step = process('next-word', ('MEMORY', 'MASK', 'EMBEDDING'), (), [
        mapped_call('attention.oak.md#process.attend', {'MEMORY': 'MEMORY', 'MASK': 'MASK', 'STATE': StateValue(state='state.hidden')}, ('CONTEXT',)),
        mapped_call('decoder.oak.md#process.decode', {'CONTEXT': 'CONTEXT', 'EMBEDDING': 'EMBEDDING',
            'STATE': StateValue(state='state.hidden'), 'PREVIOUS': StateValue(state='state.previous')}, ('NEWSTATE',)),
        mapped_call('readout.oak.md#process.readout', {'STATE': 'NEWSTATE', 'CONTEXT': 'CONTEXT',
            'TAPE': StateValue(state='state.tape')}, ('NEWPREVIOUS', 'NEWTAPE')),
        Set(state='state.hidden', value=BindingValue(binding='NEWSTATE')),
        Set(state='state.previous', value=BindingValue(binding='NEWPREVIOUS')),
        Set(state='state.tape', value=BindingValue(binding='NEWTAPE'))])
    nodes['generation.oak.md'] = Node(state=generation_states, processes=[
        process('start', ('STATE', 'PREVIOUS', 'TAPE'), (), [
            Set(state='state.hidden', value=BindingValue(binding='STATE')),
            Set(state='state.previous', value=BindingValue(binding='PREVIOUS')),
            Set(state='state.tape', value=BindingValue(binding='TAPE'))]), generation_step,
        process('finish', (), ('REPLIES',), [action('dialogue.finish', {'TAPE': StateValue(state='state.tape')})])])
    predict_steps = [action('dialogue.prepare'),
        call('encoder.oak.md#process.encode', ('TOKENS',), ('MEMORY', 'STATE', 'PREVIOUS', 'TAPE', 'EMBEDDING')),
        call('generation.oak.md#process.start', ('STATE', 'PREVIOUS', 'TAPE'), ())]
    predict_steps += [call('generation.oak.md#process.next-word', ('MEMORY', 'MASK', 'EMBEDDING'), ()) for _ in range(MAX_REPLY)]
    predict_steps += [call('generation.oak.md#process.finish', (), ('REPLIES',))]
    nodes['network.oak.md'] = Node(constants=[Constant(id='profile', value=PROFILE), Constant(id='vocabulary', value=list(VOCAB))], processes=[
        process('predict', ('HISTORIES', 'TEXTS'), ('REPLIES',), predict_steps),
        process('answer-chat', ('TEXTS',), ('REPLIES',), [
            call('memory.oak.md#process.recall', (), ('HISTORIES',)),
            call('process.predict', ('HISTORIES', 'TEXTS'), ('REPLIES',)),
            call('memory.oak.md#process.commit', ('HISTORIES', 'TEXTS', 'REPLIES'), ()), Emit(interface='interface.reply')]),
        process('answer-batch', ('HISTORIES', 'TEXTS'), ('REPLIES',), [call('process.predict', ('HISTORIES', 'TEXTS'), ('REPLIES',)), Emit(interface='interface.reply')])],
        triggers=[Trigger(id=name + '-arrival', event='A dialogue ' + name + ' arrives.', source='interface.' + name, process='process.answer-' + name) for name in ('chat', 'batch')],
        interfaces=[Interface(id='chat', flow='receives', schema=target(('TEXTS',))),
                    Interface(id='batch', flow='receives', schema=target(('HISTORIES', 'TEXTS'))),
                    Interface(id='reply', flow='emits', schema=target(('REPLIES',)))])
    shapes = {schema(ports).id: schema(ports) for spec in OPERATIONS.values() for ports in (spec.inputs, spec.outputs)}
    for node in nodes.values():
        for entry in node.processes:
            for path in (entry.input, entry.output):
                if path:
                    names_tuple = tuple(path.split('#schema.')[1].upper().split('-'))
                    shapes[schema(names_tuple).id] = schema(names_tuple)
    for ports in [('TEXTS',), ('STORED',), ('HIDDEN',), ('TOKEN',), ('TAPE',)]:
        shapes[schema(ports).id] = schema(ports)
    nodes[SCHEMA_FILE] = Node(schemas=[shapes[key] for key in sorted(shapes)])
    return nodes


def write_graph(record: dict[str, Any], destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    for name, node in build_nodes(record).items():
        (destination / name).write_text(render(node), encoding='utf-8')
    compile_graph(destination)


def join_parameters(directory: Path) -> dict[str, Any]:
    graph, weights = read_graph(directory), {}
    for group in GROUPS:
        _, constant = graph.entry(group + '.oak.md', 'constant.parameters', Constant)
        parameters(constant.value[0], group)
        weights.update(constant.value[0])
    return {'profile': PROFILE, 'vocabulary': list(VOCAB), 'weights': weights}


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
        parameters(constants[group + '.oak.md#constant.parameters'][0], group)
    join_parameters(directory)
    if constants.get('network.oak.md#constant.profile') != PROFILE or constants.get('network.oak.md#constant.vocabulary') != list(VOCAB):
        raise ValueError('changed profile or vocabulary')
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
                if ports(document, declared.schema_id) not in [('STORED',), ('HIDDEN',), ('TOKEN',), ('TAPE',)]:
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
class Revision:
    baseline: str
    allowed: tuple[str, ...]


def validate_python_revision(before: dict[str, Any], after: dict[str, Any], revision: Revision) -> list[str]:
    from runtime import load_model
    load_model(before)
    load_model(after)
    if identity(before) != revision.baseline or not revision.allowed or not set(revision.allowed) <= set(GROUPS):
        raise ValueError('stale model or invalid permission')
    changed = [name for name in GROUPS if any(before['weights'][key] != after['weights'][key] for key in GROUPS[name])]
    if not changed or not set(changed) <= set(revision.allowed):
        raise ValueError('empty revision or forbidden owner')
    return changed


def validate_oak_revision(before: Path, after: Path, revision: Revision) -> list[str]:
    old, new = join_parameters(before), join_parameters(after)
    changed = validate_python_revision(old, new, revision)
    old_nodes, new_nodes = read_graph(before).documents, read_graph(after).documents
    if set(old_nodes) != set(new_nodes):
        raise ValueError('document closure changed')
    expected = build_nodes(new)
    for name, node in new_nodes.items():
        if node != expected[name]:
            raise ValueError('nonparameter document edit')
        if name not in {owner + '.oak.md' for owner in changed} and node != old_nodes[name]:
            raise ValueError('other document changed')
    compile_graph(after)
    return changed
