"""`EB-677`: Glam's Replay on a timed card adds its turns, and Glam's own
row now says so (behaviour unchanged). Pinned on the source row, as
`test_eb521_thorns_prints_its_trigger` pins Thorns'.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

from pathlib import Path

SRC = (Path(__file__).resolve().parents[2]
       / "klee-mod" / "KleeCode" / "KleeMod.cs").read_text(encoding="utf-8")


def test_glam_row_keeps_the_shipped_sentence_and_adds_the_rule():
    start = SRC.index('GetTable("enchantments")')
    row = SRC[start:SRC.index("});", start)]
    assert '["GLAM.description"] =' in row
    text = "".join(part.split('"')[1] for part in row.split("\n")
                   if part.strip().startswith(('"', '+ "')))
    assert text == ("This card has [gold]Replay[/gold] once per combat. "
                    "Replaying a card with turns adds its turns.")
    # One added sentence, inside the tip ceiling.
    assert len("Replaying a card with turns adds its turns.") <= 135
