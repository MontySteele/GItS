"""The standing gate on generated-card STRUCTURE (tools/lint_generated_structure).

Written 2026-07-28 after the playtest-2 batch-1 review observed that two
mechanism-losing defects in one commit cycle were both invisible to a green
suite, for the same reason: every assertion on a generated card reads the
card's RENDERED TEXT, and in both cases the text is byte-identical with and
without the mechanism.

  * B1  -- a `bonus_formula` rider on a BLOCK op was dropped; the card shipped
           a flat 6 and the face still read as though it scaled.
  * R87 -- GrandFinale lost `new DynamicVar("BonusPer", 2m)` to a bad
           indentation while OnUpgrade and the description kept referencing
           it. 1296 tests stayed green; a human found it reading the diff.

Pinning each escapee individually does not close the class. These tests pin
the LINT instead, and -- this is the part that matters -- two of them
reconstruct the real defects in memory and assert the lint FIRES. A gate that
has only ever been seen to pass is not evidence of anything.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.lint_generated_structure import (
    MECHANICS,
    aim_problems,
    PROFILES,
    coverage_problems,
    generated_sources,
    problems,
    structural_problems,
)

CARDS = Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode" / "Cards"


def _sheet_card(profile, card_id):
    for card in yaml.safe_load(profile.sheet.read_text(encoding="utf-8")):
        if isinstance(card, dict) and card.get("id") == card_id:
            return card
    raise AssertionError(f"no sheet row for {card_id}")


@pytest.mark.parametrize("profile", PROFILES, ids=lambda p: p.character_id)
def test_generated_cards_are_structurally_sound(profile):
    """L1 dangling vars, L2 orphan vars, L3 sheet mechanics with no marker."""
    found = problems(profile)
    assert not found, "\n".join(found)


def test_the_gate_actually_reads_the_whole_generated_corpus():
    """Vacuity guard on the sweep itself.

    The lint derives its work list from each character's manifest. If that
    resolution silently produced nothing -- a renamed out_dir, a manifest key
    change -- every assertion above would pass while checking zero files. The
    purity sweep needed exactly this guard for exactly this reason.
    """
    per_character = {
        profile.character_id: len(generated_sources(profile))
        for profile in PROFILES
    }
    assert all(count > 0 for count in per_character.values()), per_character
    assert sum(per_character.values()) > 150, per_character


def test_every_mechanic_row_matches_at_least_one_real_card():
    """A curated row with a typo'd predicate is a row that never fires.

    Each row must apply to some card that is actually generated, or the table
    has drifted from the sheets and is reporting safety it does not provide.
    """
    rows = {mech.name: 0 for mech in MECHANICS}
    for profile in PROFILES:
        for card, _source, _where in generated_sources(profile):
            for mech in MECHANICS:
                if mech.applies(card):
                    rows[mech.name] += 1
    dead = sorted(name for name, hits in rows.items() if hits == 0)
    assert not dead, f"mechanic rows that match no generated card: {dead} ({rows})"


# --------------------------------------------------------------------------
# The two real defects, reconstructed. These are the "seen to fail" evidence.
# --------------------------------------------------------------------------

def test_the_gate_fires_on_the_grand_finale_regression():
    """R87: the var declaration vanishes, the references stay."""
    source = (CARDS / "Generated" / "GrandFinale.cs").read_text(encoding="utf-8")
    broken = source.replace(',\n            new DynamicVar("BonusPer", 2m)', "")
    assert broken != source, (
        "the BonusPer declaration is not where this test expects it; the "
        "reconstruction is stale, so it is no longer proving anything"
    )

    assert not structural_problems(source, "GrandFinale.cs")
    found = structural_problems(broken, "GrandFinale.cs")
    assert any("L1 DANGLING VAR" in line and "BonusPer" in line for line in found), found


def test_the_gate_fires_on_the_thunderous_ovation_bug():
    """B1: the block rider is replaced by the flat printed number."""
    path = CARDS / "Furina" / "Generated" / "ThunderousOvation.cs"
    source = path.read_text(encoding="utf-8")
    triple = (
        "            new CalculationBaseVar(6m),\n"
        "            new CalculationExtraVar(1m),\n"
        "            new CalculatedBlockVar(ValueProp.Move)"
    )
    assert triple in source, (
        "Thunderous Ovation no longer emits the Calculated triple this test "
        "reconstructs the bug from; the reconstruction is stale"
    )
    head, _, tail = source.partition(triple)
    # Drop the rest of the declaration line with it -- the multiplier lambda
    # is what reads Fanfare, and B1 shipped without any of it.
    broken = head + "            new BlockVar(6m, ValueProp.Move)" + tail.split("\n", 1)[1]
    broken = broken.replace(
        "DynamicVars.CalculatedBlock.Calculate(cardPlay.Target), "
        "DynamicVars.CalculatedBlock.Props",
        "DynamicVars.Block, DynamicVars.Block.Props",
    )
    broken = broken.replace("{CalculatedBlock:diff()}", "{Block:diff()}")
    broken = broken.replace(
        "DynamicVars.CalculationBase.UpgradeValueBy(2m);",
        "DynamicVars.Block.UpgradeValueBy(2m);",
    )
    for marker in ("CalculatedBlockVar", "CalculationBaseVar", "BonusPer"):
        assert marker not in broken, marker

    card = _sheet_card(
        next(p for p in PROFILES if p.character_id == "furina"), "thunderous_ovation"
    )
    assert not coverage_problems(card, source, "ThunderousOvation.cs")
    found = coverage_problems(card, broken, "ThunderousOvation.cs")
    assert any("L3 MISSING MECHANIC" in line and "bonus_formula" in line for line in found), found


# --------------------------------------------------------------------------
# EB-142, the third real defect, reconstructed the same way.
# --------------------------------------------------------------------------

def test_take_it_from_the_top_aims_at_a_chosen_enemy():
    """The shipped card, pinned on the value that was wrong in 0.2-1028.

    An attended playtest of 0.2-1028 played this card twice with the
    Spotlight already moved: Block +5 landed both times, enemy HP never
    moved, and godot.log carried
    `PlayCardAction ... completed with exception: System.ArgumentNullException
    ... (Parameter 'cardPlay.Target')`. The constructor declared
    `TargetType.Self` because the generator derived TargetType from TOP-LEVEL
    ops only and this card's damage lives inside a `conditional`.
    """
    source = (CARDS / "Furina" / "Generated" / "TakeItFromTheTop.cs").read_text(
        encoding="utf-8"
    )
    assert "TargetType.AnyEnemy" in source
    assert "TargetType.Self" not in source
    # The branch it exists for is still there.
    assert "SpotlightSystem.MovedThisTurn(Owner.Creature)" in source
    assert ".Targeting(cardPlay.Target)" in source


def test_the_gate_fires_on_the_take_it_from_the_top_defect():
    """L4: put the wrong TargetType back and the lint has to say so."""
    path = CARDS / "Furina" / "Generated" / "TakeItFromTheTop.cs"
    source = path.read_text(encoding="utf-8")
    broken = source.replace("TargetType.AnyEnemy", "TargetType.Self")
    assert broken != source, (
        "TakeItFromTheTop no longer declares AnyEnemy in the shape this test "
        "reconstructs the bug from; the reconstruction is stale"
    )

    assert not aim_problems(source, "TakeItFromTheTop.cs")
    found = aim_problems(broken, "TakeItFromTheTop.cs")
    assert any("L4 SELF-AIM" in line for line in found), found


def test_l4_does_not_fire_on_a_nullable_target_read():
    """The precision half: `Calculate(cardPlay.Target)` takes a NULL fine.

    Five shipped self-Block cards pass a possibly-null target into the
    calculated-block var on every play and are correct. An L4 that keyed on
    the identifier rather than on the two REQUIRING shapes would red-flag all
    five and would have been switched off within the week.
    """
    source = (CARDS / "Furina" / "Generated" / "DinnerService.cs").read_text(
        encoding="utf-8"
    )
    assert "TargetType.Self" in source
    assert "Calculate(cardPlay.Target)" in source
    assert not aim_problems(source, "DinnerService.cs")


def test_target_type_derivation_reads_the_whole_effect_tree():
    """The generator-side half, at the derivation rather than at the output.

    A card whose ONLY aiming op sits in a branch must still declare an aimed
    TargetType. Asserted against a synthetic row so it keeps proving the rule
    after the sheet moves.
    """
    from tools.gen_klee_cards import _aims_at_chosen_enemy, _effects_everywhere

    row = {
        "id": "synthetic_branch_aimer",
        "effects": [
            {"op": "block", "amount": 5, "target": "self"},
            {
                "op": "conditional",
                "if": "spotlight_moved_this_turn",
                "then": [{"op": "damage", "amount": 10, "target": "enemy"}],
            },
        ],
    }
    assert not any(_aims_at_chosen_enemy(e) for e in row["effects"]), (
        "the top-level read is what was wrong; if it now reports True the "
        "reconstruction is stale"
    )
    assert any(_aims_at_chosen_enemy(e) for e in _effects_everywhere(row))
