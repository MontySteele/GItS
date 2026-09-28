"""The seat glossary under Klee's and Furina's own relics (2026-09-27).

`review/active/relics-potions-klee-furina-2026-09-27.md`: four of Furina's
relics bend a rule a glossary row states outright. While the run holds one,
that row says so in one clause; without it, the row is unchanged.
"""

from __future__ import annotations

from understudy import blindplay_notes as notes

# The second text pass (2026-09-28): the fade has its own row, which
# Grand Theater Program's rider rides, so the face names it too.
FACE = ("Spend 2. Your back performer and your front performer take a Bow. "
        "Nobody fades.")


def _rows(held: list[str]) -> dict[str, str]:
    obs = {"character": "Furina", "stage_arm": True,
           "held_relics": [{"name": n, "text": "x"} for n in held],
           "hand": [{"title": "Some Card", "text": FACE}]}
    return {r["name"]: r["text"] for r in notes.keyword_notes(obs)}


def test_no_relic_no_rider():
    rows = _rows([])
    for word, riders in notes.RELIC_KEYWORD_RIDERS.items():
        assert word in rows
        for rider in riders.values():
            assert rider not in rows[word]


def test_each_held_relic_rides_its_row_once():
    held = [relic for riders in notes.RELIC_KEYWORD_RIDERS.values()
            for relic in riders]
    rows = _rows(held)
    for word, riders in notes.RELIC_KEYWORD_RIDERS.items():
        for rider in riders.values():
            assert rows[word].count(rider) == 1, word


def test_the_riders_name_the_relics_the_mod_prints():
    """Every rider is keyed by a relic title the C# declares, so a rename in
    the mod cannot leave a rider that never fires."""
    import re
    from pathlib import Path
    relics = Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode" / "Relics"
    titles = set()
    for path in relics.glob("*.cs"):
        titles |= set(re.findall(r'\("title",\s*"([^"]+)"\)',
                                 path.read_text(encoding="utf-8")))
    for riders in notes.RELIC_KEYWORD_RIDERS.values():
        assert set(riders) <= titles
