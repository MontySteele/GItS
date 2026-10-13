"""The three-refusal stop is counted by the bridge (BACKLOG: "Seat bridge:
when a fight ends partway through a batch of commands").

Co-op paired round 2026-10-09, finding 8: a fight that ended partway through
a batch turned the rest of the batch into "The fight is over" lines, which do
not start with REFUSED, so the seat never counted them and the run of refusals
went past three. The lane now keeps the streak itself.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

import argparse

import pytest

from understudy import blindplay, blindplay_shape

from tier0.tests.test_understudy_blindplay import combat_state, map_state


@pytest.fixture
def lanes(monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", None)
    monkeypatch.setenv("GITS_LANE", "3")
    monkeypatch.delenv(blindplay_shape.MAX_ACTIONS_ENV, raising=False)
    monkeypatch.setattr(blindplay_shape, "lane_embark_stamp",
                        lambda lane=None: "")
    return blindplay_shape.lane_state_root()


def _live(command):
    return argparse.Namespace(raw_file="", dry_run=False, brief=True,
                              command=command)


def test_plays_chained_after_the_fight_ended_reach_the_stop(
        lanes, monkeypatch, capsys):
    blindplay.forget_run()
    blindplay.screen_page(combat_state())        # the last page was a fight
    monkeypatch.setattr(blindplay, "_lane_guard", lambda args: "")
    monkeypatch.setattr(blindplay, "_live_load",
                        lambda args, **kw: map_state())
    posted = []
    monkeypatch.setattr(blindplay, "post_when_the_room_is_open",
                        lambda *a, **kw: posted.append(a) or {})
    # Two "The fight is over" lines: counted, no stop yet.
    for _ in range(2):
        assert blindplay.cmd_act(_live('play "Strike"')) == 1
        assert "REFUSAL STOP" not in capsys.readouterr().out
    assert blindplay_shape.refusal_streak() == 2
    # The third is the stop, said on that line.
    assert blindplay.cmd_act(_live('play "Strike"')) == 1
    assert "REFUSAL STOP: 3 commands in a row" in capsys.readouterr().out
    # And every command after it is held at the stop, sent or not.
    assert blindplay.cmd_act(_live("proceed")) == 2
    assert capsys.readouterr().out.startswith("REFUSAL STOP")
    assert posted == []
    blindplay.forget_run()


def test_a_sent_command_ends_the_streak(lanes, monkeypatch, capsys):
    blindplay.forget_run()
    blindplay.screen_page(map_state())
    monkeypatch.setattr(blindplay, "_lane_guard", lambda args: "")
    monkeypatch.setattr(blindplay, "_live_load",
                        lambda args, **kw: map_state())
    monkeypatch.setattr(blindplay, "post_when_the_room_is_open",
                        lambda *a, **kw: {})
    for _ in range(2):
        assert blindplay.cmd_act(_live('play "Strike"')) == 1
    assert blindplay_shape.refusal_streak() == 2
    assert blindplay.cmd_act(_live('go "Monster (path 2)"')) == 0, capsys.readouterr().out
    assert blindplay_shape.refusal_streak() == 0
    # With a cap, the charge itself zeroes the streak.
    blindplay_shape.set_budget(100)
    blindplay_shape.count_refusal()
    blindplay_shape.count_action()
    assert blindplay_shape.refusal_streak() == 0
    blindplay.forget_run()


def test_a_new_embark_starts_the_streak_at_zero(lanes):
    blindplay_shape.count_refusal()
    blindplay_shape.count_refusal()
    blindplay_shape.set_budget(100)
    assert blindplay_shape.refusal_streak() == 0
