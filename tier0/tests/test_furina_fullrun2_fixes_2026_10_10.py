"""The Furina whole-run round 2's page fixes
(`review/records/furina-fullrun-round-2-2026-10-10.md`, "What changes").

- While Surrounded, the hand marks the cards that take `on` (they turn you
  to face their target).
- A chooser that allows 0 picks says a bare `confirm` closes it with nothing
  taken, and `skip` there names the `confirm`.
- The `IStageSpendCard` stamp the turn-start Spend-card telemetry reads is
  derived from the sheet's `stage_spend*` ops. The telemetry itself is C#,
  pinned in `klee-mod/KleeTests/Prototype/FurinaSpendRoundFixesTests.cs`.

NOTHING MEASURED HERE IS QUOTABLE: shape assertions about a renderer.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from understudy import blindplay
from understudy.blindplay_grammar import act
from understudy.blindplay_notes import (CONFIRM_TAKES_NOTHING_NOTE,
                                        TURNS_YOU_TAG)
from tier0.tests.test_control_seat_fixes_2026_09_26 import _crab

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


# ---- 2. Surrounded: which cards turn you --------------------------------------

def _hand(state):
    state["player"]["hand"] = [
        {"index": 0, "name": "Neutralize", "id": "NEUTRALIZE",
         "description": "Deal 3 damage. Apply 1 Weak.", "type": "Attack",
         "cost": "0", "target_type": "AnyEnemy"},
        {"index": 1, "name": "Defend", "id": "DEFEND_SILENT",
         "description": "Gain 5 Block.", "type": "Skill", "cost": "1",
         "target_type": "Self"},
        {"index": 2, "name": "Dagger Spray", "id": "DAGGER_SPRAY",
         "description": "Deal 4 damage to ALL enemies twice.",
         "type": "Attack", "cost": "1", "target_type": "AllEnemies"}]
    return state


def _head(page, title):
    return next(ln for ln in page.splitlines()
                if ln.startswith(f"- **{title}**"))


def test_surrounded_marks_the_cards_that_take_on():
    page = blindplay.observe(_hand(_crab(["5"])))
    assert TURNS_YOU_TAG == " (turns you)"
    assert TURNS_YOU_TAG in _head(page, "Neutralize")
    assert TURNS_YOU_TAG not in _head(page, "Defend")
    assert TURNS_YOU_TAG not in _head(page, "Dagger Spray")


def test_surrounded_with_nobody_behind_still_marks_them():
    page = blindplay.observe(_hand(_crab([])))
    assert TURNS_YOU_TAG in _head(page, "Neutralize")


def test_no_mark_without_surrounded():
    state = _hand(_crab(["5"]))
    state["player"]["status"] = []
    page = blindplay.observe(state)
    assert TURNS_YOU_TAG not in page


# ---- 3. A chooser that allows 0 picks -----------------------------------------

def _chooser(st="card_select", **over):
    blob = {"screen_type": "NCombatPileCardSelectScreen",
            "prompt": "Choose up to 2 cards.", "can_skip": False,
            "can_cancel": False, "preview_showing": False,
            "can_confirm": True, "selection_known": True,
            "cards": [{"index": 0, "name": "Strike", "id": "STRIKE_IRONCLAD",
                       "description": "Deal 6 damage.", "type": "Attack",
                       "cost": "1", "selected": False}]}
    blob.update(over)
    return {"state_type": st,
            "player": {"character": "ironclad", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            st: blob}


def test_a_zero_pick_chooser_says_confirm_takes_nothing():
    page = blindplay.observe(_chooser())
    assert CONFIRM_TAKES_NOTHING_NOTE in page
    assert "`confirm`" in CONFIRM_TAKES_NOTHING_NOTE


@pytest.mark.parametrize("over", [
    {"can_confirm": False},
    {"selection_known": False},
    {"preview_showing": True},
    {"cards": [{"index": 0, "name": "Strike", "id": "STRIKE_IRONCLAD",
                "description": "Deal 6 damage.", "type": "Attack",
                "cost": "1", "selected": True}]},
])
def test_no_note_where_confirm_would_take_something_or_is_unknown(over):
    assert CONFIRM_TAKES_NOTHING_NOTE not in blindplay.observe(
        _chooser(**over))


def test_a_hand_chooser_with_nothing_selected_says_it_too():
    state = _chooser("hand_select", mode="simple_select")
    state["hand_select"].pop("selection_known")
    assert CONFIRM_TAKES_NOTHING_NOTE in blindplay.observe(state)
    state["hand_select"]["selected_cards"] = [{"index": 0, "name": "Strike"}]
    assert CONFIRM_TAKES_NOTHING_NOTE not in blindplay.observe(state)


def test_skip_on_a_zero_pick_chooser_names_the_confirm():
    res = act(_chooser(), "skip")
    assert not res["ok"]
    text = str(res)
    assert "a bare `confirm` closes this chooser" in text
    plain = act(_chooser(can_confirm=False), "skip")
    assert "will not let you leave without choosing" in str(plain)


# ---- 1. The Spend-card stamp the telemetry counts -----------------------------

def test_the_spend_card_stamp_follows_the_sheet_ops():
    from tools.gen_klee_cards import stage_spend_card
    assert stage_spend_card({"effects": [{"op": "stage_spend", "amount": 4}]})
    assert stage_spend_card({"effects": [{"op": "choose_one", "modes": [
        {"label": "a", "effects": [{"op": "stage_spend_all"}]}]}]})
    assert not stage_spend_card({"effects": [
        {"op": "apply_power", "power": "fs_showstopper", "amount": 1}]})
    gen = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"
    assert "IStageSpendCard" in (gen / "ProtoFsQuickCue.cs").read_text(
        encoding="utf-8")
    assert "IStageSpendCard" not in (gen / "ProtoFsShowstopper.cs").read_text(
        encoding="utf-8")
