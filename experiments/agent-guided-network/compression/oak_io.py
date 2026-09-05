"""Canonical compact kernel owners and strict OAK/numerical execution parity."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from oak import (ACT, Arrival, BindingValue, Call, Constant, ConstantValue, Emit, Interface, Node,
                 NonEmpty, Process, Schema, ToolContract, Trigger, ValueBinding, execute, parse, render,
                 resolve, where)

from compression.numeric import (FIELDS, PROFILE, Array, Inputs, Kernel, Kernels, attend, expand_kernel,
                                 kernel_record, read_kernel, softmax, validate_inputs)

_FILES = ("attention.oak.md", "attention-readout.oak.md", "network.oak.md", "contracts.oak.md")
_STAGE_INPUTS = (("QUERY", "KEY1", "VALUE1", "MASK1"), ("BRIDGE", "KEY2", "VALUE2", "MASK2"))
_STAGE_OUTPUTS = (("BRIDGE", "ALIGN1"), ("LOGITS", "ALIGN2"))


def _target(identifier: str) -> str:
    return "contracts.oak.md#schema." + identifier


def _bindings(names: tuple[str, ...]) -> list[ValueBinding]:
    return [ValueBinding(placeholder=name, value=BindingValue(binding=name)) for name in names]


def _schema(identifier: str, names: tuple[str, ...]) -> Schema:
    return Schema(id=identifier, name="Compact Attention Payload", purpose="Carry a complete compact-host payload.",
                  template="\n".join(f"{name}: <{name}>" for name in names),
                  where=[where(name, NonEmpty(), description="the host checks exact numerical shape and encoding") for name in names])


def _read_kernel_payload(payload: object) -> Kernel:
    if not isinstance(payload, list) or len(payload) != 1:
        raise ValueError("kernel payload must contain exactly one named record")
    return read_kernel(payload[0])


def documents(kernels: Kernels) -> dict[str, Node]:
    if tuple(kernel.dimension for kernel in kernels) != (8, 8, 4):
        raise ValueError("invalid compact network dimensions")
    schemas = [_schema("input", FIELDS), _schema("prediction", ("PROB",)), _schema("decode", ("LOGITS",)),
               _schema("kernel", ("KERNEL",))]
    nodes: dict[str, Node] = {}
    calls: list[Call] = []
    for index, (incoming, outgoing) in enumerate(zip(_STAGE_INPUTS, _STAGE_OUTPUTS, strict=True)):
        stage = ("first", "second")[index]
        descriptors = (("SCORE", "score-kernel", kernels[index]),)
        if index == 1:
            descriptors += (("OUTPUT", "output-kernel", kernels[2]),)
        payload = incoming + tuple(slot for slot, _, _ in descriptors)
        schemas.extend((_schema(stage + "-input", incoming), _schema(stage + "-output", outgoing),
                        _schema(stage + "-action", payload)))
        constants = [Constant(id=name, schema=_target("kernel"), placeholder="KERNEL", value=[kernel_record(kernel)])
                     for _, name, kernel in descriptors]
        constants.append(Constant(id="responsibility", value="Compute raw weighted bridge values." if index == 0
                                  else "Match the raw bridge and transform class evidence."))
        action = ACT.tool("tensor.compact." + stage + ".v1",
                          "Use " + ", ".join("<" + name + ">" for name in payload) + " to produce " + ", ".join("<" + name + ">" for name in outgoing) + ".",
                          input=_target(stage + "-action"), output=_target(stage + "-output"),
                          inputs=_bindings(incoming) + [ValueBinding(placeholder=slot, value=ConstantValue(constant="constant." + name))
                                                        for slot, name, _ in descriptors], outputs=list(outgoing))
        nodes[_FILES[index]] = Node(constants=constants, processes=[Process(id="attend", name="Attend values",
            input=_target(stage + "-input"), output=_target(stage + "-output"), steps=[action])])
        calls.append(Call(process=_FILES[index] + "#process.attend", inputs=_bindings(incoming), outputs=list(outgoing)))
    nodes["contracts.oak.md"] = Node(schemas=schemas)
    nodes["network.oak.md"] = Node(constants=[Constant(id="profile", value=PROFILE), Constant(id="dtype", value="float64"),
        Constant(id="decoder", value="argmax-first"), Constant(id="kernel-meaning", value="Finite numerical encodings, not executable code." )],
        triggers=[Trigger(id="request", event="A compact two-hop retrieval request arrives.", source="interface.input", process="process.infer")],
        processes=[Process(id="infer", name="Infer classes", input=_target("input"), output=_target("prediction"),
            steps=[*calls, ACT.tool("tensor.softmax.v1", "Normalise <LOGITS> to <PROB>.", input=_target("decode"),
            output=_target("prediction"), inputs=_bindings(("LOGITS",)), outputs=["PROB"]), Emit(interface="interface.output")])],
        interfaces=[Interface(id="input", flow="receives", schema=_target("input")), Interface(id="output", flow="emits", schema=_target("prediction"))])
    return nodes


def write_snapshot(kernels: Kernels, directory: Path) -> str:
    nodes = documents(kernels)
    directory.mkdir(parents=True, exist_ok=False)
    for filename, node in nodes.items():
        (directory / filename).write_text(render(node), encoding="utf-8")
    return snapshot_hash(directory)


def snapshot_hash(directory: Path) -> str:
    if directory.is_symlink() or {path.name for path in directory.iterdir()} != set(_FILES):
        raise ValueError("invalid snapshot directory")
    digest = hashlib.sha256()
    for filename in sorted(_FILES):
        path = directory / filename
        if path.is_symlink() or not path.is_file():
            raise ValueError("snapshot files must be regular files")
        digest.update(filename.encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def load_snapshot(directory: Path) -> Kernels:
    snapshot_hash(directory)
    nodes = {name: parse((directory / name).read_text(encoding="utf-8")) for name in _FILES}
    first = {constant.id: constant.value for constant in nodes[_FILES[0]].constants}
    second = {constant.id: constant.value for constant in nodes[_FILES[1]].constants}
    kernels = (_read_kernel_payload(first["score-kernel"]), _read_kernel_payload(second["score-kernel"]), _read_kernel_payload(second["output-kernel"]))
    for filename, expected in documents(kernels).items():
        if nodes[filename] != expected or (directory / filename).read_text(encoding="utf-8") != render(expected):
            raise ValueError("unsupported or non-canonical numerical document: " + filename)
    resolve(nodes["network.oak.md"], source="network.oak.md", load=lambda name: nodes[name])
    return kernels


def oak_forward(directory: Path, records: Inputs) -> Array:
    kernels = load_snapshot(directory)
    nodes = documents(kernels)
    inputs = validate_inputs(records)

    def stage_tool(index: int):
        def invoke(_step, payload):
            query, keys, values, mask = (np.asarray(payload[name], dtype=float) for name in _STAGE_INPUTS[index])
            mixed, alignment = attend(query, keys, values, mask, expand_kernel(_read_kernel_payload(payload["SCORE"])))
            output = mixed if index == 0 else mixed @ expand_kernel(_read_kernel_payload(payload["OUTPUT"]))
            return {_STAGE_OUTPUTS[index][0]: output.tolist(), _STAGE_OUTPUTS[index][1]: alignment.tolist()}
        return invoke

    tools = {}
    for index, stage in enumerate(("first", "second")):
        slots = ("SCORE",) if index == 0 else ("SCORE", "OUTPUT")
        tools["tensor.compact." + stage + ".v1"] = ToolContract(stage_tool(index), frozenset(_STAGE_INPUTS[index] + slots),
            frozenset(_STAGE_OUTPUTS[index]), input=_target(stage + "-action"), output=_target(stage + "-output"))
    tools["tensor.softmax.v1"] = ToolContract(lambda _step, payload: {"PROB": softmax(np.asarray(payload["LOGITS"])).tolist()},
        frozenset(("LOGITS",)), frozenset(("PROB",)), input=_target("decode"), output=_target("prediction"))
    outcome = execute(nodes["network.oak.md"], Arrival(interface="interface.input", values={name: a.tolist() for name, a in inputs.items()}),
                      {}, tools=tools, source="network.oak.md", load=lambda name: nodes[name])
    return np.asarray(outcome.emissions[0].values["PROB"])
