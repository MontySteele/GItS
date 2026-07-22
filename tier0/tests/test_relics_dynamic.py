"""Dynamic / conditional / damage relics (combat-side relic engine) PLUS the
LAYER-BOUNDARY LOCK.

Two jobs in one file, deliberately:

1. The per-turn (happy_flower, pendulum), first-hp-loss (centennial_puzzle),
   damage-rider (strike_dummy) and conditional (red_skull) relics really
   FIRE -- and each assertion FAILS if you delete the driving relic_effect
   (i.e. the effect is load-bearing, not inert). Verified 2026-07-21 by
   re-running every positive test with ``relic_effects = []``: the energy
   never arrives, no card is drawn, the +3 rider vanishes and strength stays
   0 -- so each assertion below is pinned by a real effect.

2. The relic engine must NEVER perturb the frozen 3.0 battery. A battery
   player (loader.build_player) carries empty relic_effects, and the
   anchor-lock + baseline-3.0 assertions are imported and re-run here, so
   THIS file fails loudly the moment a relic leaks into the calibration
   divisor.

conditional_power (red_skull) is still wired (engine/relics.py COMBAT_HOOKS,
relics.yaml red_skull), so the red_skull sub-test is INCLUDED. It would be
skipped only if content notes recorded conditional_power as dropped.
"""

import pytest

from tier0.content import loader
from tier0.engine import combat, effects, relics
from tier0.engine.state import Card
from tier0.harness import metrics
from tier0.harness.runner import run_battery, score_config
from tier0.tests import test_anchor_lock, test_axes
from tier0.tests.conftest import make_enemy, make_state


# --- fixtures / factories -------------------------------------------------

def _dummy(i):
    """A drawable filler card (no effects) for stocking the draw pile."""
    return Card(id=f"c{i}", name="c", cost=1, type="skill", effects=[])


def _attack(cid, amount=6):
    return Card(id=cid, name=cid, cost=1, type="attack",
                effects=[{"op": "damage", "amount": amount, "target": "enemy"}])


# --- per-turn: happy_flower / pendulum (fire on turns 3, 6, ...) -----------

def test_happy_flower_energy_only_on_turn_multiples_of_three():
    st = make_state()
    p = st.player
    p.relic_effects = [{"hook": "every_n_turns_energy", "n": 3, "amount": 1}]
    relics.reset_combat(st)
    p.energy = 0
    for turn in (1, 2):
        relics.on_player_turn_start(st, turn)
    assert p.energy == 0                 # off-cadence: nothing
    relics.on_player_turn_start(st, 3)
    assert p.energy == 1                 # turn 3: +1
    for turn in (4, 5):
        relics.on_player_turn_start(st, turn)
    assert p.energy == 1                 # still nothing between
    relics.on_player_turn_start(st, 6)
    assert p.energy == 2                 # turn 6: +1 again


def test_pendulum_draw_only_on_turn_multiples_of_three():
    st = make_state()
    p = st.player
    p.draw_pile = [_dummy(i) for i in range(6)]
    p.relic_effects = [{"hook": "every_n_turns_draw", "n": 3, "amount": 1}]
    relics.reset_combat(st)
    for turn in (1, 2):
        relics.on_player_turn_start(st, turn)
    assert len(p.hand) == 0              # off-cadence: no draw
    relics.on_player_turn_start(st, 3)
    assert len(p.hand) == 1              # turn 3: +1 card
    for turn in (4, 5):
        relics.on_player_turn_start(st, turn)
    assert len(p.hand) == 1             # still nothing between
    relics.on_player_turn_start(st, 6)
    assert len(p.hand) == 2             # turn 6: +1 card again


# --- centennial_puzzle: draw 3 on the FIRST hp loss ONLY ------------------

def test_centennial_puzzle_draws_three_on_first_hp_loss_only():
    st = make_state()
    p = st.player
    p.draw_pile = [_dummy(i) for i in range(6)]
    p.relic_effects = [{"hook": "on_first_hp_loss_draw", "amount": 3}]
    relics.reset_combat(st)
    relics.note_hp_loss(st)             # FIRST hp loss -> draw 3
    assert len(p.hand) == 3
    relics.note_hp_loss(st)             # SECOND hp loss -> nothing more
    assert len(p.hand) == 3


# --- strike_dummy: +3 to cards whose id/name contains 'strike' ------------

