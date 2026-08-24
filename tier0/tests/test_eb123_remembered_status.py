"""EB-123: a remembered STATUS must not kill the run.

Nightmare (`si_nightmare`) remembers a card in hand and copies it at the
next hand draw. `refpowers.before_hand_draw` rebuilt the remembered card
through `loader.get_card()`, but Status cards are SYNTHESIZED by
`engine.statuses` under `status_<x>` ids and are deliberately in no pool
and no loader index -- so remembering a Dazed raised
`KeyError: 'status_dazed'` and took the whole run with it. One run in 600
did exactly that (`real_silent/generic`, seed 11, run 454), which is what
blocked half of control C1 in the 2026-08-24 payoff-reach read.

WHICH HALF WAS WRONG. Not the chooser: the authority's Nightmare targets a
card in HAND, and a Status is in hand, so a hand full of clogs remembering
one is the game's own behaviour and is left alone. What was wrong is that
the payout could not rebuild what the chooser was allowed to pick.

THE FIX IS NUMBER-NEUTRAL BY CONSTRUCTION, not by argument. `token_card`
asks the loader FIRST and opens the status door only inside the handler
for the KeyError the loader raised -- so every id the loader already
resolved is resolved by the same call, with the same result, and the only
behaviour that can differ is behaviour that was previously a crash. The
two namespaces are pinned disjoint below so that stays true.
"""
import pytest

from tier0.content import loader
from tier0.engine import combat, effects, refpowers, statuses
from tier0.engine.state import Card
from tier0.tests.conftest import make_state


def _nightmare_driver(amount=3):
    return Card(id="si_nightmare", name="Nightmare", cost=3, type="skill",
                effects=[{"op": "remember_card", "power": "nightmare"},
                         {"op": "apply_power", "power": "nightmare",
                          "amount": amount, "target": "self"}])


def _remember_and_pay(state, amount=3):
    driver = _nightmare_driver(amount)
    state.player.hand.append(driver)
    combat.play_card(state, driver)
    state.player.hand.clear()
    refpowers.before_hand_draw(state)


# --- the crash itself -------------------------------------------------------

def test_remembering_a_status_pays_out_instead_of_crashing():
    """The minimal repro of the seed-454 failure: a hand whose only
    rememberable card is an enemy-injected Dazed."""
    state = make_state()
    state.player.hand.append(statuses.make_status("dazed"))
    _remember_and_pay(state)
    assert [c.id for c in state.player.hand] == ["status_dazed"] * 3


def test_every_synthesized_status_can_be_remembered():
    """Dazed is the one seed 454 found; the seam is the id shape, not the
    status, so all six go through it."""
    for sid in statuses.status_ids():
        state = make_state()
        state.player.hand.append(statuses.make_status(sid))
        _remember_and_pay(state, amount=1)
        assert [c.id for c in state.player.hand] == [f"status_{sid}"]


def test_the_copies_are_fresh_instances_not_one_shared_card():
    """`make_status`'s own contract -- pile membership is object-based, so
    three copies that are one object would be one card in three piles."""
    state = make_state()
    state.player.hand.append(statuses.make_status("wound"))
    _remember_and_pay(state)
    assert len({id(c) for c in state.player.hand}) == 3


# --- the same seam, the other limb -----------------------------------------

def test_infinite_blades_resolves_a_status_token_too():
    """`before_hand_draw`'s InfiniteBlades limb has the identical
    `loader.get_card(token)` shape three lines up. Its payload comes off a
    card row so a Status is not known to be reachable there, but it is the
    same seam and it is fixed with it."""
    state = make_state()
    state.player.powers["infinite_blades"] = 2
    state.player.power_payloads["infinite_blades"] = "status_wound"
    refpowers.before_hand_draw(state)
    assert [c.id for c in state.player.hand] == ["status_wound"] * 2


# --- the resolver's own contract -------------------------------------------

def test_token_card_prefers_the_loader():
    """Ordering is the number-neutrality proof: a pool id must still come
    from the loader, by the same call it always did."""
    assert effects.token_card("strike").id == loader.get_card("strike").id
    assert effects.token_card("strike+").id == loader.get_card("strike+").id


def test_token_card_still_fails_loudly_on_an_unknown_id():
    """The status door is not a swallow-everything handler: a typo'd
    payload is a defect and must keep saying so."""
    with pytest.raises(KeyError):
        effects.token_card("no_such_card_anywhere")
    with pytest.raises(KeyError):
        effects.token_card("status_not_a_status")


def test_the_two_id_namespaces_are_disjoint():
    """The whole fix rests on `status_<x>` never being a loader id -- if
    one ever were, the loader-first ordering would silently shadow it."""
    assert not [cid for cid in loader._card_index()
                if cid.startswith(statuses.STATUS_ID_PREFIX)]
    for sid in statuses.status_ids():
        assert statuses.make_status(sid).id.startswith(
            statuses.STATUS_ID_PREFIX)


def test_status_from_card_id_is_the_inverse_of_make_status():
    for sid in statuses.status_ids():
        made = statuses.make_status(sid)
        assert statuses.status_from_card_id(made.id).id == made.id
    assert statuses.status_from_card_id("strike") is None
    assert statuses.status_from_card_id("status_not_a_status") is None
