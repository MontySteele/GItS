"""FURINA, THE SPEND OUTLET PAPER, in the one-seat sim (ruled 2026-10-12).

`review/ruled/furina-spend-outlet-2026-10-12.md` sec.2, all defaults:
Spirited Aria spends up to 12, Crashing Waves and Hold the Stage up to 16
(`test_furina_spend_up_to.py` pins those); Packed House becomes "Gain 5 [8]
Block, plus 1 for every 4 Fanfare you have." and never spends; Rising
Applause+ gains Retain, the base card unchanged. The C# twin is
`klee-mod/KleeTests/Prototype/FurinaSpendOutletTests.cs`.
"""

from __future__ import annotations

import copy

from tier0.content import loader
from tier0.engine import combat, furina_stage as FS
from tier0.tests.conftest import make_enemy, make_state


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(fanfare=0):
    st = make_state(enemies=[make_enemy(hp=300)], hp=78)
    st.player.character_id = "furina"
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    st.player.energy = 9
    st.player.ftd.fanfare = fanfare
    return st


def _play(st, card):
    st.player.hand.append(card)
    combat.play_card(st, card)


def test_fanfare_fours_reads_the_bank_in_fours():
    st = _furina(15)
    assert FS.fanfare_fours(st.player) == 3
    assert FS.PACKED_HOUSE_FANFARE_PER == 4


def test_rising_applause_gains_retain_only_on_the_upgrade():
    base = loader.get_card("proto_fs_standing_ovation")
    up = loader.get_card("proto_fs_standing_ovation+")
    assert base.rarity == "basic" and not base.retain
    assert up.retain
    st = _furina(9)
    _play(st, _card("proto_fs_standing_ovation+"))
    assert st.player.block == 7
    assert st.enemies[0].hp == 300 - 9
    assert st.player.ftd.fanfare == 0