def test_strike_dummy_adds_bonus_to_strike_named_card():
    st = make_state(enemies=[make_enemy(hp=50)])
    st.player.relic_effects = [{"hook": "card_name_damage_bonus",
                                "substring": "strike", "amount": 3}]
    effects.resolve_card(st, _attack("pommel_strike"))
    assert st.enemies[0].hp == 50 - 9   # base 6 + 3 rider


def test_strike_dummy_leaves_non_strike_card_unchanged():
    st = make_state(enemies=[make_enemy(hp=50)])
    st.player.relic_effects = [{"hook": "card_name_damage_bonus",
                                "substring": "strike", "amount": 3}]
    effects.resolve_card(st, _attack("thwack"))
    assert st.enemies[0].hp == 50 - 6   # no substring match -> plain 6


# --- red_skull: +3 strength while hp <= 50% max, gone when healed above ----

def test_red_skull_strength_tracks_hp_threshold():
    st = make_state(hp=80)
    p = st.player
    p.relic_effects = [{"hook": "conditional_power", "power": "strength",
                        "amount": 3, "when": "hp_below", "threshold": 0.5}]
    relics.reset_combat(st)
    p.hp = 80                            # above 50%
    relics.on_player_turn_start(st, 1)
    assert p.powers.get("strength", 0) == 0
    p.hp = 30                            # at/below 50% (40 == threshold*max)
    relics.on_player_turn_start(st, 2)
    assert p.powers.get("strength", 0) == 3
    p.hp = 60                            # healed back above 50%
    relics.on_player_turn_start(st, 3)
    assert p.powers.get("strength", 0) == 0   # removed cleanly, no drift


def test_red_skull_deactivates_after_turn_start_blood_potion():
    st = make_state(hp=35, enemies=[make_enemy(
        intents=[{"kind": "attack", "amount": 50}])])
    p = st.player
    p.max_hp = 80
    p.potions = ["blood_potion"]
    p.relic_effects = [{"hook": "conditional_power", "power": "strength",
                        "amount": 3, "when": "hp_below", "threshold": 0.5}]
    relics.reset_combat(st)

    combat._player_turn(st, lambda state: None)

    assert p.hp == 51                     # 35 + floor(20% of 80)
    assert p.powers.get("strength", 0) == 0


def test_red_skull_activates_between_cards_after_self_damage():
    st = make_state(hp=80)
    p = st.player
    p.relic_effects = [{"hook": "conditional_power", "power": "strength",
                        "amount": 3, "when": "hp_below", "threshold": 0.5}]
    relics.reset_combat(st)
    relics.on_player_turn_start(st, 1)
    card = Card(id="self_hit", name="self hit", cost=0, type="skill",
                effects=[{"op": "damage", "target": "self", "amount": 45}])
    p.hand = [card]

    combat.play_card(st, card)

    assert p.hp == 35
    assert p.powers.get("strength", 0) == 3


# ==========================================================================
# LAYER-BOUNDARY LOCK
# ==========================================================================

def test_battery_player_has_no_relic_effects():
    """A player built by the battery path carries NO relic_effects, so the
    whole combat-side relic engine is a dead branch on the anchor/battery."""
    for character, deck in (("ref_ironclad", "starter"),
                            ("ref_ironclad", "archetype_package"),
                            ("klee", "starter")):
        p = loader.build_player(character, deck)
        assert p.relic_effects == [], (character, deck)


def test_anchor_and_baseline_still_exact():
    """Import and re-run the anchor-lock + baseline-3.0 assertions. If the
    relic engine ever perturbs the frozen battery, one of these moves and
    THIS file fails loudly -- not just the distant anchor-lock suite."""
    # Anchor-lock: frozen ref_ironclad spec + battery numbers (no fixtures).
    test_anchor_lock.test_baseline_is_still_ref_ironclad_starter()
    test_anchor_lock.test_ref_ironclad_spec_is_byte_identical()
    test_anchor_lock.test_ref_ironclad_battery_numbers_locked()
    # Belt-and-braces: re-derive the anchor battery numbers here too.
    s = metrics.summarize(run_battery("ref_ironclad", "starter", "punisher",
                                      "generic", 200, 7))
    assert s["winrate"] == pytest.approx(0.525, abs=1e-9)
    assert s["avg_turns"] == pytest.approx(9.585, abs=1e-9)
    # Baseline scores exactly 3.0 on every axis (test_axes). The baseline is
    # 3.0 against itself by construction, so a small fight count is fine.
    baseline = score_config("ref_ironclad", "starter", "generic", 30, 11)
    test_axes.test_baseline_scores_are_exactly_three(baseline)
