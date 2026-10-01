"""The seat rounds of 2026-10-01 (Varka, Furina, Kokomi): the bridge and
page defects they found, each pinned against the board it was found on.

Records: `review/records/varka-identities-round-2026-10-01.md`,
`varka-expansion-round-2026-10-01.md`, `furina-pool-round-2026-10-01.md`.
The lane-death fix (a slow state read retried, never torn down) is pinned in
`test_understudy_lanewatch.py`, and `--brief`'s glosses in
`test_blindplay_brief.py`.
"""
from __future__ import annotations

import argparse
import json

import pytest

from understudy import blindplay, blindplay_shape, lanewatch


@pytest.fixture(autouse=True)
def _lane(tmp_path, monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", tmp_path)
    monkeypatch.delenv(blindplay.LANE_ENV, raising=False)
    monkeypatch.delenv(blindplay.MAX_ACTIONS_ENV, raising=False)
    monkeypatch.setattr(lanewatch, "guard", lambda *a, **k: "")
    blindplay.forget_fight()
    blindplay.forget_run()
    yield tmp_path
    blindplay.forget_fight()
    blindplay.forget_run()


class _Wire:
    """Serves one state and records every POST."""

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


def _enemy(eid, name, hp=30):
    return {"entity_id": eid, "combat_id": eid, "name": name, "hp": hp,
            "max_hp": 44, "block": 0, "status": [],
            "intents": [{"type": "Attack", "label": "11"}]}


def _combat(enemies, hand=None) -> dict:
    return {"state_type": "monster",
            "player": {"character": "Varka", "hp": 13, "max_hp": 80,
                       "block": 4, "energy": 4, "max_energy": 4,
                       "hand": hand if hand is not None else [
                           {"index": 0, "id": "STRIKE", "name": "Strike",
                            "cost": 1, "type": "Attack",
                            "description": "Deal 6 damage.",
                            "target_type": "AnyEnemy", "can_play": True,
                            "keywords": []}],
                       "potions": [], "relics": [], "status": [],
                       "draw_pile_count": 5, "discard_pile_count": 0,
                       "exhaust_pile_count": 0},
            "battle": {"round": 4, "turn": "player", "is_play_phase": True,
                       "enemies": enemies}}


# --------------------- Varka lane 1, act 3: the dead boss, revive pending --

def test_an_aimed_card_with_no_living_enemy_says_so():
    """Test Subject's first phase died with its revive pending; `play "Jean
    -- Wind Companion"` was refused "there is more than one enemy, so say
    which" with no enemy listed."""
    res = blindplay.act(_combat([]), 'play "Strike"')
    assert not res["ok"]
    assert "more than one enemy" not in res["refusal"]
    assert "dead or waiting to revive" in res["refusal"]


def test_a_corpse_on_the_wire_is_not_counted_as_a_second_target():
    state = _combat([_enemy("cubex_1", "Cubex Construct", hp=0),
                     _enemy("punch_1", "Punch Construct")])
    res = blindplay.act(state, 'play "Strike"')
    assert res["ok"], res["refusal"]
    assert res["post"]["target"] == "punch_1"


# ------------- Varka lane 2, act 3: a refused batch must not end the turn --

def test_an_end_turn_after_a_refusal_on_the_same_board_is_held_once(
        monkeypatch, capsys):
    """The seat batched three bare plays and `end turn` against three
    enemies; every play was refused and the turn ended anyway."""
    wire = _live(monkeypatch, _combat([_enemy("punch_1", "Punch Construct"),
                                       _enemy("cubex_1", "Cubex Construct")]))
    assert _act('play "Strike"') == 1
    assert _act("end turn") == 1
    out = capsys.readouterr().out
    assert "was not ended" in out and 'play "Strike"' in out
    assert wire.posts == []
    # Said again, it ends the turn.
    assert _act("end turn") == 0
    assert [a for a, _ in wire.posts] == ["end_turn"]


def test_an_end_turn_with_no_refusal_before_it_goes_straight_through(
        monkeypatch):
    wire = _live(monkeypatch, _combat([_enemy("punch_1", "Punch Construct")]))
    assert _act('play "Strike"') == 0
    assert _act("end turn") == 0
    assert [a for a, _ in wire.posts] == ["play_card", "end_turn"]


def test_a_refusal_on_another_board_does_not_hold_the_end_turn(monkeypatch):
    two = _combat([_enemy("punch_1", "Punch Construct"),
                   _enemy("cubex_1", "Cubex Construct")])
    _live(monkeypatch, two)
    assert _act('play "Strike"') == 1
    moved = json.loads(json.dumps(two))
    moved["player"]["energy"] = 3
    wire = _live(monkeypatch, moved)
    assert _act("end turn") == 0
    assert [a for a, _ in wire.posts] == ["end_turn"]


# ---------- Furina, act 3: Ransack's potion and the Crystal Sphere's gold --

def _rewards(*rows) -> dict:
    return {"state_type": "rewards",
            "player": {"character": "Furina", "hp": 33, "max_hp": 109,
                       "gold": 63, "potions": [], "potion_slots": 3,
                       "relics": []},
            "rewards": {"items": list(rows), "can_proceed": True}}


HEART = {"index": 0, "type": "potion", "description": "Heart of Iron",
         "potion_id": "HEART_OF_IRON", "potion_name": "Heart of Iron",
         "potion_description": "Gain 6 Plating.", "keywords": []}
GOLD = {"index": 1, "type": "gold", "description": "30 Gold",
        "gold_amount": 30}
CARD = {"index": 0, "type": "card", "description": "Add a card to your deck"}


def test_proceed_past_an_unclaimed_potion_is_held_once(monkeypatch, capsys):
    """Potion Courier's Ransack offered Heart of Iron (the run history has
    it, `was_picked: false`) and the seat walked on without it."""
    wire = _live(monkeypatch, _rewards(HEART, GOLD))
    assert _act("proceed") == 1
    out = capsys.readouterr().out
    assert "Heart of Iron" in out and "30 Gold" in out
    assert wire.posts == []
    assert _act("proceed") == 0
    assert [a for a, _ in wire.posts] == ["proceed"]


def test_a_card_offer_alone_does_not_hold_proceed(monkeypatch):
    """Skipping a card reward is the screen's own choice, not a drop."""
    wire = _live(monkeypatch, _rewards(CARD))
    assert _act("proceed") == 0
    assert [a for a, _ in wire.posts] == ["proceed"]


def test_leave_on_the_spheres_reward_screen_is_its_proceed():
    """The sphere's exit is `leave`; once its divinations are spent the game
    hands over a reward screen, where `leave` was refused "use proceed"."""
    res = blindplay.act(_rewards(GOLD), "leave")
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "proceed"}


