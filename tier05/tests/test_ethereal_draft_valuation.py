"""EB-118: the drafter prices Ethereal as the downside it is.

A card that dies unplayed loses its value, so a drafter blind to the keyword
would score "strong, but it may vanish before you can afford it" as if the
second clause were not printed -- the mirror of every other unpriced-term
failure this scorer has been fixed for.

The term is INERT on the committed tree and this file proves it, which is the
whole reason no DRAFTER_VERSION move is taken here (see the PROPOSED note at
the call site in tier05/draft.py).
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


def test_the_term_is_inert_on_every_draftable_card_today():
    """No committed row prints the field, and the only cards the TAG
    spelling reaches are Statuses, Curses and the Spotlight token -- whose
    rarities are outside RARITY_ODDS, so no reward, shop or Neow channel can
    offer them. Nothing the drafter can be shown changes price, which is why
    the stamp does not move. This test is what becomes owed-work the day a
    draftable row prints `ethereal:`."""
    offerable = [c for c in loader._card_index().values()
                 if c.rarity in C.RARITY_ODDS]
    assert offerable, "no offerable cards loaded -- the test would be vacuous"
    assert not [c.id for c in offerable if c.is_ethereal]
