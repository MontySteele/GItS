"""Pins for the two edges of DRAFTER_VERSION 14's generic core limb that a
mutation round (track K, 2026-08-05) found bare.

`test_m5.test_generic_core_requires_a_drafted_payoff` pins that BOTH limbs
bite. What it does not pin is where each limb's edge falls: the assembly limb
is satisfied AT `DRAFT_CORE_SIZE` and not one card later, and "on-plan" means
the card is on the ARCHETYPE'S plan, not merely a payoff for somebody's. Both
mutations survive the whole suite while moving when `core_complete` flips --
and `_core_progress` feeds `score_offer`'s +3.0 core-advance bonus, so a moved
edge is a moved drafter.
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft


def _cards(*ids):
    return [loader.get_card(i) for i in ids]


def test_exactly_draft_core_size_on_plan_cards_is_a_finished_assembly():
    """`core_complete`'s docstring states the generic bar as "DRAFT_CORE_SIZE
    on-plan enabler/payoff cards, AT LEAST ONE of which is a payoff" -- so
    DRAFT_CORE_SIZE cards satisfy it, and `_core_progress`'s
    `min(1.0, on_plan / C.DRAFT_CORE_SIZE)` reaches 1.0 at the same count.
    A strict `>` moves the bar to DRAFT_CORE_SIZE + 1 while leaving progress
    at 1.0, which is precisely the drift `_generic_core_counts` was extracted
    to make impossible: the predicate and the progress meter would disagree at
    the boundary again.
    """
    deck = (_cards(*loader.starting_deck("furina"))
            + _cards("salon_debut", "casting_call", "grand_salon"))

    on_plan, payoffs = draft._generic_core_counts(deck, "salon")
    assert on_plan == C.DRAFT_CORE_SIZE and payoffs == 1
    assert draft.core_complete(deck, "salon")
    assert draft._core_progress(deck, "salon") == 1.0


def test_a_payoff_for_another_plan_is_not_this_plan_s_payoff():
    """"On-plan" is the whole of what `archetype in c.archetypes` means, and
    it governs BOTH limbs -- `_generic_core_counts` filters once and counts
    twice. Loosening it so any payoff card counts would let Klee's
    `remote_detonator`, a demolition payoff with no salon tag on it,
    complete a salon core: four cards on the plan and the card that cashes
    them belonging to a different deck entirely.
    """
    salon_deck = (_cards(*loader.starting_deck("furina"))
                  + _cards("salon_debut", "casting_call", "gentilhomme_usher"))
    off_plan_payoff = loader.get_card("remote_detonator")
    assert off_plan_payoff.role == "payoff"
    assert "salon" not in off_plan_payoff.archetypes

    with_it = salon_deck + [off_plan_payoff]
    assert draft._generic_core_counts(with_it, "salon") == \
        draft._generic_core_counts(salon_deck, "salon")
    assert draft._generic_core_counts(with_it, "salon")[0] >= C.DRAFT_CORE_SIZE
    assert not draft.core_complete(with_it, "salon")
    assert draft._core_progress(with_it, "salon") == 0.5
