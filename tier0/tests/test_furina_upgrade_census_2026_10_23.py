"""FURINA'S UPGRADE CENSUS (2026-10-23) in the one-seat sim.

[USER]: "Otherwise I agreed on all the cards!" Eight of her seventeen
cost-only upgrades became real ones, every cost kept
(`review/active/furina-next-3-2026-10-16.md`, "Upgrade census
(2026-10-23)"). The C# twin is
`klee-mod/KleeTests/Prototype/FurinaUpgradeCensusTests.cs`.
"""

from __future__ import annotations

import copy

import pytest

from tier0.content import loader
from tier0.engine import combat, furina_stage as FS, furina_tide as T
from tier0.tests.conftest import make_enemy, make_state

CENSUS = ("proto_fs_let_the_people_rejoice", "proto_fs_the_show_must_go_on",
          "proto_fs_tutti", "proto_fs_rainfall_overture",
          "proto_fs_the_masquerade", "proto_fs_critics_darling",
          "proto_fs_showstopper", "proto_fs_ensemble_cast")


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(hp=78, max_hp=78, enemies=None):
    st = make_state(enemies=enemies or [make_enemy(hp=300)], hp=max_hp)
    st.player.character_id = "furina"
    st.player.hp = hp
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    st.player.energy = 9
    return st


def _play(st, card):
    st.player.hand.append(card)
    combat.play_card(st, card)


@pytest.mark.parametrize("cid", CENSUS)
def test_no_census_card_cuts_its_cost(cid):
    assert loader.get_card(cid + "+").cost == loader.get_card(cid).cost
    assert "cost" not in (loader.get_card(cid).upgrade or {})


def test_let_the_people_rejoice_upgraded_deals_3_a_point():
    st = _furina()
    T.gain(st, 5, "test")
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_let_the_people_rejoice+"))
    assert hp - st.enemies[0].hp == 15
    assert T._f(st).fanfare == 0


def test_the_show_must_go_on_upgraded_retains():
    assert not loader.get_card("proto_fs_the_show_must_go_on").retain
    assert loader.get_card("proto_fs_the_show_must_go_on+").retain


def test_rainfall_overture_upgraded_draws_1():
    st = _furina(enemies=[make_enemy(hp=50), make_enemy(hp=50)])
    st.player.draw_pile = [_card("strike") for _ in range(3)]
    _play(st, _card("proto_fs_rainfall_overture+"))
    assert len(st.player.hand) == 1


def test_the_masquerade_upgraded_gains_2_more_a_drain():
    st = _furina()
    _play(st, _card("proto_fs_the_masquerade+"))
    assert st.player.powers.get(FS.THE_MASQUERADE_PLUS) == 1
    block = st.player.block
    T.drain(st, 3)
    assert st.player.block - block == 3 + T.MASQUERADE_PLUS_BLOCK


def test_critics_darling_upgraded_deals_1_more():
    st = _furina()
    _play(st, _card("proto_fs_critics_darling+"))
    hp = st.enemies[0].hp
    T.drain(st, 4)
    assert hp - st.enemies[0].hp == 4 + T.CRITICS_DARLING_RAISE


def test_showstopper_upgraded_spends_3():
    st = _furina()
    _play(st, _card("proto_fs_showstopper+"))
    FS.guest_star(st, "clorinde")
    f = T._f(st)
    f.fanfare = 3
    T.end_of_turn(st)
    assert f.ledger.get("showstopper_rounds", 0) == 1
    st = _furina()
    _play(st, _card("proto_fs_showstopper"))
    FS.guest_star(st, "clorinde")
    f = T._f(st)
    f.fanfare = 3
    T.end_of_turn(st)
    assert f.ledger.get("showstopper_rounds", 0) == 0


def test_ensemble_cast_upgraded_summons_2():
    st = _furina()
    _play(st, _card("proto_fs_ensemble_cast"))
    assert len(T._f(st).stage) == 1
    st = _furina()
    _play(st, _card("proto_fs_ensemble_cast+"))
    assert len(T._f(st).stage) == 2
