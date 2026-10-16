"""FURINA-NEXT PAPER 3, BUILT, in the sim (2026-10-16).

`review/active/furina-next-3-2026-10-16.md`, ruled "Agreed on both
counts": a Repay with a number that cannot return all its HP gains 1 Block
for each HP it could not return, unless the card prints another floor
(Cleansing Torrent keeps its damage). "Repay all" has no floor. The floors
Hymn of Many Waters, Grand Entrance, Charlotte and Sigewinne already paid
apply once, never twice. The readers (Universal Revelry, Critics' Darling)
read the HP returned, not the Block. Pneuma Refrain is Repay 4 [6]; Endless
Waltz Repays 2 first. The C# twin is
`klee-mod/KleeTests/Prototype/FurinaNextThreeRepayFloorTests.cs`.
"""

from __future__ import annotations

import copy

from tier0.content import loader
from tier0.engine import combat, effects, furina_stage as FS, furina_tide as T
from tier0.tests.conftest import make_enemy, make_state


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(hp=78, max_hp=78):
    st = make_state(enemies=[make_enemy(hp=300)], hp=max_hp)
    st.player.character_id = "furina"
    st.player.hp = hp
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    st.player.energy = 9
    return st


def _play(st, cid):
    card = _card(cid)
    st.player.hand.append(card)
    combat.play_card(st, card)
    return card


# ---- the rule: newly covered cards, nothing drained -------------------------

def test_pneuma_refrain_is_repay_4_6_and_pays_4_block_when_healthy():
    assert _card("proto_fs_pneuma_refrain").effects[0]["amount"] == 4
    assert _card("proto_fs_pneuma_refrain+").effects[0]["amount"] == 6
    st = _furina()
    st.player.draw_pile = [_card("strike") for _ in range(5)]
    hand = len(st.player.hand)
    _play(st, "proto_fs_pneuma_refrain")
    assert st.player.block == 4 and st.player.hp == 78
    assert len(st.player.hand) == hand + 2
    st = _furina()
    _play(st, "proto_fs_pneuma_refrain+")
    assert st.player.block == 6


def test_pneuma_refrain_returns_drained_hp_first():
    st = _furina()
    FS.drain(st, 3)
    _play(st, "proto_fs_pneuma_refrain")
    assert st.player.hp == 78 and st.player.block == 1


def test_clean_slate_pays_3_block():
    st = _furina()
    _play(st, "proto_fs_clean_slate")
    assert st.player.block == 3


def test_coup_de_theatre_kill_repay_pays_the_rest_as_block():
    # Drain 3, then the kill's Repay 6 returns those 3 and pays 3 Block (a
    # second enemy keeps the combat going: a won combat pays no floor).
    st = make_state(enemies=[make_enemy(hp=5), make_enemy(hp=300)], hp=78)
    st.player.character_id = "furina"
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    st.player.energy = 9
    _play(st, "proto_fs_riptide_lunge")
    assert st.player.hp == 78 and st.player.block == 3


def test_ousia_pneuma_pneuma_face_pays_the_floor_beside_its_block():
    st = _furina()
    card = _card("proto_fs_ousia_pneuma")
    card.flipped = True                       # on Pneuma
    st.player.hand.append(card)
    combat.play_card(st, card)
    assert st.player.block == 8 + 2


def test_ebb_and_flow_repays_what_it_drained():
    st = _furina()
    _play(st, "proto_fs_ebb_and_flow")
    assert st.player.hp == 76 and st.player.block == 0


def test_fountain_of_lucine_floor_next_turn():
    st = _furina()
    _play(st, "proto_fs_fountain_of_lucine")
    st.player.block = 0
    T.turn_start(st)
    assert st.player.block == 3


def test_salon_solitaire_pays_1_block_with_nothing_drained():
    st = _furina()
    assert st.player.ftd.singer == 1
    T.end_of_turn(st)
    assert st.player.block == 1 and st.player.hp == 78


def test_salon_solitaire_returns_drained_hp_and_pays_nothing_more():
    st = _furina()
    FS.drain(st, 1)
    T.end_of_turn(st)
    assert st.player.block == 0 and st.player.hp == 78


# ---- Endless Waltz: its own Repay counts only when it returns HP ------------

def _waltz(drained):
    st = _furina()
    if drained:
        FS.drain(st, drained)
    hp = st.enemies[0].hp
    _play(st, "proto_fs_rising_tide")
    return hp - st.enemies[0].hp, st.player.hp, st.player.block


def test_endless_waltz_nothing_drained_6_damage_2_block():
    assert _waltz(0) == (6, 78, 2)


def test_endless_waltz_one_drained_9_damage_1_hp_1_block():
    assert _waltz(1) == (9, 78, 1)


def test_endless_waltz_two_drained_9_damage_2_hp():
    assert _waltz(2) == (9, 78, 0)
    assert _waltz(5) == (9, 75, 0)


def test_endless_waltz_upgrade_is_unchanged():
    row = _card("proto_fs_rising_tide+")
    formula = row.effects[1]["amount_formula"]
    assert (formula["base"], formula["per"]) == (6, 4)


# ---- the floors already printed apply once ----------------------------------

def test_hymn_pays_its_floor_once():
    st = _furina()
    _play(st, "proto_fs_hymn_of_many_waters")
    assert st.player.block == 6 + 3


def test_grand_entrance_pays_its_floor_once():
    st = _furina()
    _play(st, "proto_fs_grand_entrance")
    _play(st, "proto_fs_guest_star_charlotte")
    assert st.player.block == 4


def test_charlotte_and_sigewinne_pay_their_floor_once():
    st = _furina()
    st.player.ftd.stage = ["charlotte"]
    T.act(st, "charlotte")
    assert st.player.block == T.CHARLOTTE_ACT_REPAY
    st = _furina()
    st.player.ftd.stage = ["sigewinne"]
    T.act(st, "sigewinne")
    assert st.player.block == T.SIGEWINNE_ACT_REPAY


# ---- the other floors ---------------------------------------------------------

def test_cleansing_torrent_keeps_damage_and_pays_no_block():
    st = _furina()
    hp = st.enemies[0].hp
    _play(st, "proto_fs_cleansing_torrent")
    assert st.player.block == 0
    assert hp - st.enemies[0].hp == 10 + 4


def test_repay_all_gives_nothing_at_0():
    for cid in ("proto_fs_singer_of_many_waters",
                "proto_fs_grand_absolution"):
        st = _furina()
        _play(st, cid)
        assert st.player.block == 0, cid


def test_teardrop_doubles_the_floor():
    assert T.floor_block(3) == 3
    assert T.floor_block(3, teardrops=1) == 6
    assert T.floor_block(0, teardrops=1) == 0


# ---- the readers read HP returned, not the Block -------------------------------

def test_revelry_reads_no_fanfare_off_the_block():
    st = _furina()
    _play(st, "proto_fs_universal_revelry")
    before = st.player.ftd.fanfare
    _play(st, "proto_fs_pneuma_refrain")
    assert st.player.block == 4
    assert st.player.ftd.fanfare == before


def test_critics_darling_deals_nothing_off_the_block():
    st = _furina()
    _play(st, "proto_fs_critics_darling")
    hp = st.enemies[0].hp
    _play(st, "proto_fs_pneuma_refrain")
    assert st.player.block == 4
    assert st.enemies[0].hp == hp
