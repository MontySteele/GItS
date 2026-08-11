"""POLICY 7 (R176): the pilot values a companion copy, and only when it has
one to copy.

EB-17p measured base Borrowed Brilliance at 40,396 draws / 0 plays and read it
as an unsatisfiable in-hand condition. It was not: `copy_companion_in_hand`
was worth nothing to `_tempo_value`, so the card's whole score was
`-cost_weight x cost` = -0.1, and the pilot's hard `best_score <= 0` rule
means a card that never scores positive is never played. These pin the fix
from both sides -- the value is REAL with a companion in hand and still ZERO
without, which is the half that keeps the card honest.
"""

import pytest

from tier0.content import loader
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.tests.conftest import make_enemy, make_state

REACTION = loader.pilot_weights("reaction")   # Klee's Borrowed Brilliance arm


def _companion() -> Card:
    return Card(id="probe_companion", name="Probe Companion", cost=1,
                type="skill", tags=["companion"], effects=[])


def _plain() -> Card:
    return Card(id="probe_plain", name="Probe Plain", cost=1, type="skill",
                effects=[{"op": "block", "amount": 1}])


def test_the_engines_own_predicate_is_what_the_pilot_asks():
    """`_op_copy_companion_in_hand` selects on `Card.is_companion` with no kit
    filter. If the two ever disagree the pilot is scoring a copy the engine
    will refuse to make (or vice versa), which is the EB-17p defect in the
    other direction."""
    assert _companion().is_companion
    assert not _plain().is_companion


def test_borrowed_brilliance_scores_positive_with_a_companion_in_hand():
    state = make_state([make_enemy()])
    bb = loader.get_card("borrowed_brilliance")
    state.player.hand = [bb, _companion()]

    # tempo 0.7 x PILOT_COMPANION_COPY_VALUE 1.5 - cost 0.1 x 1 = +0.95
    assert policy._score(state, bb, REACTION) == pytest.approx(0.95)


def test_borrowed_brilliance_stays_dead_with_no_companion_in_hand():
    """The copy has nothing to copy: the engine returns early, so the pilot
    must not pay for it. Still <= 0, so `pilot()` still declines to play it --
    the 0-play reading was CORRECT in this state and only this state."""
    state = make_state([make_enemy()])
    bb = loader.get_card("borrowed_brilliance")
    state.player.hand = [bb, _plain()]

    assert policy._score(state, bb, REACTION) <= 0


def test_the_pilot_now_actually_plays_it():
    """The end-to-end half: the hard `best_score <= 0` rule is what produced
    0 plays, so the pin that matters is the CHOICE, not the score."""
    state = make_state([make_enemy()])
    bb = loader.get_card("borrowed_brilliance")
    state.player.energy = 3
    state.player.hand = [bb, _companion()]

    assert policy.make_pilot(REACTION)(state) is bb


def test_replay_next_companion_reads_through_the_same_branch():
    """Study Buddy's replay grant is the same shape -- a second use of a
    companion you hold -- and expires with the turn, so it is equally dead
    with an empty companion slot. `times` is its amount key."""
    state = make_state([make_enemy()])
    replay = Card(id="probe_replay", name="Probe Replay", cost=1, type="skill",
                  effects=[{"op": "replay_next_companion", "times": 2}])

    state.player.hand = [replay, _companion()]
    assert policy._tempo_value(state, replay) == pytest.approx(
        2 * policy.PILOT_COMPANION_COPY_VALUE)

    state.player.hand = [replay, _plain()]
    assert policy._tempo_value(state, replay) == 0.0


def test_the_copy_is_worth_more_than_a_blind_draw():
    """The calibration argument for 1.5: a card you already chose to draft
    beats the unknown top of your deck, which the tempo term prices at 1."""
    state = make_state([make_enemy()])
    draw1 = Card(id="probe_draw", name="Probe Draw", cost=1, type="skill",
                 effects=[{"op": "draw", "amount": 1}])
    state.player.hand = [draw1, _companion()]

    assert (policy.PILOT_COMPANION_COPY_VALUE
            > policy._tempo_value(state, draw1))
