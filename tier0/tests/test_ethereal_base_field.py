"""EB-118: Ethereal printed on a PERSONAL card, and bought off on upgrade.

The engine has modelled Ethereal since Furina's Spotlight token, but only
through `tags: [ethereal]` -- the vocabulary the engine sheets use for
Statuses, Curses and tokens. Personal sheets spell lifecycle keywords as
fields (`exhaust:`, `innate:`, `retain:`), so a character card could not
declare the keyword at all. This file pins the field, the shared predicate
both spellings feed, the remove-on-upgrade delta, and the two things that
must NOT move:

  1. Ethereal is orthogonal to `Card.is_junk`. An Ethereal PERSONAL card is
     still one of Kokomi's own cards and still pays her Charge funnel when
     it burns (LAW, Kokomi identity, [USER] 2026-08-23).
  2. A card that does not print the field is untouched -- it discards.

STAGED: no committed sheet row carries `ethereal:` yet, so every card here
is synthetic on purpose.
"""
import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import combat
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy

PROBE = "eb118_ethereal_probe"


def probe(**kw) -> Card:
    d = dict(id=PROBE, name="Probe", cost=1, type="skill",
             character="kokomi", effects=[{"op": "block", "amount": 5}])
    d.update(kw)
    return Card(**d)


def hand_survives(card: Card, character: str = "kokomi"):
    """One fight, no plays, nothing to draw: the only thing that can move
    `card` is the end-of-turn flush. The idiom test_kokomi_rotation_law's
    ethereal-curse case uses, for the same reason -- the real turn loop and
    not a direct call is what is under test."""
    p = loader.build_player(character)
    p.draw_pile = []
    p.discard_pile = []
    p.hand = [card]
    return combat.run_fight(
        p, [make_enemy(hp=1, intents=[{"kind": "block", "amount": 0}])],
        lambda s: None, seed=0)


# --- 0. the field and the predicate ---

def test_the_field_is_a_sheet_field_and_feeds_the_shared_predicate():
    assert Card.from_dict(dict(id="x", name="x", cost=0, type="skill",
                               ethereal=True)).is_ethereal
    # The tag spelling still answers the same predicate: one door, two keys.
    assert loader.get_card("curse_clumsy").is_ethereal
    assert loader.get_card("ethereal_spotlight").is_ethereal
    assert not probe().is_ethereal


def test_ethereal_is_orthogonal_to_junk():
    """A timing keyword is not a rarity class. Kokomi's rotation law reads
    `is_junk`, and nothing about printing Ethereal may make a personal card
    look like a Status to it."""
    assert not probe(ethereal=True).is_junk
    assert loader.get_card("curse_clumsy").is_junk        # junk AND ethereal
    assert not loader.get_card("curse_poor_sleep").is_ethereal   # junk, not


# --- 1. base behaviour ---

def test_base_ethereal_personal_card_exhausts_at_end_of_turn():
    st = hand_survives(probe(ethereal=True))
    assert any(c.id == PROBE for c in st.player.exhaust_pile)
    assert not any(c.id == PROBE for c in st.player.discard_pile)


def test_a_card_without_the_field_is_untouched():
    """The red half. Same card, same fight, field absent: it flushes to the
    discard pile and never reaches exhaust."""
    st = hand_survives(probe())
    assert not any(c.id == PROBE for c in st.player.exhaust_pile)


def test_retain_still_beats_ethereal():
    """The flush's own precedence, unchanged by the new door: a retained
    card is not swept, so a card printing both stays in hand."""
    st = hand_survives(probe(ethereal=True, retain=True))
    assert not any(c.id == PROBE for c in st.player.exhaust_pile)


# --- 2. the Charge funnel (Kokomi's rotation law) ---

def test_an_ethereal_personal_card_still_pays_the_charge_funnel():
    """C11's law drops Statuses and Curses from the funnel by RARITY. An
    Ethereal personal card is neither, so burning unplayed is still one of
    HER cards exhausting and still pays -- the exact seam a keyword-shaped
    reading of the law would break."""
    st = hand_survives(probe(ethereal=True))
    assert any(c.id == PROBE for c in st.player.exhaust_pile)
    assert st.player.charge == C.CHARGE_PER_EXHAUST
    assert st.player.burst_energy == C.KOKOMI_BURST_PER_EXHAUST
    assert any(ev["event"] == "gain_charge" for ev in st.log)


# --- 3. the remove-on-upgrade delta ---

def test_remove_ethereal_upgrade_clears_the_printed_keyword(monkeypatch):
    monkeypatch.setattr(upgrades, "_upgrade_index",
                        lambda: {PROBE: {"remove": "ethereal"}})
    assert upgrades.has_upgrade(PROBE)
    upgraded = upgrades.apply_upgrade(probe(ethereal=True))
    assert upgraded.id == PROBE + "+"
    assert not upgraded.ethereal and not upgraded.is_ethereal


def test_the_upgraded_copy_survives_the_turn(monkeypatch):
    monkeypatch.setattr(upgrades, "_upgrade_index",
                        lambda: {PROBE: {"remove": "ethereal"}})
    st = hand_survives(upgrades.apply_upgrade(probe(ethereal=True)))
    assert not any(c.id.startswith(PROBE) for c in st.player.exhaust_pile)


def test_removing_a_keyword_the_card_never_printed_is_a_sheet_error(
        monkeypatch):
    """Loud, not silent: the delta would otherwise produce an upgraded copy
    identical to its base, and a campfire choice that does nothing is
    exactly what R24's no-partial-upgrades discipline forbids."""
    monkeypatch.setattr(upgrades, "_upgrade_index",
                        lambda: {PROBE: {"remove": "ethereal"}})
    with pytest.raises(ValueError, match="found no matching effect"):
        upgrades.apply_upgrade(probe())
