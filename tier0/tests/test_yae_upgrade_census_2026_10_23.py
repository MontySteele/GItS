"""YAE UPGRADE CENSUS (2026-10-23). [USER], on the census (Yae had 10
cost-only and 6 Innate-only upgrades, against base Ironclad 6/2 and Silent
9/3): "Otherwise I agreed on all the cards!"

  Kitsune Rite        Tenko. Draw 1 [2] card(s).          (was cost -1)
  Royalties           Edit up to 2 [3] cards ...          (was cost -1)
  Scattered Blossoms  ... a Sakura withers, draw 2 [3].   (was Innate)
  Saiguu's Lesson     ... [Apply 1 Weak to ALL enemies.]  (was Innate)

C# half: `YaeUpgradeCensusTests`. Record: the Yae block/edit pass paper,
"Upgrade census (2026-10-23)".
"""
from __future__ import annotations

import random

from tier0.content import loader
from tier0.engine import combat
from tier0.engine import yae_shrine as Y
from tier0.engine.state import CombatState, Enemy


def _card(name):
    return loader.get_card("proto_ym_" + name)


def _state(n_enemies=2):
    p = Y.build_player()
    p.draw_pile = [loader.get_card("defend") for _ in range(10)]
    enemies = [Enemy(hp=100, max_hp=100, name=f"e{i}",
                     intents=[{"kind": "block", "amount": 0}])
               for i in range(n_enemies)]
    st = CombatState(player=p, enemies=enemies, rng=random.Random(0))
    st.turn = 1
    st.in_player_turn = True
    return st


def _play(st, card):
    st.player.hand.append(card)
    st.player.energy = max(st.player.energy, 10)
    combat.play_card(st, card)


def _draw(card):
    return [fx["amount"] for fx in card.effects if fx["op"] == "draw"]


def test_no_census_card_cuts_cost_or_gains_innate():
    for name in ("kitsune_rite", "royalties", "enlightened_blessing",
                 "saiguus_lesson"):
        base, plus = _card(name), _card(name + "+")
        assert plus.cost == base.cost == 1, name
        assert not plus.innate, name


def test_kitsune_rite_draws_one_more():
    assert (_draw(_card("kitsune_rite")), _draw(_card("kitsune_rite+"))) \
        == ([1], [2])


def test_royalties_edits_one_more():
    amount = lambda c: next(fx["amount"] for fx in c.effects
                            if fx["op"] == "yae")
    assert (amount(_card("royalties")), amount(_card("royalties+"))) == (2, 3)


def test_scattered_blossoms_draws_one_more_per_wither():
    st = _state()
    _play(st, _card("enlightened_blessing+"))
    assert st.player.powers[Y.ENLIGHTENED_BLESSING] == 3
    Y.plant(st, 1)
    hand = len(st.player.hand)
    Y.wither_next(st)
    assert len(st.player.hand) == hand + 3


def test_saiguus_lesson_plus_weakens_all_and_triggers_itself():
    st = _state()
    Y.plant(st, 1)
    _play(st, _card("saiguus_lesson+"))
    assert st.player.powers[Y.SAIGUUS_LESSON] == 1
    assert [e.powers.get("weak", 0) for e in st.enemies] == [1, 1]
    # The Weak lands after the power, so the Sakura strikes each enemy.
    assert all(e.hp < 100 for e in st.enemies)


def test_saiguus_lesson_unupgraded_applies_no_weak():
    st = _state()
    Y.plant(st, 1)
    _play(st, _card("saiguus_lesson"))
    assert [e.powers.get("weak", 0) for e in st.enemies] == [0, 0]
    assert all(e.hp == 100 for e in st.enemies)


# --- Rare audit: Sacred Thunderbolt (2026-10-23) ----------------------------
# [USER]: "Sacred Thunderbolt - agreed, but is that enough at 2 cost? It
# sounds expensive... either go to 1 cost or buff the effect". Cost 1:
# "Deal 9 [12] Electro damage. If it triggers an Elemental Reaction, each
# Sakura gains a Level."

def test_sacred_thunderbolt_is_a_one_cost_nine_twelve():
    base, plus = _card("sacred_thunderbolt"), _card("sacred_thunderbolt+")
    assert (base.rarity, base.cost, plus.cost) == ("rare", 1, 1)
    hit = lambda c: next(fx["amount"] for fx in c.effects
                         if fx["op"] == "damage")
    assert (hit(base), hit(plus)) == (9, 12)


def _levels(st):
    return [s.level for s in Y.ledger(st.player).sakura]


def test_sacred_thunderbolt_levels_each_sakura_on_a_reaction():
    st = _state(n_enemies=1)
    st.enemies[0].aura, st.enemies[0].aura_turns_left = "hydro", 2
    Y.plant(st, 2)
    before = _levels(st)
    _play(st, _card("sacred_thunderbolt"))
    assert _levels(st) == [lv + 1 for lv in before]


def test_sacred_thunderbolt_without_a_reaction_levels_nothing():
    st = _state(n_enemies=1)
    Y.plant(st, 2)
    before = _levels(st)
    _play(st, _card("sacred_thunderbolt"))
    assert _levels(st) == before
    assert st.enemies[0].hp == 100 - 9
