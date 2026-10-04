"""THE COMPANION STAND-IN SEAM -- the sheet contract, the hand-off, the rules.

A stand-in is a whole Klee-only card handed to Klee IN PLACE of one named
Universal (Klee brief pick 6; the approved Mondstadt workshop sec.1; R236
sec.3). Three claims are worth pinning rather than intending, and this file is
those three:

  1. IT IS IN NO POOL. Not the character-blind Universal pool, not the Personal
     reward share, not a shop slot, not the Featured Banner.
  2. THE ODDS DO NOT MOVE. Run the same seed for Klee and for another character
     and the two offer sequences are the SAME cards, one of them with the four
     Universals swapped -- which is only possible if the candidate lists, the
     rarity rolls and the weighted draws were untouched.
  3. FLAG OFF IS BYTE-IDENTICAL. `hand_off` is the identity, and no surface can
     reach a stand-in at all.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These are
shape assertions about an engine, not numbers about a game.
"""

import pathlib
import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import companion_standins as standins
from tier0.engine import combat, effects, klee_overhaul
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards, shop

# THE SHIPPED WORLD, NAMED (legacy cleanup stage 3, 2026-10-01): the sim
# defaults to the current kits, and these pins read the shipped ones.

REPO = pathlib.Path(__file__).resolve().parents[2]


def _caches_clear():
    """Every memo whose answer depends on the flag. Same list
    `test_companion_overhaul` clears, plus the stand-in map, which is derived
    from the surface and so is a view of the content tree like the rest."""
    loader.reset_arm_caches()
    standins._replacements.cache_clear()
    rewards._companion_roster.cache_clear()
    rewards.companion_pool.cache_clear()
    rewards.five_star_roster.cache_clear()
    rewards.designed_nations.cache_clear()


@pytest.fixture
def overhaul(monkeypatch):
    _caches_clear()
    yield
    _caches_clear()


@pytest.fixture
def arms(monkeypatch, overhaul):
    """Both arms: the caretakers read the Klee overhaul's explosion ledger, so
    their rules cannot be exercised without the arm that keeps it."""
    yield


# --- 1. the sheet contract ---------------------------------------------------

def test_the_constant_and_the_sheet_agree(overhaul):
    """`C.COMPANION_STANDIN_IDS` exists for one consumer (the upgrade index's
    reachable set) and is DERIVED everywhere else, so it must equal the
    derivation."""
    assert set(C.COMPANION_STANDIN_IDS) == set(standins.standin_ids())


def test_the_seam_is_empty_since_the_klee_only_companions(overhaul):
    """The Klee-only companions (2026-10-03,
    review/active/mondstadt-companions-2026-10-03.md sec.4): four stand-ins
    cut, three to the shared pool, two to Klee's own pool. Nothing is handed
    off, and every id comes back unchanged."""
    assert C.COMPANION_STANDIN_IDS == ()
    assert standins.standin_ids() == ()
    for cid in C.MONDSTADT_OVERHAUL_POOL_IDS:
        assert standins.hand_off(cid, "klee") == cid


def test_a_shipped_row_may_not_stand_in_for_anything():
    from tier0.engine.state import Card

    with pytest.raises(ValueError, match="prototype surface only"):
        loader._validate_card_shape(Card(
            id="not_a_prototype", name="x", cost=1, type="skill",
            personal_pool="klee", replaces="proto_mc_diona_icy_paws"))


def test_a_standin_needs_a_personal_pool():
    from tier0.engine.state import Card

    with pytest.raises(ValueError, match="needs a `personal_pool:`"):
        loader._validate_card_shape(Card(
            id="proto_mc_x", name="x", cost=1, type="skill",
            replaces="proto_mc_diona_icy_paws"))


def test_personal_pool_normalises_a_one_member_list():
    from tier0.engine.state import Card

    card = Card.from_dict({"id": "proto_mc_x", "name": "x", "cost": 1,
                           "type": "skill", "personal_pool": ["klee"]})
    assert card.personal_pool == "klee"          # every existing reader works
    with pytest.raises(ValueError, match="exactly ONE character id"):
        Card.from_dict({"id": "proto_mc_y", "name": "y", "cost": 1,
                        "type": "skill", "personal_pool": ["klee", "furina"]})


# --- 2. no pool holds a stand-in ---------------------------------------------

def test_no_offer_pool_holds_a_standin(overhaul):
    standin_ids = set(C.COMPANION_STANDIN_IDS)
    assert not {c.id for c in rewards._companion_roster()} & standin_ids
    for tier in rewards.companion_pool().values():
        assert not {c.id for c in tier} & standin_ids
    for nation in rewards.designed_nations():
        assert not {c.id for c in rewards.five_star_roster(nation)} & standin_ids


# --- 3. Jean's rule (Lion's Fang, in Klee's own pool since 2026-10-03) -------

def _klee_state():
    state = make_state(enemies=[make_enemy(hp=200)])
    # `klee_overhaul.live` is the flag AND the seat: the arm is Klee's rules,
    # and a stand-in is handed to Klee, so the two gates agree by construction.
    state.player.character_id = "klee"
    state.turn = 1
    # The ledger rolls on a ROUND STAMP, so turn 1 has to be stamped or the
    # first boundary reads a jump of more than one round and honestly reports
    # zero -- `combat._player_turn` does this on every turn including the first.
    klee_overhaul.roll_to(state, state.turn)
    return state


def test_jean_pays_on_a_quiet_turn_and_draws(arms):
    state = _klee_state()
    state.player.powers[standins.LIONS_FANG] = 8
    state.player.draw_pile = [loader.peek_card("strike")] * 3
    state.turn = 2
    klee_overhaul.roll_to(state, state.turn)
    assert state.ko_set_off_last_turn == 0
    hand_before, block_before = len(state.player.hand), state.player.block
    standins.turn_start(state)
    assert state.player.block == block_before + 8
    assert len(state.player.hand) == hand_before + C.MC_LIONS_FANG_DRAW


# ---------------------------------------------------------------------------
# `EB-513` -- a companion's printed Block takes the card's Frail fold
# ---------------------------------------------------------------------------

def test_eb513_a_power_that_pays_at_turn_start_stays_raw(arms):
    """WHAT DID NOT MOVE, and it is the distinction the row turns on. Jean's
    Lion's Fang and Klee's own Grounded pay at the START of a turn off a Power
    the card only granted -- a POWER's Block, not a card's -- so Frail does not
    bite them, exactly as `GroundedPower` says in as many words."""
    state = _klee_state()
    state.player.powers["frail"] = 2
    state.player.powers[standins.LIONS_FANG] = 8
    state.player.draw_pile = [loader.peek_card("strike")] * 3
    state.turn = 2
    klee_overhaul.roll_to(state, state.turn)
    before = state.player.block
    standins.turn_start(state)
    assert state.player.block == before + 8

    state.player.powers[klee_overhaul.GROUNDED] = 6
    klee_overhaul.place(state, state.enemies[0], 5)
    before = state.player.block
    klee_overhaul.turn_start_late(state)
    assert state.player.block == before + 6
