"""R121 SHIELD: the anchor arm's instrumentation tags are invisible to
`score_offer`'s +3.0 core-advance bonus, and visible to everything else.

The 10.2 rider (R118) put `archetypes: [generic]` on `ref_ironclad`'s
package so the core-attainment instrument could read the arm at all -- it was
structurally 0.00% without them. The tags also reached the drafter's
core-advance bonus, and the anchor's drafting moved with them.
[USER] ruled SHIELD (2026-08-06, dispatch (e), `tier0/DECISIONS.md` R121).

These pins exist because the shield is invisible in the output of any single
call: `score_offer` returns one float, and a term that silently starts firing
again would move a measured anchor with nothing red.
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft

# The anchor's package, by role. `metallicize_like`/`inflame_like` are its
# two on-plan enablers, `heavy_blade_like` its one on-plan payoff.
ANCHOR_ENABLERS = ("inflame_like", "metallicize_like")
ANCHOR_PAYOFF = "heavy_blade_like"


def _anchor(card_id):
    return loader.get_card(card_id)


def test_the_rider_s_tags_are_still_on_the_package():
    """If the tags ever come off the sheet, the shield below is vacuous and
    these tests would pass by measuring nothing."""
    tagged = [c for c in loader._card_index().values()
              if c.character == draft.ANCHOR_TAG_SHIELD_CHARACTER
              and "generic" in c.archetypes]
    assert len(tagged) == 6
    assert {c.role for c in tagged} == {"enabler", "payoff", "glue"}


def test_core_advance_bonus_does_not_fire_from_the_anchor_s_tags():
    """The shield's whole content, stated as a number.

    The deck below strictly raises unshielded generic core progress when the
    anchor's on-plan payoff is added -- so without the shield the +3.0
    core-advance bonus (times `GENERIC_PLAN_BONUS_MULT` on an anchor) fires.
    With the shield it does not, and the difference between the two scorings
    is exactly that term and nothing else.
    """
    deck = [_anchor(ANCHOR_ENABLERS[0])]
    offer = _anchor(ANCHOR_PAYOFF)

    # The bonus WOULD have fired: unshielded progress strictly rises.
    assert (draft._core_progress(deck + [offer], "generic")
            > draft._core_progress(deck, "generic"))
    # ...and the shielded view flattens both sides to zero progress.
    assert draft._core_progress(
        draft._core_advance_view(deck + [offer]), "generic") == 0.0

    shielded = draft.score_offer(offer, deck, "generic")
    unshielded = _score_with_shield_disabled(offer, deck, "generic")
    assert unshielded - shielded == 3.0 * draft.GENERIC_PLAN_BONUS_MULT


def _score_with_shield_disabled(card, deck, archetype):
    """`score_offer` with `_core_advance_view` reduced to the identity --
    i.e. the pre-R121 scorer, reconstructed through the live code path so the
    delta above can only be the shielded term."""
    original = draft._core_advance_view
    draft._core_advance_view = lambda cards: cards
    try:
        return draft.score_offer(card, deck, archetype)
    finally:
        draft._core_advance_view = original


def test_instrumentation_still_reads_the_anchor_s_tags():
    """`core_complete` sets `RunResult.time_to_online`, which is what the
    RA-G1/RA-G2 core-attainment columns are. The rider's stated purpose --
    the instrument could not see the anchor at all -- survives the shield.
    """
    deck = [_anchor(ANCHOR_ENABLERS[0]), _anchor(ANCHOR_ENABLERS[1]),
            _anchor(ANCHOR_ENABLERS[0]), _anchor(ANCHOR_PAYOFF)]
    on_plan, payoffs = draft._generic_core_counts(deck, "generic")
    assert on_plan == C.DRAFT_CORE_SIZE and payoffs == 1
    assert draft.core_complete(deck, "generic")
    assert draft._core_progress(deck, "generic") == 1.0
    # Reward-relevance telemetry is outside the ruling's scope too.
    assert draft.offer_advances_plan([_anchor(ANCHOR_PAYOFF)],
                                     [_anchor(ANCHOR_ENABLERS[0])], "generic")


def test_the_shield_is_scoped_to_the_anchor_s_own_cards():
    """Scoping is by owning character, not by the tag value: 83 of the 89
    `generic`-tagged cards in the pool belong to Klee, Furina and Kokomi, and
    the ruling shields the ANCHOR ARM's tags. A deck with no anchor card in
    it is handed back unchanged -- object identity, so the non-anchor arms
    are not merely equal but bit-identical through this path.
    """
    foreign = [c for c in loader._card_index().values()
               if "generic" in c.archetypes
               and c.character != draft.ANCHOR_TAG_SHIELD_CHARACTER]
    assert foreign, "the pool's non-anchor generic tags are the control group"
    deck = foreign[:3]
    assert draft._core_advance_view(deck) is deck
    assert (draft._core_progress(draft._core_advance_view(deck), "generic")
            == draft._core_progress(deck, "generic"))


def test_the_shield_leaves_the_card_prototypes_alone():
    """`loader.peek_card` hands out SHARED prototypes (Track O slice 11's
    prototype-stability probe). A shield that stripped tags in place would
    silently disarm the instrument for the rest of the process.
    """
    card = _anchor(ANCHOR_PAYOFF)
    before = list(card.archetypes)
    draft._core_advance_view([card])
    draft.score_offer(card, [_anchor(ANCHOR_ENABLERS[0])], "generic")
    assert loader.get_card(ANCHOR_PAYOFF).archetypes == before
    assert loader.peek_card(ANCHOR_PAYOFF).archetypes == before
