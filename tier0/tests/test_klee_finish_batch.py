"""THE KLEE FINISH-LINE BATCH (2026-10-03): the sim half.

[USER], after the Klee finish-line run: "Agreed all around!" to five changes.
The C# twin is `KleeTests/Prototype/KleeFinishBatchTests.cs`; readings in
`docs/notes/prototype-surface-provenance.md`, "Klee finish-line batch,
2026-10-03". NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

from tier0.content import loader, upgrades
from tier0.engine import combat, klee_overhaul, statuses
from tier0.tests.conftest import make_enemy
from tier0.tests.test_klee_r276_expansion import (  # noqa: F401
    klee_state, load, overhaul, play, sizes)
from tier05 import relics as t05


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _first(card, op):
    return next(fx for fx in card.effects if fx.get("op") == op)


def _confiscated():
    return loader.get_card(klee_overhaul.CONFISCATED_ID)


# 1. Confiscated is a Status ----------------------------------------------------

def test_confiscated_is_a_status_that_still_plays_for_one(overhaul):
    """"Confiscated should be a Status, not a Skill?" Status type and rarity,
    and still playable for 1 Energy, doing nothing (the base game's Slimed
    shape). A base-game status stays unplayable."""
    card = _confiscated()
    assert (card.type, card.rarity, card.cost) == ("status", "status", 1)
    assert card.effects == []
    st = klee_state()
    assert combat.card_cost(st, card) == 1
    assert combat.card_playable(st, card) is True
    assert combat.card_playable(st, statuses.make_status("dazed")) is False


def test_the_status_readers_see_confiscated(overhaul):
    """Kitchen Alchemy's and Dust of Purification's exhaust takes it."""
    st = klee_state()
    st.player.hand = [_confiscated(), load("proto_ko_pop")]
    assert klee_overhaul.exhaust_statuses(st) == 1
    assert [c.id for c in st.player.hand] == ["proto_ko_pop"]


# 2. Finders Keepers draws ------------------------------------------------------

def test_finders_keepers_is_6_upgrading_to_8(overhaul):
    # 4 [6] until the Klee design review (2026-10-08): every placer +2.
    card = load("proto_ko_finders_keepers")
    assert _first(card, "apply_power")["amount"] == 6
    assert _first(_up("proto_ko_finders_keepers"), "apply_power")["amount"] == 8


# 3. Dodoco Tales opens at 5 ----------------------------------------------------

def test_dodoco_tales_banks_four_more_sparks():
    fx = t05.ancient_pool()["touch_of_orobas_klee"]["effects"]
    assert {"hook": "combat_start_spark", "amount": 4} in fx


# 4. Mine, All Mine! places a Mine ----------------------------------------------

def test_mine_all_mine_is_damage_then_a_mine(overhaul):
    card = load("proto_ko_mine_all_mine")
    assert [fx["op"] for fx in card.effects] == ["damage", "plant_bomb"]
    assert _first(card, "damage")["amount"] == 8
    assert _first(card, "plant_bomb")["size"] == 6     # 4 until 2026-10-08
    assert _first(card, "plant_bomb")["mine"] is True
    up = _up("proto_ko_mine_all_mine")
    assert _first(up, "damage")["amount"] == 11
    assert _first(up, "plant_bomb")["size"] == 8


def test_mine_all_mine_sets_nothing_off(overhaul):
    a = make_enemy(hp=200)
    st = klee_state([a])
    klee_overhaul.place(st, a, 5, is_mine=True)
    play(st, load("proto_ko_mine_all_mine"), aim=a)
    assert [(c.size, c.is_mine) for c in a.ko_charges] == [(5, True),
                                                           (6, True)]
    assert a.hp < 200


# 5. Amber is Uncommon ----------------------------------------------------------

def test_amber_explosive_puppet_is_uncommon():
    assert load("proto_mc_amber_explosive_puppet").rarity == "uncommon"
