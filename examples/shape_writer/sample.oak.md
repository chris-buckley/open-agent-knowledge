<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
request: {"REQUEST": "Reject blank task titles with one Python predicate."}

steps: [{"schema": "shape_gallery.oak.md#schema.option-comparison", "interface": "interface.comparison", "input": {"REQUEST": "Reject blank task titles with one Python predicate."}, "output": {"CRITERION": "Blank title", "CURRENT": "Accepted", "PROPOSED": "Rejected"}}, {"schema": "shape_gallery.oak.md#schema.decision-brief", "interface": "interface.decision", "input": {"CRITERION": "Blank title", "CURRENT": "Accepted", "PROPOSED": "Rejected"}, "output": {"DECISION": "Reject blank titles.", "RATIONALE": "A title must identify the task."}}, {"schema": "shape_gallery.oak.md#schema.work-outline", "interface": "interface.outline", "input": {"DECISION": "Reject blank titles.", "RATIONALE": "A title must identify the task."}, "output": {"GOAL": "Require meaningful titles.", "STEP": "Check the stripped title.", "CHECK": "Test empty, whitespace, and valid titles."}}, {"schema": "shape_gallery.oak.md#schema.code-file", "interface": "interface.file", "input": {"GOAL": "Require meaningful titles.", "STEP": "Check the stripped title.", "CHECK": "Test empty, whitespace, and valid titles."}, "output": {"FILE_PATH": "title.py", "CODE": "def valid_title(title: str) -> bool:\n    return bool(title.strip())"}}]

host: "A deterministic adapter supports only this fixture, not arbitrary requests or live inference."
</constants>