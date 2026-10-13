"""THE VARKA REVIEW'S SEAT-PAGE FIXES (review/ruled/varka-review-2026-10-12.md,
sec.4 and sec.5, ruled 2026-10-12):

  * the "Pyro Oath (left)" line after a switch goes ("noise"); the Oath
    counts stay;
  * a Four Winds' Ascension in the draw or discard pile is named on the pile
    line, so Wolfpack's shuffled copy and a played one are both visible;
  * a hand card's in-combat "(Makes Pyro current)" line is the game's own
    face text, so the page prints it unchanged.
"""
from __future__ import annotations

import pytest

from understudy import blindplay
from tier0.tests.test_varka_amber_round import _card, _hand, _rows_after
from tier0.tests.test_varka_seat_page import _status, varka_state


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


def test_the_oath_left_line_is_gone_and_the_counts_stay():
    state = varka_state()
    state["player"]["status"].append(_status(
        "Hydro Oath (left)", "Your current element switched away from Hydro "
        "this turn.", 3, "Counter"))
    page = blindplay.observe(state)
    assert "Oath (left)" not in page
    assert "- Oath: Pyro 2, Hydro 0, Electro 1, Cryo 0." in page


def _pile_line(page: str) -> str:
    return next(line for line in page.splitlines()
                if line.startswith("- Piles: "))


def test_an_ascension_in_the_draw_pile_is_named():
    state = varka_state()
    p = state["player"]
    p["draw_pile"] = [{"name": "Strike", "type": "Attack"},
                      {"name": "Four Winds' Ascension+", "type": "Attack"}]
    p["discard_pile"] = [{"name": "Four Winds' Ascension", "type": "Attack"}]
    line = _pile_line(blindplay.observe(state))
    assert "in the draw pile (1 Four Winds' Ascension+)" in line
    assert "discarded (1 Four Winds' Ascension)" in line


def test_a_plain_pile_names_nothing():
    state = varka_state()
    state["player"]["draw_pile"] = [{"name": "Strike", "type": "Attack"}]
    line = _pile_line(blindplay.observe(state))
    assert "(" not in line.split("in the draw pile", 1)[1].split(",", 1)[0]


def test_the_switch_line_prints_as_the_game_renders_it():
    state = varka_state()
    _hand(state, _card(state, "Kindled Edge",
                       "Deal 6 Pyro damage.\n(Makes Hydro current)", "Pyro"))
    rows = _rows_after(blindplay.observe(state), "Kindled Edge")
    assert "(Makes Hydro current)" in "\n".join(rows)
