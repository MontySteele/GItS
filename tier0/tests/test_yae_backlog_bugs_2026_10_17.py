"""Yae seat findings, rounds 7 to 10 (2026-10-16/17): the BACKLOG items
that were real bugs. Page and sim half; the mod half is
`klee-mod/KleeTests/Prototype/YaeBacklogBugsTests.cs`.

  * A picked hand card leaves the chooser's list (`NPlayerHand`), so the page
    names the held pick (round 10, lane 4: the list showed only Scattered
    Blossoms and the confirm Edited the Tenko Kenshin it held).
  * An Edit's receipt on the play line: the card and Annotation, "no
    chooser opened" when the game took the only card it could reach
    (round 7 lane 4, round 8 lane 4), the Sakura an Inked Branches reached
    and its empty-hand half (round 8, lane 3).
  * The shrine's count line reads the game's cap, Fox Ofuda included
    (round 10, lane 1, Torii Ward's "full").
  * Incoming folds The Shrine's Sacred Shade in (round 8, lane 3).
  * The Energy line credits a "2nd turn" relic on that turn only (round 8,
    lane 4: Very Hot Cocoa's +4 printed as +2 beside Candelabra).
  * The Tenko clause names the Sakura (round 8, lane 2) and Saiguu's Lesson
    says "a striking Sakura" (round 8, lane 3).

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tier0.engine import yae_shrine as Y
from understudy import blindplay, blindplay_render
from tier0.tests.test_varka_payoff_seat_page import _ev, _row
from tier0.tests.test_varka_seat_page import _status
from tier0.tests.test_yae_seat_page import _block, yae_state

REPO = Path(__file__).resolve().parents[2]


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


def _section(page, card):
    return page.split(f"- **{card}**", 1)[1].split("\n- **", 1)[0]


# ---- 1. A hand pick leaves the list ----------------------------------------

def _hand_chooser(selected=()):
    card = {"index": 0, "name": "Scattered Blossoms",
            "id": "KLEEMOD-PROTO_YM_ENLIGHTENED_BLESSING",
            "description": "Whenever a Sakura withers, gain 3 Block.",
            "type": "Power", "cost": "1"}
    blob = {"mode": "simple_select",
            "prompt": "Choose a card to Edit: Reprint (when played, it is "
                      "played 1 more time).",
            "cards": [card], "can_confirm": bool(selected)}
    if selected:
        blob["selected_cards"] = [{"index": i, "name": n}
                                  for i, n in enumerate(selected)]
    return {"state_type": "hand_select",
            "player": {"character": "yae", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            "hand_select": blob}


def test_a_held_hand_pick_is_named_under_the_list():
    page = blindplay.observe(_hand_chooser(
        ["Great Secret Art: Tenko Kenshin"]))
    assert blindplay_render.HAND_PICKED_HEADING in page
    assert blindplay_render.HAND_PICKED_NOTE in page
    assert "- **Great Secret Art: Tenko Kenshin** — PICKED" in page
    # The list still offers the card that was not picked.
    assert "**Scattered Blossoms**" in page


def test_no_picked_section_before_a_pick():
    page = blindplay.observe(_hand_chooser())
    assert blindplay_render.HAND_PICKED_HEADING not in page


# ---- 5 and 7d. The Edit's receipt on the play line -------------------------

def _resolved(card, *events, hits=False):
    state = yae_state()
    state["player"]["resolutions"] = [_row(card, hits=hits,
                                           events=list(events))]
    return _section(blindplay.observe(state), card)


def test_an_edit_names_the_card_and_annotation():
    line = _resolved("Proofread", _ev("yae_edit", 9601, card="Strike",
                                      power="Reprint"))
    assert "  Edited **Strike**: Reprint." in line
    assert "no chooser opened" not in line
    assert "Nothing this page can count" not in line


def test_an_edit_the_game_picked_says_no_chooser_opened():
    line = _resolved("Proofread", _ev("yae_edit", 9602, card="Defend",
                                      power="Reprint", amount=1))
    assert ("  Edited **Defend**: Reprint. It was the only card this Edit "
            "could reach, so no chooser opened.") in line


def test_inked_branches_plus_names_both_halves():
    line = _resolved("Inked Branches+",
                     _ev("yae_edit_sakura", 9603, power="Red Ink", amount=2),
                     _ev("yae_edit_none", 9604, power="Red Ink"))
    assert "  Edited 2 Sakura: Red Ink." in line
    assert "  No card in your hand that this Edit could reach." in line


def test_edit_receipts_stay_off_since_last_page():
    from understudy import blindplay_board
    state = yae_state()
    state["player"]["resolutions"] = [_row("Proofread", events=[
        _ev("yae_edit", 9605, card="Strike", power="Reprint")])]
    events = blindplay_board.page_events(state["player"]) or []
    assert not [e for e in events if e["kind"].startswith("yae_edit")]


# ---- 4. The shrine's cap is the game's ---------------------------------------

FULL4 = ((1, 1, 3, 3), (2, 1, 3, 3), (3, 1, 3, 3), (4, 1, 3, 3))


def test_fox_ofuda_raises_the_count_lines_cap():
    state = yae_state(badges=FULL4[:3])
    state["player"]["relics"] = [{"id": "KLEEMOD-FOX_OFUDA",
                                  "name": "Fox Ofuda",
                                  "description": "You can have 1 more Sakura."}]
    lines = _block(blindplay.observe(state))
    assert lines[0].startswith("- Sakura: 3 of 4.")
    assert not any(line.startswith("- Shrine full") for line in lines)


def test_the_wire_cap_wins():
    state = yae_state(badges=FULL4)
    state["player"]["yae_shrine"] = {"live": True, "max_sakura": 4}
    lines = _block(blindplay.observe(state))
    assert lines[0].startswith("- Sakura: 4 of 4.")
    assert any(line.startswith("- Shrine full") for line in lines)


# ---- 7c. Incoming folds The Shrine's Sacred Shade ----------------------------

def _shrine(n):
    return {"sakura": [{"slot": i + 1, "level": 1, "kind": "thunder",
                        "strike": 3, "turns": 3, "annotation": None}
                       for i in range(n)],
            "cap": 3, "lure": None, "annotated": 0, "edits": None}


def _attacker(n):
    return [{"name": "Hilichurl", "hp": 20, "max_hp": 20, "powers": [],
             "intents": [{"type": "Attack", "label": str(n),
                          "damage": n, "hits": 1}]}]


def _you(shade):
    powers = ([{"name": "The Shrine's Sacred Shade", "stacks": shade,
                "text": "At the end of your turn, gain {} Block for each "
                        "Sakura.".format(shade)}] if shade else [])
    return {"block": 0, "hp": 40, "max_hp": 70, "powers": powers,
            "relics": []}


def test_the_incoming_line_folds_sacred_shade_in():
    line = blindplay_render._incoming_line(_attacker(12), _you(2),
                                           shrine=_shrine(3))
    assert "you would take 6" in line, line
    assert "The Shrine's Sacred Shade adds 6 Block first" in line, line
    assert "Not counted" not in line, line


def test_sacred_shade_with_no_sakura_adds_nothing_and_is_not_unknown():
    line = blindplay_render._incoming_line(_attacker(12), _you(2),
                                           shrine=_shrine(0))
    assert "you would take 12" in line, line
    assert "Not counted" not in line, line


# ---- 8. A "2nd turn" relic pays on its turn only ----------------------------

CANDELABRA = {"name": "Candelabra",
              "text": "At the start of your 2nd turn, gain 2 Energy."}
COCOA = {"name": "Very Hot Cocoa",
         "text": "At the start of each combat, gain an additional 4 Energy."}
PAELS = {"name": "Pael's Flesh",
         "text": "Gain an additional 1 Energy at the start of your 3rd "
                 "turn, and every turn after that."}


def _energy(relics, energy, round_number):
    you = {"energy": energy, "max_energy": 3, "relics": relics}
    return blindplay_render._energy_line(you, round_number)


def test_very_hot_cocoa_takes_turn_ones_surplus_beside_candelabra():
    line = _energy([CANDELABRA, COCOA], 7, 1)
    assert "+4 Very Hot Cocoa" in line, line
    assert "Candelabra" not in line, line


def test_candelabra_is_named_on_its_turn():
    line = _energy([CANDELABRA, COCOA], 5, 2)
    assert "+2 Candelabra" in line, line
    assert "Cocoa" not in line, line


def test_an_every_turn_after_face_is_not_named_before_its_turn():
    assert "Pael" not in _energy([PAELS], 4, 2)


# ---- 7a, 7b. The Tenko clause and Saiguu's Lesson's words --------------------

def test_the_tenko_clause_names_the_sakura():
    assert Y.tenko_words({Y.THUNDER: 13}) == " (Sakura: 13 damage)"
    assert Y.tenko_words({}) == Y.NO_SAKURA
    cs = (REPO / "klee-mod/KleeCode/Powers/Prototype/YaeShrine.cs").read_text(
        encoding="utf-8")
    assert f'TenkoPrefix = "{Y.TENKO_PREFIX}"' in cs


def test_saiguus_lesson_says_a_striking_sakura():
    rows = yaml.safe_load((REPO / "docs/prototype-surface.yaml").read_text(
        encoding="utf-8"))
    row = next(r for r in rows if r["id"] == "proto_ym_saiguus_lesson")
    assert "a striking [gold]Sakura[/gold] strikes it" in row["description"]
    power = (REPO / "klee-mod/KleeCode/Powers/Prototype/YaePowers.cs").read_text(
        encoding="utf-8")
    assert '"Whenever you apply [gold]Weak[/gold] to an enemy, a striking "' \
        in power
