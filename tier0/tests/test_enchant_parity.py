"""EB-84 — the C# enchantment leg, held as an eligibility correspondence.

The backlog row opened this as a port ("no C# enchant surface exists at
all"). It does exist: `sts2.dll` ships `EnchantmentModel`, a class for each
of the eight enchantments tier0's CATALOG names, the deck enchant screen, the
save format, and the payout hooks -- `Hook.ModifyDamage` and
`Hook.ModifyBlock` both consult `cardSource.Enchantment` before any other
modifier, so a mod card that deals its damage `.FromCard(this)` or gains its
Block with the `cardPlay` attached already collects Sharp / Corrupted /
Vigorous / Nimble with no mod code at all. LAW's standing rule (sweep the
decompiled game before building infrastructure) makes a second surface the
wrong answer, so what this module gates is the correspondence that CAN drift:
what each engine believes a card is eligible for.

These tests run everywhere -- they read committed source text, never the
game. The live half is owed as a smoke: enchant one mod card of each shape on
the deck screen and confirm the number moves.
"""

import subprocess
import sys
from pathlib import Path

from tier0.content import enchantments, loader

REPO = Path(loader.__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import lint_enchant_parity as lep        # noqa: E402


def test_the_parity_lint_passes():
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_enchant_parity.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # A verdict with no denominator is the confident half of a partial check
    # (the house reading of the strict-domination defect).
    assert "8 enchantments" in res.stdout, res.stdout


def test_every_shipped_enchantment_names_the_card_fact_its_game_rule_reads():
    """The vocabulary is the base game's; the mapping is what we maintain."""
    assert set(lep.GAME_RULES) == set(enchantments.CATALOG)
    for name, rule in lep.GAME_RULES.items():
        assert rule in (None, "attack", "block", "exhaust"), (name, rule)


def test_a_recorded_divergence_carries_its_reason():
    for key, why in lep.KNOWN_DIVERGENCES.items():
        name, reason = key
        assert name in enchantments.CATALOG, key
        assert reason, key
        assert len(why.split()) >= 12, (key, why)


def test_the_lint_bites_when_a_card_stops_declaring_that_it_gains_block():
    """The regression that motivated the codegen half.

    `Nimble.CanEnchant` gates on `CardModel.GainsBlock`, and BaseLib's
    auto-detect only sees a BlockVar in CanonicalVars -- which a card whose
    Block row sits inside a `conditional` does not have. Three shipped cards
    are that shape. Without the explicit override the game would never offer
    them Nimble; this asserts the lint would say so rather than pass.
    """
    target = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated"
              / "PruneWitchHunt.cs")
    original = target.read_text(encoding="utf-8")
    line = "    public override bool GainsBlock => true;\n"
    assert line in original, "the fixture card no longer declares GainsBlock"
    try:
        target.write_text(original.replace(line, ""), encoding="utf-8")
        res = subprocess.run(
            [sys.executable, str(REPO / "tools" / "lint_enchant_parity.py")],
            capture_output=True, text=True)
        assert res.returncode == 1, res.stdout
        assert "prune_witch_hunt" in res.stdout, res.stdout
        assert "nimble" in res.stdout, res.stdout
    finally:
        target.write_text(original, encoding="utf-8")


def test_a_reason_narrow_enough_to_still_catch_the_real_splits():
    """`sim_reason` decides which splits are already-known.

    Its first draft answered "block-next-turn" for every Skill, which
    swallowed exactly the finding above. Pin the narrowness: a Skill that
    gains ordinary Block gets NO excuse.
    """
    index = loader._card_index()
    ordinary = index["prune_witch_hunt"]          # Skill, conditional Block
    assert lep.sim_reason("nimble", ordinary, True) is None
    delayed = index["tideline_watch"]             # Skill, block_next_turn only
    assert lep.sim_reason("nimble", delayed, True) == "block-next-turn"
    attack = index["freminet_pressurized_floe"]   # Attack that gains Block
    assert lep.sim_reason("nimble", attack, False) == "skill-only"
