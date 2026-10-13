"""Small BACKLOG close-outs, 2026-10-13: one pin per fixed line."""

from __future__ import annotations

from tier0.tests.test_kokomi_round2_seat_page import bundle_select_state
from understudy import blindplay


# Seat page: `choose` printed "Took: X" before the bridge refused it.
def test_a_refused_choice_prints_the_refusal_and_no_took_line():
    res = blindplay.act(bundle_select_state(), 'choose "Call to Arms"')
    refusal = {"status": "error", "error": "The scene is still being told"}
    lines = blindplay.answer_lines(res, None, refusal)
    assert not any(line.startswith("Took") for line in lines)
    assert any("still being told" in line for line in lines)


def test_an_accepted_choice_still_prints_what_was_taken():
    res = blindplay.act(bundle_select_state(), 'choose "Call to Arms"')
    lines = blindplay.answer_lines(res, None, {"status": "ok"})
    assert lines[0].startswith("Took: Call to Arms")


# The card-distinctness lint failed locally with `ModuleNotFoundError: tier0`.
def test_the_distinctness_gate_runs_as_a_script_without_pythonpath():
    import os
    import subprocess
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    out = subprocess.run(
        [sys.executable, str(root / "tools" / "card_distinctness_report.py"),
         "--gate"], cwd=root, env=env, capture_output=True, text=True,
        timeout=300)
    assert "ModuleNotFoundError" not in out.stderr, out.stderr[-2000:]


# Soak: `_escape` answered an owing Crystal Sphere with a refused proceed.
def test_soak_spends_an_owed_divination_before_leaving_the_sphere():
    from understudy import soak
    owing = {"state_type": "crystal_sphere", "crystal_sphere": {
        "can_proceed": False, "tool": "small", "can_use_small_tool": True,
        "clickable_cells": [{"x": 2, "y": 3}]}}
    want = {"action": "crystal_sphere_click_cell", "x": 2, "y": 3}
    assert soak._escape(owing) == want
    assert soak._mechanical_action(owing) == want
    done = {"state_type": "crystal_sphere",
            "crystal_sphere": {"can_proceed": True}}
    assert soak._escape(done) == {"action": "crystal_sphere_proceed"}


# EB-802: a two-lane frame that is not `complete` fails the run.
def test_two_lane_frames_refuse_an_incomplete_frame():
    from understudy import twolane_frames
    whole = {"lane": "lane1", "complete": True}
    clipped = {"lane": "lane2", "complete": False, "complete_note": "clip"}
    assert twolane_frames.verdict([whole, whole]) == 0
    assert twolane_frames.verdict([whole, clipped]) == 1
    assert twolane_frames.verdict([{"lane": "lane1"}]) == 1


# A Plan with no living enemy to aim at printed "no enemy lost HP", like a miss.
def test_a_plan_whose_target_was_already_dead_says_so():
    from tier0.tests.test_understudy_blindplay import (morning_of,
                                                       plans_combat_state)
    blindplay.forget_fight()
    page = blindplay.render(blindplay.observation(plans_combat_state(
        morning_of({"card": "Ambush", "number": None,
                    "line": "Bake-Kurage: Ambush", "on_play": False,
                    "moved": [], "no_target": True}))))
    assert "its target was already dead" in page
    assert "no enemy lost HP" not in page


# The Decimillipede brief said 25 HP; co-op scales the Reattach heal.
def test_the_decimillipede_brief_names_the_co_op_reattach_heal():
    from understudy import blindplay_enemies
    assert "60 with two players" in blindplay_enemies._DECIMILLIPEDE


# Owl Magistrate's "Soar" had no definition on the page.
def test_the_owl_magistrate_brief_defines_soar():
    from understudy import blindplay_enemies, qa_packet
    name, brief = blindplay_enemies.ENEMY_BRIEFS["OWL_MAGISTRATE"]
    assert name == "Owl Magistrate" and "Soar halves" in brief
    assert not qa_packet.leaks(brief)
