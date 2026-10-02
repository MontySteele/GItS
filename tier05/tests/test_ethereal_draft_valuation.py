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


def test_the_carrier_set_is_exactly_what_was_ruled():
    """Ethereal is a downside the drafter now pays for, so an accidental
    `ethereal:` on some row would quietly discount a card nobody meant to
    discount. Phase 2B ruled ONE draftable carrier, the shipped
    `big_badda_boom`, which left with the shipped sheets (legacy cleanup stage
    6); no current row carries the keyword, and this fails the moment one
    appears without a ruling to point at."""
    offerable = [c for c in loader.prototype_cards()
                 if c.rarity in C.RARITY_ODDS]
    assert offerable, "no offerable cards loaded -- the test would be vacuous"
    assert sorted(c.id for c in offerable if c.is_ethereal) == []
