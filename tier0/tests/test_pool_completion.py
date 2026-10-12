"""POOL COMPLETION (2026-10-01): the sim's pins for paper sec.4-6.

`review/active/pool-completion-2026-10-01.md`, all picks ruled at the
defaults. Kokomi's one Common, seven Rares and two multiplayer cards; Furina's
three Uncommons and three Rares; the Body Slam repricing. The three Ancient
cards (sec.3) are game-side only and pinned in C# alone. The C# twin is
`klee-mod/KleeTests/Prototype/PoolCompletionTests.cs`. Readings: the
provenance note, "Pool completion, 2026-10-01". THE KOKOMI RE-FOUNDING
(2026-10-12) cut Kurage School and Patient Tide and made Watatsumi Resistance
pay for written Companions in Stings; their old tests left with them. NOTHING
MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import copy
import random

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat, furina_stage, kokomi_plan, powers
from tier0.engine.state import CombatState, Enemy, Player
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    kokomi_state, overhaul, plan_card)

FS = furina_stage
QUIET = [{"kind": "block", "amount": 5}]


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _proto(cid):
    return next(c for c in loader.prototype_cards() if c.id == cid)


def _play(st, card, energy=10):
    card = _row(card) if isinstance(card, str) else card
    st.player.energy = energy
    st.player.hand.append(card)
    combat.play_card(st, card)
    return card


def _library(st, n=10):
    st.player.draw_pile = [plan_card([], cid=f"proto_kk_lib{i}")
                           for i in range(n)]


def _events(st, name):
    return [e for e in st.log if e.get("event") == name]


# ===========================================================================
# KOKOMI (sec.4, sec.6)
# ===========================================================================

def test_her_pool_is_seventy_eight(overhaul):
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    # The re-founding (2026-10-12) rewrote the pool's order; the count holds.
    assert len(ids) == len(set(ids)) == 78
    for cut in ("proto_kk_kurage_school", "proto_kk_patient_tide"):
        assert cut not in ids
    # Her co-op tier is the base game's shape: three Uncommons, two Rares.
    assert C.KOKOMI_OVERHAUL_MULTIPLAYER_IDS[-2:] == (
        "proto_kk_tactical_relay", "proto_kk_kurages_mercy")
    assert sorted(_proto(cid).rarity
                  for cid in C.KOKOMI_OVERHAUL_MULTIPLAYER_IDS) == [
        "rare", "rare", "uncommon", "uncommon", "uncommon"]


def test_coral_crash_is_body_slam_and_tidal_rebuke_keeps_no_exhaust(overhaul):
    crash = _row("proto_kk_coral_crash")
    # The Kokomi card pass (2026-10-11): costs 0; the upgrade adds 4 damage.
    assert (crash.rarity, crash.cost, _up("proto_kk_coral_crash").cost) == (
        "common", 0, 0)
    assert crash.effects[0]["amount_formula"]["base"] == 0
    assert _up("proto_kk_coral_crash").effects[0]["amount_formula"] == {
        "base": 4, "per": 1, "count": "player_block"}
    rebuke = _row("proto_kk_tidal_rebuke")
    # The Rare pass (2026-10-04): cost 2 -> 1 [0], and Retain.
    assert (rebuke.rarity, rebuke.cost, _up("proto_kk_tidal_rebuke").cost) == (
        "rare", 1, 0)
    assert not rebuke.exhaust and rebuke.retain
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET),
                               make_enemy(hp=300, intents=QUIET)])
    st.player.block = 13
    _play(st, rebuke)
    assert [e.hp for e in st.enemies] == [300 - 13, 300 - 13]


def test_noelles_sweeping_time_upgrades_to_cost_one(monkeypatch):
    loader.reset_arm_caches()
    for fn in (upgrades._upgrade_index, upgrades._prototype_upgrade_index):
        getattr(fn, "cache_clear", lambda: None)()
    try:
        row = _proto("proto_mc_noelle_sweeping_time")
        assert row.cost == 2 and row.upgrade == {"cost": -1}
    finally:
        loader.reset_arm_caches()


def test_tidal_screen_blocks_now_and_draws_two_from_the_plan(overhaul):
    # An attacking enemy, so the sim's pilot plays the now-line
    # (`kokomi_plan.plan_aimed_at_pet`).
    st = kokomi_state(enemies=[make_enemy(
        hp=300, intents=[{"kind": "attack", "amount": 5}])])
    _library(st)
    card = _play(st, "proto_kk_tidal_screen")
    assert st.player.block == 7
    assert card.plan == [{"op": "draw", "amount": 2}]
    kokomi_plan.schedule(st, card)
    kokomi_plan.resolve_all(st)
    assert len(st.player.hand) == 2
    assert _up("proto_kk_tidal_screen").effects[0]["amount"] == 10


def test_spring_tide_carries_the_whole_queue_out_now(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    st.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    kokomi_plan.schedule(st, plan_card(
        [{"op": "next_plan_extra_carry_out"}], cid="proto_kk_rider"))
    kokomi_plan.schedule(st, plan_card(
        [{"op": "energy", "amount": 1}], cid="proto_kk_next"))
    st.player.energy = 0
    kokomi_plan.kind(st, {"op": "kokomi", "kind": "spring_tide"},
                     _row("proto_kk_spring_tide"), None)
    assert st.kk_plan_queue == []
    # The rider reaches the entry behind it (twice), and Nereid's Ascension
    # does NOT double a mid-turn drain's first entry.
    assert st.kk_plans_carried_out_this_combat == 1 + 2
    assert st.player.energy == 2
    # The emptied queue can be written again for the morning.
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    assert len(st.kk_plan_queue) == 1


def test_spring_tide_on_an_empty_queue_is_a_printed_no_op(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    kokomi_plan.resolve_all_now(st)
    assert _events(st, "plan_front_empty")
    assert _row("proto_kk_spring_tide").exhaust
    assert _up("proto_kk_spring_tide").cost == 0


def test_seas_reproach_answers_her_weak_and_vulnerable(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    enemy = st.enemies[0]
    st.player.powers[kokomi_plan.SEAS_REPROACH] = 3
    powers.apply_power(st, enemy, "weak", 1, applier=st.player)
    powers.apply_power(st, enemy, "vulnerable", 2, applier=st.player)
    assert len(_events(st, "plan_seas_reproach")) == 2
    assert enemy.hp < 300
    hp = enemy.hp
    # Not an enemy's application, not one on her, not another power.
    powers.apply_power(st, enemy, "weak", 1, applier=enemy)
    powers.apply_power(st, st.player, "weak", 1, applier=st.player)
    powers.apply_power(st, enemy, "poison", 1, applier=st.player)
    assert enemy.hp == hp
    # The Kokomi card pass (2026-10-11): 1 [0] (was 2 [1]).
    assert (_row("proto_kk_seas_reproach").cost,
            _up("proto_kk_seas_reproach").cost) == (1, 0)


def test_tactical_relay_plans_energy_for_each_player(overhaul):
    row = _proto("proto_kk_tactical_relay")
    assert row.plan == [{"op": "each_player_energy", "amount": 1},
                        {"op": "each_player_draw", "amount": 0}]
    assert row.upgrade == {"plan_draw": 1}
    assert "each_player_draw" in upgrades.PLAN_DELTA_OPS["plan_draw"]
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)])
    _library(st)
    st.player.energy = 0
    kokomi_plan.schedule(st, row)
    kokomi_plan.resolve_all(st)
    assert st.player.energy == 1 and st.player.hand == []
    drawn = copy.deepcopy(row)
    drawn.plan[1]["amount"] = 1
    kokomi_plan.schedule(st, drawn)
    kokomi_plan.resolve_all(st)
    assert len(st.player.hand) == 1


def test_kurages_mercy_mends_each_player(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET)], hp=80)
    st.mi_entry_hp = 80
    st.player.hp = 60
    healed = kokomi_plan.kurages_mercy(st, 8)
    assert _events(st, "plan_kurages_mercy")
    assert healed == 8 and st.player.hp == 68
    # Never above the HP she walked in with (the Mend rule).
    assert kokomi_plan.kurages_mercy(st, 99) == 12 and st.player.hp == 80


# ===========================================================================
# FURINA (sec.5)
# ===========================================================================

def _clear_caches():
    loader.reset_arm_caches()
    for fn in (upgrades._upgrade_index, upgrades._prototype_upgrade_index):
        getattr(fn, "cache_clear", lambda: None)()


@pytest.fixture
def arm(monkeypatch):
    _clear_caches()
    yield
    _clear_caches()


def test_interval_bells_spend_is_three_then_two(arm):
    card = _proto("proto_fs_interval_bell")
    spend = card.effects[0]["modes"][1]
    assert FS.spend_mode_amount(spend) == 3
    up = copy.deepcopy(card)
    for fx in up.effects[0]["modes"][1]["effects"]:
        if fx["op"] == "stage_spend":
            fx["amount"] -= 1
    assert FS.spend_mode_amount(up.effects[0]["modes"][1]) == 2
    # Its Spend mode's Energy comes next turn (the 2026-10-04 loop fix):
    # `tier0/tests/test_furina_tide_arm.py` pins it on the Salon's Tab rules.


# --- the Rare pass (2026-10-04) ------------------------------------------------

def test_shoal_of_spears_is_one_hit_per_plan_waiting(overhaul):
    """One hit of 4 per Plan waiting (per Plan written this turn until the
    re-founding, 2026-10-12), so her Strength counts on each hit; with no
    Plan waiting it deals nothing."""
    st = kokomi_state(enemies=[make_enemy(hp=300, intents=QUIET),
                               make_enemy(hp=300, intents=QUIET)])
    st.player.powers["strength"] = 2
    _play(st, "proto_kk_shoal_of_spears")
    assert [e.hp for e in st.enemies] == [300, 300]
    for i in range(3):
        kokomi_plan.schedule(st, plan_card(
            [{"op": "energy", "amount": 1}], cid=f"proto_kk_w{i}"))
    _play(st, "proto_kk_shoal_of_spears")
    assert [e.hp for e in st.enemies] == [300 - 3 * 6, 300 - 3 * 6]

