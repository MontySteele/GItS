"""KOKOMI WHOLE-RUN ROUND 2 (2026-10-10): the seat-page polish.

Record `review/records/kokomi-fullrun-round-2-2026-10-10.md`, "What changes",
item 4: `--define` also searches enemy briefings; the Neow bundle confirm
line lists every card taken; a waiting Plan line whose number the target's
Vulnerable raised says "(after Vulnerable)".
"""

from __future__ import annotations

import copy

from tier0.tests.test_understudy_blindplay import (TWO_PLANS,
                                                    bundle_select_state,
                                                    plans_combat_state)
from understudy import blindplay, blindplay_brief, blindplay_notes
from understudy.blindplay_enemies import briefs_mentioning


# --- 4a. --define reads the enemy briefings ------------------------------------

def test_define_finds_a_word_only_an_enemy_briefing_explains():
    for word in ("Sandpit", "Frantic Escape", "sandpit"):
        out = blindplay_brief.define("", word)
        assert "No definition" not in out, word
        assert "Sandpit drops by 1 each enemy turn" in out
        assert out.rstrip().endswith(blindplay_brief.OFF_SCREEN_MARK.strip())


def test_define_by_briefing_matches_whole_words_only():
    assert briefs_mentioning("Sandpit")
    assert not briefs_mentioning("Sandp")
    assert not briefs_mentioning("")
    out = blindplay_brief.define("", "Zzyzx Unheard Of")
    assert out.startswith("No definition")


# --- 4b. the bundle confirm names every card --------------------------------------

def _armed(state, bundle):
    state = copy.deepcopy(state)
    blob = state["bundle_select"]
    blob["preview_showing"] = True
    blob["can_confirm"] = True
    blob["preview_cards"] = copy.deepcopy(blob["bundles"][bundle]["cards"])
    return state


def test_choosing_a_bundle_names_every_card_in_it():
    res = blindplay.act(bundle_select_state(), 'choose "Call to Arms"')
    assert res["ok"]
    assert blindplay.taken_line(res).startswith(
        "Took: Call to Arms, Massed Volley")


def test_the_bundle_confirm_line_lists_every_card_taken():
    res = blindplay.act(_armed(bundle_select_state(), 1), "confirm")
    assert res["ok"] and res["post"] == {
        "action": "confirm_bundle_selection"}
    assert blindplay.taken_line(res).startswith(
        "Took: Crane Wing, Massed Volley")


def test_a_confirm_with_no_armed_bundle_prints_no_names():
    res = blindplay.act(bundle_select_state(), "confirm")
    assert res["ok"]
    assert blindplay.taken_line(res) == ""


# --- 4c. "(after Vulnerable)" on a waiting Plan line ------------------------------

def _waiting(after: bool | None):
    row = {"name": "Kurage's Oath", "clauses": 1, "two_line": True,
           "now_line": "Gain 6 Block.",
           "plan_line": "Deal 15 damage.", "line": "plan"}
    if after is not None:
        row["after_vulnerable"] = after
    return dict(TWO_PLANS, queue=[{"name": "Nip", "clauses": 1}, row],
                pending=2)


def test_a_plan_line_raised_by_vulnerable_says_so():
    page = blindplay.render(blindplay.observation(
        plans_combat_state(_waiting(True))))
    assert ("**Plan line**: Deal 15 damage." + blindplay_notes.AFTER_VULNERABLE
            ) in page


def test_no_mark_without_the_flag_or_on_an_older_bridge():
    for after in (False, None):
        page = blindplay.render(blindplay.observation(
            plans_combat_state(_waiting(after))))
        assert blindplay_notes.AFTER_VULNERABLE not in page
        assert "**Plan line**: Deal 15 damage. ·" in page
