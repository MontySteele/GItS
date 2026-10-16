"""STANDING OVATION, COMMON AGAIN, SPEND HALF (2026-10-11).

Furina round 3 record, pick 1. [USER]: "On Furina - let's try standing
ovation at Common but only for half your Fanfare and see how that goes."
"Spend half your Fanfare. Deal that much damage to ALL enemies." Half the
bank, rounded down; it is not a spend-all, so Bis! keeps nothing back.
C# twin: klee-mod/KleeTests/Prototype/FurinaStandingOvationHalfTests.cs.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from tier0.content import loader
from tier0.engine import combat, furina_stage as FS, furina_tide as T
from tier0.tests.conftest import make_enemy, make_state

CID = "proto_fs_standing_ovation_all"
REPO = Path(__file__).resolve().parents[2]


def _furina(fanfare):
    st = make_state(enemies=[make_enemy(hp=300), make_enemy(hp=300)], hp=78)
    st.player.character_id = "furina"
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    st.player.energy = 9
    st.player.ftd.fanfare = fanfare
    st.player.draw_pile = [copy.deepcopy(loader.get_card(
        "proto_fs_velvet_curtain")) for _ in range(5)]
    return st


def _play(st, cid=CID):
    card = copy.deepcopy(loader.get_card(cid))
    st.player.hand.append(card)
    combat.play_card(st, card)


def test_the_sim_slice_twin_spends_half():
    st = _furina(21)
    st.player.ftd.powers["extended_run"] = 8     # no printed number
    assert T.spend_half(st) == 10
    assert st.player.ftd.fanfare == 11
