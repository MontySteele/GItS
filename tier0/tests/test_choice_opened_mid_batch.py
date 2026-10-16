"""A command refused because a choice opened since the seat's last look is
a skip, not a refusal (Furina seat 2026-10-14).

The seat chained `play "Curtain Rise"`, more plays and `end turn`. Curtain
Rise opened its chooser; the rest of the batch was refused against the
choice, three of those tripped the sticky REFUSAL STOP, and the `choose` that
followed was refused too. A choice is a fight overlay, so it keeps the room
and neither `screen_changed_after` nor `changed_under` saw it. Now a refusal
on an overlay the last look was not rendered on is skipped (not sent, not
counted), and a `choose` on that chooser goes through.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

import argparse

import pytest

from understudy import blindplay, blindplay_shape

from tier0.tests.test_understudy_blindplay import (
    card_select_state, combat_state)


@pytest.fixture
def lane(monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", None)
    monkeypatch.setenv("GITS_LANE", "2")
    monkeypatch.delenv(blindplay_shape.MAX_ACTIONS_ENV, raising=False)
    monkeypatch.setattr(blindplay_shape, "lane_embark_stamp",
                        lambda lane=None: "")
    monkeypatch.setattr(blindplay, "_lane_guard", lambda args: "")
    monkeypatch.setattr(blindplay, "_warn_build_skew", lambda state: None)
    screen = {"now": combat_state()}
    monkeypatch.setattr(blindplay, "_live_load",
                        lambda args, **kw: screen["now"])
    posted: list = []
    monkeypatch.setattr(blindplay, "post_when_the_room_is_open",
                        lambda *a, **kw: posted.append(a) or {})
    blindplay.forget_run()
    yield screen, posted
    blindplay.forget_run()


def _act(command):
    return argparse.Namespace(raw_file="", dry_run=False, brief=True,
                              command=command)


def _observe():
    return argparse.Namespace(raw_file="", brief=True, define="")


def _chooser():
    state = card_select_state()
    state["card_select"]["prompt"] = "Choose one."
    return state


def _play_opens_the_chooser(screen, posted, capsys):
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    assert blindplay.cmd_act(_act('play "Pearl Barrage" on "Nibbit"')) == 0, \
        capsys.readouterr().out
    assert len(posted) == 1
    capsys.readouterr()
    screen["now"] = _chooser()


def test_the_rest_of_the_batch_is_skipped_uncounted(lane, capsys):
    screen, posted = lane
    _play_opens_the_chooser(screen, posted, capsys)
    for command in ('play "Pearl Barrage" on "Nibbit"',
                    'play "All Streams Flow to the Sea" on "A"',
                    'play "Pearl Barrage"', "end turn"):
        assert blindplay.cmd_act(_act(command)) == 1
        out = capsys.readouterr().out
        assert out.strip() == (
            'Not sent: a choice opened since your last look ("Pearl '
            'Barrage"). This is not counted as a refusal. Look, then '
            'choose.'), out
    assert blindplay_shape.refusal_streak() == 0
    assert len(posted) == 1


def test_choose_on_the_chooser_still_goes_through(lane, capsys):
    screen, posted = lane
    _play_opens_the_chooser(screen, posted, capsys)
    # Skipped commands first, as the batch would have them...
    for _ in range(3):
        assert blindplay.cmd_act(_act("end turn")) == 1
    capsys.readouterr()
    # ...and the pick typed blind on the chooser is sent, no stop reached.
    assert blindplay.cmd_act(_act('choose "Coral Guard"')) == 0, \
        capsys.readouterr().out
    assert len(posted) == 2
    assert blindplay_shape.refusal_streak() == 0


def test_a_refusal_on_a_chooser_the_seat_looked_at_counts(lane, capsys):
    screen, posted = lane
    _play_opens_the_chooser(screen, posted, capsys)
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    assert blindplay.cmd_act(_act('play "Pearl Barrage"')) == 1
    assert "REFUSED" in capsys.readouterr().out
    assert blindplay_shape.refusal_streak() == 1
    assert len(posted) == 1


def test_the_look_remembers_its_screen(lane):
    blindplay_shape.remember_look("fight", [], screen="card_select")
    assert blindplay_shape.read_look()["screen"] == "card_select"
