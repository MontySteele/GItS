"""The combat-side potion USE POLICY + FAIRY revive PLUS the LAYER-BOUNDARY LOCK.

Two jobs in one file, mirroring test_relics_dynamic:

1. The bounded-greedy use policy (engine/potions.py) really FIRES, and each
   positive assertion is pinned by a real drink -- every policy test carries a
   CONTROL that removes the potion (or flips the node context) and shows the
   effect vanish. Verified 2026-07-21 by running each pair: with the potion the
   player survives / the enemy dies / Strength lands; with it removed the player
   dies / the enemy lives / Strength stays 0. So no assertion is inert.

2. The potion engine must NEVER perturb the frozen 3.0 battery. A battery
   player (loader.build_player) carries EMPTY potions, and the anchor-lock +
   baseline-3.0 assertions are imported and re-run here, so THIS file fails
   loudly the moment a potion leaks into the calibration divisor.

The defensive + fairy tests drive the REAL enemy turn (combat._enemy_turn) so
"survives a hit it would otherwise die to" is a real block/heal/revive against a
real hit, not a hand-computed one. The offensive tests exercise try_use_potions
directly with a node context set, since the offensive branch is gated on
Player.node_kind (the elite/boss context the run layer injects).
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, potions
from tier0.harness import metrics
from tier0.harness.runner import run_battery, score_config
from tier0.tests import test_anchor_lock, test_axes
from tier0.tests.conftest import make_enemy, make_state


def _attacker(amount, times=1, hp=50, is_boss=False, name="dummy"):
    return make_enemy(hp=hp, name=name, is_boss=is_boss,
                      intents=[{"kind": "attack", "amount": amount,
                                "times": times}])


# ==========================================================================
# DEFENSIVE: about to die -> drink block/blood at turn start -> survive the hit.
# Control (no potion) dies to the identical hit, so the drink is load-bearing.
# ==========================================================================

def _run_defensive(potion):
    """Player at 15/80 faces a lethal 20 attack. Run the turn-start policy,
    then the REAL enemy turn. Return whether the player is alive after."""
    st = make_state(hp=15, enemies=[_attacker(20)])
    st.player.max_hp = 80
    if potion is not None:
        st.player.potions = [potion]
    potions.try_use_potions(st)               # turn-start use policy
    combat._enemy_turn(st, st.enemies[0])     # the real hit
    return st


def test_block_potion_saves_from_a_lethal_hit_control_dies():
    saved = _run_defensive("block_potion")
    assert saved.player.alive                             # block soaked it
    assert saved.player.potions == []                    # potion consumed
    assert saved.player.block == 0                        # block spent on the hit
    # CONTROL: identical hit, no potion -> dead (the drink is what saved it).
    assert not _run_defensive(None).player.alive


def test_blood_potion_saves_from_a_lethal_hit_control_dies():
    saved = _run_defensive("blood_potion")
    assert saved.player.alive                             # heal outran the hit
    assert saved.player.potions == []
    # heal was 20% of max = 16, so entry HP 15 -> 31, minus the 20 hit -> 11.
    assert saved.player.hp == 15 + int(C.POTION_BLOOD_HEAL_FRACTION * 80) - 20
    assert not _run_defensive(None).player.alive          # CONTROL


# ==========================================================================
# OFFENSIVE: elite/boss only. fire closes a kill; strength races the boss.
# On a NORMAL fight the offensive branch never fires (node_kind gate).
# ==========================================================================

def test_fire_potion_closes_a_kill_on_an_elite_normal_does_not_fire():
    fire_hp = C.POTION_FIRE_DAMAGE - 5           # inside fire's kill range
    # ELITE: fire is drunk to close the kill.
    st = make_state(hp=80, enemies=[_attacker(5, hp=fire_hp)])
    st.player.max_hp = 80
    st.player.potions = ["fire_potion"]
    st.player.node_kind = "elite"
    potions.try_use_potions(st)
    assert not st.enemies[0].alive                        # fire finished it
    assert st.player.potions == []                        # fire consumed

    # CONTROL -- identical fight, NORMAL node: offensive branch is gated off.
    st2 = make_state(hp=80, enemies=[_attacker(5, hp=fire_hp)])
    st2.player.max_hp = 80
    st2.player.potions = ["fire_potion"]
    st2.player.node_kind = "normal"
    potions.try_use_potions(st2)
    assert st2.enemies[0].alive                           # nothing drunk
    assert st2.player.potions == ["fire_potion"]          # still held


def test_strength_potion_races_the_boss_normal_does_not_fire():
    big = int(C.POTION_BIG_HIT_FRACTION * 80) + 5         # a big telegraph
    # BOSS: strength is drunk to race it.
    st = make_state(hp=80, enemies=[_attacker(big, is_boss=True)])
    st.player.max_hp = 80
    st.player.potions = ["strength_potion"]
    st.player.node_kind = "boss"
    potions.try_use_potions(st)
    assert st.player.powers.get("strength", 0) == C.POTION_STRENGTH
    assert st.player.potions == []

    # CONTROL -- same-size hit but a NORMAL (non-boss) fight: no offensive use.
    st2 = make_state(hp=80, enemies=[_attacker(big, is_boss=False)])
    st2.player.max_hp = 80
    st2.player.potions = ["strength_potion"]
    st2.player.node_kind = "normal"
    potions.try_use_potions(st2)
    assert st2.player.powers.get("strength", 0) == 0      # nothing drunk
    assert st2.player.potions == ["strength_potion"]


# ==========================================================================
# FAIRY IN A BOTTLE: passive revive at the lethal-damage site. Not drunk.
# ==========================================================================

def test_fairy_revives_once_then_a_second_lethal_hit_kills():
    st = make_state(hp=10, enemies=[_attacker(50)])
    st.player.max_hp = 80
    st.player.potions = ["fairy_in_a_bottle"]

    combat._enemy_turn(st, st.enemies[0])                 # FIRST lethal hit
    assert st.player.alive                                # fairy caught it
    assert st.player.hp == max(1, int(C.POTION_FAIRY_REVIVE_FRACTION * 80))
    assert st.player.potions == []                        # fairy consumed
    assert any(e["event"] == "fairy_revive" for e in st.log)

    combat._enemy_turn(st, st.enemies[0])                 # SECOND lethal hit
    assert not st.player.alive                            # no fairy left -> dies


def test_fairy_control_no_fairy_dies_on_the_first_lethal_hit():
    # Same first hit with NO fairy held: the player dies immediately, proving
    # the revive above is what kept them alive.
    st = make_state(hp=10, enemies=[_attacker(50)])
    st.player.max_hp = 80
    combat._enemy_turn(st, st.enemies[0])
    assert not st.player.alive


def test_fairy_is_not_proactively_drunk_by_the_use_policy():
    # A fairy is the ONLY potion held and a lethal turn looms. The use policy
    # must leave it untouched -- fairy is excluded from DRINKABLE and is a
    # passive revive, never a turn-start drink.
    st = make_state(hp=10, enemies=[_attacker(50)])
    st.player.max_hp = 80
    st.player.potions = ["fairy_in_a_bottle"]
    st.player.node_kind = "elite"                # even the offensive gate open
    before_hp = st.player.hp
    potions.try_use_potions(st)
    assert st.player.potions == ["fairy_in_a_bottle"]     # not drunk
    assert st.player.hp == before_hp                      # no heal/effect landed
    assert "fairy_in_a_bottle" not in potions.DRINKABLE   # by construction


# ==========================================================================
# LAYER-BOUNDARY LOCK
# ==========================================================================

def test_battery_player_has_no_potions():
    """A player built by the battery path carries NO potions (and the default
    slots / empty node context), so the whole potion engine is a dead branch on
    the anchor/battery."""
    for character, deck in (("ref_ironclad", "starter"),
                            ("ref_ironclad", "archetype_package"),
                            ("klee", "starter")):
        p = loader.build_player(character, deck)
        assert p.potions == [], (character, deck)
        assert p.potion_slots == C.POTION_SLOTS, (character, deck)
        assert p.node_kind == "", (character, deck)


def test_anchor_and_baseline_still_exact():
    """Import and re-run the anchor-lock + baseline-3.0 assertions. If the
    potion engine ever perturbs the frozen battery, one of these moves and THIS
    file fails loudly -- not just the distant anchor-lock suite."""
    # Anchor-lock: frozen ref_ironclad spec + battery numbers (no fixtures).
    test_anchor_lock.test_baseline_is_still_ref_ironclad_starter()
    test_anchor_lock.test_ref_ironclad_spec_is_byte_identical()
    test_anchor_lock.test_ref_ironclad_battery_numbers_locked()
    # Belt-and-braces: re-derive the anchor battery numbers here too.
    s = metrics.summarize(run_battery("ref_ironclad", "starter", "punisher",
                                      "generic", 200, 7))
    assert s["winrate"] == pytest.approx(0.525, abs=1e-9)
    assert s["avg_turns"] == pytest.approx(9.585, abs=1e-9)
    # Baseline scores exactly 3.0 on every axis (test_axes).
    baseline = score_config("ref_ironclad", "starter", "generic", 30, 11)
    test_axes.test_baseline_scores_are_exactly_three(baseline)
