<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
scenario-catalog: CSV<<
order,entry,lesson,omitted,requires,regenerate,detached,documents
1,fixed_knowledge/example.oak.md,Two fixed facts need no workflow.,"authored instructions, schemas, state, triggers, processes, interfaces",No action host.,python -m examples.fixed_knowledge.example (repository); python -m examples.catalog refreshes the complete bundle,python example.py,example.oak.md
2,shape_gallery/example.oak.md,"Compare, explain, outline, and present code with populated fixed-cardinality shapes.","authored instructions, state, triggers, processes, interfaces",No action host; regeneration imports the shared schema library.,python -m examples.shape_gallery.example (repository); python -m examples.catalog refreshes the complete bundle,OAK interpretation and resolution only; no action host is needed,example.oak.md
3,shape_writer/example.oak.md,Receive and CALL typed phases; emit four ordered shapes without state.,"constants, state",Fixture-only native host; regeneration imports shared shapes and bindings.,python -m examples.shape_writer.example (repository); python -m examples.catalog refreshes the complete bundle,python run.py,"example.oak.md, shape_gallery.oak.md, sample.oak.md"
4,compound_growth/example.oak.md,Carry committed state across two arrivals and discard staged writes on failure.,,Exact math.multiply fixture and deterministic reflection; no live model or automatic scheduler.,python -m examples.compound_growth.example (repository); python -m examples.catalog refreshes the complete bundle,python example.py,"example.oak.md, sample.oak.md"
5,interpreter_context/example.oak.md,Compare direct and OAK-context interpretation of one title policy.,"constants, state","Two deterministic adapters, not live model inference.",python -m examples.interpreter_context.example (repository); python -m examples.catalog refreshes the complete bundle,python example.py,example.oak.md
6,implementer/example.oak.md,Bind acceptance to the exact verified revision before a host effect.,state,"Detached script validates structure only. Execution needs native actions and the declared snapshot, verification, and commit tools; repository checks use a simulated commit sink.",python -m examples.implementer.example (repository); python -m examples.catalog refreshes the complete bundle,python example.py,"example.oak.md, verification.oak.md"
7,delegation/example.oak.md,Delegate through an exact tool while retaining the worker document scope.,"constants, schemas, state",Included deterministic agent.reviewer fixture; no live delegated model.,python -m examples.delegation.example (repository); python -m examples.catalog refreshes the complete bundle,python example.py,"example.oak.md, task_reviewer.oak.md"
8,successor/example.oak.md,"Separate amendment review, compilation, verification, and publication across arrivals.",,"Included fixed amendment and verification adapters; proof covers the fixture, not arbitrary amendment quality.",python -m examples.successor.example (repository); python -m examples.catalog refreshes the complete bundle,python example.py,"example.oak.md, amendment_reviewer.oak.md, successor_verifier.oak.md"
>>

delivery-boundary: "Run detached commands inside a copied scenario with OAK and its declared dependencies installed. The runtime is not vendored. Shared Python authoring imports require the repository; the shape gallery has no detached Python regeneration claim. Read each host disclosure. Scenario bindings.py files are generated from examples/bindings.py."

schema-library: CSV<<
source,document
schemas/api_coverage_table.py,schemas/api_coverage_table.oak.md
schemas/code_changes.py,schemas/code_changes.oak.md
schemas/code_map.py,schemas/code_map.oak.md
schemas/docs_index.py,schemas/docs_index.oak.md
schemas/error.py,schemas/error.oak.md
schemas/hierarchical_outline.py,schemas/hierarchical_outline.oak.md
schemas/ideation_list.py,schemas/ideation_list.oak.md
schemas/link_manifest.py,schemas/link_manifest.oak.md
schemas/process_execution_table.py,schemas/process_execution_table.oak.md
schemas/smeac_plan.py,schemas/smeac_plan.oak.md
schemas/shape_gallery.py,schemas/shape_gallery.oak.md
schemas/verification.py,schemas/verification.oak.md
>>
</constants>