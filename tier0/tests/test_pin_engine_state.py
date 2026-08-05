"""Pin tests for CombatState pile primitives (draw cap, reshuffle order)."""

from tier0 import constants as C
from tier0.engine.state import Card
from tier0.tests.conftest import make_state


def card(cid="t", **kw):
    base = dict(id=cid, name=cid, cost=1, type="attack")
    base.update(kw)
    return Card(**base)


def test_draw_into_full_hand_draws_nothing():
    """A draw requested while the hand already holds MAX_HAND_SIZE cards adds
    no card at all: the hand stays at the cap, the draw pile is untouched and
    the combat draw counter does not move."""
    st = make_state()
    p = st.player
    p.hand = [card(f"h{i}") for i in range(C.MAX_HAND_SIZE)]
    p.draw_pile = [card("d0"), card("d1")]
    st.cards_drawn_this_combat = 0

    st.draw(1)

    assert len(p.hand) == C.MAX_HAND_SIZE
    assert [c.id for c in p.draw_pile] == ["d0", "d1"]
    assert st.cards_drawn_this_combat == 0


def test_draw_stops_at_max_hand_size_mid_draw():
    """A multi-card draw fills the hand only up to MAX_HAND_SIZE and then
    stops: the cards it did not have room for stay on top of the draw pile."""
    st = make_state()
    p = st.player
    p.hand = [card(f"h{i}") for i in range(C.MAX_HAND_SIZE - 1)]
    p.draw_pile = [card("d0"), card("d1"), card("d2")]
    st.cards_drawn_this_combat = 0

    st.draw(3)

    assert len(p.hand) == C.MAX_HAND_SIZE
    assert p.hand[-1].id == "d0"
    assert [c.id for c in p.draw_pile] == ["d1", "d2"]
    assert st.cards_drawn_this_combat == 1


def test_reshuffled_discard_goes_on_top_of_the_draw_pile():
    """Shuffling the discard pile back in splices it ABOVE whatever is left in
    the draw pile -- the reshuffled cards are drawn before the survivors --
    and empties the discard pile."""
    st = make_state()
    p = st.player
    p.draw_pile = [card("leftover")]
    p.discard_pile = [card("discarded")]

    st.shuffle_discard_into_draw()

    assert [c.id for c in p.draw_pile] == ["discarded", "leftover"]
    assert p.discard_pile == []
