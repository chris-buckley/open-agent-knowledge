"""One canonical, stateful OAK numerical node and its isolated export boundary."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

from oak import (ACT, Arrival, BindingValue, Constant, ConstantValue, Emit, Interface, Node, NonEmpty, Process,
                 Schema, Set, State, StateValue, ToolContract, Trigger, ValueBinding, execute, parse, render, resolve, where)

from runtime import PROFILE, MAX_EVENTS, Session, canonical_bytes, encode_words, load_record


def _schema(identifier: str, names: tuple[str, ...]) -> Schema:
    return Schema(id=identifier, name='Meaning Payload', purpose='Carry a complete numerical-host payload.',
                  template='\n'.join(f'{name}: <{name}>' for name in names),
                  where=[where(name, NonEmpty(), description='the host validates the exact profile shape and capacity') for name in names])


def _binding(name: str, value: object) -> ValueBinding:
    return ValueBinding(placeholder=name, value=value)


def document(record: dict) -> Node:
    load_record(record)
    memory_schema = _schema('memory-payload', ('MEMORY',))
    utterance_schema = _schema('utterance', ('TEXT',))
    question_schema = _schema('question', ('QUESTION',))
    answer_schema = _schema('reply', ('ANSWER',))
    remember_schema = _schema('remember-input', ('HISTORY', 'TEXT'))
    inference_schema = _schema('infer-input', ('HISTORY', 'QUESTION', 'MODEL'))
    remember_action = ACT.tool('meaning.remember.v1', 'Append <TEXT> to <HISTORY> within the capacity to produce <MEMORY>.',
        input='schema.remember-input', output='schema.memory-payload',
        inputs=[_binding('TEXT', BindingValue(binding='TEXT')), _binding('HISTORY', StateValue(state='state.history'))],
        outputs=['MEMORY'])
    infer_action = ACT.tool('meaning.answer.v1', 'Use <MODEL> to answer <QUESTION> from <HISTORY> numerically as <ANSWER>.',
        input='schema.infer-input', output='schema.reply', inputs=[
            _binding('QUESTION', BindingValue(binding='QUESTION')),
            _binding('HISTORY', StateValue(state='state.history')),
            _binding('MODEL', ConstantValue(constant='constant.model'))], outputs=['ANSWER'])
    remember_process = Process(id='remember', name='Remember observation', input='schema.utterance', steps=[
        remember_action, Set(state='state.history', value=BindingValue(binding='MEMORY'))])
    answer_process = Process(id='answer', name='Answer question', input='schema.question', output='schema.reply',
        steps=[infer_action, Emit(interface='interface.reply-output')])
    return Node(constants=[Constant(id='model', value=[record]), Constant(id='profile', value=PROFILE),
                          Constant(id='responsibility', value='Which location is supported for this object now or before its latest reported move?')],
                schemas=[memory_schema, utterance_schema, question_schema, answer_schema, remember_schema, inference_schema],
                state=[State(id='history', schema='schema.memory-payload', placeholder='MEMORY', value=[[]])],
                triggers=[Trigger(id='observation', event='An observation is supplied.', source='interface.observation-input', process='process.remember'),
                          Trigger(id='question-arrival', event='A question is supplied.', source='interface.question-input', process='process.answer')],
                processes=[remember_process, answer_process], interfaces=[
                    Interface(id='observation-input', flow='receives', schema='schema.utterance'),
                    Interface(id='question-input', flow='receives', schema='schema.question'),
                    Interface(id='reply-output', flow='emits', schema='schema.reply')])


def write_node(record: dict, path: Path) -> None:
    path.write_text(render(document(record)), encoding='utf-8')


def read_node(path: Path) -> tuple[Node, dict]:
    if path.is_symlink() or not path.is_file():
        raise ValueError('model node must be a regular file')
    text = path.read_text(encoding='utf-8')
    node = parse(text)
    constants = {value.id: value.value for value in node.constants}
    payload = constants.get('model')
    if not isinstance(payload, list) or len(payload) != 1:
        raise ValueError('invalid model envelope')
    record = payload[0]
    if not isinstance(record, dict):
        raise ValueError('missing model parameters')
    if node != document(record) or render(node) != text:
        raise ValueError('altered numerical profile')
    resolve(node, source='network.oak.md', load=lambda _: None)
    return node, record


def _remember(_step: object, payload: dict) -> dict:
    memory, text = payload['HISTORY'], payload['TEXT']
    if not isinstance(memory, list) or len(memory) != 1:
        raise ValueError('invalid memory fields')
    history = memory[0]
    if not isinstance(history, list) or len(history) >= MAX_EVENTS:
        raise ValueError('invalid history capacity')
    for event in [*history, text]:
        encode_words(event)
    return {'MEMORY': [[*history, text]]}


def _answer(_step: object, payload: dict) -> dict:
    session = Session(payload['MODEL'][0])
    for text in payload['HISTORY'][0]:
        session.observe(text)
    return {'ANSWER': session.answer(payload['QUESTION'])}


def oak_dialogue(path: Path, events: list[str], questions: list[str]) -> list[str]:
    node, _ = read_node(path)
    tools = {
        'meaning.remember.v1': ToolContract(_remember, frozenset(('HISTORY', 'TEXT')), frozenset(('MEMORY',)),
                                          input='schema.remember-input', output='schema.memory-payload'),
        'meaning.answer.v1': ToolContract(_answer, frozenset(('HISTORY', 'QUESTION', 'MODEL')), frozenset(('ANSWER',)),
                                        input='schema.infer-input', output='schema.reply'),
    }
    state = {'state.history': [[]]}
    for text in events:
        cycle = execute(node, Arrival(interface='interface.observation-input', values={'TEXT': text}), state,
                        tools=tools, source='network.oak.md')
        state = json.loads(json.dumps(cycle.state))
    replies = []
    for question in questions:
        cycle = execute(node, Arrival(interface='interface.question-input', values={'QUESTION': question}), state,
                        tools=tools, source='network.oak.md')
        replies.append(cycle.emissions[0].values['ANSWER'])
        state = json.loads(json.dumps(cycle.state))
    return replies


def export_node(node_file: Path, destination: Path) -> dict:
    _, record = read_node(node_file)
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'model.json').write_bytes(canonical_bytes(record))
    shutil.copyfile(Path(__file__).with_name('runtime.py'), destination / 'inference.py')
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in destination.iterdir()}
    (destination / 'manifest.json').write_bytes(canonical_bytes(hashes))
    return {'files': hashes, 'source_oak_sha256': hashlib.sha256(node_file.read_bytes()).hexdigest(),
            'bytes': sum(path.stat().st_size for path in destination.iterdir())}
