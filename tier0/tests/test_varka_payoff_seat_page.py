"""THE VARKA PAYOFF ROUND'S SEAT-PAGE FIXES
(review/records/varka-payoff-round-2026-10-10.md, "What changes" and
"Defects to fix"):

  * the Oath-gain line names the relic held (Wolf's Gravestone after Orobas);
  * "WhatMod: KleeMod" never reaches a page, inside a text or as a tip;
  * Four Winds' Ascension's once-per-combat rule under the card in the hand;
  * Sucrose on a bare board says "no aura to Swirl";
  * the current-element block sits directly above the hand;
  * Wolfpack firing and what each Swirl paid under Twin Gales are said.

The fixture is `test_varka_seat_page.varka_state` (a recorded turn, re-dressed
as his).
"""
from __future__ import annotations

import copy

import pytest

from understudy import blindplay, blindplay_board
from understudy.blindplay_read import _text
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


def _row(card, *, oath=(), fang=False, fang_relic="", hits=False,
         no_aura=0, on_aura=0, events=()):
    return {"card_id": "X", "card": card, "auto_played": False,
            "carried": False, "overflowed": False,
            "hits": ([{"target": "Hilichurl 1", "amount": 6, "blocked": 0,
                       "combat_id": "100", "killed": False}] if hits else []),
            "applied": [], "summoned": [], "oath": list(oath),
            "fang_ascension": fang, "fang_relic": fang_relic,
            "swirl_no_aura": no_aura, "swirl_on_aura": on_aura,
            "between": False, "events": list(events)}


def _ev(kind, seq, card="", target="", power="", amount=0):
    return {"kind": kind, "card": card, "target": target, "power": power,
            "combat_id": "100" if target else "", "on_player": False,
            "seq": seq, "amount": amount}


PYRO_GAIN = [{"element": "Pyro", "amount": 1, "source": "applied"}]


def test_the_fang_line_names_wolfs_gravestone_after_orobas():
    state = varka_state()
    state["player"]["resolutions"] = [
        _row("Lunge", oath=PYRO_GAIN, fang=True,
             fang_relic="Wolf's Gravestone", hits=True)]
    page = blindplay.observe(state)
    assert ("  That gain made **Wolf's Gravestone** add **Four Winds' "
            "Ascension** to your hand.") in page
    assert "**Boreas's Fang** add" not in page


def test_an_older_mod_with_no_relic_name_still_reads_as_the_fang():
    state = varka_state()
    row = _row("Lunge", oath=PYRO_GAIN, fang=True, hits=True)
    del row["fang_relic"]
    state["player"]["resolutions"] = [row]
    assert ("That gain made **Boreas's Fang** add"
            in blindplay.observe(state))


def test_sucrose_on_a_bare_board_says_there_was_no_aura():
    state = varka_state()
    state["player"]["resolutions"] = [
        _row("Sucrose — Wind Spirit Creation", no_aura=3)]
    page = blindplay.observe(state)
    section = page.split("- **Sucrose — Wind Spirit Creation**", 1)[1]
    first = section.split("\n\n", 1)[0]
    assert ("No aura to Swirl: no enemy had an element on it, so the Swirl "
            "did nothing.") in first
    assert "Nothing this page can count" not in first


def test_a_swirl_that_found_an_aura_keeps_the_old_line():
    state = varka_state()
    state["player"]["resolutions"] = [
        _row("Sucrose — Wind Spirit Creation", no_aura=2, on_aura=1)]
    page = blindplay.observe(state)
    assert "No aura to Swirl" not in page
    assert "Nothing this page can count landed off it." in page


def test_the_oath_block_sits_directly_above_the_hand():
    page = blindplay.observe(varka_state())
    oath = page.index("## Your Oath")
    hand = page.index("## Your hand")
    assert oath < hand
    between = page[oath:hand]
    # Nothing but his block between the two headings.
    assert between.count("## ") == 1, between


def _with_ascension(state, relic="Boreas's Fang"):
    hand = state["player"]["hand"]
    card = copy.deepcopy(hand[0])
    card.update({"id": "KLEEMOD-PROTO_VK_FOUR_WINDS_ASCENSION",
                 "name": "Four Winds' Ascension", "type": "Attack",
                 "cost": "2", "keywords": [],
                 "description": "Deal 10 Anemo damage. Then deal 3 for each "
                                "Oath of your current element, as that "
                                "element, in one hit."})
    hand.append(card)
    state["player"]["relics"][0]["name"] = relic
    return state


def test_the_ascension_in_hand_says_where_it_came_from():
    page = blindplay.observe(_with_ascension(varka_state()))
    head = page.index("**Four Winds' Ascension**")
    note = page.index("    - Added by Boreas's Fang the first time each "
                      "combat you gain Oath.")
    assert note > head
    gravestone = blindplay.observe(
        _with_ascension(varka_state(), "Wolf's Gravestone"))
    assert ("Added by Wolf's Gravestone the first time each combat"
            in gravestone)


def test_no_note_without_the_relic():
    state = _with_ascension(varka_state())
    state["player"]["relics"] = []
    assert "Added by" not in blindplay.observe(state)


def test_wolfpack_and_twin_gales_are_said_since_last_page():
    state = varka_state()
    state["player"]["resolutions"] = [
        _row("Four Winds' Ascension", hits=True, events=[
            _ev("wolfpack", 9001, card="Four Winds' Ascension",
                power="Wolfpack", amount=1)]),
        _row("Windbound Execution", hits=True, events=[
            _ev("paid", 9002, card="Cryo", target="Hilichurl 1",
                power="Pyro (3 damage) and Cryo (1 Vulnerable)")]),
    ]
    page = blindplay.observe(state)
    line = next(ln for ln in page.splitlines()
                if ln.startswith("- Since last page: "))
    assert ("Wolfpack shuffled a copy of Four Winds' Ascension into your "
            "draw pile (it Exhausts when played)") in line
    assert ("Twin Gales: the Swirl of Cryo on Hilichurl 1 paid Pyro (3 "
            "damage) and Cryo (1 Vulnerable)") in line


def test_the_board_reads_the_new_row_keys():
    rows = blindplay_board.resolutions({"resolutions": [
        _row("Lunge", oath=PYRO_GAIN, fang=True,
             fang_relic="Wolf's Gravestone", no_aura=1)]})
    assert rows[0]["fang_relic"] == "Wolf's Gravestone"
    assert rows[0]["swirl_no_aura"] == 1 and rows[0]["swirl_on_aura"] == 0
    assert {"wolfpack", "paid"} <= set(blindplay_board.PAGE_EVENT_KINDS)


def test_the_mod_source_label_is_scrubbed_from_any_text():
    assert _text("Upgrade your starter relic. WhatMod: KleeMod") == (
        "Upgrade your starter relic.")
    assert _text("A.\nWhatMod: KleeMod\nWhatMod: KleeMod") == "A."
    # The bare tip name is left for the tip filter.
    assert _text("WhatMod") == "WhatMod"
    assert _text("No label here.") == "No label here."
