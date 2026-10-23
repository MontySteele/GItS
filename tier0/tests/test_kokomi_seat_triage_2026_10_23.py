"""Kokomi seat triage (2026-10-23): the seat page's halves.

- Kelp Wall+'s no-attack warning says what its flat bonus deals (the wire's
  `counter_deals`), not "deals 0".
- Following Current's hit after each Plan is one line under the Plan list.
- A hand chooser offers only the cards it lists: `choose` of a hand card it
  does not list is refused by name, never posted at another card's index.
- A `choose` chained after the play that opened its chooser is not hidden by
  the "a choice opened since your last look" skip.
- Notes: Grand Design's chooser, Intangible on the Plan panel, Mend's 0.

The C# halves (the strip caption, `counter_deals`) are pinned in
`klee-mod/KleeTests/Prototype/KokomiSeatTriageTests.cs`.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""
from __future__ import annotations

import copy

from understudy import blindplay, blindplay_faces, blindplay_shape
from understudy.blindplay_board import _screen_cards
from understudy.blindplay_render import (GRAND_DESIGN_CHOOSER_NOTE,
                                         following_current_lines, render)

from tier0.tests.test_kokomi_review_r6_2026_10_14 import SCULPTOR, _page
from tier0.tests.test_refusal_changed_under_the_seat import (  # noqa: F401
    _act, _hand_of, _observe, _sting, lane)
from tier0.tests.test_understudy_blindplay import _past_lethal_state


# ---- 1. Kelp Wall+'s warning -------------------------------------------------

def test_kelp_wall_plus_warning_names_its_flat_bonus():
    lines = _page([{"name": "Kelp Wall+", "clauses": 1,
                    "needs_attack": "blocked", "counter_deals": 4,
                    "live": "No enemy intends to attack: deals 4"}],
                  enemies=[SCULPTOR])
    assert ("     - Sculptor does not intend to attack: Kelp Wall+'s Plan "
            "deals 4.") in lines


def test_base_kelp_wall_and_an_older_bridge_still_say_deals_0():
    lines = _page([{"name": "Kelp Wall", "clauses": 1,
                    "needs_attack": "blocked",
                    "live": "No enemy intends to attack"}],
                  enemies=[SCULPTOR])
    assert ("     - Sculptor does not intend to attack: Kelp Wall's Plan "
            "deals 0.") in lines


# ---- 2. Following Current ----------------------------------------------------

def _you(stacks):
    return {"powers": [{"name": "Following Current", "stacks": stacks}]}


def test_following_current_is_one_line_under_the_plans():
    queue = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    assert following_current_lines(_you(4), queue, False) == [
        "- Following Current adds 4 Hydro after each Plan (3 Plans: 12 "
        "more)."]
    # Nereid's Ascension carries the first Plan out twice.
    assert following_current_lines(_you(4), queue[:1], True) == [
        "- Following Current adds 4 Hydro after each Plan (2 Plans: 8 "
        "more)."]
    assert following_current_lines(_you(4), [], False) == []
    assert following_current_lines({"powers": []}, queue, False) == []


def test_the_plan_page_prints_following_current():
    state = _past_lethal_state(queue=[{"name": "Kurage's Oath",
                                       "clauses": 1}], hp=40)
    state = copy.deepcopy(state)
    state["player"].setdefault("status", []).append(
        {"id": "FOLLOWING_CURRENT_POWER", "name": "Following Current",
         "amount": 3, "type": "Buff",
         "description": "Whenever a Plan is carried out, the Bake-Kurage "
                        "deals 3 Hydro damage."})
    lines = render(blindplay.observation(state)).splitlines()
    assert ("- Following Current adds 3 Hydro after each Plan (1 Plan: 3 "
            "more).") in lines


# ---- 3 and 4. A hand chooser that lists part of the hand --------------------

def _card(name, text, **over):
    return _sting(**dict({"id": name.upper().replace(" ", "_"),
                          "name": name, "description": text,
                          "cost": "0", "type": "Skill",
                          "target_type": "Self"}, **over))


def _grand_design_chooser(hand, listed):
    state = copy.deepcopy(_hand_of(hand))
    state["state_type"] = "hand_select"
    state["hand_select"] = {
        "mode": "simple_select", "prompt": "Choose up to 3 cards to plan.",
        "cards": [dict(c, index=i) for i, c in enumerate(listed)],
        "can_confirm": True}
    return state


HAND = [_card("Grand Design", "Plan up to 3 cards from your Hand."),
        _card("Tidal Surge", "Deal 9 damage.", type="Attack"),
        _card("Kelp Wall", "Plan: deal the damage you blocked.")]


def test_choose_of_an_unlisted_hand_card_is_refused_by_name(lane, capsys):
    screen, posted = lane
    screen["now"] = _hand_of(HAND)
    capsys.readouterr()
    assert blindplay.cmd_observe(_observe()) == 0
    assert blindplay.cmd_act(_act('play "Grand Design"')) == 0, \
        capsys.readouterr().out
    assert len(posted) == 1
    # The chooser opened mid-batch and lists Kelp Wall only.
    screen["now"] = _grand_design_chooser(HAND[1:], [HAND[2]])
    capsys.readouterr()
    assert blindplay.cmd_act(_act('choose "Tidal Surge"')) == 1
    out = capsys.readouterr().out
    assert "REFUSED: 'Tidal Surge' is not offered on this chooser." in out, out
    assert "Not sent: a choice opened" not in out
    assert len(posted) == 1, "nothing was posted at another card's index"
    assert blindplay_shape.refusal_streak() == 1
    # The listed card still goes through.
    assert blindplay.cmd_act(_act('choose "Kelp Wall"')) == 0, \
        capsys.readouterr().out
    assert posted[-1][1:] == ("combat_select_card", {"card_index": 0})


def test_an_empty_hand_chooser_offers_nothing():
    state = _grand_design_chooser(HAND, [])
    assert _screen_cards(state) == []
    res = blindplay.act(state, 'choose "Tidal Surge"')
    assert not res["ok"]
    assert res["refusal"].startswith(
        "'Tidal Surge' is not offered on this chooser.")


def test_a_play_refused_on_a_fresh_chooser_is_still_skipped(lane, capsys):
    """The Furina skip stands for every verb but `choose`."""
    screen, posted = lane
    screen["now"] = _hand_of(HAND)
    capsys.readouterr()
    assert blindplay.cmd_observe(_observe()) == 0
    assert blindplay.cmd_act(_act('play "Grand Design"')) == 0
    screen["now"] = _grand_design_chooser(HAND[1:], [HAND[2]])
    capsys.readouterr()
    assert blindplay.cmd_act(_act('play "Tidal Surge"')) == 1
    assert "Not sent: a choice opened" in capsys.readouterr().out
    assert blindplay_shape.refusal_streak() == 0


# ---- 5. Notes ------------------------------------------------------------------

def test_grand_designs_chooser_says_what_it_lists():
    state = _grand_design_chooser(HAND[1:], [HAND[2]])
    page = render(blindplay.observation(state))
    assert GRAND_DESIGN_CHOOSER_NOTE in page.splitlines()
    assert GRAND_DESIGN_CHOOSER_NOTE == (
        "*Grand Design lists only cards with a Plan line, plus Basic Strike "
        "and Defend; other cards in your hand are not offered.*")


def test_the_plan_panel_says_intangible_takes_1():
    assert ("A Plan meets the enemy as it is when it lands: an Intangible "
            "enemy takes 1 per hit.") in blindplay.PLAN_WRITTEN_NUMBER_NOTE


def test_a_mend_that_lands_0_says_why():
    face = blindplay_faces._card_face(
        {"name": "The Moon", "description": "Plan: Mend 6 (0 will land)."})
    assert face["text"] == ("Plan: Mend 6 (0 will land: you are at or above "
                            "the HP you started this combat with).")
    # A Mend that lands something is left as the game printed it.
    face = blindplay_faces._card_face(
        {"name": "The Moon", "description": "Plan: Mend 6 (2 will land)."})
    assert face["text"] == "Plan: Mend 6 (2 will land)."
