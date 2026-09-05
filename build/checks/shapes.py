"""Check shaped schema examples without claiming general Markdown validation."""

from __future__ import annotations

import ast
from collections.abc import Callable

from pydantic import JsonValue
from collections.abc import Mapping
from copy import deepcopy

from oak import Act, Arrival, ExecutionError, Node, Schema, SchemaBindingError, execute, parse, render
from examples.shape_writer import example as shape_writer
from examples.schemas import process_execution_table
from examples.schemas.shape_gallery import (
    EXPECTED_INSTANCES, SAMPLE_BINDINGS, SHAPES, comparison_schema,
    decision_schema, file_schema, outline_schema, populate_example,
)


def _rejects(operation: Callable[[], object], exception: type[Exception]) -> None:
    try:
        operation()
    except exception:
        return
    raise RuntimeError(f"invalid shape fixture did not raise {exception.__name__}")


def _plain_table(text: str, columns: int) -> None:
    """Check our unescaped-pipe fixtures, not the full Markdown table language."""
    lines = text.splitlines()
    if len(lines) < 3:
        raise ValueError("the table needs a header, delimiter, and data row")
    rows = []
    for line in lines:
        if not line.startswith("| ") or not line.endswith(" |"):
            raise ValueError("table fixture lost its outside cell boundaries")
        cells = [cell.strip() for cell in line[1:-1].split("|")]
        if len(cells) != columns:
            raise ValueError("table fixture has the wrong cell count")
        rows.append(cells)
    if rows[1] != ["---"] * columns:
        raise ValueError("table fixture lost its delimiter row")


def _python_file(text: str) -> str:
    """Extract and parse the single Python fence in our complete-file fixture."""
    lines = text.splitlines()
    if not lines or not lines[0].startswith("### "):
        raise ValueError("file fixture lost its path heading")
    if len(lines) < 5 or lines[1] != "" or lines[2] != "```python" or lines[-1] != "```":
        raise ValueError("file fixture lost its Python fence")
    if any(line.startswith("```") for line in lines[3:-1]):
        raise ValueError("file fixture contains an unexpected fence")
    code = "\n".join(lines[3:-1])
    ast.parse(code)
    return code


