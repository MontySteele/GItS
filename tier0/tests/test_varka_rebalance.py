"""VARKA, THE REBALANCE -- the sim engine's pins.

`review/active/varka-rebalance-2026-10-03.md` secs.2-5 (ruled 2026-10-03,
the starters at the PR #863 sim's variant A) and the Varka part of
`review/active/aoe-trim-2026-10-03.md` sec.4. Rows: the `proto_vk_` block of
`docs/prototype-surface.yaml`; rules: `tier0/engine/varka_oath.py`. The C#
twin is `klee-mod/KleeTests/Prototype/VarkaRebalanceTests.cs`.
"""

from __future__ import annotations

import copy
import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier0.engine import varka_oath as V
from tier0.engine.state import CombatState, Enemy
from tools import varka_expansion_sim as X


@pytest.fixture
def rebalance():
    saved = (C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA)
    C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA = True, True
    loader.reset_arm_caches()
    try:
        yield
    finally:
        C.SWIRL_PAYS, C.CRYSTALLIZE_KEEPS_AURA = saved
        loader.reset_arm_caches()


def _enemy(hp=100, name="e", aura=None):
    e = Enemy(hp=hp, max_hp=hp, name=name,
              intents=[{"kind": "block", "amount": 0}])
    if aura:
        e.aura, e.aura_turns_left, e.aura_spent = aura, 2, False
    return e


def _state(n=1, element="pyro", enemies=None):
    enemies = enemies or [_enemy(name=f"e{i}") for i in range(n)]
    p = V.build_player(element, fang=False)
    p.draw_pile = [loader.get_card("strike") for _ in range(10)]
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _vk(name):
    return "proto_vk_" + name


def _play(st, card, energy=10):
    if isinstance(card, str):
        card = loader.get_card(card)
    st.player.hand.append(card)
    st.player.energy = energy
    combat.play_card(st, card)
    return card


def _attack(amount=8):
    """A plain one-hit Anemo Attack (Favonius Cut, re-numbered)."""
    card = copy.deepcopy(loader.get_card(_vk("favonius_cut")))
    card.cost = 1
    card.effects = [{"op": "damage", "amount": amount, "target": "enemy"}]
    return card


# ---------------------------------------------------------------------------
# 1. The overlay and the worlds.
# ---------------------------------------------------------------------------

NEW = ("rippling_guard", "kindled_edge", "storm_battery", "frost_ward")
GONE = ("wind_wall", "cavalry_charge", "gust_ward", "favonius_drill")


def test_four_rows_swapped_and_the_pool_stays_78(rebalance):
    pool = X.pool()
    ids = {c for r in pool.values() for c in r}
    assert sum(len(v) for v in pool.values()) == 78
    assert {k: len(v) for k, v in pool.items()} == {
        "common": 20, "uncommon": 35, "rare": 23}
    assert {_vk(c) for c in NEW} <= ids
    sheet = {c.id for c in loader.prototype_cards()}
    assert not ({_vk(c) for c in GONE} & sheet)


def test_every_changed_row_upgrades(rebalance):
    for cid in [_vk(c) for c in NEW] + [
            _vk("barbara_show_begin"), _vk("barbara_whisper_of_water"),
            _vk("razor_claw_and_thunder")] + list(
            V.STARTER_KNIGHT_IDS.values()):
        assert loader.get_card(cid + "+").effects != \
            loader.get_card(cid).effects, cid


# ---------------------------------------------------------------------------
# 2. The Oath rule (sec.2).
# ---------------------------------------------------------------------------

def test_wildfire_is_half_pyro_oath_whatever_the_element(rebalance):
    st = _state()
    led = V.ledger(st.player)
    led.current, led.oath["pyro"] = "hydro", 7
    st.player.powers[V.WILDFIRE_OATH] = 1
    _play(st, _attack(8))
    assert st.enemies[0].hp == 100 - 8 - 3          # half of 7, rounded down
    _play(st, _attack(8))                           # not the first Attack
    assert st.enemies[0].hp == 100 - 8 - 3 - 8


