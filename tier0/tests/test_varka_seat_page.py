"""VARKA, PROTOTYPE BATCH ONE: what a blind seat reads on his combat page.

The paper kit's first-round question (review/active/varka-paper-kit-
2026-09-28.md sec.10.4) is "is choosing between Absorb and Swirl a decision on
the turn, or a chore?", and every such choice turns on three facts: the Winds
he holds, whether Boreas's Fang has taken this turn's hit, and whether each
enemy's aura is FRESH (an Absorb takes it, an Anemo hit Swirls it) or SPENT
(both do nothing). The page prints the three in one block, off the wire's own
status rows and relic counter.

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


def varka_state(winds=("Pyro",), fang_counter=1,
                auras=((FRESH_PYRO, "Pyro"), (SPENT_HYDRO, "Hydro"), None),
                character="Varka") -> dict:
    """The recorded turn, as his: Winds on him, the Fang in his relics, and
    one enemy per `auras` entry (text, element) or None for a bare body."""
    state = json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))["state"]
    p = state["player"]
    p["character"] = character
    p["status"] = [_status(f"{w} Wind", f"Whenever you Swirl, {w}.")
                   for w in winds]
    p["relics"] = [{"id": "KLEEMOD-BOREAS_FANG", "name": "Boreas's Fang",
                    "description": "Once each turn, the first non-Anemo "
                                   "Attack that hits a fresh aura Absorbs it.",
                    "counter": fang_counter, "keywords": []}]
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
    assert "## Your Winds" in page, page
    body = page.split("## Your Winds", 1)[1].strip().split("\n\n")[0]
    return body.splitlines()


def test_the_page_prints_his_winds_his_fang_and_every_auras_state():
    page = blindplay.observe(varka_state())
    lines = _block(page)
    assert lines[0] == ("- Winds held: Pyro (1 of 4). Not yet: Cryo, Hydro, "
                        "Electro.")
    assert lines[1].startswith("- Boreas's Fang: ready.")
    auras = [line for line in lines if line.startswith("- **Hilichurl")]
    assert len(auras) == 3
    assert "Pyro, fresh: an Absorb takes it; an Anemo hit Swirls it." in auras[0]
    assert ("Hydro, spent: Absorb and Swirl do nothing to it until Hydro "
            "hits it again.") in auras[1]
    assert auras[2].endswith("no aura.")


def test_a_used_fang_and_no_winds_say_so():
    page = blindplay.observe(varka_state(winds=(), fang_counter=0))
    lines = _block(page)
    assert lines[0] == ("- Winds held: none. Absorb a fresh aura to gain its "
                        "Wind.")
    assert lines[1] == "- Boreas's Fang: used this turn."


def test_all_four_winds_read_in_payout_order():
    page = blindplay.observe(
        varka_state(winds=("Electro", "Hydro", "Pyro", "Cryo")))
    assert _block(page)[0] == ("- Winds held: Cryo, Pyro, Hydro, Electro "
                               "(all 4).")


def test_another_kit_prints_no_winds_block():
    state = varka_state(winds=(), character="Kokomi")
    state["player"]["relics"] = []
    assert "## Your Winds" not in blindplay.observe(state)


def test_the_block_is_built_off_the_wires_own_rows():
    """The board half, on its own: SPENT is the badge's own sentence, never a
    guess, and the Fang's state is its icon's counter."""
    state = varka_state()
    combat = blindplay_board._combat(state)
    winds = combat["winds"]
    assert winds["held"] == ["Pyro"]
    assert winds["missing"] == ["Cryo", "Hydro", "Electro"]
    assert winds["fang"] == "ready"
    assert [(r["element"], r["state"]) for r in winds["auras"]] == [
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
        "description": "Deal 6 damage. Absorb. Each Swirl pays every Wind; "
                       "a Knight paints."}]
    page = blindplay.observe(state)
    glossary = page.split("## Words on this screen", 1)[1]
    for word in ("Absorb", "Wind", "Knight"):
        assert f"- **{word}** — " in glossary, word


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


MUSTER = ("Knights' Muster",
          "Choose a Knight: deal 4 damage of their element.")


def test_knights_muster_is_an_element_source():
    """"NO REACTION IS REACHABLE HERE ... this screen supplies no element"
    printed with Knights' Muster in hand: its element is chosen at play."""
    updraft = _card("Updraft", "Deal 5 damage. Applies Anemo.")
    updraft["keywords"] = [{"name": "Applies Anemo", "description":
                            "An Anemo hit Swirls an aura."}]
    control = blindplay.observe(_bare_hand(
        varka_state(winds=(), auras=(None,)), updraft))
    assert "supplies no element" in control
    blindplay.forget_fight()
    page = blindplay.observe(_bare_hand(
        varka_state(winds=(), auras=(None,)), updraft,
        _card(*MUSTER, kind="Skill")))
    assert "supplies no element" not in page


def test_an_absorb_is_named_on_the_reaction_log():
    state = varka_state()
    state["player"]["reactions"] = [
        {"reaction": "Absorb", "source": "Strike", "target": "Hilichurl 1",
         "combat_id": "100", "carried": False,
         "detail": "Took the Pyro aura; you gained Pyro Wind."},
        {"reaction": "Swirl", "source": "Charlotte", "target": "Hilichurl 2",
         "combat_id": "101", "carried": False,
         "detail": ("You already held Hydro Wind, so it Swirled instead of "
                    "Absorbing.")},
        {"reaction": "Melt", "source": "Amber", "target": "Hilichurl 1",
         "combat_id": "100", "carried": False},
    ]
    page = blindplay.observe(state)
    assert ("- **Absorb** on **Hilichurl 1**, off Strike. Took the Pyro "
            "aura; you gained Pyro Wind.") in page
    assert ("off Charlotte. You already held Hydro Wind, so it Swirled "
            "instead of Absorbing.") in page
    # Every reaction the log carries prints, not only Swirl.
    assert "- **Melt** on **Hilichurl 1**, off Amber." in page


def test_an_absorb_is_named_under_the_card_that_made_it():
    state = varka_state()
    state["player"]["resolutions"] = [
        {"card_id": "STRIKE_VARKA", "card": "Strike", "auto_played": False,
         "carried": False, "overflowed": False,
         "hits": [{"target": "Hilichurl 1", "amount": 6, "blocked": 0,
                   "combat_id": "100", "killed": False}],
         "applied": [], "summoned": [],
         "absorbed": [{"target": "Hilichurl 1", "element": "Pyro",
                       "swirled": False, "combat_id": "100"}]},
        {"card_id": "CHARLOTTE", "card": "Charlotte", "auto_played": False,
         "carried": False, "overflowed": False, "hits": [], "applied": [],
         "summoned": [],
         "absorbed": [{"target": "Hilichurl 2", "element": "Hydro",
                       "swirled": True, "combat_id": "101"}]},
    ]
    page = blindplay.observe(state)
    assert ("Absorbed the **Pyro** aura off **Hilichurl 1**: gained Pyro "
            "Wind.") in page
    assert ("Swirled the **Hydro** aura on **Hilichurl 2** instead of "
            "Absorbing it: you already held Hydro Wind.") in page


def test_the_words_say_a_spent_aura_still_reacts_and_swirl_copies_are_spent():
    from understudy import blindplay_notes as notes
    assert ("A spent aura still reacts with Pyro, Hydro, Electro and Cryo."
            in notes.ELEMENT_KEYWORDS["aura"])
    assert "The aura and its copies stay spent." in notes.ARM_KEYWORDS["Swirl"]
    page = blindplay.observe(varka_state())
    assert "Other elements still react with it." in page
