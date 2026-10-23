"""Klee text-only fixes (2026-10-13, [USER]: "Let's go with (a). Minor text
cleanup doesn't need a whole character stage branch,"). Four one-card riders,
each a fact the code decides and the face left a seat unsure of, and the Set
off and Mine tips' added clauses. No number and no rule moves."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools import gen_klee_cards as gen  # noqa: E402

GENERATED = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
TIPS_CS = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "ArmKeywordTips.cs"
MOD_CS = REPO / "klee-mod" / "KleeCode" / "KleeMod.cs"

RIDERS = {
    "ProtoKoBigBaddaBoom": ("ForBigBaddaBoomTotal", "BigBaddaBoomTotalKey"),
    "ProtoKoBoomBadge": ("ForBoomBadgeTurn", "BoomBadgeTurnKey"),
    "ProtoMcJeanLionsFang": ("ForLionsFangLastTurn", "LionsFangLastTurnKey"),
    "ProtoKoPassTheMatch": ("ForPassTheMatchActing", "PassTheMatchActingKey"),
}


@pytest.mark.parametrize("stem", sorted(RIDERS))
def test_each_rider_rides_its_card_and_has_a_title(stem):
    method, key = RIDERS[stem]
    card = (GENERATED / f"{stem}.cs").read_text(encoding="utf-8")
    assert f"ArmKeywordTips.{method}(" in card
    assert f"IEnumerable<IHoverTip> {method}(" in TIPS_CS.read_text(
        encoding="utf-8")
    assert f"ArmKeywordTips.{key} + \".title\"" in MOD_CS.read_text(
        encoding="utf-8")


def test_no_other_card_carries_the_riders():
    methods = {m for m, _ in RIDERS.values()}
    for path in GENERATED.glob("*.cs"):
        text = path.read_text(encoding="utf-8")
        for method in methods:
            if f"ArmKeywordTips.{method}(" in text:
                assert RIDERS.get(path.stem, ("",))[0] == method, path.stem


def test_the_rider_table_is_asked_of_effects():
    assert gen.klee_text_rider_calls(
        {"effects": [{"op": "damage_set_off_total", "target": "enemy"}]}) == [
        "ArmKeywordTips.ForBigBaddaBoomTotal"]
    assert gen.klee_text_rider_calls(
        {"effects": [{"op": "apply_power", "power": "ko_dodoco"}]}) == []


def test_the_tips_say_what_the_code_does():
    sys.path.insert(0, str(REPO))
    from tools import lint_text_conventions as ltc
    tips = {row.ident: ltc.render(row.raw) for row in ltc.tip_rows()}
    assert "Bombs on other enemies stay." in tips["SetOffKey"]
    assert "The enemy's other Bombs stay." in tips["MineKey"]
    for ident in ("BigBaddaBoomTotalKey", "BoomBadgeTurnKey",
                  "LionsFangLastTurnKey", "PassTheMatchActingKey"):
        assert ident in tips, ident
        assert len(tips[ident]) <= 135
        assert len(re.findall(r"[.!?](?:\s|$)", tips[ident])) <= 2, ident
