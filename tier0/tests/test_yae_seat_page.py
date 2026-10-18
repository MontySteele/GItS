"""YAE MIKO: what a blind seat reads on her combat page (built 2026-10-13).

Her turn turns on her shrine: how many Sakura stand, each one's Level, what
it strikes for and how many strikes it has left (the badge "Sakura N" and
its sentence, `SakuraBadgePower`), which enemy Foxfire Lure aimed them at,
and how many Annotated cards she holds (each hand face's `enchantment`, the
bridge's own field). The page prints them in one block above the hand.

The fixture is the recorded Kokomi combat turn re-dressed as hers, Varka's
seat-page test's arrangement: it proves the renderer on a real wire's shape,
never the wire itself -- a live capture is the first seat round's.
"""

from __future__ import annotations

import copy
import json

import pytest

from understudy import blindplay, blindplay_board
from tier0.tests.test_varka_seat_page import RECORDED_COMBAT, _status


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


def _badge(slot: int, level: int, strike: int, turns: int,
           tail: str = "", kind: str = "Sakura",
           planted: int | None = None) -> dict:
    """`SakuraBadgePower`'s sentence (review r3): the kind, the Level and
    the Level it was planted at, the action, the turns left."""
    action = {"Sakura": f"Strikes a random enemy for {strike} Electro damage.",
              "Foxfire Sakura": f"Hits ALL enemies for {strike} Electro damage.",
              "Kitsune Sakura": f"You gain {strike} Block."}[kind]
    return _status(
        f"Sakura {slot}",
        f"{kind}, Level {level}, planted at {planted or level}. {action}"
        f"{tail} Turns left: {turns}.",
        level, "Counter")


# The Sakura Levels paper (2026-10-17): a Sakura strikes for 1 + 2 per Level.
def yae_state(badges=((1, 3, 7, 1), (2, 2, 5, 2), (3, 1, 3, 3)),
              lure_on: int | None = None, annotate: int = 0,
              character: str = "Yae Miko") -> dict:
    state = json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))["state"]
    p = state["player"]
    p["character"] = character
    p["status"] = [_badge(*b) for b in badges]
    for card in p["hand"][:annotate]:
        card["enchantment"] = {"id": "KLEEMOD-RED_INK_ANNOTATION",
                               "name": "Red Ink",
                               "description": "This card deals 3 more damage "
                                              "and gives 3 more Block.",
                               "amount": 1, "shows_amount": False}
    template = state["battle"]["enemies"][0]
    enemies = []
    for i in range(2):
        enemy = copy.deepcopy(template)
        enemy["name"] = f"Hilichurl {i + 1}"
        enemy["combat_id"] = str(100 + i)
        enemy["entity_id"] = f"HILICHURL_{i}"
        enemy["status"] = ([_status("Foxfire Lure",
                                    "This turn, Yae's Sakura strike this "
                                    "enemy.", 1, "Single")]
                           if lure_on == i else [])
        enemies.append(enemy)
    state["battle"]["enemies"] = enemies
    return state


def _block(page: str) -> list[str]:
    assert "## Your shrine" in page, page
    body = page.split("## Your shrine", 1)[1].strip().split("\n\n")[0]
    return body.splitlines()


def test_the_page_prints_every_sakura_oldest_first():
    lines = _block(blindplay.observe(yae_state()))
    assert lines[0] == ("- Sakura: 3 of 3. At the end of your turn each "
                        "acts, oldest first.")
    assert lines[1] == ("- Sakura 1: Sakura, Level 3 (planted at 3), strikes "
                        "an enemy for 7, 1 turn left.")
    assert lines[2] == ("- Sakura 2: Sakura, Level 2 (planted at 2), strikes "
                        "an enemy for 5, 2 turns left.")
    assert lines[3] == ("- Sakura 3: Sakura, Level 1 (planted at 1), strikes "
                        "an enemy for 3, 3 turns left.")
    # Review r3: full, so the next plant makes the oldest act first.
    # Yae review r5, item 5: the hover's sentences.
    # The Sakura Levels paper (2026-10-17): Levels carry over on a replace.
    assert lines[4] == ("- Shrine full: planting makes the Sakura closest "
                        "to withering act. Same kind: it refreshes and gains "
                        "a Level. Other kind: it withers, and the new one "
                        "takes its Level if higher.")
    assert lines[-1] == "- Annotated cards in your hand: 0."


def test_a_sakuras_annotation_prints_in_the_block_and_no_rite_line():
    # Shrine r2 (2026-10-14): the Rite line left with the Rite.
    state = yae_state(badges=((1, 1, 6, 2, " [gold]Red Ink[/gold]: +3."),))
    lines = _block(blindplay.observe(state))
    assert lines[1] == ("- Sakura 1: Sakura, Level 1 (planted at 1), strikes "
                        "an enemy for 6, 2 turns left, Red Ink.")
    assert not any("Rite" in line for line in lines)


