"""Yae draft pass, 2026-10-17 (review/active/yae-draft-pass-2026-10-17.md
sec.1 and sec.3). [USER] on round 9's pick: "I agree with the starter change,
but let's also scan the draft rates and see what cards the seats refuse to
take and wherever they are bad value or just undervalued by the seats." Sim
half; the C# half is `klee-mod/KleeTests/Prototype/YaeDraftPassTests.cs`.

Pinned: Yakan Evocation's "It strikes now." (no target: the Lure's, Hunting
Gaze's or a random enemy); Falling Blossom's "Your oldest Sakura strikes this
enemy." (no wither); Dawn Prayer's Levels, then its strike; Kitsune Pounce's
"deal 5 more" on a Weak enemy, read before the hit; Mikage Thunder's 7 first;
The Seven Glamours at 1. Every strike here uses none of its turns and is not
a Tenko.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import combat, effects
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy


@pytest.fixture(autouse=True)
def yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        loader.reset_arm_caches()


def _enemy(name="e0", hp=100):
    return Enemy(hp=hp, max_hp=hp, name=name,
                 intents=[{"kind": "block", "amount": 0}])


def _state(n_enemies=1, seed=0, hps=None):
    p = Y.build_player()
    p.draw_pile = [loader.get_card("defend") for _ in range(10)]
    hps = hps or [100] * n_enemies
    st = CombatState(player=p,
                     enemies=[_enemy(f"e{i}", hp) for i, hp in enumerate(hps)],
                     rng=random.Random(seed))
    st.turn = 1
    st.in_player_turn = True
    return st


def _card(name):
    return loader.get_card("proto_ym_" + name)


def _play(st, card, target=None):
    if isinstance(card, str):
        card = _card(card)
    if card not in st.player.hand:
        st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    if target is None:
        combat.play_card(st, card)
        return card
    orig = effects.bind_card_aim
    effects.bind_card_aim = lambda state, c: target
    try:
        combat.play_card(st, card)
    finally:
        effects.bind_card_aim = orig
    return card


def _led(st):
    return Y.ledger(st.player)


def _hp(st):
    return [e.hp for e in st.enemies]


def _strikes(st):
    return [r for r in st.log if r["event"] == "yae_sakura_strike"]


# --- sec.1: Yakan Evocation, "It strikes now." --------------------------------------

def test_yakan_evocation_plants_and_its_sakura_strikes_now():
    st = _state()
    _play(st, "yakan_evocation")
    led = _led(st)
    assert len(led.sakura) == 1 and led.sakura[0].level == Y.PLANT_LEVEL
    strikes = _strikes(st)
    assert len(strikes) == 1 and strikes[0]["reason"] == "strike_planted"
    assert _hp(st) == [100 - (Y.SAKURA_BASE + Y.SAKURA_PER_LEVEL * 1)]
    assert led.sakura[0].turns_left == Y.SAKURA_TURNS   # none of its turns
    assert not [r for r in st.log if r["event"] == "yae_tenko"]


def test_yakan_evocation_has_no_target_so_the_lure_aims_it():
    # e0 is the lowest-HP enemy the sim binds a play to; the Lure is on e2.
    # An aimed strike would land on e0, so landing on e2 shows no aim.
    st = _state(hps=[50, 100, 100])
    _play(st, "foxfire_lure", target=st.enemies[2])
    _play(st, "yakan_evocation")
    assert [r["target"] for r in _strikes(st)] == ["e2"]


def test_yakan_evocation_strikes_hunting_gazes_target():
    st = _state(hps=[50, 100, 100], seed=3)
    _play(st, "hunting_gaze")
    _play(st, loader.get_card("strike"), target=st.enemies[1])
    _play(st, "yakan_evocation")
    assert [r["target"] for r in _strikes(st)] == ["e1"]


def test_yakan_evocation_with_neither_picks_a_random_enemy():
    seen = set()
    for seed in range(12):
        st = _state(hps=[50, 100, 100], seed=seed)
        _play(st, "yakan_evocation")
        seen |= {r["target"] for r in _strikes(st)}
    assert len(seen) > 1                     # not always the bound lowest-HP


def test_yakan_evocation_upgrade_stays_cost_minus_one():
    assert (_card("yakan_evocation").cost,
            loader.get_card("proto_ym_yakan_evocation+").cost) == (1, 0)


# --- sec.3: Falling Blossom ---------------------------------------------------------

def test_falling_blossom_the_oldest_strikes_this_enemy_and_stays():
    st = _state(n_enemies=3)
    Y.plant(st, 2)
    oldest = _led(st).sakura[0]
    _play(st, "falling_blossom", target=st.enemies[1])
    led = _led(st)
    assert len(led.sakura) == 2 and led.sakura[0] is oldest
    assert oldest.turns_left == Y.SAKURA_TURNS
    assert not [r for r in st.log if r["event"] == "yae_wither"]
    strikes = _strikes(st)
    assert len(strikes) == 1 and strikes[0]["target"] == "e1"
    assert _hp(st) == [100, 100 - 7 - (Y.SAKURA_BASE + Y.SAKURA_PER_LEVEL * 1), 100]


def test_falling_blossom_upgrade_is_10():
    st = _state()
    _play(st, "falling_blossom+")
    assert _hp(st) == [90] and not _strikes(st)


# --- sec.3: Dawn Prayer -------------------------------------------------------------

def test_dawn_prayer_levels_the_newest_then_it_strikes_now():
    st = _state()
    Y.plant(st, 2)
    _play(st, "dawn_prayer")
    led = _led(st)
    assert [s.level for s in led.sakura] == [1, 3]
    strikes = _strikes(st)
    assert len(strikes) == 1 and strikes[0]["level"] == 3   # Levels first
    assert _hp(st) == [100 - (Y.SAKURA_BASE + Y.SAKURA_PER_LEVEL * 3)]
    assert led.sakura[-1].turns_left == Y.SAKURA_TURNS
    assert not [r for r in st.log if r["event"] == "yae_tenko"]


def test_dawn_prayer_upgraded_gains_3_and_strikes():
    st = _state()
    Y.plant(st, 1)
    _play(st, "dawn_prayer+")
    assert _led(st).sakura[0].level == 4
    assert _hp(st) == [100 - (Y.SAKURA_BASE + Y.SAKURA_PER_LEVEL * 4)]


def test_dawn_prayer_strikes_the_lures_target():
    st = _state(hps=[50, 100, 100])
    Y.plant(st, 1)
    _play(st, "foxfire_lure", target=st.enemies[2])
    _play(st, "dawn_prayer")
    assert [r["target"] for r in _strikes(st)] == ["e2"]


def test_dawn_prayer_with_none_standing_does_nothing():
    st = _state()
    _play(st, "dawn_prayer")
    assert not _led(st).sakura and not _strikes(st) and _hp(st) == [100]


# --- sec.3: Kitsune Pounce ----------------------------------------------------------

def test_kitsune_pounce_deals_5_more_to_a_weak_enemy():
    for name, plain, weak in (("kitsune_pounce", 8, 13),
                              ("kitsune_pounce+", 11, 16)):
        st = _state()
        Y.plant(st, 1)
        _play(st, name)
        assert _hp(st) == [100 - plain], name
        st = _state()
        Y.plant(st, 1)
        st.enemies[0].powers["weak"] = 1
        _play(st, name)
        assert _hp(st) == [100 - weak], name
        assert not _strikes(st), name            # no Sakura strike any more


def test_kitsune_pounce_reads_weak_before_the_hit():
    row = _card("kitsune_pounce").effects
    assert row[0]["op"] == "conditional"
    assert row[0]["if"] == "target_has_power_weak"
    assert row[1] == {"op": "damage", "amount": 8, "target": "enemy"}
    # A Weak enemy at 6 HP: the bonus 5 and the 8 both land on it; the kill
    # does not lose the bonus.
    st = _state(hps=[6])
    st.enemies[0].powers["weak"] = 1
    _play(st, "kitsune_pounce")
    assert not st.enemies[0].alive


# --- sec.3: Mikage Thunder ----------------------------------------------------------

def test_mikage_thunder_deals_7_first_then_levels_then_tenko():
    st = _state(n_enemies=2)
    Y.plant(st, 1)
    _play(st, "mikage_thunder", target=st.enemies[1])
    assert _led(st).sakura[0].level == 2
    tenko = [r for r in _strikes(st) if r["reason"] == "tenko"]
    assert len(tenko) == 1 and tenko[0]["level"] == 2
    # 7 on its target; the Tenko's strike (Level 2) on a random enemy.
    assert sum(100 - h for h in _hp(st)) == 7 + (Y.SAKURA_BASE + Y.SAKURA_PER_LEVEL * 2)
    assert st.enemies[1].hp <= 100 - 7
    events = [r["event"] for r in st.log]
    assert events.index("damage") < events.index("yae_tenko")


def test_mikage_thunder_upgrade_is_2_levels_and_still_7():
    st = _state()
    Y.plant(st, 1)
    _play(st, "mikage_thunder+")
    assert _led(st).sakura[0].level == 3
    assert _hp(st) == [100 - 7 - (Y.SAKURA_BASE + Y.SAKURA_PER_LEVEL * 3)]


def test_mikage_thunder_with_an_empty_shrine_still_deals_7():
    st = _state()
    _play(st, "mikage_thunder")
    assert _hp(st) == [93] and not _strikes(st)


# --- sec.3: The Seven Glamours ------------------------------------------------------

def test_the_seven_glamours_costs_1_and_upgrades_to_16():
    c = _card("the_seven_glamours")
    up = loader.get_card("proto_ym_the_seven_glamours+")
    assert (c.cost, up.cost, c.exhaust) == (1, 1, True)
    st = _state()
    _play(st, "the_seven_glamours+")
    assert _hp(st) == [84]


# --- BACKLOG check, Yae round 9 lane 4: Narukami Ray through Reprint ---------------
# Not a bug. A replay is the whole card again (5 to ALL and the Level), and a
# Published Reprint replays only the card's FIRST play each combat, so a
# later Narukami Ray that combat plays once and levels once.

def test_narukami_ray_reprinted_levels_on_each_play():
    st = _state(n_enemies=2)
    Y.plant(st, 1)
    ray = _card("narukami_ray")
    st.player.hand.append(ray)
    Y.annotate(st, ray, Y.REPRINT)
    _play(st, ray)
    assert _led(st).sakura[0].level == 3                 # two plays, two Levels
    assert _hp(st) == [90, 90]


def test_a_published_reprint_ray_levels_twice_then_once_that_combat():
    slot = len(Y.starter_ids())
    ray = Y.build_player(extra=("proto_ym_narukami_ray",),
                         published={slot: Y.REPRINT}).draw_pile[slot]
    assert ray.id == "proto_ym_narukami_ray" and Y.stack(ray) == [Y.REPRINT]
    st = _state(n_enemies=2)
    Y.plant(st, 1)
    _play(st, ray)
    assert _led(st).sakura[0].level == 3                 # first play: twice
    _play(st, ray)
    assert _led(st).sakura[0].level == 4                 # spent: once
    assert _hp(st) == [85, 85]
