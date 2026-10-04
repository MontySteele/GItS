"""FURINA, THE STAGE -- THE SUPPORTING-POOL SEAT ROUND (2026-09-26,
0.2.3859+proto): the sim's pins and the seat page's.

Records (gitignored): `review/qa/seats-2026-09-26/furina-*.md`. The mod's
pins are `klee-mod/KleeTests/Prototype/FurinaSeatDefects20260926Tests.cs`.

NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

from understudy import blindplay, blindplay_faces, qa_packet
from understudy.blindplay_notes import ARM_KEYWORDS, keyword_notes
from understudy.blindplay_render import (_render_stage_forecast,
                                         _render_stage_log)
from understudy.blindplay_shape import sphere_reveal_action

# The sim's pins of this round (A Five-Century Act's resting returnee, its
# order against the regen) left with the bars: the re-founded Stage
# (review/active/furina-refounding-2026-10-03.md) has no resting rule, and a
# returner acts at the end of the turn with everyone
# (`tier0/tests/test_furina_stage.py`).


# ---- the page's stage block --------------------------------------------------

def _seat(member, name, index, key):
    return {"member": member, "name": name, "long_name": name, "seat": index,
            "entity_id": None, "key": key, "guest": False, "price": 0}


def _beat(event, member, name, seat=0, fanfare=0, moved=0, key=None,
          standing=None, source=""):
    return {"event": event, "member": member, "name": name, "seat": seat,
            "key": key, "fanfare": fanfare, "moved": moved, "why": "",
            "target": "", "combat_id": "", "standing": standing,
            "source": source}


# (The resting returnee and the rotation lines left with the re-founding,
# 2026-10-04: no rule makes a performer sit out, and no beat rotates a bar.)


def test_every_act_prints_and_a_repeat_says_again():
    """Lane 1: "one 'Usher acted' with two Ushers on stage", and Full House's
    second act "not printed though its damage landed". Two acts in a row read
    the same, so twins name their seats and a repeat says "again"."""
    seats = [_seat("usher", "Usher", 0, 1), _seat("usher", "Usher", 1, 2)]
    twins = _render_stage_log({"seats": seats, "log": [
        _beat("act", "usher", "Usher", 0, 5, 4, key=1),
        _beat("act", "usher", "Usher", 1, 5, 4, key=2)]})
    assert twins == ["  - **Usher** (seat 1) acted: Furina gains 4 Block.",
                     "  - **Usher** (seat 2) acted: Furina gains 4 Block."]
    full_house = _render_stage_log({"seats": seats[:1], "log": [
        _beat("act", "usher", "Usher", 0, 5, 4, key=1),
        _beat("act", "usher", "Usher", 0, 5, 4, key=1)]})
    assert full_house == ["  - **Usher** acted: Furina gains 4 Block.",
                          "  - **Usher** acted again: Furina gains 4 Block."]


def test_the_acts_forecast_counts_a_repeated_act():
    """Full House's repeats are one forecast row with its count."""
    forecast = {"fanfare_after": 2, "block": 0, "acts": [
        {"name": "Crabaletta", "kind": "damage", "amount": 5, "element": "",
         "target": "a random enemy", "times": 2, "price": 0,
         "skips": False}]}
    lines = _render_stage_forecast(forecast)
    assert lines[1] == "  - **Crabaletta**: 5 damage to a random enemy, twice"
    assert len(lines) == 3


def test_a_move_no_card_made_names_the_power_behind_it():
    """Lane 4: an Usher joined at turn start "with no card named"."""
    lines = _render_stage_log({"seats": [_seat("usher", "Usher", 0, 1)],
                               "log": [
        _beat("arrive", "usher", "Usher", 0, 3, key=1, standing=1,
              source="All the World's a Stage"),
        _beat("gain", "usher", "Usher", -1, 5, 2,
              source="Season Tickets")]})
    assert lines == [
        "  - **Usher** joined the stage from All the World's a Stage.",
        "  - You gained 2 Fanfare from Season Tickets: 3 → 5."]


