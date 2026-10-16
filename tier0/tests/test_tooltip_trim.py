"""The tooltip trim (2026-10-14, review/active/tooltip-trim-2026-10-14.md).

A player's hover is `gen_klee_cards.player_tip_layers`' cut of the seat's
full chain; the seat chain is unchanged. `tools/lint_hover_tips.py` measures
the emitted player branch; this pins the cut's rules.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import gen_klee_cards as g  # noqa: E402

FLASH_POINT = (
    "ArmKeywordTips.ForElementalReaction(ArmKeywordTips.ForSpark("
    "ArmKeywordTips.ForSetOff(ArmKeywordTips.ForBomb(ArmKeywordTips."
    "ForEmptyField(KleeCardTooltips.ForCard(base.ExtraHoverTips, this, "
    "Element.Pyro), this, true), this), this), this), this)")


def calls(layers):
    return [c for c, _ in layers]


def test_the_chain_splits_and_folds_back_to_itself():
    assert g.fold_tip_layers(g.split_tip_layers(FLASH_POINT)) == FLASH_POINT


def test_flash_point_drops_spark_and_the_reaction_box_under_applies_pyro():
    cut = g.player_tip_layers(g.split_tip_layers(FLASH_POINT),
                              ["KleeKeywords.AppliesPyro"], False)
    assert calls(cut) == ["KleeCardTooltips.ForCard",
                          "ArmKeywordTips.ForEmptyField",
                          "ArmKeywordTips.ForBomb",
                          "ArmKeywordTips.ForSetOff"]


def test_a_spark_priced_card_keeps_spark():
    cut = g.player_tip_layers(g.split_tip_layers(FLASH_POINT), [], True)
    assert "ArmKeywordTips.ForSpark" in calls(cut)


def test_riders_are_the_seats_and_a_guest_star_drops_summon():
    expr = ("ArmKeywordTips.ForOldestGuest(ArmKeywordTips.ForNavia("
            "ArmKeywordTips.ForGuestStar(ArmKeywordTips.ForSummon("
            "base.ExtraHoverTips, this), this), this), this)")
    cut = g.player_tip_layers(g.split_tip_layers(expr), [], False)
    assert calls(cut) == ["ArmKeywordTips.ForGuestStar",
                          "ArmKeywordTips.ForNavia"]


def test_the_cap_cuts_base_words_first():
    expr = ("BaseKeywordTips.ForWeak(BaseKeywordTips.ForVulnerable("
            "ArmKeywordTips.ForOath(base.ExtraHoverTips, this), this), this)")
    cut = g.player_tip_layers(g.split_tip_layers(expr),
                              ["KleeKeywords.Knight",
                               "KleeKeywords.AppliesCryo"], False)
    assert calls(cut) == ["ArmKeywordTips.ForOath"]


def test_the_hover_tip_lint_passes():
    out = subprocess.run([sys.executable, str(REPO / "tools" /
                                              "lint_hover_tips.py")],
                         capture_output=True, text=True, encoding="utf-8",
                         cwd=REPO)
    assert out.returncode == 0, out.stdout