# The pool to 78, pick 2 (a): distinct Annotations coexist on a Sakura. The
# badge sentence flags each in a fixed order (Red Ink, Deadline Extension,
# Fox Fire); the wire's `player.yae_shrine.sakura` rows give the order applied.

ALL_THREE = (" [gold]Red Ink[/gold]: +3. [gold]Deadline Extension[/gold]: no "
             "wither. [gold]Fox Fire[/gold]: +3 to a random enemy.")


def test_a_sakura_lists_every_annotation_it_carries():
    state = yae_state(badges=((1, 1, 6, 2, ALL_THREE), (2, 1, 3, 3)))
    lines = _block(blindplay.observe(state))
    assert lines[1] == ("- Sakura 1: Sakura, Level 1 (planted at 1), strikes "
                        "an enemy for 6, 2 turns left, Red Ink, Deadline "
                        "Extension, Fox Fire.")
    assert lines[2] == ("- Sakura 2: Sakura, Level 1 (planted at 1), strikes "
                        "an enemy for 3, 3 turns left.")


def test_the_annotations_print_in_the_order_applied_off_the_wire():
    state = yae_state(badges=((1, 1, 6, 2, ALL_THREE),
                              (2, 1, 6, 3, " [gold]Red Ink[/gold]: +3."
                                           " [gold]Fox Fire[/gold]: +3 to a "
                                           "random enemy.")))
    state["player"]["yae_shrine"] = {
        "live": True, "edits_this_combat": 5,
        "sakura": [{"slot": 1, "annotations": ["Fox Fire", "Red Ink",
                                               "Deadline Extension"]},
                   {"slot": 2, "annotations": ["Fox Fire", "Red Ink"]}]}
    shrine = blindplay_board.yae_shrine(
        state["player"], {"you": {"powers": [
            {"name": pw["name"], "text": pw["description"]}
            for pw in state["player"]["status"]]}, "enemies": []})
    assert shrine["sakura"][0]["annotations"] == [
        "Fox Fire", "Red Ink", "Deadline Extension"]
    # The old one-value field stays, the first applied.
    assert shrine["sakura"][0]["annotation"] == "Fox Fire"
    lines = _block(blindplay.observe(state))
    assert lines[1].endswith("2 turns left, Fox Fire, Red Ink, Deadline "
                             "Extension.")
    assert lines[2].endswith("3 turns left, Fox Fire, Red Ink.")


def test_the_badge_decides_which_annotations_a_stale_wire_row_adds_none():
    state = yae_state(badges=((1, 1, 6, 2, " [gold]Red Ink[/gold]: +3."),))
    state["player"]["yae_shrine"] = {
        "live": True, "edits_this_combat": 1,
        "sakura": [{"slot": 1, "annotations": ["Fox Fire", "Red Ink"]}]}
    lines = _block(blindplay.observe(state))
    assert lines[1].endswith("2 turns left, Red Ink.")


def test_her_badges_leave_the_power_list_for_the_block():
    page = blindplay.observe(yae_state())
    assert "Sakura 1 3" not in page.split("## Your shrine")[0]


def test_an_empty_shrine_still_prints_her_block():
    lines = _block(blindplay.observe(yae_state(badges=())))
    assert lines[0] == "- Sakura: none. Plant one to start your shrine."


def test_the_lure_names_its_enemy_and_annotations_are_counted():
    lines = _block(blindplay.observe(yae_state(lure_on=1, annotate=2)))
    assert "- Foxfire Lure: your Sakura strike **Hilichurl 2** this turn." in lines
    assert lines[-1] == "- Annotated cards in your hand: 2."


def test_the_hand_prints_the_annotation_beside_the_title():
    page = blindplay.observe(yae_state(annotate=1))
    hand = page.split("## Your hand", 1)[1]
    assert "(Red Ink)" in hand


def test_another_character_gets_no_shrine_block():
    state = yae_state(badges=(), character="Varka")
    assert blindplay_board.yae_shrine(
        state["player"], {"you": {"powers": []}, "enemies": [],
                          "hand": []}) is None


def test_her_option_id_and_her_display_name_fold_together():
    from understudy import embark, soak_navigate
    assert embark.option_id("yae") == "KLEEMOD-YAE"
    assert soak_navigate.character_matches("KLEEMOD-YAE", "Yae Miko")
    assert not soak_navigate.character_matches("KLEEMOD-YAE", "Varka")


