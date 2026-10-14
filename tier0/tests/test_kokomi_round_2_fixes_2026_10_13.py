"""Kokomi round 2 on build 0.2.5212 (2026-10-13): the three fixes.

1. Grand Design's gate counts exactly the cards the Bake-Kurage takes: every
   row with a Plan line and every Companion, upgraded or not, Grand Design
   itself never (`kokomi_plan.refuses_for_no_plan`). C# twin:
   `klee-mod/KleeTests/Prototype/KokomiRoundTwoFixesTests.cs`.
2. A sent `skip` on a card reward clears the reward screen's `proceed` hold
   for that card row (lane 5 had to `proceed` twice).
3. A numbered card name means the copy the last `observe` printed, so a
   chained `play "Coral Guard (3)"` then `play "Coral Guard (4)"` plays both
   (lane 4, Matriarch fight; the Furina wave saw the same).
"""
from __future__ import annotations

import argparse
import copy
import json

import pytest

from tier0.content import loader, upgrades
from tier0.engine import combat
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, kokomi_state)
from tier0.tests.test_understudy_blindplay import combat_state
from understudy import blindplay, blindplay_grammar, blindplay_shape, lanewatch


# ---- 1. Grand Design counts what the Bake-Kurage takes ---------------------

def _upgraded(card):
    try:
        return upgrades.apply_upgrade(copy.deepcopy(card))
    except Exception:  # noqa: BLE001 - a row with no upgrade path
        return None


def test_grand_design_counts_every_plan_card_and_companion_and_nothing_else():
    rows = loader.prototype_cards()
    checked = 0
    wrong = []
    for row in rows:
        for card in (copy.deepcopy(row), _upgraded(row)):
            if card is None:
                continue
            st = kokomi_state()
            st.player.energy = 3
            gd = copy.deepcopy(loader.get_card("proto_kk_grand_design"))
            st.player.hand = [gd, card]
            want = ((bool(card.plan) or card.is_companion)
                    and card.id != "proto_kk_grand_design")
            if combat.card_playable(st, gd) != want:
                wrong.append((card.id, card.upgraded))
            checked += 1
    assert checked > 400
    assert wrong == []
    # The generated jellyfish cards are among them.
    ids = {r.id for r in rows}
    assert {"proto_kk_sting", "proto_kk_ward"} <= ids


# ---- shared lane fixture ---------------------------------------------------

