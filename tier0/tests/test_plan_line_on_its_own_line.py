"""Two 2026-09-28 rulings on Kokomi's Plan cards.

1. Kurage's Oath, [USER]: "The non-plan effect is quite bad (worse than a
   basic defend)" ... "Option 1 is fine for now." Now-line 6 Block; the
   upgrade moves both halves (8 Block / Plan 10 to ALL).
2. [USER]: "Can we move all Plan lines to the next line down?" Every emitted
   face that prints a Plan clause starts it on a new line, done once in
   `gen_klee_cards.plan_line_on_its_own_line`; the sheet keeps one-line prose.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import gen_klee_cards as gen                    # noqa: E402
import gen_prototype_cards as proto             # noqa: E402

_FACE = re.compile(r'\("description", "(.*?)"\),\n', re.S)
_CLAUSE = re.compile(r"(?:\[gold\]Dusk\[/gold\] )?\[gold\]Plan\[/gold\]:")


def test_kurages_oath_now_line_is_six_and_upgrades_both_halves():
    row = next(c for c in proto._rows() if c["id"] == "proto_kk_kurages_oath")
    assert row["effects"] == [{"op": "block", "amount": 6}]
    assert row["plan"] == [{"op": "damage", "amount": 7,
                            "target": "all_enemies"}]
    assert row["upgrade"] == {"block": 2, "plan_damage": 3}
    text = (proto.OUT_DIR / "ProtoKkKuragesOath.cs").read_text(
        encoding="utf-8")
    assert "new BlockVar(6m, ValueProp.Move)" in text
    assert "DynamicVars.Block.UpgradeValueBy(2m);" in text
    assert 'DynamicVars["PlanDamage"].UpgradeValueBy(3m);' in text


def test_the_break_is_a_plan_clause_only():
    f = gen.plan_line_on_its_own_line
    assert f("Gain 6 [gold]Block[/gold]. [gold]Plan[/gold]: Draw 1.") == (
        "Gain 6 [gold]Block[/gold].\n[gold]Plan[/gold]: Draw 1.")
    assert f("Draw 1. [gold]Dusk[/gold] [gold]Plan[/gold]: Gain 5.") == (
        "Draw 1.\n[gold]Dusk[/gold] [gold]Plan[/gold]: Gain 5.")
    # A face that opens with its Plan, and a sentence ABOUT a Plan, stay.
    for same in ("[gold]Plan[/gold]: Draw 1.",
                 "Cancel your last [gold]Plan[/gold]: its card returns.",
                 "if a [gold]Plan[/gold] was carried out this turn."):
        assert f(same) == same


def test_every_emitted_plan_clause_opens_a_line():
    seen = 0
    for path in sorted(proto.OUT_DIR.glob("*.cs")):
        for face in _FACE.findall(path.read_text(encoding="utf-8")):
            for m in _CLAUSE.finditer(face):
                before = face[:m.start()]
                if before.endswith("your last "):   # Change of Plans' verb
                    continue
                seen += 1
                assert before == "" or before.endswith("\\n"), (
                    f"{path.name}: Plan clause not on its own line: {face}")
    assert seen >= 25
