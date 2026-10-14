"""VARKA ROUND 5'S DISPLAY AND LOG FIXES
(review/records/varka-round-5-2026-10-13.md, "What to change" 1 and 2):

  * a hand card's switch line, now "(Makes Cryo current: 2 Oath)", and a
    Swirl card's "(No aura to Swirl)" are the game's own face text, so the
    page prints them unchanged;
  * Chain Lightning and Short Circuit name what they discarded on their own
    play line, and say when the game picked the cards because the hand held
    no more than it asked for.

The mod half is `klee-mod/KleeTests/Prototype/VarkaRound5LegibilityTests.cs`.
"""
from __future__ import annotations

import pytest

from understudy import blindplay, blindplay_board
from tier0.tests.test_varka_amber_round import _card, _hand, _rows_after
from tier0.tests.test_varka_payoff_seat_page import _ev, _row
from tier0.tests.test_varka_seat_page import varka_state


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


def test_the_switch_line_with_its_oath_prints_as_the_game_renders_it():
    state = varka_state()
    _hand(state, _card(state, "Kaeya: Heart of the Abyss",
                       "Deal 6 Cryo damage. Apply 1 Vulnerable.\n"
                       "(Makes Cryo current: 2 Oath)", "Cryo"))
    rows = _rows_after(blindplay.observe(state), "Kaeya: Heart of the Abyss")
    assert "(Makes Cryo current: 2 Oath)" in "\n".join(rows)


def test_the_no_aura_line_prints_as_the_game_renders_it():
    state = varka_state()
    _hand(state, _card(state, "Crosscurrent",
                       "Swirl the enemy. This Swirl pays your current "
                       "element twice.\n(No aura to Swirl)", "Anemo"))
    rows = _rows_after(blindplay.observe(state), "Crosscurrent")
    assert "(No aura to Swirl)" in "\n".join(rows)


def _discard(seq, card, picked=False):
    return _ev("play_discard", seq, card=card,
               power="only cards in hand" if picked else "")


def _section(page, card):
    return page.split(f"- **{card}**", 1)[1].split("\n- **", 1)[0]


def test_chain_lightning_names_what_it_discarded():
    state = varka_state()
    state["player"]["resolutions"] = [
        _row("Chain Lightning", hits=True, events=[
            _discard(9201, "Strike"), _discard(9202, "Kaeya: Hidden Strength")])]
    page = blindplay.observe(state)
    line = _section(page, "Chain Lightning")
    assert ("  Discarded: **Strike** and **Kaeya: Hidden Strength**."
            in line)
    assert "only cards in hand" not in line


def test_a_discard_the_game_picked_says_so():
    state = varka_state()
    state["player"]["resolutions"] = [
        _row("Chain Lightning", hits=True, events=[
            _discard(9301, "Strike", picked=True),
            _discard(9302, "Defend", picked=True)])]
    line = _section(blindplay.observe(state), "Chain Lightning")
    assert ("  Discarded: **Strike** and **Defend** (the only cards in "
            "hand).") in line


def test_short_circuit_with_no_hit_still_names_its_discard():
    state = varka_state()
    state["player"]["resolutions"] = [
        _row("Short Circuit", events=[_discard(9401, "Defend")])]
    line = _section(blindplay.observe(state), "Short Circuit")
    assert "  Discarded: **Defend**." in line
    assert "Nothing this page can count" not in line


def test_the_discard_event_is_not_repeated_under_since_last_page():
    state = varka_state()
    state["player"]["resolutions"] = [
        _row("Chain Lightning", hits=True, events=[_discard(9501, "Strike")])]
    events = blindplay_board.page_events(state["player"]) or []
    assert not [e for e in events if e["kind"] == "play_discard"]
    assert blindplay.observe(state).count("**Strike**") >= 1


def test_an_older_mod_sends_no_discards():
    rows = blindplay_board.resolutions(
        {"resolutions": [_row("Chain Lightning", hits=True)]})
    assert rows[0]["discarded"] == []
    assert rows[0]["discard_picked_for_you"] is False
