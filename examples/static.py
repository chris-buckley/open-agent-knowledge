"""Static knowledge as an OAK composition: a team glossary.

Run this file to author and validate the composition.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "docs"))
from vocabulary_sketch import Constant, Instruction, Knowledge, Ref, Trigger

glossary = Knowledge(
    id="oak:knowledge/team-glossary",
    interpretation=[Ref(ref="oak:knowledge/team-glossary/quote-exactly")],
    children=[
        Trigger(
            id="oak:knowledge/team-glossary/on-term-lookup",
            type="trigger",
            when="someone asks what a team term means",
        ),
        Instruction(
            id="oak:knowledge/team-glossary/quote-exactly",
            type="instruction",
            body="Quote definitions exactly as written.",
        ),
        Constant(
            id="oak:knowledge/team-glossary/oak",
            type="constant",
            value="OAK is Open Agent Knowledge, the universal knowledge standard.",
        ),
        Constant(
            id="oak:knowledge/team-glossary/interpreter",
            type="constant",
            value="The interpreter is the human, agent, or program that interprets OAK knowledge before using it.",
        ),
        Constant(
            id="oak:knowledge/team-glossary/trigger",
            type="constant",
            value="A trigger is the node that signposts knowledge to the outside.",
        ),
    ],
)

if __name__ == "__main__":
    print(f"static ok: {glossary.id}, {len(glossary.children)} children")
