"""VARKA ROUND 5 (review/records/varka-round-5-2026-10-13.md, "What did not"):
"Kaeya, Barbara and Short Circuit switch the current element and silently
lower Ascension's Oath. A reaction that uses up an aura leaves a later Swirl
card with nothing to Swirl, and the screen does not say the aura is gone."

The page layer answers both, from fields the wire already sends ([USER]: no
more text on the cards themselves, "but it might go into the harness layer"):

  * under a hand card whose play would make another element current, the
    switch and the Oath it moves cards to, read off his badge;
  * in his Oath block, a bare body whose aura a logged reaction used up says
    there is nothing on it to Swirl, while a Swirl card is in hand.
"""
from __future__ import annotations

import pytest

from understudy import blindplay
from tier0.tests.test_varka_amber_round import _card, _hand, _rows_after
from tier0.tests.test_varka_seat_page import (NO_ELEMENT_TEXT, _block,
                                              _status, varka_state)


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


SHORT_CIRCUIT = ("Discard 2 cards. Draw 2 cards. Gain 1 Energy. Apply "
                 "Electro to an enemy.")
BARBARA = "Gain 6 Block. Apply Hydro to an enemy. Next turn, gain 3 Block."
KAEYA_KNIGHT = "Knight. Deal 7 damage. Apply 1 Weak."
SWIRL_CARD = "Deal 6 damage. Swirl the enemy."
BANNER_TEXT = ("Only Knights can change your current element. Whenever "
               "another card would, gain 1 Oath of your current element "
               "instead.")
ALL_FOUR_TEXT = "Your cards read your Oath of every element together."


def _switch_lines(page, title):
    return [line for line in _rows_after(page, title)
            if "Switches you to" in line]


def test_a_card_applying_another_element_names_the_switch_and_the_oath():
    # The badge: current Pyro, Oath Pyro 2, Hydro 0, Electro 1, Cryo 0.
    state = varka_state()
    _hand(state,
          _card(state, "Short Circuit", SHORT_CIRCUIT, "Electro", "Skill"),
          _card(state, "Barbara: Glorious Season", BARBARA, "Hydro",
                "Skill"),
          _card(state, "Kindled Edge", "Deal 9 damage.", "Pyro"))
    page = blindplay.observe(state)
    assert _switch_lines(page, "Short Circuit") == [
        "    - Switches you to Electro: your cards read Electro Oath 1 (plus "
        "what this gains). Your Pyro Oath 2 is kept for when you switch "
        "back."]
    assert _switch_lines(page, "Barbara: Glorious Season") == [
        "    - Switches you to Hydro: your cards read Hydro Oath 0 (plus what "
        "this gains). Your Pyro Oath 2 is kept for when you switch back."]
    # The current element's own card switches nothing.
    assert _switch_lines(page, "Kindled Edge") == []


def test_an_anemo_card_and_an_elementless_card_switch_nothing():
    state = varka_state()
    _hand(state, _card(state, "Gust", SWIRL_CARD, "Anemo"),
          _card(state, "Guard", "Gain 5 Block.", None, "Skill"))
    page = blindplay.observe(state)
    assert "Switches you to" not in page


def test_the_banner_holds_the_element_against_all_but_a_knight():
    state = varka_state()
    state["player"]["status"].append(
        _status("Unwavering Banner", BANNER_TEXT))
    _hand(state,
          _card(state, "Short Circuit", SHORT_CIRCUIT, "Electro", "Skill"),
          _card(state, "Kaeya", KAEYA_KNIGHT, "Cryo"))
    page = blindplay.observe(state)
    assert _switch_lines(page, "Short Circuit") == []
    assert _switch_lines(page, "Kaeya") == [
        "    - Switches you to Cryo: your cards read Cryo Oath 0 (plus what "
        "this gains). Your Pyro Oath 2 is kept for when you switch back."]


def test_under_all_four_winds_a_switch_moves_nothing():
    state = varka_state()
    state["player"]["status"].append(
        _status("All Four Winds", ALL_FOUR_TEXT))
    _hand(state,
          _card(state, "Short Circuit", SHORT_CIRCUIT, "Electro", "Skill"))
    assert "Switches you to" not in blindplay.observe(state)


def test_with_no_current_element_the_first_one_reads_from_zero():
    state = varka_state(badge=("Oath", NO_ELEMENT_TEXT, 1))
    _hand(state, _card(state, "Barbara: Glorious Season", BARBARA, "Hydro",
                       "Skill"))
    page = blindplay.observe(state)
    assert _switch_lines(page, "Barbara: Glorious Season") == [
        "    - Switches you to Hydro: your cards read Hydro Oath 1 (plus what "
        "this gains)."]


def _melted_third(state):
    """A Melt this turn used up the third body's aura (it is bare now)."""
    state["player"]["reactions"] = [
        {"reaction": "Melt", "source": "Kindled Edge",
         "target": "Hilichurl 3", "combat_id": "102"}]
    return state


def test_an_aura_a_reaction_used_up_says_there_is_nothing_to_swirl():
    state = _melted_third(varka_state())
    _hand(state, _card(state, "Gust", SWIRL_CARD, "Anemo"))
    lines = _block(blindplay.observe(state))
    assert "- **Hilichurl 3**: no aura to Swirl (Melt used it up)." in lines
    # The bodies that still carry an aura read as before.
    assert "- **Hilichurl 1**: Pyro: an Anemo hit Swirls it." in lines


def test_without_a_swirl_card_in_hand_the_bare_body_reads_as_before():
    state = _melted_third(varka_state())
    _hand(state, _card(state, "Kindled Edge", "Deal 9 damage.", "Pyro"))
    lines = _block(blindplay.observe(state))
    assert "- **Hilichurl 3**: no aura." in lines


def test_a_body_whose_aura_came_back_is_not_called_bare():
    state = _melted_third(varka_state())
    state["player"]["reactions"][0].update(target="Hilichurl 1",
                                           combat_id="100")
    _hand(state, _card(state, "Gust", SWIRL_CARD, "Anemo"))
    lines = _block(blindplay.observe(state))
    assert "- **Hilichurl 1**: Pyro: an Anemo hit Swirls it." in lines
    assert "- **Hilichurl 3**: no aura." in lines