def test_the_wire_source_crosses_to_the_observation():
    from understudy.blindplay_board import furina_stage as stage_block
    stage = stage_block({"furina_stage": {
        "live": True,
        "seats": [{"member": "usher", "name": "Gentilhomme Usher",
                   "seat": 0}],
        "log": [{"event": "arrive", "member": "usher", "seat": 0,
                 "fanfare": 1, "source": "Thunderous Applause"}]}})
    assert stage["log"][0]["source"] == "Thunderous Applause"


# ---- 5 and 6. The glossary --------------------------------------------------

def _reward(*faces):
    return {"screen": "card_reward", "character": "Furina",
            "stage_arm": True,
            "offers": [{"title": t, "text": x} for t, x in faces]}


def test_star_billings_reward_screen_defines_guest_star():
    names = [r["name"] for r in keyword_notes(_reward(
        ("Star Billing+", "Whenever a Guest Star joins the stage, draw 2 "
                          "cards.")))]
    assert "Guest Star" in names


def test_bring_the_house_down_is_glossed_by_its_own_words():
    """The re-founding (2026-10-04): its face reads the Fanfare she spent
    this turn, so the Fanfare row defines it."""
    names = [r["name"] for r in keyword_notes(_reward(
        ("Bring the House Down", "Deal damage to ALL enemies equal to 3 "
                                 "times the Fanfare you spent this turn.")))]
    assert "Fanfare" in names
    assert "back performer" not in names
    # A real Spend mode still is.
    names = [r["name"] for r in keyword_notes(_reward(
        ("Curtain Rise", "Deal 8 damage. Spend 3: deal 14 instead.")))]
    assert "Spend" in names


# ---- 7. The Crystal Sphere --------------------------------------------------

def _sphere(can_proceed=False, tool="big", cells=((0, 0), (1, 0)),
            left="3 Divinations remain"):
    """The wire's shape (`McpMod.StateBuilder.BuildCrystalSphereState`)."""
    return {"state_type": "crystal_sphere",
            "crystal_sphere": {
                "instructions_title": "Crystal Sphere",
                "grid_width": 2, "grid_height": 1,
                "cells": [{"x": x, "y": y, "is_hidden": True,
                           "is_clickable": True} for x, y in cells],
                "clickable_cells": [{"x": x, "y": y} for x, y in cells],
                "revealed_items": [{"item_type": "CrystalSphereRelicItem",
                                    "x": 5, "y": 5, "width": 1, "height": 1,
                                    "is_good": True}],
                "tool": tool, "can_use_big_tool": True,
                "can_use_small_tool": True,
                "divinations_left_text": left,
                "can_proceed": can_proceed}}


def test_the_sphere_offers_reveal_while_it_owes_divinations():
    """Lanes 1 and 2: `leave` was offered and refused five times over while
    "3 Divinations remain". While they remain the page offers `reveal`."""
    state = _sphere()
    obs = blindplay.observation(state)
    assert obs["commands"] == ["reveal"]
    page = blindplay.render(obs)
    assert "3 Divinations remain" in page and "`reveal`" in page
    # Blind: nothing about what a cell hides crosses.
    assert "CrystalSphereRelicItem" not in page
    res = blindplay.act(state, "reveal")
    assert not res["refusal"]
    assert res["post"] == {"action": "crystal_sphere_click_cell",
                           "x": 0, "y": 0}
    refused = blindplay.act(state, "leave")
    assert refused["refusal"] and "reveal" in refused["refusal"]


def test_reveal_selects_a_tool_first_where_none_is_selected():
    assert sphere_reveal_action(_sphere(tool="none")["crystal_sphere"]) == {
        "action": "crystal_sphere_set_tool", "tool": "big"}


def test_the_sphere_offers_leave_once_the_game_lets_the_run_go_on():
    """And the path lane 2 met after the Sphere's reward screen: back on the
    sphere with `can_proceed`, `leave` is the verb and it posts proceed."""
    state = _sphere(can_proceed=True, cells=(), left="0 Divinations remain")
    obs = blindplay.observation(state)
    assert obs["commands"] == ["leave"]
    assert blindplay.act(state, "leave")["post"] == {
        "action": "crystal_sphere_proceed"}
    assert blindplay.act(state, "reveal")["refusal"]


