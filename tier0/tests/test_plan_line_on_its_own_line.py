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
# THE STATUS BATCH (2026-10-01, sec.3 pick 2): every Plan clause prints
# "Or plan:" (or "Or dusk plan:").
_CLAUSE = re.compile(
    r"Or (?:\[gold\]dusk\[/gold\] )?\[gold\]plan\[/gold\]:")


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
                before = before[:-len("Or ")] if before.endswith("Or ") \
                    else before
                seen += 1
                assert before == "" or before.endswith("\\n"), (
                    f"{path.name}: Plan clause not on its own line: {face}")
    assert seen >= 25


def test_the_status_batch_face_says_or():
    """THE STATUS BATCH (2026-10-01, sec.3 pick 2, [USER]: "Agreed on the
    Plan text change"). Every Plan line's keyword prints "Or plan:", the
    starter's Kurage's Oath and Slack Water included; a Dusk Plan prints
    "Or dusk plan:"; the sheet keeps "Plan:"."""
    def face(stem):
        text = (proto.OUT_DIR / f"{stem}.cs").read_text(encoding="utf-8")
        return _FACE.search(text).group(1)
    assert face("ProtoKkKuragesOath") == (
        "Gain {Block:diff()} [gold]Block[/gold].\\nOr [gold]plan[/gold]: "
        "Deal {PlanDamage:diff()} damage to ALL enemies.")
    assert "\\nOr [gold]plan[/gold]: " in face("ProtoKkSlackWater")
    assert "\\nOr [gold]dusk[/gold] [gold]plan[/gold]: " in face(
        "ProtoKkBreakwater")
    f = gen.plan_line_says_or
    row = {"plan": [{"op": "draw", "amount": 1}],
           "effects": [{"op": "block", "amount": 1}]}
    assert f(row, "Gain 1.\n[gold]Plan[/gold]: Draw 1.") == (
        "Gain 1.\nOr [gold]plan[/gold]: Draw 1.")
    # A row with no Plan line is untouched.
    assert f({"effects": []}, "Gain 1.\n[gold]Plan[/gold]: x") == (
        "Gain 1.\n[gold]Plan[/gold]: x")
