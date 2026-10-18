"""Seat page 8 (2026-10-18): the "Seat page" BACKLOG lines this batch closes.

1. Whispering Earring's turn: the relic note names the cards it played and
   points at the ledger, instead of saying no record exists beside the record
   (Furina suite 1, lane 1).
2. An event option that offers a choice of N cards drawn at the pick says
   the cards are drawn after the pick (Varka, Dispatch from Mondstadt).
3. Each resolution hit carries its kind (an element, an amplifier, a
   reaction's own damage) where the mod named one (Four Winds' Ascension+).
5. The seat brief names the record path (Yae round 7).
6. `proceed` right after `rest` rides out the rest site's Proceed button
   (Yae round 8, lane 5), and a command skipped after a screen change tells
   the seat to observe first (round 11).
7. A POST the game itself refused is not charged to the lane's budget
   (the first rest's "Rest site room is not open").

C# twin for 3: `ResolutionLedgerTests`. NOTHING MEASURED HERE IS QUOTABLE
(R215 B): shape assertions.
"""
from __future__ import annotations

import copy
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

from understudy import blindplay, blindplay_session

from tier0.tests.test_understudy_blindplay import combat_state

REPO = Path(__file__).resolve().parents[2]

EARRING = {"name": "Whispering Earring",
           "description": "Gain 1 Energy at the start of each turn. Vakuu "
                          "plays your first turn for you."}


