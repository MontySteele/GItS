"""Errata verification: Frozen v2, companion healing law, the
control_uptime/SUPPORT_CARRY detector, and Klee's current balance locks.

The 1000-fight band tests are slow by design: bands only mean anything at
adequate sample size. The scorecard lock moved to v0.2 after the July 23
playtest pass deliberately changed defense, companions, reactions, and Burst.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import Card
from tier0.harness import metrics
from tier0.harness.runner import score_character
from tier0.tests.retired_calibration import RETIRED_CALIBRATION
from tier0.tests.conftest import make_enemy, make_state

SEED = 42


# --- healing law (R8, supersedes the v0.3.1 exhaust errata) ---

def test_healing_law_is_conjunctive():
    """R8: true in-combat healing is Rare-tier AND Exhausts; no 4-star
    companion may true-heal (4-stars cap at uncommon). This replaces the
    v0.3.1 test that asserted Barbara/Bennett heals Exhaust -- those
    heals no longer exist (converted to block/meter). Enforced over the
    WHOLE sheet so the next heal that lands in the pool answers to the
    law, not to a review."""
    for card in loader._card_index().values():
        if card.character in loader.EXTERNAL_CARD_SHEETS.values():
            # R8 is OUR design law. The base-game reference pool is EVIDENCE
            # we measure against, not a sheet we author -- auditing it here
            # would fail the suite for a MegaCrit design decision.
            continue
        heals = any(fx.get("op") == "heal" for fx in card.effects)
        if not heals:
            continue
        assert card.rarity == "rare" and card.exhaust, (
            f"{card.id}: true heal below Rare-and-Exhausts (R8 law)")
        assert not (card.is_companion and card.star == 4), (
            f"{card.id}: 4-star companion may not true-heal (R8)")


def _freeze_via_companion(st):
    """Seed hydro, then freeze with a companion cryo attack."""
    from tier0.engine import effects
    e = st.enemies[0]
    effects.resolve_card(st, _companion_hit("hydro"))
    frost = _companion_hit("cryo")
    st.player.hand.append(frost)
    effects.resolve_card(st, frost)
    return e


def _companion_hit(element):
    """The retired Dahlia / Kaeya Commons' shape (legacy cleanup stage 6
    deleted the companion sheets): a companion Attack, 6 damage applying its
    element."""
    return Card(id=f"{element}_companion", name=f"{element} companion",
                cost=1, type="attack", rarity="common", role_c="applier",
                element=element, tags=["companion"], effects=[
                    {"op": "damage", "amount": 6, "target": "enemy",
                     "applies_element": True}])


def test_control_uptime_counts_companion_frozen_attacks():
    from tier0.engine.combat import _enemy_turn
    st = make_state(enemies=[make_enemy(hp=200)])
    e = _freeze_via_companion(st)
    assert e.frozen and e.frozen_by_companion
    e.intents = [{"kind": "attack", "amount": 8}]
    _enemy_turn(st, e)                      # halved action: 0.5 negated
    # NC-7 (R116): the freeze is spent by the CLOCK at the end of the enemy
    # side, not by the action. `_enemy_turn` is called directly here, so the
    # side boundary has to be stepped by hand -- one decrement, exactly what
    # `combat._run_rounds` does after `after_enemy_side_turn_end`.
    e.frozen -= 1
    _enemy_turn(st, e)                      # normal action
    st.emit("fight_end", won=True, turns=st.turn)
    stats = metrics.extract(st, hp_start=st.player.max_hp)
    assert stats.control_negated == pytest.approx(1 - C.FROZEN_DAMAGE_MULT)
    assert stats.enemy_actions == 2
    # 0.25 uptime < 0.40 threshold: no flag on this fight.
    assert "SUPPORT_CARRY" not in stats.flags


def test_support_carry_flags_control_carried_wins():
    from tier0.engine.combat import _enemy_turn
    st = make_state(enemies=[make_enemy(hp=200)])
    e = st.enemies[0]
    e.intents = [{"kind": "attack", "amount": 8}]
    for _ in range(5):                      # every action frozen-halved
        e.frozen = True
        e.frozen_by_companion = True
        _enemy_turn(st, e)
    st.emit("fight_end", won=True, turns=st.turn)
    stats = metrics.extract(st, hp_start=st.player.max_hp)
    assert stats.control_negated / stats.enemy_actions > C.CONTROL_UPTIME_CARRY
    assert "SUPPORT_CARRY" in stats.flags


def test_klee_cannot_source_frozen_alone():
    # Klee is pyro; every Frozen in her fights is companion-sourced.
    # (Provenance sanity for the detector, not a balance claim.)
    st = make_state(enemies=[make_enemy(hp=200)])
    e = _freeze_via_companion(st)
    assert e.frozen_by_companion


# --- the frozen v0.2 median identity (regression lock) ---

# Measured post-playtest pass at 300 fights / seed 42. Deterministic at fixed
# seed; the tolerance is headroom for benign engine changes, not noise.
V02_MEDIAN = {"A1_frontload": 4.77, "A2_scaling": 3.82, "A3_block": 2.09,
              "A4_sustain": 0.50, "A5_velocity": 3.07, "A6_utility": 4.05,
              "A7_setup_tax": 2.37}


@RETIRED_CALIBRATION
@pytest.mark.battery
def test_v02_median_scorecard_locked():
    rep = score_character("klee", 300, SEED)
    for ax, frozen in V02_MEDIAN.items():
        assert rep["median_scores"][ax] == pytest.approx(frozen, abs=0.3), ax
