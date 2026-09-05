"""Canonical OAK source for a restricted numerical network, not a new OAK grammar."""
from __future__ import annotations
from pathlib import Path
from oak import (ACT, Node, Constant, Schema, NonEmpty, where, Process, Call, Emit,
                 Interface, Trigger, BindingValue, ConstantValue, ValueBinding, render)
from runtime.numeric import parameters

SPEC = {
    "left": ("relations", ["X"], "left-values", "LEFT", "Select the first relation channel for two-hop composition."),
    "right": ("relations", ["X"], "right-values", "RIGHT", "Select the second relation channel for two-hop composition."),
    "compose": ("pair", ["LEFT", "RIGHT"], "counts", "COUNT", "Multiply the selected relation matrices to count two-hop support."),
    "readout": ("evidence", ["COUNT", "X"], "probabilities", "PROB", "Score support while suppressing explicitly vetoed entity pairs."),
}


def target(name):
    return "contracts.oak.md#schema." + name


def bindings(names):
    return [ValueBinding(placeholder=k, value=BindingValue(binding=k)) for k in names]


def schema(name, names):
    return Schema(id=name, name="Tensor Payload", purpose="Carry complete float64 tensors checked by the numerical host.",
                  template="\n".join(f"{k}: <{k}>" for k in names),
                  where=[where(k, NonEmpty(), description="a finite rectangular numerical tensor with exact dimensions are checked by the profile") for k in names])


def documents(values: dict) -> dict[str, Node]:
    w = parameters(values)
    shapes = {"relations": ["X"], "pair": ["LEFT", "RIGHT"], "evidence": ["COUNT", "X"],
              "left-values": ["LEFT"], "right-values": ["RIGHT"], "counts": ["COUNT"],
              "probabilities": ["PROB"], "parameters": ["W"]}
    for owner, (inp, names, out, output, role) in SPEC.items():
        shapes[owner+"-action"] = names+["W"]
    docs = {"contracts.oak.md": Node(schemas=[schema(k, v) for k, v in shapes.items()])}
    for owner, (inp, names, out, output, role) in SPEC.items():
        docs[owner+".oak.md"] = Node(
            constants=[Constant(id="weights", schema=target("parameters"), placeholder="W", value=w[owner].tolist()),
                       Constant(id="responsibility", value=role),
                       Constant(id="trainable", value=owner != "compose")],
            processes=[Process(id="forward", name="Compute tensor", input=target(inp), output=target(out),
                steps=[ACT.tool("tensor."+owner+".v1", "Apply the fixed numerical operator to "+", ".join("<"+k+">" for k in names+["W"])+" to produce <"+output+">.",
                      input=target(owner+"-action"), output=target(out),
                      inputs=bindings(names)+[ValueBinding(placeholder="W", value=ConstantValue(constant="constant.weights"))],
                      outputs=[output])])])
    docs["network.oak.md"] = Node(
        constants=[Constant(id="profile", value="oak-two-hop-v1"),
                   Constant(id="input-shape", value=["batch", 4, 4, 3]),
                   Constant(id="dtype", value="float64"), Constant(id="threshold", value=.5)],
        triggers=[Trigger(id="request", event="Numerical relation tensors arrive.", source="interface.input", process="process.infer")],
        processes=[Process(id="infer", name="Infer relations", input=target("relations"), output=target("probabilities"),
            steps=[Call(process=k+".oak.md#process.forward", inputs=bindings(v[1]), outputs=[v[3]]) for k, v in SPEC.items()]
                  +[Emit(interface="interface.output")])],
        interfaces=[Interface(id="input", flow="receives", schema=target("relations")),
                    Interface(id="output", flow="emits", schema=target("probabilities"))])
    return docs


def write(values: dict, directory: Path):
    directory.mkdir(parents=True, exist_ok=False)
    for name, doc in documents(values).items():
        (directory/name).write_text(render(doc), encoding="utf-8")
