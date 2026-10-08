"""Jean's Lion's Fang, the `replaces:` sheet contract, and `personal_pool:`.

Kept from the deleted stand-in seam's test file (project review 2026-10-08,
pick 3): the seam had nothing to hand off since 2026-10-03, but Jean's rule,
the `replaces:` schema check and the one-member `personal_pool:` list are live.
"""

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import klee_overhaul, lions_fang
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


@pytest.fixture
def arms():
    loader.reset_arm_caches()
    yield
    loader.reset_arm_caches()


# --- the sheet contract ------------------------------------------------------

def test_a_shipped_row_may_not_replace_anything():
    with pytest.raises(ValueError, match="prototype surface only"):
        loader._validate_card_shape(Card(
            id="not_a_prototype", name="x", cost=1, type="skill",
            replaces="proto_mc_diona_icy_paws"))


def test_a_replaces_row_needs_an_arms_map():
    with pytest.raises(ValueError, match="substitution map"):
        loader._validate_card_shape(Card(
            id="proto_mc_x", name="x", cost=1, type="skill",
            personal_pool="klee", replaces="proto_mc_diona_icy_paws"))


def test_personal_pool_normalises_a_one_member_list():
    card = Card.from_dict({"id": "proto_mc_x", "name": "x", "cost": 1,
                           "type": "skill", "personal_pool": ["klee"]})
    assert card.personal_pool == "klee"          # every existing reader works
    with pytest.raises(ValueError, match="exactly ONE character id"):
        Card.from_dict({"id": "proto_mc_y", "name": "y", "cost": 1,
                        "type": "skill", "personal_pool": ["klee", "furina"]})


# --- Jean's rule (Lion's Fang, in Klee's own pool since 2026-10-03) ----------

def _klee_state():
    state = make_state(enemies=[make_enemy(hp=200)])
    state.player.character_id = "klee"
    state.turn = 1
    # The ledger rolls on a ROUND STAMP, so turn 1 has to be stamped or the
    # first boundary reads a jump of more than one round and honestly reports
    # zero -- `combat._player_turn` does this on every turn including the first.
    klee_overhaul.roll_to(state, state.turn)
    return state


def test_jean_pays_on_a_quiet_turn_and_draws(arms):
    state = _klee_state()
    state.player.powers[lions_fang.LIONS_FANG] = 8
    state.player.draw_pile = [loader.peek_card("strike")] * 3
    state.turn = 2
    klee_overhaul.roll_to(state, state.turn)
    assert state.ko_set_off_last_turn == 0
    hand_before, block_before = len(state.player.hand), state.player.block
    lions_fang.turn_start(state)
    assert state.player.block == block_before + 8
    assert len(state.player.hand) == hand_before + C.MC_LIONS_FANG_DRAW


def test_eb513_a_power_that_pays_at_turn_start_stays_raw(arms):
    """`EB-513`. Jean's Lion's Fang and Klee's own Grounded pay at the START
    of a turn off a Power the card only granted -- a POWER's Block, not a
    card's -- so Frail does not bite them, exactly as `GroundedPower` says."""
    state = _klee_state()
    state.player.powers["frail"] = 2
    state.player.powers[lions_fang.LIONS_FANG] = 8
    state.player.draw_pile = [loader.peek_card("strike")] * 3
    state.turn = 2
    klee_overhaul.roll_to(state, state.turn)
    before = state.player.block
    lions_fang.turn_start(state)
    assert state.player.block == before + 8

    state.player.powers[klee_overhaul.GROUNDED] = 6
    klee_overhaul.place(state, state.enemies[0], 5)
    before = state.player.block
    klee_overhaul.turn_start_late(state)
    assert state.player.block == before + 6