@pytest.fixture
def lane(tmp_path, monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", tmp_path)
    monkeypatch.delenv(blindplay.LANE_ENV, raising=False)
    monkeypatch.delenv(blindplay.MAX_ACTIONS_ENV, raising=False)
    monkeypatch.setattr(lanewatch, "guard", lambda *a, **k: "")
    blindplay.forget_fight()
    blindplay.forget_run()
    yield
    blindplay.forget_fight()
    blindplay.forget_run()


class _Wire:
    def __init__(self, state):
        self.state = state
        self.posts: list = []

    def get_state(self):
        return json.loads(json.dumps(self.state))

    def health(self):
        return {"status": "ok"}

    def post(self, action, **kw):
        self.posts.append((action, kw))
        return {"status": "ok", "message": f"Doing {action}"}


def _live(monkeypatch, state) -> _Wire:
    wire = _Wire(state)
    monkeypatch.setattr(blindplay, "bridge", wire)
    monkeypatch.setattr(blindplay, "_load_state", lambda _a: wire.get_state())
    return wire


def _act(command: str) -> int:
    return blindplay.cmd_act(argparse.Namespace(
        raw_file="", command=command, dry_run=False, brief=True))


def _observe() -> int:
    return blindplay.cmd_observe(argparse.Namespace(
        raw_file="", brief=True, define=""))


# ---- 2. a sent `skip` is the skip -----------------------------------------

RUN = {"act": 1, "floor": 6, "ascension": 0}
PLAYER = {"character": "Kokomi", "hp": 60, "max_hp": 80, "gold": 100,
          "potions": [], "relics": []}


def _rewards(*items) -> dict:
    return {"state_type": "rewards", "run": RUN, "player": dict(PLAYER),
            "rewards": {"can_proceed": True, "items": list(items)}}


CARD_ROW = {"index": 0, "type": "card", "description": "Add a card to your deck"}
GOLD_ROW = {"index": 1, "type": "gold", "description": "25 Gold", "amount": 25}


def _card_reward() -> dict:
    return {"state_type": "card_reward", "run": RUN, "player": dict(PLAYER),
            "card_reward": {"can_skip": True, "cards": [
                {"index": 0, "id": "POMMEL_STRIKE", "name": "Pommel Strike",
                 "type": "Attack", "cost": "1", "rarity": "Common",
                 "is_upgraded": False, "description": "Deal 9 damage."}]}}


def test_a_card_offer_still_holds_proceed_once(lane, monkeypatch):
    wire = _live(monkeypatch, _rewards(CARD_ROW))
    assert _act("proceed") == 1
    assert wire.posts == []


def test_skip_on_the_card_reward_clears_the_hold(lane, monkeypatch, capsys):
    wire = _live(monkeypatch, _card_reward())
    assert _act("skip") == 0
    assert [a for a, _ in wire.posts] == ["skip_card_reward"]
    # Back on the reward screen, the skipped offer is still a row.
    wire.state = _rewards(CARD_ROW)
    capsys.readouterr()
    assert _act("proceed") == 0
    assert [a for a, _ in wire.posts] == ["skip_card_reward", "proceed"]
    assert "REFUSED" not in capsys.readouterr().out
    # The proceed cleared the count: the next screen's offer holds again.
    assert blindplay_shape.card_skips() == 0


def test_a_skipped_card_does_not_excuse_the_gold(lane, monkeypatch, capsys):
    wire = _live(monkeypatch, _card_reward())
    assert _act("skip") == 0
    wire.state = _rewards(CARD_ROW, GOLD_ROW)
    capsys.readouterr()
    assert _act("proceed") == 1
    out = capsys.readouterr().out
    assert "25 Gold" in out and "Add a card" not in out


def test_unclaimed_rewards_drops_only_the_skipped_card_rows():
    two = _rewards(CARD_ROW, dict(CARD_ROW, index=1))
    assert len(blindplay_grammar.unclaimed_rewards(two)) == 2
    assert len(blindplay_grammar.unclaimed_rewards(two, skipped_cards=1)) == 1
    assert blindplay_grammar.unclaimed_rewards(two, skipped_cards=2) == []


# ---- 3. a numbered card names the copy the page showed ---------------------

def _guard(**over) -> dict:
    base = {"id": "KLEEMOD-CORAL_GUARD", "name": "Coral Guard", "type": "Skill",
            "cost": "1", "star_cost": None, "description": "Gain 5 Block.",
            "rarity": "Basic", "is_upgraded": False, "keywords": [],
            "target_type": "Self", "can_play": True,
            "unplayable_reason": None}
    base.update(over)
    return base


def _fight(hand: list[dict]) -> dict:
    state = combat_state()
    state["player"]["energy"] = 9
    state["player"]["hand"] = [dict(c, index=i) for i, c in enumerate(hand)]
    return state


def _play_index(wire, n) -> None:
    """The game's answer to a play: that card leaves the hand."""
    hand = wire.state["player"]["hand"]
    del hand[n]
    for i, c in enumerate(hand):
        c["index"] = i


def test_a_chained_numbered_play_names_the_copy_the_page_showed(
        lane, monkeypatch, capsys):
    wire = _live(monkeypatch, _fight([_guard() for _ in range(4)]))
    assert _observe() == 0
    assert "Coral Guard (4)" in capsys.readouterr().out
    assert _act('play "Coral Guard (3)"') == 0
    _play_index(wire, wire.posts[-1][1]["card_index"])
    # Three left; the re-counted hand has no "(4)", the page the seat read did.
    assert _act('play "Coral Guard (4)"') == 0
    assert [a for a, _ in wire.posts] == ["play_card", "play_card"]


def test_a_copy_already_played_is_skipped_not_re_aimed(
        lane, monkeypatch, capsys):
    # 2026-10-14 (Kokomi, lane 5): skipped, not counted -- and still never
    # re-aimed at a neighbour (`test_refusal_changed_under_the_seat.py`).
    wire = _live(monkeypatch, _fight([_guard() for _ in range(3)]))
    assert _observe() == 0
    assert _act('play "Coral Guard (2)"') == 0
    _play_index(wire, wire.posts[-1][1]["card_index"])
    capsys.readouterr()
    assert _act('play "Coral Guard (2)"') == 1
    assert ('Skipped: "Coral Guard (2)" was played since your last look'
            in capsys.readouterr().out)
    assert len(wire.posts) == 1


def test_the_copy_is_found_by_its_face_not_its_new_number(
        lane, monkeypatch):
    # (1) costs 1, (2) costs 0, (3) costs 1. Play (1); the old (2), the
    # 0-cost copy, is now the hand's (1) -- and "(2)" must still find it.
    wire = _live(monkeypatch, _fight([_guard(), _guard(cost="0"), _guard()]))
    assert _observe() == 0
    assert _act('play "Coral Guard (1)"') == 0
    assert wire.posts[-1][1]["card_index"] == 0
    _play_index(wire, 0)
    assert _act('play "Coral Guard (2)"') == 0
    assert wire.posts[-1][1]["card_index"] == 0
    assert wire.state["player"]["hand"][0]["cost"] == "0"


def test_a_memory_from_another_turn_names_nothing(lane, monkeypatch):
    wire = _live(monkeypatch, _fight([_guard() for _ in range(3)]))
    assert _observe() == 0
    wire.state["battle"]["round"] = (wire.state["battle"].get("round") or 1) + 1
    shown = blindplay_shape.read_shown_hand()
    assert blindplay_grammar.resolve_shown_card(
        wire.get_state(), 'play "Coral Guard (3)"', shown) == (
        'play "Coral Guard (3)"', None, "")


def test_the_page_and_the_brief_say_the_number_holds():
    from understudy import blindplay_notes
    assert "does not shift as you play" in blindplay_notes.HAND_REPEAT_NOTE
    brief = (blindplay.REPO / "docs" / "current" / "operations"
             / "seat-brief.md").read_text(encoding="utf-8")
    assert "does not shift as" in brief
    assert "opened and left with `skip` is already skipped" in brief
