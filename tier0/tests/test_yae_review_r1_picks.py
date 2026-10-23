"""YAE MIKO, review r1 picks (ruled 2026-10-14) -- the sim's pins.

Design: `review/active/yae-design-axes-2026-10-14.md`, "Review r1, ruled
2026-10-14". Pick 1 (a), LAST BLOOM: a Sakura that withers strikes once more
(as Thunder since shrine r2), then leaves (Fallen Petals banks it after).
Pick 2: Levels have no cap; Fox's Mooncall plants 1 Level higher per copy;
Sakura Grove levels every Sakura at her turn start (shrine r2); Mikage
Thunder levels every Sakura, then Tenko. C# twin: `KleeTests/Prototype/YaeReviewR1PicksTests.cs`.
"""

from __future__ import annotations

import random

import pytest

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy


@pytest.fixture(autouse=True)
def _yae():
    loader.reset_arm_caches()
    Y.SCALING = "level"
    try:
        yield
    finally:
        Y.SCALING = "level"
        loader.reset_arm_caches()


def _enemy(name="e"):
    return Enemy(hp=200, max_hp=200, name=name,
                 intents=[{"kind": "block", "amount": 0}])


def _state(n=1):
    p = Y.build_player()
    p.draw_pile = []
    st = CombatState(player=p, enemies=[_enemy(f"e{i}") for i in range(n)],
                     rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _led(st):
    return Y.ledger(st.player)


def _ym(name):
    return "proto_ym_" + name


def _play(st, card_id, upgraded=False):
    card = loader.get_card(card_id)
    if upgraded:
        card = loader.upgrade_card(card) if hasattr(loader, "upgrade_card") \
            else card.upgraded()
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)
    return card


def _strikes(st, reason=None):
    return [r for r in st.log if r["event"] == "yae_sakura_strike"
            and (reason is None or r["reason"] == reason)]


def _run_out(st):
    """Two turn ends: a fresh Sakura has one strike left."""
    Y.turn_end(st)
    Y.turn_end(st)


# --- Last Bloom ------------------------------------------------------------

def test_a_withering_sakura_blooms_as_thunder():
    # Shrine r2: there is no Rite; the bloom is a Thunder strike.
    st = _state(n=2)
    _play(st, _ym("yakan_evocation"))                # Level 1
    _run_out(st)
    hp = sum(e.hp for e in st.enemies)
    st.player.block = 0
    Y.turn_end(st)
    bloom = _strikes(st, "bloom")
    assert len(bloom) == 1 and bloom[0]["kind"] == Y.THUNDER
    assert bloom[0]["amount"] == _strikes(st, "turn_end")[-1]["amount"]
    assert _led(st).sakura == []
    assert hp - sum(e.hp for e in st.enemies) == 2 * 3
    assert st.player.block == 0


def test_the_bloom_carries_the_sakuras_annotation():
    st = _state()
    _play(st, _ym("yakan_evocation"))
    Y.edit_sakura(st, "every", 1, Y.FOX_FIRE)
    _run_out(st)
    fires = sum(1 for r in st.log if r["event"] == "yae_fox_fire")
    Y.turn_end(st)
    assert sum(1 for r in st.log if r["event"] == "yae_fox_fire") - fires == 2


def test_deadline_extension_never_withers_so_never_blooms():
    st = _state()
    _play(st, _ym("yakan_evocation"))
    Y.edit_sakura(st, "every", 1, Y.DEADLINE)
    for _ in range(6):
        Y.turn_end(st)
    assert len(_led(st).sakura) == 1
    assert not _strikes(st, "bloom")
    assert not any(r["event"] == "yae_wither" for r in st.log)


def test_the_bloom_comes_before_the_wither():
    # (Fallen Petals no longer banks a wither: review r3 made it a Skill.)
    st = _state()
    _play(st, _ym("yakan_evocation"))
    _run_out(st)
    mark = len(st.log)
    Y.turn_end(st)
    events = [r["event"] for r in st.log[mark:]
              if r["event"] in ("yae_sakura_strike", "yae_wither")]
    assert events == ["yae_sakura_strike", "yae_sakura_strike", "yae_wither"]


# --- No Level cap ------------------------------------------------------------

def test_levels_go_past_three():
    st = _state()
    _play(st, _ym("yakan_evocation"))
    for _ in range(4):
        _play(st, _ym("narukami_ray"))           # Rooted Shrine's until cut
    assert _led(st).sakura[0].level == 5
    # The Sakura Levels paper (2026-10-17): 1 + 2 per Level.
    assert Y.tenko_totals(st)[Y.THUNDER] == 1 + 2 * 5
    assert Y.tenko_line(st) == " (Sakura: 11 damage)"


def test_mooncall_copies_stack():
    st = _state()
    _play(st, _ym("foxs_mooncall"))
    _play(st, _ym("yakan_evocation"))
    assert _led(st).sakura[-1].level == 2
    _play(st, _ym("foxs_mooncall"))
    _play(st, _ym("yakan_evocation"))
    assert [s.level for s in _led(st).sakura] == [2, 3]   # no levelling


def test_mooncall_raises_a_plant_at_a_level_too():
    # Guardian of Narukami (Grafted Branch's role until the dedupe cut it,
    # 2026-10-16).
    st = _state()
    _play(st, _ym("foxs_mooncall"))
    _play(st, _ym("guardian_of_narukami"))           # 3, +1
    assert _led(st).sakura[-1].level == 4
    _play(st, _ym("foxs_mooncall"))
    _play(st, _ym("guardian_of_narukami") + "+")     # 3, +2
    assert _led(st).sakura[-1].level == 5


def test_grove_levels_every_sakura_each_turn_start():
    # Shrine r2 (ruled 2026-10-14): "each Sakura gains a Level".
    st = _state()
    _play(st, _ym("sakura_grove"))
    Y.turn_start(st)                                 # none standing: nothing
    _play(st, _ym("yakan_evocation"))
    Y.plant(st, 1, level=3)                          # levels 1 / 3
    Y.turn_start(st)
    assert [s.level for s in _led(st).sakura] == [2, 4]
    _play(st, _ym("sakura_grove"))                   # a second copy
    Y.turn_start(st)
    assert [s.level for s in _led(st).sakura] == [4, 6]
    assert Y.act_size(st, _led(st).sakura[0]) == 1 + 2 * 4


def test_grove_upgrade_costs_zero():
    # Yae deck read 2026-10-23: cost 0, was Innate.
    base, plus = loader.get_card(_ym("sakura_grove")), loader.get_card(_ym("sakura_grove") + "+")
    assert (base.cost, plus.cost) == (1, 0)
    assert not base.innate and not plus.innate


def test_mikage_levels_then_tenkos():
    st = _state()
    _play(st, _ym("yakan_evocation"))                # Level 1
    _play(st, _ym("mikage_thunder"))
    assert _led(st).sakura[0].level == 2
    assert _strikes(st)[-1]["reason"] == "tenko"
    assert _strikes(st)[-1]["amount"] == 1 + 2 * 2   # the Level came first
    assert _led(st).sakura[0].turns_left == Y.SAKURA_TURNS
    _play(st, _ym("mikage_thunder") + "+")           # 2 Levels
    assert _led(st).sakura[0].level == 4
    assert _strikes(st)[-1]["amount"] == 1 + 2 * 4