def test_reveal_off_the_sphere_is_refused():
    assert blindplay.act({"state_type": "map", "map": {}}, "reveal")[
        "refusal"]


# ---- 9a and 17. The cost line -----------------------------------------------

def test_an_upgrade_that_leaves_the_cost_alone_does_not_explain_a_free_card():
    """Lane 3: Spirited Aria+ free under Mummified Hand read "because this
    copy is upgraded -- that is permanent"; its upgrade moves damage."""
    note = qa_packet.cost_note({"cost": "0", "printed_cost": 1,
                                "upgraded": True, "upgrade_cost_delta": 0})
    assert "because this copy is upgraded" not in note
    assert ("Its upgrade does not change its cost, so the cut is this turn's "
            "board") in note


def test_an_upgrade_that_cuts_the_cost_is_named_without_a_duration():
    """Lane 2: Bellows' copies read "that is permanent" and last a combat."""
    note = qa_packet.cost_note({"cost": "0", "printed_cost": 1,
                                "upgraded": True, "upgrade_cost_delta": -1})
    assert note == ("The cost printed on this card is 1; it is showing 0 "
                    "here, because this copy is upgraded.")


# ---- 8. A freeze from the enemies' own turn ------------------------------

def _frozen_board(powers, state_type="monster"):
    return {"state_type": state_type}, {
        "enemies": [{"name": "Devoted Sculptor", "powers": powers}]}


def test_a_carried_frozen_row_says_it_has_worn_off():
    from understudy.blindplay_render import _frozen_clause
    row = {"reaction": "Frozen", "target": "Devoted Sculptor",
           "carried": True}
    obs, board = _frozen_board([{"name": "Ritual"}])
    assert "worn off" in _frozen_clause(row, obs, board)
    obs, board = _frozen_board([{"name": "Frozen"}])
    assert _frozen_clause(row, obs, board) == ""
    # A boss is never Frozen, so nothing wears off.
    obs, board = _frozen_board([], "boss")
    assert _frozen_clause(row, obs, board) == ""


# ---- 9b. No enemies on the screen -------------------------------------------

def test_a_screen_with_no_enemies_does_not_claim_none_wears_an_aura():
    from understudy.blindplay_notes import _no_reaction_clause
    text = _no_reaction_clause({"Anemo"}, aura=False, board_shown=False)
    assert "no enemy is wearing one" not in text
    assert "this screen does not show the enemies" in text


# ---- 16. Enemy letters -------------------------------------------------------

def test_a_hatching_egg_does_not_reletter_the_ovicopter():
    """Lane 2: the Ovicopter went from [A] to [C] when its eggs hatched: an
    id the fight had lettered came back under another name, and the clash
    wiped the fight's letters."""
    blindplay_faces.forget_fight()
    try:
        first = [{"combat_id": 1, "name": "Ovicopter", "hp": 91,
                  "max_hp": 128},
                 {"combat_id": 2, "name": "Tough Egg", "hp": 12, "max_hp": 12},
                 {"combat_id": 3, "name": "Tough Egg", "hp": 12, "max_hp": 12}]
        blindplay_faces._enemy_names(first, 2)
        assert blindplay_faces._enemy_handles(first) == ["A", "B", "C"]
        hatched = [{"combat_id": 2, "name": "Hatchling", "hp": 9, "max_hp": 9},
                   {"combat_id": 3, "name": "Hatchling", "hp": 9, "max_hp": 9},
                   {"combat_id": 1, "name": "Ovicopter", "hp": 55,
                    "max_hp": 128}]
        blindplay_faces._enemy_names(hatched, 3)
        handles = blindplay_faces._enemy_handles(hatched)
        assert handles[2] == "A"
        assert handles[:2] == ["D", "E"]
        assert blindplay_faces.enemy_replacements(hatched)[:2] == ["B", "C"]
    finally:
        blindplay_faces.forget_fight()


