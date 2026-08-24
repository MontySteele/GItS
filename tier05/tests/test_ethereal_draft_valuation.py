"""EB-118: the drafter prices Ethereal as the downside it is.

A card that dies unplayed loses its value, so a drafter blind to the keyword
would score "strong, but it may vanish before you can afford it" as if the
second clause were not printed -- the mirror of every other unpriced-term
failure this scorer has been fixed for.

EB-118 Phase 2B: the term is NO LONGER INERT. `big_badda_boom` prints
`ethereal:` in docs/klee-cards.yaml and is a Common, so every reward, shop and
Neow channel can offer it. The inertness test this file used to carry named
that row as the thing that would end it; it did, and what replaced it is the
live-carrier pin below. The DRAFTER_VERSION bump is consequently OWED and is
taken at integration (see the call site in tier05/draft.py).
"""
from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import Card
from tier05 import draft


def probe(**kw) -> Card:
    d = dict(id="eb118_draft_probe", name="Probe", cost=1, type="attack",
             character="klee", effects=[{"op": "damage", "amount": 12}])
    d.update(kw)
    return Card(**d)


def test_ethereal_discounts_the_whole_card():
    """A LIFECYCLE discount, not an op price: the keyword decides whether the
    printed effects resolve at all, so it scales what the card printed rather
    than sitting as a term beside it."""
    plain = draft._static_power(probe())
    assert draft._static_power(probe(ethereal=True)) == (
        plain * draft.STATIC_ETHEREAL_SHARE)
    assert draft.STATIC_ETHEREAL_SHARE < 1.0     # it is a DOWNSIDE


def test_the_tag_spelling_prices_the_same():
    assert (draft._static_power(probe(tags=["ethereal"]))
            == draft._static_power(probe(ethereal=True)))


def test_removing_it_on_upgrade_restores_the_full_price():
    assert (draft._static_power(probe(ethereal=False))
            > draft._static_power(probe(ethereal=True)))


def test_the_share_is_exercised_by_a_real_draftable_carrier():
    """The pin that replaces the inertness test.

    A probe-only pricing test proves the arithmetic and nothing about the
    tree. This one runs the share on the card the drafter can actually be
    shown, through the same `_static_power` the offer scorer calls, and
    pins the exact ratio -- so a silent change to STATIC_ETHEREAL_SHARE, to
    the placement of the multiplier, or to the card's body is caught by the
    number a drafted price is actually built from.
    """
    base = loader.get_card("big_badda_boom")
    up = loader.get_card("big_badda_boom+")
    assert base.rarity in C.RARITY_ODDS, "the carrier must be offerable"
    assert base.is_ethereal and not up.is_ethereal

    priced = draft._static_power(base)
    full = draft._static_power(up)
    assert full > 0.0                     # the test would be vacuous otherwise
    assert priced == full * draft.STATIC_ETHEREAL_SHARE
    assert priced < full                  # the downside costs the card price

    # The upgrade is the WHOLE difference: the ruled body (16 + the kill rider)
    # rides BOTH faces, so the gap between the two prices is exactly the
    # keyword. That is what makes the card a one-variable read of the share
    # (R193's armed trigger) even after the 2026-08-24 body ruling.
    assert base.cost == up.cost and base.effects == up.effects


def test_the_ruled_kill_rider_is_credited_at_zero():
    """THE HONEST NUMBER, AND THE UNDER-CREDIT NAMED WITH IT.

    [USER]'s 2026-08-24 body ruling hung a rider on this card -- 8 more damage
    to a random other enemy when the swing kills. The drafter cannot see it:
    `killed_target` is deliberately absent from STATIC_STATE_CONDITIONS, so
    `effect_power` never recurses into the branch and it contributes exactly
    0.0. The card prices identically with the rider and without it.

    This is pinned rather than fixed, on R194's terms (the note at
    STATIC_STATE_CONDITIONS): the error is one-directional -- the drafter
    UNDERvalues the card, never over-values it -- because crediting the branch
    would mean guessing a kill rate off a board the drafter has never seen.
    The test exists so the zero is a recorded decision and not an unnoticed
    hole: if a later change starts crediting kill branches, this fails and the
    acceptance gets revisited on purpose.
    """
    base = loader.get_card("big_badda_boom")
    rider = next(fx for fx in base.effects if fx.get("op") == "conditional")
    assert rider["if"] == "killed_target"
    assert rider["if"] not in draft.STATIC_STATE_CONDITIONS

    stripped = Card(**{**vars(base),
                       "effects": [fx for fx in base.effects
                                   if fx.get("op") != "conditional"]})
    assert draft._static_power(base) == draft._static_power(stripped)

    # The absolute numbers, so a silent move in the share, the placement of the
    # multiplier or the body is caught by the price a draft is built from.
    assert draft._static_power(base) == 4.8
    assert draft._static_power(loader.get_card("big_badda_boom+")) == 8.0


def test_the_carrier_set_is_exactly_what_was_ruled():
    """Ethereal is a downside the drafter now pays for, so an accidental
    `ethereal:` on some other row would quietly discount a card nobody meant
    to discount. Phase 2B rules ONE draftable carrier; this fails the moment
    a second appears without a ruling to point at."""
    offerable = [c for c in loader._card_index().values()
                 if c.rarity in C.RARITY_ODDS]
    assert offerable, "no offerable cards loaded -- the test would be vacuous"
    assert sorted(c.id for c in offerable
                  if c.is_ethereal) == ["big_badda_boom"]