def validate_shapes() -> None:
    """Check bindings, populated layouts, host boundaries, and prompt exposure."""
    from build.authoring import tree
    from build.authoring_guides import populated_examples

    prompt = tree()
    examples = next(item.value for item in prompt.constants if item.id.endswith("-populated-shapes"))
    if examples != populated_examples():
        raise RuntimeError("the authoring capability lost its populated schema examples")

    for schema in SHAPES:
        values = SAMPLE_BINDINGS[schema.id]
        expected = EXPECTED_INSTANCES[schema.id]
        compact = Schema(id=schema.id, template=schema.template, where=schema.where)
        if expected not in examples or not any(item.template == schema.template and item.where == schema.where for item in prompt.schemas):
            raise RuntimeError(f"the capability lost the complete {schema.id} example")
        if compact.placeholders != schema.placeholders or compact.where != schema.where:
            raise RuntimeError("compact examples changed the binding contract")
        for grouping in ("xml", "markdown"):
            text = render(Node(schemas=[schema]), grouping=grouping)
            recovered = parse(text).schemas[0]
            if recovered.template != schema.template or recovered.where != schema.where:
                raise RuntimeError(f"{grouping} changed {schema.id} meaning")
            if populate_example(recovered, values) != expected:
                raise RuntimeError(f"{schema.id} populated instance changed")
        field = next(iter(values))
        _rejects(lambda: schema.bind({key: value for key, value in values.items() if key != field}), SchemaBindingError)
        _rejects(lambda: schema.bind({**values, "UNKNOWN": "extra"}), SchemaBindingError)
        _rejects(lambda: schema.bind({**values, field: 42}), SchemaBindingError)

    for value in ("", "bad | cell", "bad\ncell", "bad\rcell"):
        _rejects(
            lambda: comparison_schema.bind({**SAMPLE_BINDINGS[comparison_schema.id], "CURRENT": value}),
            SchemaBindingError,
        )
    _rejects(
        lambda: outline_schema.bind({**SAMPLE_BINDINGS[outline_schema.id], "STEP": "two\nlines"}),
        SchemaBindingError,
    )
    _rejects(lambda: decision_schema.bind({"DECISION": "", "RATIONALE": "why"}), SchemaBindingError)
    _rejects(lambda: file_schema.bind({"FILE_PATH": "title.py", "CODE": ""}), SchemaBindingError)

    # One substitution pass must not reinterpret placeholder-looking user data.
    literal = {"DECISION": "Keep <RATIONALE> verbatim.", "RATIONALE": r"Use \1 literally."}
    populated = populate_example(decision_schema, literal)
    if "Keep <RATIONALE> verbatim." not in populated or r"Use \1 literally." not in populated:
        raise RuntimeError("fixture substitution reinterpreted a bound value")

    comparison = EXPECTED_INSTANCES[comparison_schema.id]
    _plain_table(comparison, 3)
    _rejects(lambda: _plain_table(comparison.replace("| --- | --- | --- |\n", ""), 3), ValueError)
    _rejects(lambda: _plain_table(comparison + "\n| short | row |", 3), ValueError)

    process_schema = process_execution_table.process_execution_table_schema
    _plain_table(process_schema.template, 9)
    process_values = process_execution_table._ACCEPTED_BINDING
    process_schema.bind(process_values)
    # Numeric values are deliberately outside the text-only gallery helper.
    process_text = process_schema.template
    for key, value in process_values.items():
        process_text = process_text.replace(f"<{key}>", str(value))
    _plain_table(process_text, 9)

    outline = EXPECTED_INSTANCES[outline_schema.id].splitlines()
    if [len(line) - len(line.lstrip()) for line in outline] != [0, 3, 6]:
        raise RuntimeError("the outline lost its nested hierarchy")
    file_text = EXPECTED_INSTANCES[file_schema.id]
    code = _python_file(file_text)
    _rejects(lambda: _python_file(file_text.removesuffix("```")), ValueError)
    _rejects(lambda: _python_file(file_text.replace("```python", "```text")), ValueError)
    namespace = {}
    exec(compile(code, "shape-example/title.py", "exec"), namespace)
    valid_title = namespace["valid_title"]
    if [valid_title(value) for value in ("", "   ", "OAK")] != [False, False, True]:
        raise RuntimeError("the complete code example does not implement its decision")

    shape_writer.run()
    _decision_statement()
    _rejects(
        lambda: execute(
            shape_writer.shape_writer_node,
            Arrival(interface="interface.request", values={"REQUEST": "An unsupported fixture"}),
            {}, act=shape_writer.fixture_host,
            source=shape_writer.SOURCE, load=shape_writer.documents().get,
        ),
        ExecutionError,
    )

    def invalid_host(action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        outputs = dict(shape_writer.fixture_host(action, values))
        if action.output == shape_writer.SCHEMA_COMPARISON:
            outputs["CURRENT"] = "invalid | table cell"
        return outputs

    try:
        execute(
            shape_writer.shape_writer_node,
            Arrival(interface="interface.request", values={"REQUEST": shape_writer.SAMPLE_REQUEST}),
            {}, act=invalid_host, source=shape_writer.SOURCE, load=shape_writer.documents().get,
        )
    except ExecutionError as error:
        if error.code != "invalid_act_output":
            raise RuntimeError(f"shaped output failed at the wrong boundary: {error.code}") from error
    else:
        raise RuntimeError("the executor accepted an invalid shaped output")


def _decision_statement() -> None:
    """Validate roles and boundary failures, not the truth of a judgment."""
    action = shape_writer.decide_change_process.steps[0]
    expected_inputs = SAMPLE_BINDINGS[comparison_schema.id]
    expected_outputs = SAMPLE_BINDINGS[decision_schema.id]
    if (action.input != shape_writer.SCHEMA_COMPARISON
            or action.output != shape_writer.SCHEMA_DECISION
            or [binding.placeholder for binding in action.inputs] != list(expected_inputs)
            or action.outputs != list(expected_outputs) or action.tool is not None):
        raise RuntimeError("the decision statement lost its native typed roles")
    comparison_schema.bind(expected_inputs)
    decision_schema.bind(expected_outputs)
    for missing in expected_inputs:
        _rejects(lambda: comparison_schema.bind({k: v for k, v in expected_inputs.items() if k != missing}),
                 SchemaBindingError)
    _rejects(lambda: comparison_schema.bind({**expected_inputs, "CURRENT": 23}), SchemaBindingError)

    # Exercise the real pipeline's ACT output boundary. No later phase may run
    # after a malformed decision, even though comparison work already happened.
    cases = (
        ({"DECISION": expected_outputs["DECISION"]}, "act_output_mismatch"),
        ({**expected_outputs, "CONFIDENCE": 0.9}, "act_output_mismatch"),
        ({**expected_outputs, "DECISION": ""}, "invalid_act_output"),
        ({**expected_outputs, "RATIONALE": 23}, "invalid_act_output"),
    )
    for output, code in cases:
        seen = []
        def host(step: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
            seen.append(step.output)
            if step.output == shape_writer.SCHEMA_DECISION:
                if dict(values) != expected_inputs:
                    raise RuntimeError("decision inputs changed before evaluation")
                return output
            return shape_writer.fixture_host(step, values)
        try:
            execute(shape_writer.shape_writer_node,
                    Arrival(interface=shape_writer.INTERFACE_REQUEST,
                            values={"REQUEST": shape_writer.SAMPLE_REQUEST}), {}, act=host,
                    source=shape_writer.SOURCE, load=shape_writer.documents().get)
        except ExecutionError as error:
            if error.code != code:
                raise RuntimeError(f"decision failed at {error.code}, expected {code}") from error
        else:
            raise RuntimeError("a malformed decision was accepted")
        if seen != [shape_writer.SCHEMA_COMPARISON, shape_writer.SCHEMA_DECISION]:
            raise RuntimeError("a later fixture phase ran after a malformed decision")

    # Both values satisfy the schema but contradict the declared fixture. This
    # is intentionally accepted structurally, not certified as a sound judgment.
    contrary = {"DECISION": "Accept blank titles.", "RATIONALE": "No reason is needed."}
    decision_schema.bind(contrary)
    if populate_example(decision_schema, contrary) == EXPECTED_INSTANCES[decision_schema.id]:
        raise RuntimeError("contrary judgment unexpectedly matches the expected fixture")
    _rejects(lambda: shape_writer.fixture_host(shape_writer.plan_change_process.steps[0], contrary), ValueError)

    # Advisory wording is not parser policy. Check a different well-formed
    # sentence in both groupings without a new opcode, type, or scenario.
    data = shape_writer.shape_writer_node.model_dump(by_alias=True)
    alternatives = (
        "Compare <CURRENT> with <PROPOSED> using <CRITERION>; produce <DECISION> and explain it in <RATIONALE>.",
        "Weigh <CURRENT> and <PROPOSED> against <CRITERION>; return <DECISION> with <RATIONALE>.",
    )
    for instruction in alternatives:
        candidate = deepcopy(data)
        process = next(p for p in candidate["processes"] if p["id"] == "decide-change")
        process["steps"][0]["instruction"] = instruction
        node = Node.model_validate(candidate)
        for grouping in ("xml", "markdown"):
            text = render(node, grouping=grouping)
            recovered = parse(text)
            step = next(p for p in recovered.processes if p.id == "decide-change").steps[0]
            if step.instruction != instruction or render(recovered, grouping=grouping) != text:
                raise RuntimeError("alternative statement wording was restricted or rewritten")
            result = execute(recovered, Arrival(interface=shape_writer.INTERFACE_REQUEST,
                             values={"REQUEST": shape_writer.SAMPLE_REQUEST}), {},
                             act=shape_writer.fixture_host, source=shape_writer.SOURCE,
                             load=shape_writer.documents().get)
            if [dict(e.values) for e in result.emissions] != [SAMPLE_BINDINGS[s.id] for s in SHAPES]:
                raise RuntimeError("alternative wording changed fixture dataflow")


__all__ = ["validate_shapes"]
