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
           tail: str = "") -> dict:
    return _status(
        f"Sakura {slot}",
        f"Level {level}. At the end of your turn it strikes a random enemy "
        f"for {strike} Electro damage.{tail} Strikes left: {turns}.",
        level, "Counter")


def yae_state(badges=((1, 3, 5, 1), (2, 2, 4, 2), (3, 1, 3, 3)),
              lure_on: int | None = None, annotate: int = 0,
              character: str = "Yae Miko", rite: str | None = None) -> dict:
    state = json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))["state"]
    p = state["player"]
    p["character"] = character
    p["status"] = [_badge(*b) for b in badges]
    if rite:
        p["status"].append(_status(f"Rite: {rite}", "Each Sakura strike ...",
                                   1, "Single"))
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
                        "strikes, oldest first.")
    assert lines[1] == "- Sakura 1: Level 3, strikes for 5, 1 strike left."
    assert lines[2] == "- Sakura 2: Level 2, strikes for 4, 2 strikes left."
    assert lines[3] == "- Sakura 3: Level 1, strikes for 3, 3 strikes left."
    assert lines[-1] == "- Annotated cards in your hand: 0."


def test_the_rite_and_a_sakuras_annotation_print_in_the_block():
    state = yae_state(badges=((1, 1, 6, 2, " [gold]Red Ink[/gold] makes its "
                               "strike 3 bigger."),), rite="Warding")
    lines = _block(blindplay.observe(state))
    assert lines[1] == ("- Rite: Warding. Each strike gives you its number "
                        "in Block.")
    assert lines[2] == ("- Sakura 1: Level 1, strikes for 6, 2 strikes left, "
                        "Red Ink.")
    assert "Rite: Warding" not in blindplay.observe(state).split(
        "## Your shrine")[0]


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
