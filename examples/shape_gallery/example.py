"""Four populated fixed-cardinality shapes, authored once in the schema library.

Regenerate: python -m examples.shape_gallery.example in the repository.
The delivered OAK is self-contained and needs no execution host. Repeated slots
reuse a value; this lesson does not invent independently typed repeated rows.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if (ROOT / "oak").is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from examples.schemas.shape_gallery import build as build_shapes

TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    return build_shapes()


def write() -> Path:
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
