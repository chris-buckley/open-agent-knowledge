# Shape-first schema authoring report

## Outcome

The generated authoring prompt teaches information design rather than a default
labelled-record layout. It contains ordinary OAK schemas and populated examples
for comparison tables, decision briefs, nested outlines, and complete code files.
The same schemas drive an executable, explicitly linked OAK process pipeline.
No schema kind, grammar token, task-specific format, or dependency was added.

## Changed owners

- oak/rules/guidance.py owns the shape-selection and instance guidance.
- examples/AGENTS.md records the durable authoring correction.
- examples/schemas/shape_gallery.py authors the four reusable shapes and fixtures.
- examples/agents/shape_writer.py uses all four through typed calls and emissions.
- build/authoring.py includes compact schema/instance pairs and binds them to the
  authoring action; outputs/authoring.md is regenerated at 17,830 UTF-8 bytes.
- The interpreter-context example now has a sectioned title-review result.
- The process-execution table includes its Markdown delimiter row and explicitly
  describes one data row, not an unimplemented repeated-row binding.
- build/checks/shapes.py and existing registered checks cover the new examples.
- Affected sibling OAK renders and the accepted plan are committed with the source.

## Verification

Passed in the local isolated copy whose baseline Git tree matched main exactly:

```text
python -m compileall -q oak build examples
python -m build.examples
python build/examples.py
git diff --cached --check
```

The repository now registers 19 check groups. Checks cover exact populated output,
valid bindings, missing/extra/mistyped values, invalid table cells, lost delimiters,
ragged rows, nested indentation, Python fence structure, executable sample code,
non-recursive substitution, both OAK groupings, cross-document resolution, and
runtime rejection before promotion. The fixture host rejects unsupported requests.
Two further generation passes reproduced the staged Git tree exactly.

Local dependency versions: Pydantic 2.13.4, pydantic-extra-types 2.11.1,
pydantic-settings 2.14.1, and PyYAML 6.0.3. Local pydantic-settings is below the
repository's declared minimum, so the PR's separate GitHub verification installs
the declared dependencies before checking the published tree.

## Boundaries

The host is a deterministic fixture, not a measured comparison of model behaviour.
The example text substitution helper is not a production escaping or layout engine.
Presentation checks cover the committed fixtures, not arbitrary Markdown.
Schema binding still validates one value per placeholder. The generic repetition
sketch in [plan.md](plan.md) is design material only, not current language semantics.

Markdown reference: https://github.github.com/gfm/#tables-extension-
