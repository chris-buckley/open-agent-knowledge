"""Author one OAK tree and write its render to outline.oak.md."""

import pathlib

from oak import (
    Constant,
    Instruction,
    Interface,
    Lines,
    MaxChars,
    Node,
    NonEmpty,
    Process,
    Regex,
    Root,
    Schema,
    State,
    Trigger,
    Type,
    schema_xml,
    where,
)

request = Schema(
    id="oak:schema/outline-request",
    name="Outline Request",
    purpose="Describe the topic to outline.",
    template="<TOPIC>",
    where=[
        where(
            "TOPIC",
            Type(of="string"),
            NonEmpty(),
            description="topic to outline",
        )
    ],
)

outline = Schema(
    id="oak:schema/outline",
    name="Hierarchical Outline",
    purpose="Generate a semantic multilevel numbered outline, one space of indentation per level.",
    template="""## <OUTLINE_TITLE>

<LEVEL_1_NUMBER> <STATEMENT>
 <LEVEL_2_NUMBER> <STATEMENT>
  <LEVEL_3_NUMBER> <STATEMENT>
...
""",
    where=[
        where(
            "OUTLINE_TITLE",
            Type(of="string"),
            MaxChars(n=80),
            description="title for the outline",
        ),
        where(
            "LEVEL_1_NUMBER",
            Regex(pattern="^[0-9]+$"),
            examples=["1", "2"],
        ),
        where(
            "LEVEL_2_NUMBER",
            Regex(pattern="^[0-9]+[.][0-9]+$"),
            examples=["1.1", "1.2"],
        ),
        where(
            "LEVEL_3_NUMBER",
            Regex(pattern="^[0-9]+[.][0-9]+[.][0-9]+$"),
            examples=["1.1.1"],
            description="maximum depth",
        ),
        where(
            "STATEMENT",
            Lines(max=1),
            description="one atomic topic, instruction, or information, no obvious statements",
        ),
    ],
)

root = Root(
    id="oak:root",
    instructions=[
        Instruction(
            part="instructions",
            id="oak:instruction/schema",
            body="Use the outline schema for every outline.",
        ),
    ],
    constants=[
        Constant(
            part="constants",
            id="oak:constant/tz",
            name="DEFAULT_TZ",
            value="Z",
        ),
    ],
    schemas=[request, outline],
    state=[
        State(
            part="state",
            id="oak:state/status",
            name="STATUS",
            value="ready",
        ),
    ],
    triggers=[
        Trigger(
            part="triggers",
            id="oak:trigger/write",
            when="The interpreter arrives to write an outline.",
            process="oak:process/write",
        ),
    ],
    processes=[
        Process(
            part="processes",
            id="oak:process/write",
            name="Write an outline",
            consumes=["oak:interface/request"],
            emits=["oak:interface/outline"],
            steps=["Collect the topic.", "Emit the outline schema."],
        ),
    ],
    interfaces=[
        Interface(
            part="interfaces",
            id="oak:interface/request",
            direction="in",
            schema="oak:schema/outline-request",
            description="The topic supplied to the outline process.",
        ),
        Interface(
            part="interfaces",
            id="oak:interface/outline",
            direction="out",
            schema="oak:schema/outline",
            description="The outline returned by the outline process.",
        ),
    ],
    children=[Node(id="oak:node/child")],
)

target = pathlib.Path(__file__).with_name("outline.oak.md")
target.write_text(schema_xml(outline) + "\n", encoding="utf-8", newline="\n")
print(f"wrote {target}")
