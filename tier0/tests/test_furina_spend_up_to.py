"""THE SPEND PAPER, BUILT AT ITS DEFAULTS, in the sim (2026-10-10).

`review/ruled/furina-spend-paper-2026-10-10.md` picks 1 and 2 (the picks
are open on #1014). "Spend up to X" spends X, or all she holds if that is
less, never fails, and is a Spend only when at least 1 counts; it is not a
spend-all, so Bis! and Standing Room Only ignore it. Navia's line makes the
first 2 [3] points of the first Spend each turn free. Navia's act Spends half
the bank and Freminet's a quarter (ruled 2026-10-10), rounded down, oldest
first. The C# twin is
`klee-mod/KleeTests/Prototype/FurinaSpendUpToTests.cs`.
"""

from __future__ import annotations

import copy

import pytest

from tier0.content import loader
from tier0.engine import combat, furina_stage as FS, furina_tide as T
from tier0.tests.conftest import make_enemy, make_state


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(fanfare=0, stage=(), enemies=None):
    st = make_state(enemies=enemies or [make_enemy(hp=300)], hp=78)
    st.player.character_id = "furina"
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    st.player.energy = 9
    st.player.ftd.fanfare = fanfare
    st.player.ftd.stage = list(stage)
    st.player.draw_pile = [_card("proto_fs_velvet_curtain") for _ in range(5)]
    return st


def _play(st, card):
    st.player.hand.append(card)
    combat.play_card(st, card)


# ---- the rule ------------------------------------------------------------------

@pytest.mark.parametrize("bank, spent, left", [
    (0, 0, 0),        # nothing held: nothing spent, no Spend
    (3, 3, 0),        # partial: all 3
    (10, 10, 0),      # exactly X
    (25, 10, 15),     # over X: X
])
def test_spend_up_to_spends_x_or_all_you_have(bank, spent, left):
    st = _furina(bank)
    assert FS.spend_up_to(st, 10) == spent
    assert st.player.ftd.fanfare == left
    assert st.player.ftd.spends_this_turn == (1 if spent else 0)


def test_it_is_a_spend_only_when_at_least_one_is_spent():
    st = _furina(0, stage=["chevreuse"])
    st.player.ftd.powers["thunderous"] = 1
    hp = st.enemies[0].hp
    assert FS.spend_up_to(st, 10) == 0
    assert st.enemies[0].hp == hp                       # no Thunderous
    assert not st.enemies[0].powers.get("vulnerable")   # no Chevreuse
    st.player.ftd.fanfare = 1
    assert FS.spend_up_to(st, 10) == 1
    assert st.enemies[0].hp == hp - T.THUNDEROUS_DAMAGE
    assert st.enemies[0].powers.get("vulnerable") == 1


def test_standing_room_only_answers_an_up_to_spend_and_a_spend_all():
    # furina-next (2026-10-16): Standing Room Only answers every Spend.
    st = _furina(20)
    st.player.powers[FS.STANDING_ROOM_ONLY] = 2
    assert FS.spend_up_to(st, 12) == 12
    assert st.player.ftd.fanfare == 8
    assert st.player.powers.get("strength") == 2
    st.player.powers["strength"] = 0
    # The same bank through a spend-all (Bis! is gone: nothing comes back).
    st.player.ftd.fanfare = 20
    assert FS.spend_all(st) == 20
    assert st.player.ftd.fanfare == 0
    assert st.player.powers.get("strength") == 2


def test_navias_first_two_points_are_free_on_an_up_to_spend():
    st = _furina(5, stage=["navia"])
    assert FS.spend_up_to(st, 10) == 7                  # 2 free + all 5
    assert st.player.ftd.fanfare == 0
    st.player.ftd.fanfare = 5
    assert FS.spend_up_to(st, 10) == 5                  # second: full price
    empty = _furina(0, stage=["navia"])
    assert FS.spend_up_to(empty, 10) == 2               # still a Spend
    assert empty.player.ftd.spends_this_turn == 1
    rich = _furina(20, stage=["navia"])
    assert FS.spend_up_to(rich, 10) == 10
    assert rich.player.ftd.fanfare == 12
    up = _furina(10, stage=["navia"])
    up.player.ftd.stage_up = {"navia"}
    assert FS.spend_up_to(up, 8) == 8                   # 3 free
    assert up.player.ftd.fanfare == 5


# ---- the four cards --------------------------------------------------------------

def test_tidal_flourish_deals_5_plus_1_per_point_up_to_10():
    st = _furina(7, enemies=[make_enemy(hp=300), make_enemy(hp=300)])
    _play(st, _card("proto_fs_tidal_flourish"))
    assert [e.hp for e in st.enemies] == [288, 288]     # 5 + 7, to ALL
    assert st.player.ftd.fanfare == 0
    st.player.ftd.fanfare = 30
    _play(st, _card("proto_fs_tidal_flourish+"))        # 8 + 10
    assert [e.hp for e in st.enemies] == [270, 270]
    assert st.player.ftd.fanfare == 20