def _seat():
    spec = importlib.util.spec_from_file_location(
        "seat_tool_8", REPO / "tools" / "seat.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _row(card, hits=(), auto=False, carried=False):
    return {"card_id": card.lower().replace(" ", "_"), "card": card,
            "auto_played": auto, "carried": carried, "overflowed": False,
            "hits": list(hits)}


def _hit(target="Damp Cultist", amount=6, label=""):
    return {"target": target, "amount": amount, "blocked": 0,
            "combat_id": "", "label": label}


def _turn_one(*rows, ledger=True):
    state = copy.deepcopy(combat_state())
    state["battle"]["round"] = 1
    state["player"]["hand"] = []
    state["player"]["relics"] = [dict(EARRING)]
    if ledger:
        state["player"]["resolutions"] = list(rows)
    else:
        state["player"].pop("resolutions", None)
    return state


# ---- 1. Whispering Earring ---------------------------------------------------

def test_the_earring_note_names_what_it_played_and_points_at_the_ledger():
    page = blindplay.observe(_turn_one(
        _row("Strike", [_hit()], auto=True), _row("Defend", auto=True)))
    assert ("**Whispering Earring** plays a turn of yours for you, and it "
            "has already played this one: **Strike** and **Defend**") in page
    assert "- **Strike** *(the game played this one, not you)*" in page
    # The old sentence, that no record exists, is gone where the record is.
    assert "no record of a card resolving" not in page


def test_the_earring_note_with_nothing_auto_played_says_so():
    page = blindplay.observe(_turn_one(_row("Strike", [_hit()])))
    assert "names no card it played" in page
    assert "no record of a card resolving" not in page


def test_a_build_with_no_ledger_keeps_the_old_gap_note():
    page = blindplay.observe(_turn_one(ledger=False))
    assert "no record of a card resolving on the wire" in page


# ---- 2. A choice of N drawn at the pick --------------------------------------

def _event(description):
    return {"state_type": "event", "run": {"act": 1, "floor": 5},
            "player": {"hp": 70, "max_hp": 80, "gold": 99},
            "event": {"event_id": "DISPATCH", "event_name":
                      "Dispatch from Mondstadt", "in_dialogue": False,
                      "body": "A courier catches up with Varka.",
                      "options": [{"index": 0, "title":
                                   "Request reinforcements for the "
                                   "expedition.",
                                   "description": description}]}}


def test_a_choice_of_cards_drawn_at_the_pick_says_so():
    page = blindplay.observe(_event(
        "Choose 1 of 3 random Knights to add to your deck."))
    assert blindplay.OPTION_ROLLED_GRANT in page
    assert blindplay.OPTION_UNNAMED_GRANT not in page


def test_a_named_card_with_no_face_keeps_the_gap_note():
    page = blindplay.observe(_event("Add Exterminate to your Deck"))
    assert blindplay.OPTION_UNNAMED_GRANT in page
    assert blindplay.OPTION_ROLLED_GRANT not in page


# ---- 3. Which hit was which --------------------------------------------------

def test_each_hit_prints_its_kind_where_the_mod_named_one():
    state = copy.deepcopy(combat_state())
    state["player"]["resolutions"] = [_row("Four Winds' Ascension+", [
        _hit(amount=2), _hit(amount=3, label="Swirl"),
        _hit(amount=9, label="Pyro"),
        _hit(amount=36, label="Pyro, Vaporize")])]
    page = blindplay.observe(state)
    lines = [ln.strip() for ln in page.splitlines()
             if ln.strip()[:2] in ("1.", "2.", "3.", "4.")]
    assert lines == ["1. **Damp Cultist** -- 2",
                     "2. **Damp Cultist** -- 3 [Swirl]",
                     "3. **Damp Cultist** -- 9 [Pyro]",
                     "4. **Damp Cultist** -- 36 [Pyro, Vaporize]"]


def test_an_older_mod_with_no_label_prints_as_before():
    state = copy.deepcopy(combat_state())
    hit = _hit()
    del hit["label"]
    state["player"]["resolutions"] = [_row("Strike", [hit])]
    assert "1. **Damp Cultist** -- 6\n" in blindplay.observe(state) + "\n"


# ---- 5. The record path ------------------------------------------------------

def test_the_brief_names_the_record_path_under_scratch(tmp_path):
    seat = _seat()
    plain = seat.brief_text(2, "KLEEMOD-KLEE")
    filled = seat.brief_text(2, "KLEEMOD-KLEE", scratch=str(tmp_path))
    record = (tmp_path / "seat-lane2" / "record.md").as_posix()
    head, _, body = filled.partition("\n")
    assert f"Write your record (the one Write call) to `{record}`" in head
    assert "record.md" not in plain.partition("\n")[0]
    # The instrument text is untouched: only the lane line gained the path.
    assert body == plain.partition("\n")[2]


def test_an_explicit_record_path_wins(tmp_path):
    seat = _seat()
    mine = (tmp_path / "r" / "lane3.md").as_posix()
    head = seat.brief_text(3, "X", scratch=str(tmp_path),
                           record=mine).partition("\n")[0]
    assert f"`{mine}`" in head
    assert "seat-lane3/record.md" not in head


def test_the_coordinator_is_told_the_record_path_or_its_absence(tmp_path):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    run = [sys.executable, str(REPO / "tools" / "seat.py"), "--opus-brief",
           "--lane", "2"]
    res = subprocess.run(run + ["--scratch", str(tmp_path)],
                         capture_output=True, text=True, encoding="utf-8",
                         cwd=str(REPO), env=env)
    assert res.returncode == 0, res.stderr
    assert "record: " + (tmp_path / "seat-lane2" / "record.md").as_posix() \
        in res.stderr
    bare = subprocess.run(run, capture_output=True, text=True,
                          encoding="utf-8", cwd=str(REPO), env=env)
    assert "no record path" in bare.stderr


# ---- 6. proceed after rest, and the screen-changed skip ----------------------

class _Wire:
    def __init__(self, answers):
        self.answers = list(answers)
        self.posts = 0

    def post(self, action, **params):
        self.posts += 1
        return self.answers.pop(0) if self.answers else {"status": "ok"}


NO_BUTTON = {"status": "error",
             "error": "No proceed button available or enabled"}


def test_proceed_on_a_rest_site_rides_out_the_button(monkeypatch):
    monkeypatch.setattr(blindplay_session.time, "sleep", lambda s: None)
    wire = _Wire([NO_BUTTON, NO_BUTTON, {"status": "ok"}])
    got = blindplay_session.post_when_the_room_is_open(
        wire, "proceed", {}, tries=60, delay=0.5, screen="rest_site")
    assert got == {"status": "ok"}
    assert wire.posts == 3


def test_the_ride_is_bounded_and_off_the_rest_site_is_not_taken(monkeypatch):
    monkeypatch.setattr(blindplay_session.time, "sleep", lambda s: None)
    wire = _Wire([NO_BUTTON] * 100)
    got = blindplay_session.post_when_the_room_is_open(
        wire, "proceed", {}, tries=60, delay=0.5, screen="rest_site")
    assert got == NO_BUTTON
    assert wire.posts == blindplay_session.REST_PROCEED_TRIES + 1
    # A reward screen's (or a co-op rest site's, `screen=""`) refusal is an
    # answer, posted once.
    for screen in ("rewards", ""):
        wire = _Wire([NO_BUTTON] * 3)
        blindplay_session.post_when_the_room_is_open(
            wire, "proceed", {}, tries=60, delay=0.5, screen=screen)
        assert wire.posts == 1


def test_the_no_proceed_answer_tells_the_seat_to_observe():
    line = blindplay_session._result_line(NO_BUTTON)
    assert "`observe`, then `proceed` again" in line


def test_the_screen_changed_skip_says_observe_first():
    text = blindplay.SCREEN_CHANGED_SKIP.format(command='go "Rest (path 1)"')
    assert text.startswith('Skipped: the screen changed after go "Rest')
    assert "`observe` first" in text
    assert "not counted as a refusal" in text


# ---- 7. A POST the game refused is not charged (EB-391's rest) ---------------

def test_a_post_the_game_refused_is_not_charged(monkeypatch, capsys):
    import argparse

    from understudy import blindplay_shape
    from tier0.tests.test_understudy_blindplay import rest_state

    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", None)
    monkeypatch.setenv("GITS_LANE", "3")
    monkeypatch.delenv(blindplay_shape.MAX_ACTIONS_ENV, raising=False)
    monkeypatch.setattr(blindplay_shape, "lane_embark_stamp",
                        lambda lane=None: "")
    monkeypatch.setattr(blindplay, "_lane_guard", lambda args: "")
    monkeypatch.setattr(blindplay, "_warn_build_skew", lambda state: None)
    monkeypatch.setattr(blindplay, "_live_load",
                        lambda args, **kw: rest_state())
    answers = [{"status": "error", "error": "Rest site room is not open"},
               {"status": "ok", "message": "Rested"}]
    monkeypatch.setattr(blindplay, "post_when_the_room_is_open",
                        lambda *a, **kw: answers.pop(0))
    blindplay.forget_run()
    blindplay_shape.set_budget(100)
    try:
        args = argparse.Namespace(raw_file="", dry_run=False, brief=True,
                                  command="rest")
        assert blindplay.cmd_act(args) == 1
        out = capsys.readouterr().out
        assert "Took:" not in out
        assert "actions: 0 of 100 (the game refused this one" in out
        assert blindplay_shape.budget_spent() == (0, 100)
        assert blindplay.cmd_act(args) == 0
        assert "actions: 1 of 100" in capsys.readouterr().out
    finally:
        blindplay_shape.set_budget(0)
        blindplay.forget_run()
