"""A CHOSEN discard picks its whole batch before any of it resolves.

The defect this file pins: `_op_discard`'s chosen path used to re-poll
`state.player.hand` on every pick while resolving each victim's authored Sly
rider INLINE. Kokomi's riders draw, recall and create, so a card that did not
exist when the player was asked could become the next victim -- the engine was
answering a question the selection screen never asked.

Canon's discard screen picks all N first and then discards them. The fix
captures the batch up front off one shrinking candidate list; rider TIMING is
untouched (each victim still discards and fires in order), only MEMBERSHIP is
fixed. The random path deliberately keeps its per-pick re-poll: it is the
default every existing discard was priced against, and nothing was read to say
canon batches it too.

Twin: `tools/gen_klee_cards.py`'s `discard` emitter, whose chosen branch opens
one `CardSelectCmd.FromHandForDiscard` selection for the same reason
(`tier0/tests/test_roster_codegen.py`).
"""

from tier0.engine import effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_state


def card(cid, type="skill", cost=0, fx=None, sly=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [],
                sly=sly if sly is not None else [], **kw)


def _discard(state, amount, select="chosen"):
    effects.resolve_card(state, card("discarder", fx=[
        {"op": "discard", "amount": amount, "select": select}]))


def _ids(pile):
    return [c.id for c in pile]


# `_worst_card` ranks (non-attack, then cost), so a costlier Skill is always
# picked before a cheaper one and any Skill before any Attack. Every fixture
# below is built so the pick order is forced, never rng-dependent.

def test_a_rider_that_draws_cannot_add_to_the_batch_it_is_part_of():
    """THE DEFECT. `drifting_lantern`'s `sly: draw 1` thrown to a discard-2
    used to hand the engine a fresh card to pick from -- the drawn Skill
    outranked the second card the player had actually been offered."""
    state = make_state()
    drawn = card("drawn", cost=5)               # the worst card in the game
    state.player.draw_pile = [drawn]
    a = card("a", cost=3, sly=[{"op": "draw", "amount": 1}])
    b = card("b", cost=2)
    state.player.hand = [a, b]

    _discard(state, 2)

    # The batch was [a, b] -- decided before a's rider ran. Pre-fix this read
    # ["a", "drawn"], with `b` still sitting in a hand the player had already
    # been asked about.
    assert _ids(state.player.discard_pile) == ["a", "b"]
    assert _ids(state.player.hand) == ["drawn"]
    assert state.discards_this_card == 2


def test_a_rider_that_removes_a_pending_victim_is_skipped_not_crashed():
    """`open_the_stores` is the live shape: discard 2 chosen, and the first
    victim's Sly exhaust can take the card the batch had already picked
    second. Follow the `sly_batch` precedent -- an effect already moved it,
    so do not resurrect it."""
    state = make_state()
    a = card("a", cost=3,
             sly=[{"op": "exhaust_from", "amount": 1, "select": "chosen"}])
    b = card("b", cost=2)
    c = card("c", type="attack", cost=0)
    state.player.hand = [a, b, c]

    _discard(state, 2)

    # a discards and its rider exhausts b (the worst card left in hand); b is
    # then skipped rather than pulled back out of the exhaust pile.
    assert _ids(state.player.discard_pile) == ["a"]
    assert _ids(state.player.exhaust_pile) == ["b"]
    assert _ids(state.player.hand) == ["c"]
    assert state.discards_this_card == 1


def test_amount_one_is_unaffected_by_construction():
    """Silent's Survivor-class chosen discards are all amount 1, and one pick
    has no second pick to poison. Pinned so the claim "no existing card's
    behaviour moves" is a test rather than a paragraph."""
    state = make_state()
    drawn = card("drawn", cost=5)
    state.player.draw_pile = [drawn]
    a = card("a", cost=3, sly=[{"op": "draw", "amount": 1}])
    b = card("b", cost=2)
    state.player.hand = [a, b]

    _discard(state, 1)

    assert _ids(state.player.discard_pile) == ["a"]
    assert sorted(_ids(state.player.hand)) == ["b", "drawn"]


def test_discard_your_hand_batches_the_hand_it_was_played_against():
    """`amount: hand_size` (si_calculated_gamble) already resolved its COUNT
    once; the batch now fixes the MEMBERSHIP the same way, so a mid-resolution
    draw is not swept up by the card that caused it."""
    state = make_state()
    state.player.draw_pile = [card("drawn", cost=5)]
    a = card("a", cost=3, sly=[{"op": "draw", "amount": 1}])
    b = card("b", cost=2)
    state.player.hand = [a, b]

    _discard(state, "hand_size")

    assert _ids(state.player.discard_pile) == ["a", "b"]
    assert _ids(state.player.hand) == ["drawn"]


def test_the_batch_keeps_the_kit_exemption():
    """The v1.9 invariant (the Burst never enters a pile) is a property of
    the CANDIDATE list, so moving selection up front must carry it."""
    state = make_state()
    burst = card("burst", cost=9, kit_card=True)
    a = card("a", cost=3)
    state.player.hand = [burst, a]

    _discard(state, 2)

    assert _ids(state.player.discard_pile) == ["a"]
    assert _ids(state.player.hand) == ["burst"]


def test_the_random_path_still_re_polls_the_hand():
    """The other half of the pin, and the reason the fix is scoped. A random
    discard is not a selection screen; it picks one card at a time out of the
    hand as it then stands, and a rider that draws feeds the next pick. Both
    picks below have a one-card pool, so this is exact, not rng-shaped."""
    state = make_state()
    state.player.draw_pile = [card("drawn", cost=5)]
    a = card("a", cost=3, sly=[{"op": "draw", "amount": 1}])
    state.player.hand = [a]

    _discard(state, 2, select="random")

    assert _ids(state.player.discard_pile) == ["a", "drawn"]
    assert state.player.hand == []
