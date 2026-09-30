"""VARKA, THE OATH REWORK: what a blind seat reads on his combat page.

His turn turns on three facts, all read off the wire: his current element
(the badge title, "Pyro Oath" or plain "Oath" before his first Knight), the
four Oath counts (the badge sentence "Oath: Pyro N, Hydro N, Electro N,
Cryo N."), and what a Swirl he makes pays right now. The page prints them in
one block, with each enemy's aura FRESH or SPENT beneath.

The fixture is the recorded Kokomi combat turn (`combat_state`'s file), re-
dressed as his: that proves the renderer on a real wire's shape, never the
wire itself -- a live capture is the first seat round's.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from understudy import blindplay, blindplay_board, embark, soak_navigate

REPO = Path(__file__).resolve().parents[2]
RECORDED_COMBAT = (REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                   / "observed.json")

FRESH_PYRO = ("Pyro clings to this enemy for 2 more turns. A hit of another "
              "element triggers an Elemental Reaction.")
SPENT_HYDRO = ("Spent: Anemo and Geo do nothing to it until Hydro hits it "
               "again. 1 more turn.")
PYRO_OATH_TEXT = ("Your current element is Pyro. Your Swirls deal 3 damage "
                  "to that enemy. Oath: Pyro 2, Hydro 0, Electro 1, Cryo 0.")
NO_ELEMENT_TEXT = ("You have no current element yet. "
                   "Oath: Pyro 0, Hydro 1, Electro 0, Cryo 0.")


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


def _status(name: str, text: str, amount: int = 1,
            stack: str = "Single") -> dict:
    return {"id": name.upper().replace(" ", "_"), "name": name,
            "amount": amount, "stack": stack, "type": "Buff",
            "description": text, "keywords": []}


def varka_state(badge=("Pyro Oath", PYRO_OATH_TEXT, 2),
                auras=((FRESH_PYRO, "Pyro"), (SPENT_HYDRO, "Hydro"), None),
                character="Varka") -> dict:
    """The recorded turn, as his: the Oath badge on him (title, sentence,
    amount) or none, the Fang in his relics, and one enemy per `auras` entry
    (text, element) or None for a bare body."""
    state = json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))["state"]
    p = state["player"]
    p["character"] = character
    p["status"] = ([] if badge is None else
                   [_status(badge[0], badge[1], badge[2], "Counter")])
    p["relics"] = [{"id": "KLEEMOD-BOREAS_FANG", "name": "Boreas's Fang",
                    "description": "The first time you gain Oath each "
                                   "fight, add Four Winds' Ascension to "
                                   "your hand.",
                    "counter": None, "keywords": []}]
    template = state["battle"]["enemies"][0]
    enemies = []
    for i, aura in enumerate(auras):
        enemy = copy.deepcopy(template)
        enemy["name"] = f"Hilichurl {i + 1}"
        enemy["combat_id"] = str(100 + i)
        enemy["entity_id"] = f"HILICHURL_{i}"
        enemy["status"] = ([] if aura is None else
                           [_status(f"{aura[1]} Aura", aura[0], 2,
                                    "Counter")])
        enemies.append(enemy)
    state["battle"]["enemies"] = enemies
    return state


def _block(page: str) -> list[str]:
    assert "## Your Oath" in page, page
    body = page.split("## Your Oath", 1)[1].strip().split("\n\n")[0]
    return body.splitlines()


def test_the_page_prints_his_element_his_oath_and_what_a_swirl_pays():
    page = blindplay.observe(varka_state())
    lines = _block(page)
    assert lines[0] == "- Current element: Pyro."
    assert lines[1] == "- Oath: Pyro 2, Hydro 0, Electro 1, Cryo 0."
    assert lines[2] == "- Your Swirls deal 3 damage to that enemy."
    auras = [line for line in lines if line.startswith("- **Hilichurl")]
    assert len(auras) == 3
    assert "Pyro, fresh: an Anemo hit Swirls it." in auras[0]
    assert ("Hydro, spent: Swirl does nothing to it until Hydro hits it "
            "again.") in auras[1]
    assert auras[2].endswith("no aura.")


def test_a_plain_oath_badge_means_no_current_element_yet():
    page = blindplay.observe(varka_state(
        badge=("Oath", NO_ELEMENT_TEXT, 1)))
    lines = _block(page)
    assert lines[0] == "- Current element: none. Play a Knight to set it."
    assert lines[1] == "- Oath: Pyro 0, Hydro 1, Electro 0, Cryo 0."
    assert lines[2] == "- Your Swirls pay nothing until you play a Knight."


def test_no_badge_still_prints_his_block_with_zero_counts():
    page = blindplay.observe(varka_state(badge=None))
    lines = _block(page)
    assert lines[0].startswith("- Current element: none.")
    assert lines[1] == "- Oath: Pyro 0, Hydro 0, Electro 0, Cryo 0."
    assert lines[2].startswith("- Your Swirls pay nothing")


def test_every_current_element_names_its_own_payout():
    for element, sentence in (
            ("Pyro", "Your Swirls deal 3 damage to that enemy."),
            ("Hydro", "Your Swirls give you 3 Block."),
            ("Cryo", "Your Swirls apply 1 Vulnerable to that enemy."),
            ("Electro", "Your Swirls deal 3 damage to ALL enemies.")):
        blindplay.forget_fight()
        text = (f"Your current element is {element}. {sentence} "
                "Oath: Pyro 1, Hydro 1, Electro 1, Cryo 1.")
        page = blindplay.observe(varka_state(
            badge=(f"{element} Oath", text, 1)))
        lines = _block(page)
        assert lines[0] == f"- Current element: {element}."
        assert lines[2] == f"- {sentence}", element


def test_a_missing_sentence_falls_back_to_the_badge_amount():
    combat = blindplay_board._combat(varka_state(
        badge=("Cryo Oath", "", 3)))
    oath = combat["oath"]
    assert oath["element"] == "Cryo"
    assert oath["counts"] == {"Pyro": 0, "Hydro": 0, "Electro": 0, "Cryo": 3}


def test_another_kit_prints_no_oath_block():
    state = varka_state(badge=None, character="Kokomi")
    state["player"]["relics"] = []
    page = blindplay.observe(state)
    assert "## Your Oath" not in page
    assert "oath" not in blindplay_board._combat(state)


def test_the_block_is_built_off_the_wires_own_rows():
    """The board half, on its own: SPENT is the badge's own sentence, never a
    guess, and the counts are the badge sentence's."""
    combat = blindplay_board._combat(varka_state())
    oath = combat["oath"]
    assert oath["element"] == "Pyro"
    assert oath["counts"] == {"Pyro": 2, "Hydro": 0, "Electro": 1, "Cryo": 0}
    assert oath["payout"] == "Your Swirls deal 3 damage to that enemy."
    assert [(r["element"], r["state"]) for r in oath["auras"]] == [
        ("Pyro", "fresh"), ("Hydro", "spent"), (None, None)]


