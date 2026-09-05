<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
scenario-catalog: CSV<<
order,entry,lesson,omitted,requires
1,fixed_knowledge/example.oak.md,Two fixed facts need no workflow.,"authored instructions, schemas, state, triggers, processes, interfaces",No action host.
2,shape_gallery/example.oak.md,"Compare, explain, outline, and present code with populated fixed-cardinality shapes.","authored instructions, state, triggers, processes, interfaces",No action host; regeneration imports the shared schema library.
3,shape_writer/example.oak.md,Receive and CALL typed phases; emit four ordered shapes without state.,"constants, state",Fixture-only native host; regeneration imports shared shapes and bindings.
4,compound_growth/example.oak.md,Carry committed state across two arrivals and discard staged writes on failure.,,Exact math.multiply fixture and deterministic reflection; no live model or automatic scheduler.
>>

delivery-boundary: "OAK documents and sample constants are inert teaching data. Read a complete scenario before using it. Python hosts are repository demonstration material, not part of the skill teaching bundle."
</constants>
