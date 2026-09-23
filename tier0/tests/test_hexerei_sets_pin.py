"""R274 pick 4 (2026-09-17), re-read under R276 pick 2: the companion set a
Klee player can meet is ONE.

R274 counted two words -- `Hexerei`, the family mark printed on every face whose
play paid Klee a Spark, and `Companion`. R276 pick 2 retired the first: ANY
Companion card pays the Spark and feeds her three readers, so the set the face
names and the set that pays are the same set, `Companion`. The third word the
r12 run-2 seat met, "Klee's own Companions", stays retired; `personal_pool` is
a SHELF fact -- which character the card is offered to -- and prints nowhere.

Two things keep that true, and both are pinned here rather than remembered:

* no prototype row carries the retired `hexerei:` key, so no face can print a
  second family word again;
* no game-facing string in the mod says "Klee's own". Comments may.
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


def test_no_klee_row_carries_the_retired_family_mark():
    rows = _klee_rows()
    assert rows, "the sheet emptied; the pin has nothing to hold"
    marked = sorted(r["id"] for r in rows if "hexerei" in r)
    assert not marked, (
        "R276 pick 2 retired the Hexerei mark; a row carrying it names a "
        f"second companion set the rules no longer read: {marked}")
    printed = sorted(r["id"] for r in rows
                     if "Hexerei" in str(r.get("description", "")))
    assert not printed, printed


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