def test_absolute_zero_pays_cryo_oath_per_debuff(rebalance):
    st = _state()
    led = V.ledger(st.player)
    led.current, led.oath["cryo"] = "pyro", 3
    st.player.powers[V.ABSOLUTE_ZERO] = 1
    _play(st, _vk("mika_starfrost_swirl"))          # Cryo and 2 Weak
    # The Cryo landed first and credited 1 Oath: 4, once for the one apply.
    assert st.enemies[0].hp == 100 - 4
    assert st.enemies[0].powers.get("weak") == 2


def test_absolute_zero_no_longer_widens_the_swirl(rebalance):
    st = _state(n=2, enemies=[_enemy(name="a", aura="hydro"),
                              _enemy(name="b", aura="hydro")])
    led = V.ledger(st.player)
    led.current = "cryo"
    st.player.powers[V.ABSOLUTE_ZERO] = 1
    _play(st, _vk("jean_dandelion_breeze"))
    weak = [e.powers.get("weak", 0) for e in st.enemies]
    assert weak == [0, 0]


def test_cycle_of_seasons_hits_one_random_enemy(rebalance):
    st = _state(n=3)
    st.player.powers[V.CYCLE_OF_SEASONS] = 4
    V.set_current(st, "hydro", knight=False)
    lost = sorted(100 - e.hp for e in st.enemies)
    assert lost == [0, 0, 4]


# ---------------------------------------------------------------------------
# 3. Hydro (sec.3).
# ---------------------------------------------------------------------------

def test_gleeful_songs_pays_per_reacting_enemy(rebalance):
    st = _state(n=3, enemies=[_enemy(name="a", aura="pyro"),
                              _enemy(name="b", aura="cryo"),
                              _enemy(name="c")])
    _play(st, _vk("barbara_show_begin"))
    assert st.player.block == 4 + 3 * 2
    assert st.enemies[2].aura == "hydro"


def test_rippling_guard_counts_the_other_cards_played(rebalance):
    st = _state()
    _play(st, _attack(1))
    _play(st, _attack(1))
    _play(st, _vk("rippling_guard"))
    assert st.player.block == 3 + 2 * 2
    assert st.enemies[0].aura == "hydro"


def test_whisper_of_water_lasts_two_more_turns(rebalance):
    st = _state()
    _play(st, _vk("barbara_whisper_of_water"))
    assert st.player.block == 4
    for turn in (2, 3, 4):
        st.player.block = 0
        st.turn = turn
        V.turn_start(st)
        assert st.player.block == (4 if turn < 4 else 0), turn


# ---------------------------------------------------------------------------
# 4. Payoffs that borrow (sec.4) and the AoE trim (aoe-trim sec.4).
# ---------------------------------------------------------------------------

def _hits(st, name):
    return [r for r in st.log if r.get("event") == "damage"
            and r.get("target") == name]


def test_kindled_edge_hits_again_on_a_reaction(rebalance):
    st = _state(enemies=[_enemy(name="a", aura="hydro")])
    _play(st, _vk("kindled_edge"))
    assert len(_hits(st, "a")) == 2
    st = _state(enemies=[_enemy(name="b")])
    _play(st, _vk("kindled_edge"))
    assert len(_hits(st, "b")) == 1
    assert st.enemies[0].hp == 100 - 7 and st.enemies[0].aura == "pyro"


def test_storm_battery_counts_the_other_cards_in_hand(rebalance):
    st = _state(n=2)
    st.player.hand = [loader.get_card("strike") for _ in range(4)]
    _play(st, _vk("storm_battery"))
    assert [e.hp for e in st.enemies] == [100 - 8, 100 - 8]
    assert loader.get_card(_vk("storm_battery")).cost == 1


