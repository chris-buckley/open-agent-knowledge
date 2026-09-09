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
6,local_contracts/example.oak.md,Explain public boundaries locally and adapt a separately typed private worker.,"authored instructions, state","The complete scenario supplies its graph and a deterministic trimming host; the entry alone is boundary-complete, not execution-complete. No external effects or live model.",python -m examples.local_contracts.example (repository); python -m examples.catalog refreshes the complete bundle,python example.py,"example.oak.md, worker.oak.md, sample.oak.md"
7,implementer/example.oak.md,Bind acceptance to the exact verified revision before a host effect.,state,"Detached script validates structure only. Execution needs native actions and the declared snapshot, verification, and commit tools; repository checks use a simulated commit sink.",python -m examples.implementer.example (repository); python -m examples.catalog refreshes the complete bundle,python example.py,"example.oak.md, verification.oak.md"
8,delegation/example.oak.md,Delegate through an exact tool while retaining the worker document scope.,"constants, schemas, state",Included deterministic agent.reviewer fixture; no live delegated model.,python -m examples.delegation.example (repository); python -m examples.catalog refreshes the complete bundle,python example.py,"example.oak.md, task_reviewer.oak.md"
9,parallel_exploration/example.oak.md,"Dispatch two independent exact tools, JOIN validated reports, and reconcile evidence.","authored instructions, state","Repository-only deterministic fixture workers; native Codex TOML is a separate artifact, not a host adapter or live permission proof.",python -m examples.parallel_exploration.example (repository); python -m examples.catalog refreshes the complete bundle,OAK inspection only; the action demonstration requires repository sources,"example.oak.md, explorer.oak.md, sample.oak.md"
10,successor/example.oak.md,"Separate amendment review, compilation, verification, and publication across arrivals.",,"Included fixed amendment and verification adapters; proof covers the fixture, not arbitrary amendment quality.",python -m examples.successor.example (repository); python -m examples.catalog refreshes the complete bundle,python example.py,"example.oak.md, amendment_reviewer.oak.md, successor_verifier.oak.md"
11,skill_profiles/example.oak.md,Select one stateless foundation or owned memory extension and reuse a separate classifier.,authored instructions,"Complete package maps are inert constants; repository-only file fixtures verify synthetic instances, not installed-host discovery or live effects.",python -m examples.skill_profiles.example (repository); python -m examples.catalog refreshes the complete bundle,OAK interpretation and resolution only; no action host is needed,"example.oak.md, classifier.oak.md, memory.oak.md, packages.oak.md, sample.oak.md"
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