"""`EB-509`: once the Spotlight is lit, the relic stops dealing the selector.

WHAT THE SEAT SAW (Furina r11, natural lane). The starting relic adds an
Ethereal Spotlight to hand every turn. Under the reframe Center Stage is
retired, so Guest Cast is the only target and the second copy is refused by
the card's own `IsPlayable` -- "the Spotlight is already on your Companion
cards". The seat met that as five to seven dead draws a fight: a hand slot, a
hover, and a refusal, every turn, from turn 2 on.

THE RELIC ALREADY SAID SO. Its arm face is "Each turn, add an Ethereal
Spotlight to your Hand. It does nothing once your Companion cards are lit for
this combat" -- the sentence was true about the CARD and false about the
relic, which went on dealing it.

ONE PREDICATE, TWO CALLERS. `effects.spotlight_designate_is_redundant` is the
designation's own refusal, and the grant asks it one broadcast earlier so the
relic cannot start dealing a card the card would refuse. C# twin:
`SpotlightSystem.DesignateOneModeIsRedundant`, read by
`EtherealSpotlight.IsPlayable` and now by
`EtherealSpotlightRelic.BeforeSideTurnStart`.

NOT THE PRICE HALF. A seat short of Encore this turn may have it next turn, so
a refusal on price is temporary and the card belongs in hand; being lit lasts
the rest of the combat.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, furina_reframe
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy


@pytest.fixture(autouse=True)
def spotlight_arm(monkeypatch):
    for flag in ("FURINA_REFRAME", "FURINA_REFRAME_SPOTLIGHT"):
        monkeypatch.setattr(furina_reframe, flag, True)


def _state(lit: bool):
    p = loader.build_player("furina")
    p.hand = []
    if lit:
        p.spotlight = C.SPOTLIGHT_GUEST_CAST
    return CombatState(player=p, enemies=[make_enemy()],
                       rng=random.Random(5))


def _selectors(state):
    return [card for card in state.player.hand
            if card.id == "ethereal_spotlight"]


def test_an_unlit_combat_still_gets_its_selector():
    state = _state(lit=False)

    effects.player_turn_start_triggers(state)

    assert len(_selectors(state)) == 1


def test_a_lit_combat_is_dealt_no_second_selector():
    """Turn 2 of the seat's fight: the Spotlight was lit on turn 1."""
    state = _state(lit=True)

    effects.player_turn_start_triggers(state)

    assert _selectors(state) == []


def test_the_lit_combat_stays_silent_turn_after_turn():
    state = _state(lit=True)

    for _ in range(5):
        effects.player_turn_start_triggers(state)

    assert state.player.hand == []


def test_being_short_of_encore_does_not_stop_the_grant():
    """The price is temporary and the card belongs in hand; only the lighting
    is for the rest of the combat."""
    state = _state(lit=False)
    state.player.encore = 0

    effects.player_turn_start_triggers(state)

    assert len(_selectors(state)) == 1


def test_off_the_arm_a_lit_spotlight_still_gets_its_selector(monkeypatch):
    """The quarantine: off the reframe the selector has two targets and a
    second play RE-AIMS, so nothing here may withhold it."""
    monkeypatch.setattr(furina_reframe, "FURINA_REFRAME_SPOTLIGHT", False)
    state = _state(lit=True)

    effects.player_turn_start_triggers(state)

    assert len(_selectors(state)) == 1


def test_the_designation_and_the_grant_ask_the_same_question():
    """SOURCE-READ, and the whole point of the row: a second copy of the
    predicate is what let the relic and the card disagree in the first
    place."""
    body = effects.player_turn_start_triggers.__code__.co_names
    designate = effects._spotlight_designate_one_mode.__code__.co_names

    assert "spotlight_designate_is_redundant" in body
    assert "spotlight_designate_is_redundant" in designate