def test_crashing_waves_hits_twice_plus_once_per_4_up_to_16():
    for bank, hits, left in ((0, 2, 0), (3, 2, 0), (8, 4, 0), (30, 6, 14)):
        st = _furina(bank)
        _play(st, _card("proto_fs_crashing_waves"))
        assert st.enemies[0].hp == 300 - 4 * hits, bank
        assert st.player.ftd.fanfare == left
    st = _furina(12)
    _play(st, _card("proto_fs_crashing_waves+"))        # 5 a hit, 5 hits
    assert st.enemies[0].hp == 300 - 25


def test_hold_the_stage_gains_6_plus_1_per_point_up_to_16():
    st = _furina(0)
    _play(st, _card("proto_fs_hold_the_stage"))
    assert st.player.block == 6
    st = _furina(5)
    _play(st, _card("proto_fs_hold_the_stage"))
    assert st.player.block == 11
    st = _furina(40)
    _play(st, _card("proto_fs_hold_the_stage+"))        # 8 + 16
    assert st.player.block == 24
    assert st.player.ftd.fanfare == 24


def test_the_three_cards_have_no_chooser():
    for cid in ("proto_fs_tidal_flourish",
                "proto_fs_crashing_waves", "proto_fs_hold_the_stage"):
        ops = [fx["op"] for fx in loader.get_card(cid).effects]
        assert "choose_one" not in ops, cid
        assert ops[0] == "stage_spend_up_to", cid


# ---- the guests' share-Spend (Navia half, Freminet a quarter) ----------------------

def test_navias_act_spends_a_third_and_deals_twice_it_as_geo():
    st = _furina(23, stage=["navia", "chevreuse"])
    st.player.ftd.powers["thunderous"] = 1
    T.spend(st, 3)                                      # uses her discount
    assert st.player.ftd.fanfare == 22
    hp = st.enemies[0].hp
    T.act(st, "navia")
    assert st.player.ftd.fanfare == 15              # a third of 22 is 7
    # 14 Geo plus Thunderous's 3, through the Vulnerable Chevreuse applied.
    assert st.enemies[0].hp < hp - 14
    assert st.enemies[0].powers.get("vulnerable") == 2  # a Spend each
    poor = _furina(1, stage=["navia"])
    hp = poor.enemies[0].hp
    T.act(poor, "navia")                                # a third of 1 is 0
    assert poor.enemies[0].hp == hp
    assert poor.player.ftd.spends_this_turn == 0


def test_freminets_act_gains_4_then_a_quarter_of_the_bank_as_block():
    st = _furina(9, stage=["freminet"])
    hp = st.enemies[0].hp
    T.act(st, "freminet")
    assert st.player.block == 4 + 2                     # a quarter of 9
    assert st.player.ftd.fanfare == 7
    assert st.enemies[0].hp == hp                       # no Cryo hit
    up = _furina(0, stage=["freminet"])
    up.player.ftd.stage_up = {"freminet"}
    T.act(up, "freminet")
    assert up.player.block == 7


def test_two_guests_split_the_bank_oldest_first():
    # Freminet first: a quarter of 40 is 10 (2 of it free, Navia's line on
    # the turn's first Spend), 32 left; Navia takes a third of that, 10,
    # for 20 Geo.
    st = _furina(40, stage=["freminet", "navia"])
    hp = st.enemies[0].hp
    T.act_all(st)
    assert st.player.block == 4 + 10
    assert st.enemies[0].hp == hp - 20
    assert st.player.ftd.fanfare == 22
    assert st.player.ftd.spends_this_turn == 2


def test_freminet_then_navia_on_40_with_no_discount():
    # A Spend first uses up Navia's discount (41, 3 spent, 2 free: 40).
    # Freminet takes a quarter of 40, 10 (30 left); Navia a third of 30, 10, for 20.
    st = _furina(41, stage=["freminet", "navia"])
    T.spend(st, 3)
    assert st.player.ftd.fanfare == 40
    hp = st.enemies[0].hp
    T.act_all(st)
    assert st.player.block == 4 + 10
    assert st.enemies[0].hp == hp - 20
    assert st.player.ftd.fanfare == 20


def test_showstopper_makes_each_take_their_share_again():
    st = _furina(40, stage=["navia", "freminet"])
    st.player.ftd.powers["showstopper"] = 1
    st.player.ftd.singer = 0
    hp = st.enemies[0].hp
    T.end_of_turn(st)
    # Round one: Navia 13 (2 free, 29 left) for 26, Freminet 7 (22 left).
    # Showstopper Spends 5 (17 left). Round two: Navia 5 for 10, Freminet 3.
    assert st.enemies[0].hp == hp - 36
    assert st.player.block == 4 + 7 + 4 + 3
    assert st.player.ftd.fanfare == 9


def test_the_constants_match_the_paper():
    assert (T.FREMINET_ACT_BLOCK, T.FREMINET_ACT_BLOCK_UPGRADED) == (4, 7)
    assert T.NAVIA_SPEND_DIVISOR == 3
    assert T.NAVIA_ACT_MULTIPLIER == 2
    assert T.FREMINET_SPEND_DIVISOR == 4
    assert not hasattr(T, "GUEST_SPEND_DIVISOR")
    assert T.SPEND_UP_TO_EVERY == 4
    assert not hasattr(T, "FREMINET_ACT")
