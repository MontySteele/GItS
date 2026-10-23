"""furina-next paper 2 (review/active/furina-next-2-2026-10-16.md sec.2,
ruled 2026-10-16): Bravura spends up to 18, Bring the House Down up to 10
for each guest on stage, and Extended Run takes Bis!'s slot: "Attacks and
Skills that Spend up to a number can Spend 8 [12] more." It adds once, flat,
to a played card's whole cap; copies add; Full House, a guest's share-Spend,
Spend half and fixed Spends do not read it. C# twin:
`klee-mod/KleeTests/Prototype/FurinaExtendedRunTests.cs`.
"""
from __future__ import annotations

import copy

from tier0.content import loader
from tier0.engine import combat, furina_stage as FS, furina_tide as T
from tier0.tests.conftest import make_enemy, make_state


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(fanfare=0, stage=()):
    st = make_state(enemies=[make_enemy(hp=999)], hp=78)
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


def test_extended_run_is_8_and_12_upgraded_and_copies_add():
    st = _furina()
    _play(st, _card("proto_fs_bis"))
    assert st.player.powers.get(FS.EXTENDED_RUN) == 8
    _play(st, _card("proto_fs_bis+"))
    assert st.player.powers.get(FS.EXTENDED_RUN) == 20
    assert T.card_up_to_cap(st, 18) == 38


def test_bring_the_house_down_is_a_fixed_spend_extended_run_leaves_alone():
    # The upgrade census (2026-10-23): "Spend 5 for each guest on stage" is a
    # Spend N, not a "Spend up to", so Extended Run does not raise it.
    st = _furina(200, stage=["charlotte", "wriothesley", "clorinde"])
    st.player.powers[FS.EXTENDED_RUN] = 8
    _play(st, _card("proto_fs_bring_the_house_down"))
    assert st.player.ftd.fanfare == 200 - 15
    assert st.player.ftd.ledger["spends"] == 1


def test_bravura_two_upgraded_copies_spend_42_for_14_hits():
    st = _furina(200)
    st.player.powers[FS.EXTENDED_RUN] = 24
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_bravura"))
    assert st.player.ftd.fanfare == 200 - 42
    assert hp - st.enemies[0].hp == 14 * 7


def test_bravura_two_copies_spend_34_for_11_hits():
    st = _furina(200)
    st.player.powers[FS.EXTENDED_RUN] = 16
    hp = st.enemies[0].hp
    _play(st, _card("proto_fs_bravura"))
    assert st.player.ftd.fanfare == 200 - 34
    assert hp - st.enemies[0].hp == 11 * 7


def test_bravura_alone_spends_18():
    st = _furina(200)
    _play(st, _card("proto_fs_bravura"))
    assert st.player.ftd.fanfare == 200 - 18


def test_full_house_and_fixed_spends_and_shares_are_unchanged():
    st = _furina(20)
    st.player.powers[FS.EXTENDED_RUN] = 12
    st.player.powers[FS.FULL_HOUSE] = 4
    assert T.full_house(st) == 4                     # Full House: 4
    assert st.player.ftd.fanfare == 16
    assert T.spend_share(st, 4) == 4                 # a quarter of 16
    assert st.player.ftd.fanfare == 12
    _play(st, _card("proto_fs_quick_cue"))           # Quick Flourish: 4
    assert st.player.ftd.fanfare == 8