def test_a_body_whose_maximum_moves_keeps_its_letter():
    blindplay_faces.forget_fight()
    try:
        board = [{"combat_id": 1, "name": "Ovicopter", "hp": 91,
                  "max_hp": 128}]
        blindplay_faces._enemy_names(board, 2)
        grown = [{"combat_id": 1, "name": "Ovicopter", "hp": 91,
                  "max_hp": 140}]
        blindplay_faces._enemy_names(grown, 3)
        assert blindplay_faces._enemy_handles(grown) == ["A"]
        assert blindplay_faces.enemy_replacements(grown) == [""]
    finally:
        blindplay_faces.forget_fight()


def test_a_new_fight_on_round_one_still_letters_afresh():
    blindplay_faces.forget_fight()
    try:
        blindplay_faces._enemy_names(
            [{"combat_id": 1, "name": "Ovicopter", "hp": 5, "max_hp": 128},
             {"combat_id": 2, "name": "Tough Egg", "hp": 5, "max_hp": 12}], 4)
        nxt = [{"combat_id": 2, "name": "Slug", "hp": 20, "max_hp": 20}]
        blindplay_faces._enemy_names(nxt, 1)
        assert blindplay_faces._enemy_handles(nxt) == ["A"]
    finally:
        blindplay_faces.forget_fight()


# ---- 18 and 22. (Damage no enemy dealt and the intent split left with the
# re-founding, 2026-10-04: performers take no hits, and the forecast is the
# acts', not the enemies'.)


# ---- 24. (Wriothesley's "always front" left with the re-founding.) ---


# ---- 25. An every-N-cards counter ----------------------------------------

def test_withering_presence_says_its_count_carries_over():
    from understudy.blindplay_render import _render_power
    line = _render_power({"name": "Withering Presence", "stacks": 1,
                          "kind": "buff",
                          "text": "Every 6 cards you play, add a Wither to "
                                  "your hand."}, "- ")
    assert line.endswith("The number is the cards left before the next one, "
                         "and it carries over from turn to turn.")
    other = _render_power({"name": "Strength", "stacks": 3, "kind": "buff",
                           "text": "Increases attack damage by 3."}, "- ")
    assert "carries over" not in other


# ---- 27. Numbered potions --------------------------------------------------

def test_a_numbered_potion_resolves_like_a_numbered_card():
    """The Solo seat: `use potion "Vulnerable Potion (1)"` was refused with
    two on the belt, and the bare name worked."""
    state = {"state_type": "monster",
             "battle": {"round": 1, "enemies": [
                 {"name": "Nibbit", "hp": 20, "max_hp": 20, "block": 0,
                  "entity_id": "7", "combat_id": 1, "status": [],
                  "intents": []}]},
             "player": {"hp": 30, "max_hp": 60, "block": 0, "energy": 3,
                        "hand": [], "relics": [], "status": [],
                        "potions": [
                            {"name": "Vulnerable Potion", "slot": 0,
                             "target_type": "AnyEnemy"},
                            {"name": "Vulnerable Potion", "slot": 2,
                             "target_type": "AnyEnemy"}]}}
    blindplay_faces.forget_fight()
    try:
        second = blindplay.act(state,
                               'use potion "Vulnerable Potion (2)" on "Nibbit"')
        assert not second["refusal"], second["refusal"]
        assert second["post"]["slot"] == 2
        bare = blindplay.act(state, 'use potion "Vulnerable Potion" on "Nibbit"')
        assert not bare["refusal"] and bare["post"]["slot"] == 0
        dropped = blindplay.act(state, 'drop potion "Vulnerable Potion (1)"')
        assert not dropped["refusal"] and dropped["post"]["slot"] == 0
    finally:
        blindplay_faces.forget_fight()


# ---- 29. Lyney, in the glossary --------------------------------------------

def test_lyneys_row_is_the_new_act():
    # The re-founding (2026-10-04): his badge's sentence.
    assert ARM_KEYWORDS["Lyney"] == (
        "The first Cue card you play each turn costs 0. Act: pay 1 Fanfare to "
        "add a Trick to your hand.")
