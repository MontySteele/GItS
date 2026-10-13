"""Design-session calls on the backlog triage hand-back (2026-10-13).

Text only; no number or behavior moves:

  * Lynette's Guest Star line reads "The first time each turn you lose HP to
    an enemy, gain double Fanfare." and her tip fits the 135 ceiling with no
    lint exception;
  * Bis! says a card Spends all your Fanfare, and its hover says a "Spend up
    to" card does not count;
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


def test_bis_face_and_hover_say_which_spends_count():
    assert _rows()["proto_fs_bis"]["description"] == (
        "Whenever a card [gold]Spends[/gold] all your [gold]Fanfare[/gold], "
        "keep half of it.")
    face = (PROTOTYPE_DIR / "ProtoFsBis.cs").read_text(encoding="utf-8")
    assert "Whenever a card [gold]Spends[/gold] all your" in face
    assert "ArmKeywordTips.ForBisSpendUpTo(" in face
    assert ('"A card that [gold]Spends[/gold] up to an amount does not count, "'
            in TIPS_CS.read_text(encoding="utf-8"))
    for rid, row in _rows().items():
        assert gen.keeps_half_a_spend_all(row) == (rid == "proto_fs_bis"), rid


def test_four_winds_ascension_says_its_hit_gains_no_oath():
    src = (PROTOTYPE_DIR / "ProtoVkFourWindsAscension.cs").read_text(
        encoding="utf-8")
    assert "ArmKeywordTips.ForAscensionNoOath(" in src
    assert '"This hit does not gain Oath."' in TIPS_CS.read_text(
        encoding="utf-8")
    for rid, row in _rows().items():
        assert gen.ascension_hit_gains_no_oath(row) == (
            rid == "proto_vk_four_winds_ascension"), rid
