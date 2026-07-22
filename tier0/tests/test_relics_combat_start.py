"""COMBAT-START relic effects (engine/relics.py, relic pass).

Each relic's combat half is a dict keyed by ``hook`` on ``Player.relic_effects``.
This module drives the exact turn-1 sequence combat._player_turn runs
(reset_combat -> apply_combat_start -> on_player_turn_start) and asserts, for
every combat-start relic, the DELTA between a player carrying the single
relic_effect and an otherwise-identical player carrying none.

The with/without pairing is the seen-to-fail guard: an inert hook (the engine
dropping the effect) collapses the delta to zero and every assertion below
fails. The relic_effect dicts are inlined verbatim from tier05/content/
relics.yaml so the tier0 test stays layer-pure (no tier05 import).
"""

from tier0 import constants as C
from tier0.engine import relics
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


def _fire_start(st):
    """Run the turn-1 combat-start sequence on a prepared state."""
    st.turn = 1
    relics.reset_combat(st)
    relics.apply_combat_start(st)
    return st


def _dummy_cards(n):
    return [Card(id=f"c{i}", name=f"c{i}", cost=1, type="skill")
            for i in range(n)]


# --- anchor: 10 block at combat start ---------------------------------------

def test_anchor_grants_block_at_start():
    st = make_state()
    st.player.relic_effects = [{"hook": "combat_start_block", "amount": 10}]
    _fire_start(st)
    assert st.player.block == 10

    st_no = make_state()
    _fire_start(st_no)
    assert st_no.player.block == 0


# --- vajra: 1 strength -------------------------------------------------------

def test_vajra_grants_strength_at_start():
    st = make_state()
    st.player.relic_effects = [
        {"hook": "combat_start_power", "power": "strength", "amount": 1}]
    _fire_start(st)
    assert st.player.powers.get("strength", 0) == 1

    st_no = make_state()
    _fire_start(st_no)
    assert st_no.player.powers.get("strength", 0) == 0


# --- blood_vial: heal 2, capped at max_hp -----------------------------------

def test_blood_vial_heals_at_start():
    st = make_state()
    st.player.hp = st.player.max_hp - 5
    st.player.relic_effects = [{"hook": "combat_start_heal", "amount": 2}]
    _fire_start(st)
    assert st.player.hp == st.player.max_hp - 3        # +2

    st_no = make_state()
    st_no.player.hp = st_no.player.max_hp - 5
    _fire_start(st_no)
    assert st_no.player.hp == st_no.player.max_hp - 5   # untouched


def test_blood_vial_heal_capped_at_max_hp():
    st = make_state()
    st.player.hp = st.player.max_hp - 1                 # room for only 1
    st.player.relic_effects = [{"hook": "combat_start_heal", "amount": 2}]
    _fire_start(st)
    assert st.player.hp == st.player.max_hp             # capped, not +1 over


# --- lantern: +1 energy on turn 1 ONLY --------------------------------------

def test_lantern_extra_energy_turn_one_only():
    st = make_state()
    st.player.relic_effects = [{"hook": "combat_start_energy", "amount": 1}]
    st.player.energy = C.BASE_ENERGY_PER_TURN
    _fire_start(st)
    relics.on_player_turn_start(st, 1)
    assert st.player.energy == C.BASE_ENERGY_PER_TURN + 1   # turn 1: +1

    # Turn 2: the loop refills energy, then runs the per-turn hooks only;
    # the combat_start rider is turn-1 exclusive and adds nothing.
    st.player.energy = C.BASE_ENERGY_PER_TURN
    relics.on_player_turn_start(st, 2)
    assert st.player.energy == C.BASE_ENERGY_PER_TURN       # back to normal

    st_no = make_state()
    st_no.player.energy = C.BASE_ENERGY_PER_TURN
    _fire_start(st_no)
    relics.on_player_turn_start(st_no, 1)
    assert st_no.player.energy == C.BASE_ENERGY_PER_TURN    # no bonus at all


# --- bag_of_preparation: 2 extra cards on turn 1 ONLY -----------------------

def test_bag_of_preparation_extra_draw_turn_one_only():
    st = make_state()
    st.player.draw_pile = _dummy_cards(6)
    st.player.relic_effects = [{"hook": "combat_start_draw", "amount": 2}]
    _fire_start(st)
    assert len(st.player.hand) == 2            # 2 extra cards on turn 1
    assert len(st.player.draw_pile) == 4

    # Turn 2: per-turn hook draws nothing extra.
    hand_before = len(st.player.hand)
    relics.on_player_turn_start(st, 2)
    assert len(st.player.hand) == hand_before  # back to normal

    st_no = make_state()
    st_no.player.draw_pile = _dummy_cards(6)
    _fire_start(st_no)
    assert len(st_no.player.hand) == 0         # no relic -> no extra draw


# --- bag_of_marbles: vulnerable on all enemies ------------------------------

def test_bag_of_marbles_vulnerable_all_enemies():
    st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    st.player.relic_effects = [
        {"hook": "combat_start_enemy_power", "power": "vulnerable",
         "amount": 1}]
    _fire_start(st)
    for e in st.enemies:
        assert e.powers.get("vulnerable", 0) == 1

    st_no = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    _fire_start(st_no)
    for e in st_no.enemies:
        assert e.powers.get("vulnerable", 0) == 0


# --- red_mask: weak on all enemies ------------------------------------------

def test_red_mask_weak_all_enemies():
    st = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    st.player.relic_effects = [
        {"hook": "combat_start_enemy_power", "power": "weak", "amount": 1}]
    _fire_start(st)
    for e in st.enemies:
        assert e.powers.get("weak", 0) == 1

    st_no = make_state(enemies=[make_enemy(name="a"), make_enemy(name="b")])
    _fire_start(st_no)
    for e in st_no.enemies:
        assert e.powers.get("weak", 0) == 0


# --- festive_popper: 9 to all, UNPOWERED (ignores strength & vulnerable) ----

def test_festive_popper_unpowered_aoe():
    st = make_state(enemies=[make_enemy(hp=50, name="a"),
                             make_enemy(hp=50, name="b")])
    st.player.relic_effects = [{"hook": "combat_start_aoe", "amount": 9}]
    # Both would inflate a POWERED hit; the unpowered path must ignore them.
    st.player.powers["strength"] = 5
    for e in st.enemies:
        e.powers["vulnerable"] = 3
    _fire_start(st)
    for e in st.enemies:
        assert e.hp == 50 - 9      # exactly 9: no strength, no vulnerable

    st_no = make_state(enemies=[make_enemy(hp=50, name="a"),
                                make_enemy(hp=50, name="b")])
    _fire_start(st_no)
    for e in st_no.enemies:
        assert e.hp == 50          # untouched


# --- gorget: 4 plating -------------------------------------------------------

def test_gorget_grants_plating_at_start():
    st = make_state()
    st.player.relic_effects = [
        {"hook": "combat_start_power", "power": "plating", "amount": 4}]
    _fire_start(st)
    assert st.player.powers.get("plating", 0) == 4

    st_no = make_state()
    _fire_start(st_no)
    assert st_no.player.powers.get("plating", 0) == 0