def test_embark_names_him_and_the_run_check_knows_him():
    """`understudy.embark --character varka` asks the select screen for his
    option id, and the run it starts is checked against the name the game
    reads back."""
    assert embark.option_id("varka") == "KLEEMOD-VARKA"
    assert soak_navigate.character_matches("KLEEMOD-VARKA", "Varka")
    assert not soak_navigate.character_matches("KLEEMOD-VARKA", "Kokomi")


def test_the_page_glossary_defines_his_three_words():
    state = varka_state()
    state["player"]["hand"] = [{
        "name": "Windbound Execution", "type": "Attack", "cost": "1",
        "can_play": True, "index": 0, "target_type": "AnyEnemy",
        "is_upgraded": False, "keywords": [],
        "description": "Deal 6 damage. Gain 1 Oath of your current element. "
                       "A Knight sets it."}]
    page = blindplay.observe(state)
    glossary = page.split("## Words on this screen", 1)[1]
    for word in ("Oath", "current element", "Knight"):
        assert f"- **{word}** — " in glossary, word
    assert ("- **Oath** — Gained when your card applies or Swirls an "
            "element: 1 of each, per card. Kept all fight. Cards read your "
            "current element's Oath.") in glossary
    for retired in ("Absorb", "Wind"):
        assert f"- **{retired}** — " not in glossary, retired


# ---- seat fixes 2026-09-29 ---------------------------------------------------

def _bare_hand(state: dict, *cards: dict) -> dict:
    """His turn with only `cards` in hand, empty piles and no auras."""
    p = state["player"]
    p["hand"] = list(cards)
    for pile in ("draw_pile", "discard_pile", "exhaust_pile"):
        p[pile] = []
    for enemy in state["battle"]["enemies"]:
        enemy["status"] = []
    return state


def _card(name: str, text: str, kind: str = "Attack") -> dict:
    return {"id": "KLEEMOD-" + name.upper().replace(" ", "_"), "name": name,
            "type": kind, "cost": "1", "star_cost": None,
            "description": text, "rarity": "Basic", "is_upgraded": False,
            "keywords": [], "index": 0, "target_type": "AnyEnemy",
            "can_play": True, "unplayable_reason": None}


ROLL_CALL = ("Knights' Roll Call", "Add a random Knight to your hand.")


def test_knights_roll_call_is_an_element_source():
    """"NO REACTION IS REACHABLE HERE ... this screen supplies no element"
    printed with a Knight chooser in hand: its element is chosen at play."""
    updraft = _card("Updraft", "Deal 5 damage. Applies Anemo.")
    updraft["keywords"] = [{"name": "Applies Anemo", "description":
                            "An Anemo hit Swirls an aura."}]
    control = blindplay.observe(_bare_hand(
        varka_state(badge=None, auras=(None,)), updraft))
    assert "supplies no element" in control
    blindplay.forget_fight()
    page = blindplay.observe(_bare_hand(
        varka_state(badge=None, auras=(None,)), updraft,
        _card(*ROLL_CALL, kind="Skill")))
    assert "supplies no element" not in page


def test_the_retired_absorb_receipt_prints_nothing():
    """The C# side stopped emitting `absorbed` rows; an old one is ignored."""
    state = varka_state()
    state["player"]["resolutions"] = [
        {"card_id": "STRIKE_VARKA", "card": "Strike", "auto_played": False,
         "carried": False, "overflowed": False,
         "hits": [{"target": "Hilichurl 1", "amount": 6, "blocked": 0,
                   "combat_id": "100", "killed": False}],
         "applied": [], "summoned": [],
         "absorbed": [{"target": "Hilichurl 1", "element": "Pyro",
                       "swirled": False, "combat_id": "100"}]}]
    page = blindplay.observe(state)
    assert "Absorbed" not in page and "Wind." not in page


def test_the_words_say_a_spent_aura_still_reacts_and_swirl_copies_are_spent():
    from understudy import blindplay_notes as notes
    assert ("A spent aura still reacts with Pyro, Hydro, Electro and Cryo."
            in notes.ELEMENT_KEYWORDS["aura"])
    assert "The aura and its copies stay spent." in notes.ARM_KEYWORDS["Swirl"]
    page = blindplay.observe(varka_state())
    assert "Other elements still react with it." in page
