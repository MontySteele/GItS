"""Design-session calls on the backlog triage hand-back (2026-10-13).

Text only; no number or behavior moves:

  * Lynette's Guest Star line reads "The first time each turn you lose HP to
    an enemy, gain double Fanfare." and her tip fits the 135 ceiling with no
    lint exception;
  * (Bis!'s face and rider left with Bis!, furina-next paper 2,
    2026-10-16: `test_furina_extended_run`.)
  * Four Winds' Ascension's hover says its element hit gains no Oath.
  * (Wolfpack's play line: `test_varka_payoff_seat_page`.)
"""
from __future__ import annotations

from pathlib import Path

from tier0.tests.test_arm_keyword_tips import (  # noqa: E402
    PROTOTYPE_DIR, TIPS_CS, gen, proto)

ROOT = Path(__file__).resolve().parents[2]
POWERS = ROOT / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
LINT = ROOT / "tools" / "lint_text_conventions.py"


def _rows() -> dict[str, dict]:
    return {r["id"]: r for r in proto._rows()}


def test_lynettes_line_reads_that_much_again_and_needs_no_exception():
    badges = (POWERS / "FurinaStageBadges.cs").read_text(encoding="utf-8")
    assert ('"The first time each turn you lose HP to an enemy, gain that much "'
            in badges)
    assert "an enemy makes you lose HP" not in badges
    assert '"LynetteKey"' not in LINT.read_text(encoding="utf-8")
    # Rendered (Act 5, the base number), golds stripped: under the ceiling
    # (the guest package, 2026-10-13, reworded the line and the act).
    tip = ("The first time each turn you lose HP to an enemy, gain that much "
           "Fanfare again. Act: deal 5 Anemo damage to an enemy, aura first.")
    assert len(tip) <= 135


def test_bis_rider_left_with_bis():
    face = (PROTOTYPE_DIR / "ProtoFsBis.cs").read_text(encoding="utf-8")
    assert "ForBisSpendUpTo" not in face
    assert "ForBisSpendUpTo" not in TIPS_CS.read_text(encoding="utf-8")
    assert not hasattr(gen, "keeps_half_a_spend_all")


def test_four_winds_ascension_says_its_hit_gains_no_oath():
    src = (PROTOTYPE_DIR / "ProtoVkFourWindsAscension.cs").read_text(
        encoding="utf-8")
    assert "ArmKeywordTips.ForAscensionNoOath(" in src
    assert '"This hit does not gain Oath."' in TIPS_CS.read_text(
        encoding="utf-8")
    for rid, row in _rows().items():
        assert gen.ascension_hit_gains_no_oath(row) == (
            rid == "proto_vk_four_winds_ascension"), rid
