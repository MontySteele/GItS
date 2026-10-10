"""THE VARKA HYDRO ROUND'S SEAT-PAGE FIXES
(review/records/varka-hydro-round-2026-10-10.md, "Defects and legibility"):

  * Wolfpack's copy of Four Winds' Ascension, which Exhausts, is told apart
    from the original in the hand by "(exhausts)" beside its number;
  * the Ascension a relic adds says it is not in your deck.
"""
from __future__ import annotations

import copy

import pytest

from understudy import blindplay
from tier0.tests.test_varka_seat_page import varka_state
from tier0.tests.test_varka_payoff_seat_page import _with_ascension


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    blindplay.forget_run()
    yield
    blindplay.forget_fight()
    blindplay.forget_run()


@pytest.fixture(autouse=True)
def _no_live_speed(monkeypatch):
    from understudy import blindplay_faces as faces
    monkeypatch.setattr(faces, "FAST_MODE_READER", lambda: "")


EXHAUST = {"name": "Exhaust", "description": "Removed until end of combat."}


def _two_ascensions(state, copy_exhausts=True):
    state = _with_ascension(state)
    hand = state["player"]["hand"]
    twin = copy.deepcopy(hand[-1])
    if copy_exhausts:
        twin["description"] += " Exhaust."
        twin["keywords"] = [EXHAUST]
    hand.append(twin)
    return state


def _head_lines(page):
    return [ln for ln in page.splitlines()
            if ln.startswith("- **Four Winds' Ascension")]


def test_the_exhausting_copy_is_marked():
    heads = _head_lines(blindplay.observe(_two_ascensions(varka_state())))
    assert len(heads) == 2
    assert "(exhausts)" not in heads[0]
    assert heads[1].startswith("- **Four Winds' Ascension (2)** (exhausts)")


def test_copies_that_agree_are_not_marked():
    page = blindplay.observe(_two_ascensions(varka_state(),
                                             copy_exhausts=False))
    assert "(exhausts)" not in page


def test_the_relic_ascension_says_it_is_not_in_the_deck():
    page = blindplay.observe(_with_ascension(varka_state()))
    assert ("    - Added by Boreas's Fang the first time each combat you "
            "gain Oath. It is not in your deck.") in page
