"""A batch that crosses a screen change stops cleanly, and the coordinator
can lift a sticky REFUSAL STOP (Varka round 2026-10-13, lanes 1 and 2).

A seat played Chain Lightning into the last enemy with `choose`, `choose`,
`confirm` queued for a discard prompt that never came: the fight ended, the
three were refused against the reward screen, and the third tripped the stop
for every later seat on the lane. Now a command typed after an earlier one of
its batch left the room is skipped, not sent and not counted; refusals on an
unchanged screen still count; `reset-refusals --lane N` clears the stop.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

import argparse

import pytest

from understudy import blindplay, blindplay_shape

from tier0.tests.test_understudy_blindplay import (
    card_select_state, combat_state, rewards_state)


@pytest.fixture
def lane(monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", None)
    monkeypatch.setenv("GITS_LANE", "3")
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


def test_commands_after_the_fight_ended_mid_batch_are_skipped_uncounted(
        lane, capsys):
    screen, posted = lane
    blindplay.screen_page(combat_state())
    # The command that ends the fight is sent from the fight...
    assert blindplay.cmd_act(_act("end turn")) == 0, capsys.readouterr().out
    assert len(posted) == 1
    capsys.readouterr()
    # ...and the fight is over: the rest of the batch lands on the rewards.
    screen["now"] = rewards_state()
    for command in ('choose "Defend"', 'choose "Strike"', "confirm",
                    'choose "Strike"'):
        assert blindplay.cmd_act(_act(command)) == 1
        out = capsys.readouterr().out
        assert out.strip() == ("Skipped: the screen changed after end turn; "
                               "look again.")
    assert blindplay_shape.refusal_streak() == 0
    assert len(posted) == 1


def test_refusals_on_an_unchanged_screen_still_reach_the_stop(lane, capsys):
    screen, posted = lane
    blindplay.screen_page(combat_state())
    assert blindplay.cmd_act(_act("end turn")) == 0
    screen["now"] = rewards_state()
    # A look ends the stale batch; refusals after it are refusals.
    assert blindplay.cmd_observe(_observe()) == 0
    capsys.readouterr()
    for _ in range(2):
        assert blindplay.cmd_act(_act('choose "Strike"')) == 1
        assert "REFUSED" in capsys.readouterr().out
    assert blindplay_shape.refusal_streak() == 2
    assert blindplay.cmd_act(_act('choose "Strike"')) == 1
    assert "REFUSAL STOP: 3 commands in a row" in capsys.readouterr().out
    assert blindplay.cmd_act(_act("proceed")) == 2
    assert len(posted) == 1


def test_a_fight_overlay_is_not_a_screen_change(lane, capsys):
    screen, posted = lane
    blindplay.screen_page(combat_state())
    assert blindplay.cmd_act(_act("end turn")) == 0
    # A discard or choose-one prompt opens over the fight: the queued pick
    # goes through.
    screen["now"] = card_select_state()
    assert blindplay.cmd_act(_act('choose "Coral Guard"')) == 0, \
        capsys.readouterr().out
    assert len(posted) == 2
    # And the fight it opened over is still the fight.
    screen["now"] = combat_state()
    assert blindplay.cmd_act(_act("end turn")) == 0, capsys.readouterr().out
    assert len(posted) == 3


def test_room_of_groups_overlays_and_the_card_offer():
    assert blindplay_shape.room_of("monster") == "fight"
    assert blindplay_shape.room_of("boss") == "fight"
    assert blindplay_shape.room_of("hand_select") == ""
    assert blindplay_shape.room_of("card_reward") == "rewards"
    assert blindplay_shape.room_of("rewards") == "rewards"
    assert blindplay_shape.room_of("map") == "map"


def test_a_stale_mark_does_not_skip(lane):
    blindplay_shape.mark_sent("end turn", "fight", now=0.0)
    assert blindplay_shape.screen_changed_after("rewards", now=1.0) == \
        "end turn"
    late = blindplay_shape.REFUSAL_MARK_TTL_S + 1.0
    assert blindplay_shape.screen_changed_after("rewards", now=late) is None


def test_reset_refusals_lifts_the_stop(lane, capsys):
    for _ in range(3):
        blindplay_shape.count_refusal()
    blindplay_shape.mark_refusal("board", 'play "Strike"', "no such card")
    blindplay_shape.mark_sent("end turn", "fight")
    assert blindplay_shape.refusal_streak() == 3
    # The coordinator names the lane; the seat's environment is not needed.
    assert blindplay.main(["reset-refusals", "--lane", "lane3"]) == 0
    out = capsys.readouterr().out
    assert "lane 3 before: streak 3 of 3, refusal mark set" in out
    assert "lane 3 after:  streak 0 of 3, refusal mark none" in out
    assert blindplay_shape.refusal_streak() == 0
    assert blindplay_shape.pending_refusal("board") is None
    assert blindplay_shape.screen_changed_after("rewards") is None


def test_new_seat_clears_its_own_lanes_streak(lane, capsys):
    """2026-10-16: a fresh seat taking over a stopped run inherited the stop
    (twice) until the coordinator cleared the streak by hand. `new-seat`
    now clears it for the lane GITS_LANE names, and no other lane's."""
    for _ in range(3):
        blindplay_shape.count_refusal()
        blindplay_shape.count_refusal("4")
    assert blindplay_shape.refusal_streak() == 3
    assert blindplay.main(["new-seat"]) == 0
    assert "lane 3" in capsys.readouterr().out
    assert blindplay_shape.refusal_streak() == 0
    assert blindplay_shape.refusal_streak("4") == 3
    blindplay_shape.clear_refusal_streak("4")
