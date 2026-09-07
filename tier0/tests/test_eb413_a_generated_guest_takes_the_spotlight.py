"""`EB-413`: a Companion card An Invitation generates in combat DOES take the
Spotlight. The row's find does not reproduce, and this file is why.

WHAT THE SEAT SAW (Furina r4 run 2 (c) 1, again at r7): "Charlotte -- Framing
dealt 6 under Guest Cast where Freminet printed 9 in the same fight; Shinobu
gave 6 Block under an active Spotlight."

THE TWO NUMBERS SUBTRACTED WERE DIFFERENT CARDS. Guest Cast multiplies a
card's own printed base by `SPOTLIGHT_BASE_MULT` and truncates. Charlotte --
Framing prints 4 and Freminet -- Pers, Deploy! prints 6, so under one and the
same Spotlight they read 6 and 9 -- which is exactly the pair the seat filed as
a discrepancy. Shinobu -- Grass Ring prints 4, so its 6 Block is the lit
number too. Round 17 read a Chevreuse the same way and reached the same answer
(`Round17Tests`): the seat's arithmetic, not the engine.

AND THERE IS NO CREATION-PATH GAP TO FIND. `is_outward_spotlighted` asks
`card.is_companion` and nothing about provenance; `_generate` deep-copies the
canonical row, so the token is the same Companion the draft would have handed
over. `generated_by_guest_star` is combat-local bookkeeping (it keeps the token
out of the permanent deck and out of the upgrade lint) and no Spotlight reader
consults it. The mod's twin is `GeneratedGuestSpotlightTests`.
"""

from __future__ import annotations

import copy
import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

ENEMY_HP = 400


def _board():
    p = loader.build_player("furina")
    p.spotlight = C.SPOTLIGHT_GUEST_CAST
    return CombatState(player=p, enemies=[make_enemy(hp=ENEMY_HP)],
                       rng=random.Random(1))


def _dealt(state, card):
    before = state.enemies[0].hp
    effects.resolve_card(state, card)
    return before - state.enemies[0].hp


def _generated(card_id):
    made = copy.deepcopy(loader.get_card(card_id))
    made.generated_by_guest_star = True
    return made


def test_a_generated_companion_deals_the_spotlighted_number():
    state = _board()
    printed = loader.get_card("charlotte_freezing_point").effects[0]["amount"]

    dealt = _dealt(state, _generated("charlotte_freezing_point"))

    assert dealt == int(printed * C.SPOTLIGHT_BASE_MULT)
    assert dealt > printed


def test_the_generated_copy_and_the_drafted_copy_deal_the_same():
    """The row's claim in one assertion: provenance changes no number."""
    state = _board()

    generated = _dealt(state, _generated("charlotte_freezing_point"))
    drafted = _dealt(state, loader.get_card("charlotte_freezing_point"))

    assert generated == drafted


def test_the_seats_two_numbers_are_two_printed_bases_under_one_spotlight():
    state = _board()

    charlotte = _dealt(state, _generated("charlotte_freezing_point"))
    freminet = _dealt(state, loader.get_card("freminet_pers_deploy"))

    assert (charlotte, freminet) == (6, 9)


def test_shinobus_six_block_is_the_lit_number():
    state = _board()
    state.player.block = 0

    effects.resolve_card(state, _generated("shinobu_grass_ring_bond"))

    printed = loader.get_card("shinobu_grass_ring_bond").effects[0]["amount"]
    assert state.player.block == int(printed * C.SPOTLIGHT_BASE_MULT) == 6


def test_an_invitations_own_token_is_lit_the_moment_it_arrives():
    """Not a hand-built copy: the card's own generation path."""
    state = _board()

    effects.resolve_card(state, loader.get_card("an_invitation"))
    guest = state.player.hand[0]

    assert guest.generated_by_guest_star
    assert effects.spotlight_mult(state, guest) == C.SPOTLIGHT_BASE_MULT


@pytest.mark.parametrize("card_id", ["charlotte_freezing_point",
                                     "shinobu_grass_ring_bond",
                                     "freminet_pers_deploy"])
def test_the_gate_never_reads_the_token_flag(card_id):
    state = _board()
    drafted = loader.get_card(card_id)

    assert (effects.is_outward_spotlighted(state, _generated(card_id))
            is effects.is_outward_spotlighted(state, drafted) is True)
