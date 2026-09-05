"""Canonical OAK owners for two attention blocks and their numerical boundary."""
from __future__ import annotations

import hashlib
from pathlib import Path
import numpy as np
from oak import (ACT, Arrival, BindingValue, Call, Constant, ConstantValue, Emit, Interface,
                 Node, NonEmpty, Process, Schema, ToolContract, Trigger, ValueBinding,
                 execute, parse, render, resolve, where)
from attention.numeric import PROFILE, FIELDS, attention, inputs, parameters, softmax

STAGES = {
    "first": ("attention.oak.md", ["QUERY", "KEY1", "VALUE1", "MASK1"], ["BRIDGE", "ALIGN1"]),
    "second": ("attention-readout.oak.md", ["BRIDGE", "KEY2", "VALUE2", "MASK2"], ["LOGITS", "ALIGN2"]),
}
PARAMETERS = {"WQ": "query", "WK": "key", "WV": "value", "WO": "output"}


def target(name: str) -> str:
    return "contracts.oak.md#schema."+name


def bindings(names: list[str]) -> list[ValueBinding]:
    return [ValueBinding(placeholder=name, value=BindingValue(binding=name)) for name in names]


def schema(name: str, names: list[str]) -> Schema:
    return Schema(id=name, name="Attention Payload", purpose="Carry complete tensor instances for the closed attention host.",
                  template="\n".join(f"{key}: <{key}>" for key in names),
                  where=[where(key, NonEmpty(), description="exact rank, dimensions, finite values and masking are checked by the numerical host") for key in names])


def documents(values: dict) -> dict[str, Node]:
    w = parameters(values)
    schemas = [schema("input", list(FIELDS)), schema("prediction", ["PROB"]),
               schema("decode", ["LOGITS"]), schema("parameters", list(PARAMETERS))]
    docs = {}
    for stage, (filename, incoming, outgoing) in STAGES.items():
        schemas += [schema(stage+"-input", incoming), schema(stage+"-output", outgoing),
                    schema(stage+"-action", incoming+list(PARAMETERS))]
        constants = [Constant(id=name, schema=target("parameters"), placeholder=slot, value=w[stage+"-"+name].tolist())
                     for slot, name in PARAMETERS.items()]
        constants += [Constant(id="equation", value="softmax(mask((query @ WQ) @ (keys @ WK).T / sqrt(8))) @ (values @ WV) @ WO"),
                      Constant(id="responsibility", value="Retrieve a bridge key." if stage == "first" else "Retrieve class evidence from the bridge key."),
                      Constant(id="head-count", value=1), Constant(id="key-dimension", value=8),
                      Constant(id="value-dimension", value=8 if stage == "first" else 4),
                      Constant(id="mask-policy", value="One means valid, zero means masked; an all-masked row is invalid."),
                      Constant(id="axes", value={"query": ["batch", 8], "keys": ["batch", "length", 8],
                                                  "values": ["batch", "length", 8 if stage == "first" else 4], "mask": ["batch", "length"]})]
        action = ACT.tool("tensor.attention."+stage+".v1",
                          "Compute scaled dot-product cross-attention from "+", ".join("<"+key+">" for key in incoming+list(PARAMETERS))+" to produce "+", ".join("<"+key+">" for key in outgoing)+".",
                          input=target(stage+"-action"), output=target(stage+"-output"),
                          inputs=bindings(incoming)+[ValueBinding(placeholder=slot, value=ConstantValue(constant="constant."+name)) for slot, name in PARAMETERS.items()],
                          outputs=outgoing)
        docs[filename] = Node(constants=constants, processes=[Process(id="attend", name="Attend values",
                              input=target(stage+"-input"), output=target(stage+"-output"), steps=[action])])
    docs["contracts.oak.md"] = Node(schemas=schemas)
    docs["network.oak.md"] = Node(
        constants=[Constant(id="profile", value=PROFILE), Constant(id="dtype", value="float64"),
                   Constant(id="decoder", value="argmax-first"), Constant(id="length-limit", value=64)],
        triggers=[Trigger(id="request", event="A two-hop numerical retrieval request arrives.", source="interface.input", process="process.infer")],
        processes=[Process(id="infer", name="Retrieve classes", input=target("input"), output=target("prediction"),
                           steps=[Call(process=filename+"#process.attend", inputs=bindings(inc), outputs=out) for filename, inc, out in STAGES.values()]
                           +[ACT.tool("tensor.softmax.v1", "Normalise class <LOGITS> to <PROB>.", input=target("decode"),
                                      output=target("prediction"), inputs=bindings(["LOGITS"]), outputs=["PROB"]), Emit(interface="interface.output")])],
        interfaces=[Interface(id="input", flow="receives", schema=target("input")),
                    Interface(id="output", flow="emits", schema=target("prediction"))])
    return docs


def write(values: dict, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    for name, node in documents(values).items():
        (destination/name).write_text(render(node), encoding="utf-8")


def revision(directory: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(directory.iterdir()):
        if path.is_symlink() or not path.is_file() or not path.name.endswith(".oak.md"):
            raise ValueError("only regular OAK documents are permitted")
        h.update(path.name.encode()+b"\0"+path.read_bytes()+b"\0")
    return h.hexdigest()


def load(directory: Path) -> tuple[dict, object]:
    revision(directory)
    nodes = {path.name: parse(path.read_text()) for path in directory.iterdir()}
    if set(nodes) != {"attention.oak.md", "attention-readout.oak.md", "contracts.oak.md", "network.oak.md"}:
        raise ValueError("missing or extra attention document")
    values = {stage+"-"+c.id: c.value for stage, (filename, _, _) in STAGES.items()
              for c in nodes[filename].constants if c.id in PARAMETERS.values()}
    w = parameters(values)
    for name, expected in documents(w).items():
        if nodes[name] != expected or (directory/name).read_text() != render(expected):
            raise ValueError("unsupported or non-canonical attention document: "+name)
    graph = resolve(nodes["network.oak.md"], source="network.oak.md", load=lambda name: nodes[name])
    return w, graph


def oak_forward(directory: Path, data: dict) -> np.ndarray:
    w, graph = load(directory)
    x = inputs(data)
    def handler(stage: str):
        def run(_step, values):
            _, incoming, outgoing = STAGES[stage]
            a = [np.array(values[name], dtype=float) for name in incoming]
            local = {stage+"-"+name: np.array(values[slot]) for slot, name in PARAMETERS.items()}
            out, cache = attention(*a, local, stage)
            return {outgoing[0]: out.tolist(), outgoing[1]: cache[6].tolist()}
        return run
    tools = {"tensor.attention."+stage+".v1": ToolContract(handler(stage), frozenset(inc+list(PARAMETERS)), frozenset(out),
                  input=target(stage+"-action"), output=target(stage+"-output")) for stage, (_, inc, out) in STAGES.items()}
    tools["tensor.softmax.v1"] = ToolContract(lambda _s, v: {"PROB": softmax(np.array(v["LOGITS"])).tolist()},
                          frozenset(["LOGITS"]), frozenset(["PROB"]), input=target("decode"), output=target("prediction"))
    result = execute(graph.documents[graph.root], Arrival(interface="interface.input", values={k: v.tolist() for k, v in x.items()}),
                     {}, tools=tools, source=graph.root, load=lambda name: graph.documents[name])
    return np.array(result.emissions[0].values["PROB"])