def test_leave_on_the_spheres_reward_screen_keeps_the_unclaimed_check(
        monkeypatch, capsys):
    wire = _live(monkeypatch, _rewards(GOLD))
    assert _act("leave") == 1
    assert "30 Gold" in capsys.readouterr().out
    assert wire.posts == []


# ------------------ Varka lane 1, act 3: the ? room's merchant with shelves --

def _fake_merchant() -> dict:
    """`BuildFakeMerchantState`'s shape: the shelves sit one level deeper,
    under `fake_merchant.shop.items`."""
    return {"state_type": "fake_merchant",
            "player": {"character": "Varka", "hp": 60, "max_hp": 80,
                       "gold": 364, "potions": [], "relics": []},
            "fake_merchant": {
                "event_id": "FAKE_MERCHANT", "event_name": "Merchant?",
                "started_fight": False,
                "shop": {"can_proceed": True, "items": [
                    {"index": 0, "category": "relic", "price": 150,
                     "is_stocked": True, "can_afford": True,
                     "relic_id": "FAKE_ANCHOR", "relic_name": "Anchor?",
                     "relic_description": "Start each combat with 4 Block.",
                     "keywords": []}]}}}


def test_the_fake_merchants_shelves_are_printed_and_bought():
    page = blindplay.observe(_fake_merchant())
    assert "Anchor?" in page
    assert "returned no shelves" not in page
    res = blindplay.act(_fake_merchant(), 'buy "Anchor?"')
    assert res["ok"], res["refusal"]
    assert res["post"] == {"action": "shop_purchase", "index": 0}
