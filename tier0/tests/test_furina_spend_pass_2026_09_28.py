"""FURINA, THE SPEND PASS (2026-09-28): the sheet's five fixed-Spend cards,
and the page printing a Spend mode the board cannot pay.

[USER], 2026-09-28: "If Furina is still generating too much Fanfare and not
enough damage, we could solve her problem by upping both the spend and output
of her cards." Both Sonnet seats after balance pass one: "Spend 2 wasn't
offered on some turns and offered on others; I only learned by trying."

The C# pins are `FurinaStageRoundTwoTests`, `FurinaStageRoundThreeTests` and
`FurinaHydroHitsTests`. NOTHING MEASURED ON A PROTOTYPE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tier0.content import loader
from tier0.engine import furina_stage as FS
from understudy import blindplay, blindplay_board
from understudy.blindplay_board import spend_unavailable
from understudy.blindplay_render import _render_card


# ---- 1. the sheet ------------------------------------------------------------

def _row(cid):
    rows = yaml.safe_load((Path(__file__).resolve().parents[2] / "docs"
                           / "prototype-surface.yaml").read_text(
                               encoding="utf-8"))
    rows = rows["cards"] if isinstance(rows, dict) else rows
    return next(r for r in rows if r["id"] == cid)


@pytest.fixture
def arm(monkeypatch):
    yield


#: id -> (plain, Spend price, Spend amount, upgrade). THE FADE PASS
#: (2026-09-29) raised every Spend damage number here (Interposition, a Block
#: card, did not move): Quick Cue 11 -> 14, Spirited Aria 11 -> 14, Tidal
#: Flourish 10 -> 13, Grand Entrance 32 -> 40; Quick Cue's and Grand
#: Entrance's Spend numbers upgrade by one more than their plain ones. THE
#: RULES PASS (2026-10-01): Quick Cue 14 -> 11.
SPEND_PASS = {
    "proto_fs_quick_cue": (3, 3, 11, {"conditional_damage": 1,
                                      "conditional_then_damage": 1}),
    "proto_fs_spirited_aria": (8, 3, 14, {"conditional_damage": 3}),
    "proto_fs_tidal_flourish": (5, 3, 13, {"conditional_damage": 3}),
    "proto_fs_interposition": (5, 3, 13, {"conditional_block": 3}),
    "proto_fs_grand_entrance": (12, 7, 40, {"conditional_damage": 4,
                                            "conditional_then_damage": 1}),
}


@pytest.mark.parametrize("cid", sorted(SPEND_PASS))
def test_the_spend_pass_numbers(arm, cid):
    plain, price, branch, upgrade = SPEND_PASS[cid]
    card = loader.get_card(cid)
    modes = card.effects[0]["modes"]
    assert modes[0]["effects"][0]["amount"] == plain
    assert modes[1]["effects"][0] == {"op": "stage_spend", "amount": price}
    assert modes[1]["effects"][1]["amount"] == branch
    assert card.upgrade == upgrade
    assert f"Spend[/gold] {price}:" in _row(cid)["description"]


def test_spirited_arias_spend_mode_deals_more_and_reads_as_instead(arm):
    assert _row("proto_fs_spirited_aria")["description"] == (
        "Deal {PlainDamage:diff()} damage. [gold]Spend[/gold] 3: deal "
        "{BranchDamage:diff()} and draw 2 cards instead.")


# ---- 2. the page -------------------------------------------------------------

QUICK_CUE = "Deal 3 damage. Spend 3: deal 11 and apply Hydro instead."


def _stage(*bars):
    return {"seats": [{"member": "usher", "name": "Usher", "seat": i,
                       "fanfare": bar} for i, bar in enumerate(bars)],
            "log": []}


def test_a_short_stage_prints_the_mode_marked_with_the_reason():
    """The rules pass (2026-10-01): the Spend pays back first, then forward,
    so it is refused only when the whole stage holds less."""
    assert spend_unavailable(QUICK_CUE, _stage(1, 1)) == [
        "Spend 3: deal 11 and apply Hydro instead — unavailable: your "
        "performers hold 2 Fanfare between them"]


def test_a_payable_spend_prints_nothing_extra():
    assert spend_unavailable(QUICK_CUE, _stage(1, 3)) == []
    # A lone performer is both front and back.
    assert spend_unavailable(QUICK_CUE, _stage(4)) == []


def test_the_front_bar_pays_after_the_back():
    assert spend_unavailable(QUICK_CUE, _stage(9, 1)) == []


def test_an_empty_stage_says_so():
    assert spend_unavailable(QUICK_CUE, _stage()) == [
        "Spend 3: deal 11 and apply Hydro instead — unavailable: the stage "
        "is empty"]


def test_palais_ledger_takes_one_off_the_price():
    """The rules pass (2026-10-01): "Your Spends cost 1 less Fanfare." """
    ledger = [{"name": "Palais Ledger", "text": ""}]
    assert spend_unavailable(QUICK_CUE, _stage(1, 1), ledger) == []
    [line] = spend_unavailable(QUICK_CUE, _stage(1), ledger)
    assert line.endswith("your performers hold 1 Fanfare between them, and "
                         "it costs 2 with Palais Ledger")


@pytest.mark.parametrize("text", [
    "Spend all of your back performer's Fanfare. Deal 2 damage per point.",
    "Spend all your Sparks. Deal 5 damage to ALL enemies for each Spark spent.",
    "Spend 6 Charge: gain 12 Block.",
    "Deal 6 damage.",
])
def test_only_a_stage_spend_mode_is_read(text):
    assert spend_unavailable(text, _stage(0)) == []


def test_no_stage_in_this_build_prints_nothing():
    assert spend_unavailable(QUICK_CUE, None) == []


def test_the_card_face_prints_the_line_under_its_text():
    face = {"title": "Quick Cue", "upgraded": False, "cost": "0",
            "kind": "Attack", "text": QUICK_CUE, "keywords": [],
            "playable": True, "spend_unavailable": spend_unavailable(
                QUICK_CUE, _stage(2))}
    lines = _render_card(face)
    assert lines[1] == f"    {QUICK_CUE}"
    assert lines[2] == ("    Spend 3: deal 11 and apply Hydro instead — "
                        "unavailable: your performers hold 2 Fanfare between "
                        "them")


@pytest.fixture
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def _combat_state(bars):
    return {
        "state_type": "monster", "screen": "combat", "floor": 3,
        "battle": {"round": 3},
        "player": {
            "character": "Furina", "hp": 62, "max_hp": 78, "block": 0,
            "energy": 3, "max_energy": 3, "gold": 0,
            "hand": [{"id": "KLEEMOD-PROTO_FS_QUICK_CUE", "name": "Quick Cue",
                      "description": QUICK_CUE, "cost": "0", "type": "Attack",
                      "can_play": True, "target_type": "AnyEnemy"}],
            "draw_pile_count": 5, "discard_pile_count": 0,
            "exhaust_pile_count": 0, "draw_pile": [], "discard_pile": [],
            "exhaust_pile": [], "relics": [], "potions": [], "status": [],
            "resources": {}, "pets": [],
            "furina_stage": {"live": True, "log": [], "seats": [
                {"member": "usher", "name": "Gentilhomme Usher", "seat": i,
                 "fanfare": bar, "entity_id": str(7 + i)}
                for i, bar in enumerate(bars)]}},
        "enemies": [{"name": "Nibbit", "hp": 20, "max_hp": 44, "block": 0,
                     "intents": [{"kind": "attack", "amount": 12}],
                     "status": []}],
    }


def test_the_observed_page_marks_the_hand_card(_fresh_fight):
    page = blindplay.observe(_combat_state([1, 1]))
    assert ("Spend 3: deal 11 and apply Hydro instead — unavailable: your "
            "performers hold 2 Fanfare between them") in page
    blindplay.forget_fight()
    page = blindplay.observe(_combat_state([5, 3]))
    assert "unavailable:" not in page
    hand = blindplay_board._combat(_combat_state([5, 3]))["hand"]
    assert hand[0]["spend_unavailable"] == []
