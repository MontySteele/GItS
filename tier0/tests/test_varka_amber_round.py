"""THE VARKA FORCED-AMBER ROUND'S SEAT-PAGE FIXES
(review/records/varka-amber-round-2026-10-10.md, "What changes"):

  * 2. Wildfire Oath's bonus, under every card in the hand that applies Pyro
    while the power is up ("Wildfire: +N a hit", N its per-application
    damage: the Pyro Oath per stack). Not on an Anemo card: it does not fire
    on a Swirl's spread.
  * 6. A Knight's hand row prints "Knight". The game already prints the
    keyword's line, "Knight.", at the head of the rules box
    (`KleeKeywords.Knight`, `AutoKeywordPosition.Before`), and the page
    prints the wire's sentence unchanged; this pins that it stays there.

The card changes (Ashen Oath, Frost Ward, Oath Unto Death) are pinned in
`test_varka_combo`, `test_varka_rebalance` and `test_varka_expansion`.
"""
from __future__ import annotations

import copy

import pytest

from understudy import blindplay
from tier0.tests.test_varka_seat_page import _status, varka_state


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


WILDFIRE_TEXT = ("Whenever you apply Pyro to an enemy, deal damage equal to "
                 "your Pyro Oath to it.")


def _card(state, name, text, element=None, card_type="Attack"):
    card = copy.deepcopy(state["player"]["hand"][0])
    card.update({"id": "KLEEMOD-PROTO_VK_" + name.upper().replace(" ", "_"),
                 "name": name, "type": card_type, "cost": "1",
                 "description": text, "keywords": []})
    if element:
        card["keywords"] = [{"name": f"Applies {element}",
                             "description": f"Applies {element}."}]
    return card


def _hand(state, *cards):
    state["player"]["hand"] = list(cards)
    return state


def _with_wildfire(state, stacks=1):
    state["player"]["status"].append(
        _status("Wildfire Oath", WILDFIRE_TEXT, stacks, "Counter"))
    return state


def _rows_after(page, title):
    """The lines of the card row headed `title`, up to the next row."""
    body = page.split("## Your hand", 1)[1].split("## The other side", 1)[0]
    lines = body.splitlines()
    start = next(i for i, line in enumerate(lines)
                 if line.startswith(f"- **{title}**"))
    out = [lines[start]]
    for line in lines[start + 1:]:
        if line.startswith("- "):
            break
        out.append(line)
    return out


def test_wildfire_prints_its_hit_on_a_pyro_card():
    state = varka_state()                                # Pyro Oath 2
    _hand(state,
          _card(state, "Kindled Edge", "Deal 6 Pyro damage.", "Pyro"),
          _card(state, "Gale Sweep", "Deal 5 Anemo damage.", "Anemo"),
          _card(state, "Defend", "Gain 5 Block.", card_type="Skill"))
    page = blindplay.observe(_with_wildfire(state))
    assert "    - Wildfire: +2 a hit." in _rows_after(page, "Kindled Edge")
    # Not on a Swirl card, and not on a card that applies nothing.
    assert page.count("Wildfire: +") == 1


def test_wildfire_reads_the_stack_and_the_current_pyro_oath():
    state = varka_state(badge=(
        "Pyro Oath", "Your current element is Pyro. Your Swirls deal 3 "
        "damage to that enemy. Oath: Pyro 19, Hydro 0, Electro 0, Cryo 0.",
        19))
    _hand(state, _card(state, "Stoke", "Apply Pyro.", "Pyro", "Skill"))
    page = blindplay.observe(_with_wildfire(state, stacks=2))
    assert "    - Wildfire: +38 a hit." in _rows_after(page, "Stoke")


def test_no_wildfire_line_without_the_power():
    state = varka_state()
    _hand(state, _card(state, "Kindled Edge", "Deal 6 Pyro damage.", "Pyro"))
    assert "Wildfire:" not in blindplay.observe(state)


def test_a_knight_row_prints_knight():
    state = varka_state()
    knight = _card(state, "Amber: Precise Shot",
                   "Knight. Deal 6 Pyro damage.", "Pyro")
    _hand(state, knight)
    rows = _rows_after(blindplay.observe(state), "Amber: Precise Shot")
    # Varka round 3 (2026-10-10): the tag carries the Knight's element.
    assert rows[1].strip().startswith("Knight, Pyro.")