def test_sakura_channeling_raises_the_count_lines_cap():
    # Designed 2026-10-14: "You can have 2 more Sakura", per copy.
    state = yae_state(badges=((1, 1, 3, 3), (2, 1, 3, 3), (3, 1, 3, 3),
                              (4, 1, 3, 3)))
    state["player"]["status"].append(_status(
        "Sakura Channeling", "You can have 2 more Sakura.", 2, "Counter"))
    lines = _block(blindplay.observe(state))
    assert lines[0] == ("- Sakura: 4 of 5. At the end of your turn each "
                        "acts, oldest first.")
    assert lines[4] == ("- Sakura 4: Sakura, Level 1 (planted at 1), strikes "
                        "an enemy for 3, 3 turns left.")
    assert not any(line.startswith("- Shrine full") for line in lines)


# ---- review r3 (ruled 2026-10-14): kinds, Levels' origin, the Masterpiece --

def test_each_sakura_shows_its_kind_and_where_its_levels_came_from():
    state = yae_state(badges=((1, 5, 6, 2, "", "Foxfire Sakura", 2),
                              (2, 3, 5, 3, "", "Kitsune Sakura", 1)))
    lines = _block(blindplay.observe(state))
    assert lines[1] == ("- Sakura 1: Foxfire Sakura, Level 5 (planted at 2, "
                        "+3 since), hits ALL enemies for 6 each, 2 turns "
                        "left.")
    assert lines[2] == ("- Sakura 2: Kitsune Sakura, Level 3 (planted at 1, "
                        "+2 since), gives you 5 Block, 3 turns left.")


def test_a_published_card_shows_its_stack_beside_its_title():
    state = yae_state()
    card = state["player"]["hand"][0]
    card["enchantment"] = {"id": "KLEEMOD-YAE_MASTERPIECE",
                           "name": "Annotated",
                           "description": "Published: Red Ink x2, Reprint. "
                                          "This combat: Footnote.",
                           "amount": 4, "shows_amount": True}
    page = blindplay.observe(state)
    hand = page.split("## Your hand", 1)[1]
    assert "(Published: Red Ink x2, Reprint. This combat: Footnote)" in hand
    assert _block(page)[-1] == "- Annotated cards in your hand: 1."


def _edit_chooser(prompt: str) -> dict:
    """SYNTHETIC, in `BuildCardSelectState`'s grid shape, with an Edit's
    prompt."""
    card = lambda i, name, text: {"index": i, "id": f"KLEEMOD-{name.upper()}",
                                  "name": name, "description": text,
                                  "cost": 1, "card_type": "Skill"}
    return {"state_type": "card_select",
            "player": {"character": "yae", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            "card_select": {"screen_type": "simple_select",
                            "closes_on_last_pick": False,
                            "prompt": prompt,
                            "can_skip": False, "can_cancel": False,
                            "preview_showing": False, "can_confirm": False,
                            "selection_known": True,
                            "cards": [card(0, "Strike", "Deal 6 damage."),
                                      card(1, "Defend", "Gain 5 Block.")]}}


def test_a_multi_card_edit_is_one_chooser_of_up_to_n():
    # Yae review r5, item 1: since #1330 a multi-card Edit is ONE chooser of
    # up to N different cards; the page no longer promises a second one.
    from understudy import blindplay_render as R
    assert R.EDIT_PROMPT_HEAD == "Choose a card to Edit"
    assert not hasattr(R, "EDIT_SECOND_CHOOSER_NOTE")
    page = blindplay.observe(_edit_chooser(
        "Choose up to 2 cards to Edit: Footnote (when played, draw 1 card)."))
    assert ("*Pick up to 2 different cards on this one screen, then "
            "confirm. Fewer, or none, is allowed.*") in page
    assert "chooser again" not in page
    one = blindplay.observe(_edit_chooser(
        "Choose a card to Edit: Footnote (when played, draw 1 card)."))
    assert "Pick up to" not in one


# Bestseller and Print Run count the cards she Edited this combat (Yae review
# r5, pick 1 (a)); no card on the board shows it, so the bridge carries it
# (`player.yae_shrine`, the mod's `YaeShrine.Snapshot`) and her block says it.

def test_the_block_prints_the_cards_edited_this_combat():
    for n in (0, 3):
        state = yae_state(annotate=1)
        state["player"]["yae_shrine"] = {"live": True, "edits_this_combat": n}
        lines = _block(blindplay.observe(state))
        assert lines[-2] == "- Annotated cards in your hand: 1."
        assert lines[-1] == f"- Cards Edited this combat: {n}."


def test_no_edits_line_when_the_wire_does_not_carry_the_count():
    for raw in (None, {}):
        state = yae_state()
        if raw is not None:
            state["player"]["yae_shrine"] = raw
        lines = _block(blindplay.observe(state))
        assert not any("Edited this combat" in line for line in lines)
