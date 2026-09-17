"""R274 pick 4 (2026-09-17): the companion sets a Klee player can meet are TWO.

`Hexerei` is the family word, printed on every face whose play pays Klee a
Spark (R265 pick 1, `EB-642`: every Hexerei card pays, Universals included),
and `Companion` is the keyword every companion card carries. The third word
the r12 run-2 seat met on 2026-09-04, "Klee's own Companions", was the Spark
tip as it stood before R265; [USER]'s own act-1 read retired it ("the
'Klee's own' text on the Personals is not needed"). `personal_pool` is a
SHELF fact -- which character the card is offered to -- and prints nowhere.

Two things keep that true, and both are pinned here rather than remembered:

* every prototype row in Klee's personal pool carries the Hexerei mark, so a
  personal card can never be a payer the family word does not cover. Thirteen
  of thirteen today; a fourteenth added without the tag would quietly recreate
  the third set the seat could not name.
* no game-facing string in the mod says "Klee's own". Comments may.

The shipped (Balance) arm still keys `PersonalPool == "klee"` in
`KleeCompanionSpark.PaysKleesSpark` because no shipped row carries `hexerei`
(R213 B): that is the surface the overhaul replaces when it ships, not a third
set on the arm anyone plays.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SHEET = ROOT / "docs" / "prototype-surface.yaml"
CODE = ROOT / "klee-mod" / "KleeCode"


def _klee_rows():
    rows = yaml.safe_load(SHEET.read_text(encoding="utf-8"))
    return [r for r in rows if isinstance(r, dict) and r.get("character") == "klee"]


def test_every_personal_pool_row_of_klees_is_hexerei():
    personal = [r for r in _klee_rows() if "klee" in (r.get("personal_pool") or [])]
    assert personal, "the personal pool emptied; the pin has nothing to hold"
    untagged = sorted(r["id"] for r in personal if not r.get("hexerei"))
    assert not untagged, (
        "a Klee personal companion without the Hexerei mark is a third set "
        f"the face cannot name (R274 pick 4): {untagged}")


def test_klees_own_is_a_shelf_fact_and_prints_nowhere():
    offenders = []
    for path in sorted(CODE.rglob("*.cs")):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("//", 1)[0]
            if re.search(r'"[^"]*Klee\'s own[^"]*"', code):
                offenders.append(f"{path.relative_to(ROOT)}:{n}")
    assert not offenders, (
        "a game-facing string names the third set R265 pick 1 retired: "
        f"{offenders}")