def test_frost_ward_weakens_each_aura_and_blocks_for_each(rebalance):
    st = _state(n=3, enemies=[_enemy(name="a", aura="pyro"),
                              _enemy(name="b", aura="hydro"),
                              _enemy(name="c")])
    _play(st, _vk("frost_ward"))
    assert [e.powers.get("weak", 0) for e in st.enemies] == [1, 1, 0]
    assert st.player.block == 6


def test_awakening_hits_one_enemy_more_if_electro(rebalance):
    st = _state(n=2, enemies=[_enemy(name="a", aura="electro"),
                              _enemy(name="b", aura="electro")])
    _play(st, _vk("razor_claw_and_thunder"))
    lost = sorted(100 - e.hp for e in st.enemies)
    assert lost == [0, 4 + 3]


# ---------------------------------------------------------------------------
# 5. The four starter Knights (sec.5).
# ---------------------------------------------------------------------------

def test_amber_hits_and_blocks(rebalance):
    st = _state()
    _play(st, V.STARTER_KNIGHT_IDS["pyro"])
    assert st.enemies[0].hp == 100 - 7 and st.player.block == 5
    assert st.enemies[0].aura == "pyro"


def test_barbara_blocks_now_and_next_turn(rebalance):
    st = _state(element="hydro")
    _play(st, V.STARTER_KNIGHT_IDS["hydro"])
    assert st.player.block == 6 and st.enemies[0].aura == "hydro"
    assert st.player.powers.get("block_next_turn") == 3


def test_lisa_blocks_and_draws(rebalance):
    st = _state(element="electro")
    _play(st, V.STARTER_KNIGHT_IDS["electro"])
    assert st.player.block == 6 and len(st.player.hand) == 1
    assert st.enemies[0].aura == "electro"


def test_kaeya_blocks_and_weakens(rebalance):
    st = _state(element="cryo")
    _play(st, V.STARTER_KNIGHT_IDS["cryo"])
    assert st.player.block == 5 and st.enemies[0].aura == "cryo"
    assert st.enemies[0].powers.get("weak") == 1


# ---------------------------------------------------------------------------
# 5b. The starter ruling, 2026-10-03: Ascension costs 2 with Retain (Regent's
#     Sovereign Blade), 10 [13]; Windbound Execution costs 0, one enemy.
# ---------------------------------------------------------------------------

def test_ascension_costs_2_retains_and_hits_10(rebalance):
    card = loader.get_card(_vk("four_winds_ascension"))
    assert (card.cost, card.retain) == (2, True)
    assert [e["amount"] for e in card.effects if e["op"] == "damage"] == [10]
    up = loader.get_card(_vk("four_winds_ascension") + "+")
    assert (up.cost, up.retain) == (2, True)
    assert [e["amount"] for e in up.effects if e["op"] == "damage"] == [13]
    # The Fang's created copy carries the keyword the end-of-turn flush reads.
    st = _state()
    V._add_ascension(st, upgraded=False)
    made = [c for c in st.player.hand if c.id == _vk("four_winds_ascension")]
    assert made and made[0].retain is True


def test_windbound_costs_0_and_hits_one_enemy(rebalance):
    card = loader.get_card(_vk("windbound_execution"))
    assert card.cost == 0
    assert [e.get("target") for e in card.effects] == ["enemy"]
    st = _state(n=3)
    _play(st, card)
    assert sorted(e.hp for e in st.enemies) == [96, 100, 100]


# ---------------------------------------------------------------------------
# 6. The harness's reads.
# ---------------------------------------------------------------------------

def test_multi_target_groups():
    log = [{"turn": 1, "event": "play", "card": "x"},
           {"turn": 1, "event": "damage", "target": "a#0", "amount": 4},
           {"turn": 1, "event": "damage", "target": "a#1", "amount": 4},
           {"turn": 1, "event": "block", "amount": 5},
           {"turn": 1, "event": "play", "card": "y"},
           {"turn": 1, "event": "damage", "target": "a#0", "amount": 6,
            "blocked": 2}]
    assert X._log_reads(log) == (5, 16.0, 8.0)
