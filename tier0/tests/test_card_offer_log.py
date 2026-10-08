"""The card-offer log and its reader (project review 2026-10-08, pick 10).

The writer (`understudy/offer_log.py`) turns one POSTED `blindplay act` on an
offer screen into one JSONL row; the reader (`tools/offer_report.py`) folds
those rows into offers and counts offered / taken per card.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from understudy import offer_log
from understudy.blindplay_grammar import act

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
import offer_report  # noqa: E402
import telemetry_report  # noqa: E402


def _player(deck=()):
    return {"character": "Varka", "hp": 70, "max_hp": 80, "gold": 300,
            "master_deck": [{"name": n} for n in deck], "potions": []}


def _card(i, name, cid, rarity="Uncommon", upgraded=False):
    return {"index": i, "id": cid, "name": name + ("+" if upgraded else ""),
            "type": "Skill", "cost": "1", "rarity": rarity,
            "is_upgraded": upgraded, "description": "Text."}


RUN = {"act": 1, "floor": 6, "ascension": 0}
REWARD = {"state_type": "card_reward", "run": RUN, "player": _player(),
          "card_reward": {"can_skip": True, "cards": [
              _card(0, "Deep Freeze", "KLEEMOD-PROTO_VK_DEEP_FREEZE"),
              _card(1, "Blazing Charge", "KLEEMOD-PROTO_VK_BLAZING_CHARGE",
                    upgraded=True),
              _card(2, "Pommel Strike", "POMMEL_STRIKE", "Common")]}}
MAP = {"state_type": "map", "run": dict(RUN, floor=5), "player": _player(),
       "map": {"next_options": [{"index": 0, "type": "Monster"},
                                {"index": 1, "type": "Elite"}]}}


def _shop():
    return {"state_type": "shop", "run": RUN, "player": _player(),
            "shop": {"can_proceed": True, "items": [
                {"index": 0, "category": "card", "price": 75,
                 "is_stocked": True, "can_afford": True,
                 "card_id": "KLEEMOD-PROTO_VK_ABSOLUTE_ZERO",
                 "card_name": "Absolute Zero", "card_type": "Power",
                 "card_cost": "2", "card_rarity": "Rare",
                 "card_description": "Text."},
                {"index": 1, "category": "card", "price": 50,
                 "is_stocked": True, "can_afford": True,
                 "card_id": "KLEEMOD-PROTO_VK_PYRE_OATH",
                 "card_name": "Pyre Oath", "card_type": "Power",
                 "card_cost": "1", "card_rarity": "Uncommon",
                 "card_description": "Text."},
                {"index": 2, "category": "relic", "price": 150,
                 "is_stocked": True, "can_afford": True,
                 "relic_name": "Anchor", "relic_description": "Text."}]}}


def _record(state, command):
    res = act(state, command)
    assert res["ok"], res["refusal"]
    return offer_log.record(state, res, command)


def _rows():
    path = offer_log.log_path()
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]


# ----------------------------------------------------------------- writer --

def test_a_taken_card_reward_names_the_cards_the_pick_and_the_room():
    _record(MAP, 'go "Elite (path 2)"')
    row = _record(REWARD, 'choose "Deep Freeze"')
    assert row["screen"] == "card_reward" and row["outcome"] == "taken"
    assert row["room"] == "elite"
    assert [c["name"] for c in row["offered"]] == [
        "Deep Freeze", "Blazing Charge", "Pommel Strike"]
    assert row["offered"][1]["upgraded"] is True
    assert row["taken"][0]["id"] == "KLEEMOD-PROTO_VK_DEEP_FREEZE"
    assert (row["character"], row["act"], row["floor"]) == ("Varka", 1, 6)
    assert row["lane"] == "lane0"
    assert _rows() == [row]


def test_a_skipped_card_reward_is_skipped_with_nothing_taken():
    row = _record(REWARD, "skip")
    assert row["outcome"] == "skipped" and row["taken"] == []


def test_a_shop_logs_card_shelves_only_and_a_buy_is_bought():
    row = _record(_shop(), 'buy "Pyre Oath"')
    assert row["screen"] == "shop" and row["outcome"] == "bought"
    assert [c["name"] for c in row["offered"]] == ["Absolute Zero",
                                                    "Pyre Oath"]
    assert row["offered"][0]["price"] == 75
    assert row["taken"][0]["name"] == "Pyre Oath"
    assert _record(_shop(), "proceed")["outcome"] == "seen"
    assert _record(_shop(), 'buy "Anchor"')["outcome"] == "seen"


def test_an_event_chooser_out_of_a_fight_is_an_offer():
    state = {"state_type": "card_select", "run": RUN, "player": _player(),
             "card_select": {"screen_type": "choose",
                             "prompt": "Choose a card.", "cards": [
                                 _card(0, "Wildfire Oath",
                                       "KLEEMOD-PROTO_VK_WILDFIRE_OATH"),
                                 _card(1, "Pommel Strike", "POMMEL_STRIKE")]}}
    row = _record(state, 'choose "Wildfire Oath"')
    assert row["screen"] == "choose" and row["taken"][0]["name"] == \
        "Wildfire Oath"


def test_a_chooser_inside_a_fight_and_the_deck_screens_are_not_offers():
    fight = {"state_type": "card_select", "run": RUN, "player": _player(),
             "battle": {"round": 1},
             "card_select": {"screen_type": "choose", "cards": [
                 _card(0, "A", "A"), _card(1, "B", "B")]}}
    deck = {"state_type": "card_select", "run": RUN, "player": _player(),
            "card_select": {"screen_type": "select", "cards": [
                _card(0, "Strike", "STRIKE")]}}
    for state in (fight, deck):
        res = {"ok": True, "verb": "choose", "post": {"index": 0},
               "printed": {}}
        assert offer_log.offer_row(state, res) is None


def test_a_simple_grid_of_deck_cards_is_a_deck_operation():
    state = {"state_type": "card_select", "run": RUN,
             "player": _player(deck=("Strike", "Defend")),
             "card_select": {"screen_type": "simple_select", "cards": [
                 _card(0, "Strike", "STRIKE")]}}
    res = {"ok": True, "verb": "choose", "post": {"index": 0}, "printed": {}}
    assert offer_log.offer_row(state, res) is None
    state["card_select"]["cards"] = [_card(0, "Deep Freeze", "X")]
    assert offer_log.offer_row(state, res)["screen"] == "simple_select"


def test_a_bundle_takes_every_card_in_the_chosen_bundle():
    state = {"state_type": "bundle_select", "run": RUN, "player": _player(),
             "bundle_select": {"bundles": [
                 {"index": 0, "cards": [_card(0, "A", "A"),
                                        _card(1, "B", "B")]},
                 {"index": 1, "cards": [_card(0, "C", "C")]}]}}
    res = {"ok": True, "verb": "choose", "post": {"index": 1}, "printed": {}}
    row = offer_log.offer_row(state, res)
    assert [c["bundle"] for c in row["offered"]] == [0, 0, 1]
    assert [c["name"] for c in row["taken"]] == ["C"]


def test_leaving_an_unopened_card_reward_is_counted():
    state = {"state_type": "rewards", "run": RUN, "player": _player(),
             "rewards": {"can_proceed": True, "items": [
                 {"index": 0, "type": "card",
                  "description": "Add a card to your deck"}]}}
    res = {"ok": True, "verb": "proceed", "post": {"action": "proceed"},
           "printed": {}}
    row = offer_log.offer_row(state, res)
    assert row["screen"] == "card_reward_unopened" and row["offered"] == []


def test_other_commands_write_nothing_and_record_never_raises():
    res = {"ok": True, "verb": "end turn", "post": {}, "printed": {}}
    assert offer_log.record({"state_type": "monster"}, res) is None
    assert offer_log.record(None, None) is None          # type: ignore[arg-type]
    assert _rows() == []


def test_the_row_carries_the_lane_embark_and_seed(monkeypatch):
    from understudy import blindplay_shape as shape
    monkeypatch.setenv("GITS_LANE", "3")
    d = shape.lane_state_dir("3")
    d.mkdir(parents=True, exist_ok=True)
    (d / "embark-20261008-120000.json").write_text(json.dumps(
        {"instance": "lane3", "stamp": "20261008-120000",
         "run_seed": "ABC123"}), encoding="utf-8")
    row = _record(REWARD, "skip")
    assert (row["lane"], row["embark"], row["seed"]) == (
        "lane3", "20261008-120000", "ABC123")
    assert offer_log.log_path().name == "card-offers-lane3.jsonl"


# ----------------------------------------------------------------- reader --

def _args(**kw):
    base = dict(character=None, element=None, rarity=None, type=None,
                tag=None, card=None, embark=None, since=None)
    base.update(kw)
    return argparse.Namespace(**base)


def _sheet():
    return offer_report.load_sheet(REPO / "docs" / "prototype-surface.yaml")


def test_a_reward_skipped_then_taken_is_one_taken_offer():
    _record(REWARD, "skip")
    _record(REWARD, 'choose "Deep Freeze"')
    offers = offer_report.fold(_rows())
    assert len(offers) == 1 and offers[0]["outcome"] == "taken"
    table = offer_report.card_table(offers, _sheet())
    deep = next(r for r in table if r["card"] == "Deep Freeze")
    assert (deep["offered"], deep["taken"], deep["rate"]) == (1, 1, 1.0)
    assert deep["owner"] == "varka" and deep["elements"] == ["cryo"]
    blaze = next(r for r in table if r["card"] == "Blazing Charge")
    assert (blaze["offered"], blaze["taken"], blaze["upgraded"]) == (1, 0, 1)
    assert "pyro" in blaze["elements"]


def test_a_shop_visit_is_one_offer_and_unopened_drops_when_opened():
    _record(_shop(), 'buy "Pyre Oath"')
    _record(_shop(), "proceed")
    rows = _rows() + [dict(_rows()[0], screen="card_reward_unopened",
                           offered=[], taken=[], outcome="unopened",
                           floor=9)]
    offers = offer_report.fold(rows)
    assert sorted(o["screen"] for o in offers) == [
        "card_reward_unopened", "shop"]
    shop = next(o for o in offers if o["screen"] == "shop")
    assert shop["outcome"] == "bought"
    rows.append(dict(rows[-1], screen="card_reward", offered=[], taken=[],
                     outcome="skipped"))
    assert "card_reward_unopened" not in {
        o["screen"] for o in offer_report.fold(rows)}


def test_the_element_filter_and_the_never_offered_list():
    _record(REWARD, 'choose "Deep Freeze"')
    report = offer_report.build(
        _args(character=["Varka"], element=["cryo"]), _rows(), _sheet())
    (entry,) = report["characters"]
    assert [r["card"] for r in entry["cards"]] == ["Deep Freeze"]
    never = {r["card"] for r in entry["never_offered"]}
    assert "Absolute Zero" in never and "Deep Freeze" not in never
    assert "Blazing Charge" not in never           # pyro only
    text = offer_report.render(report, 10)
    assert "Deep Freeze" in text and "never offered" in text


def test_telemetry_report_offers_delegates(tmp_path, capsys):
    _record(REWARD, "skip")
    code = telemetry_report.main(["--offers", "--dir",
                                  str(offer_log.log_dir())])
    assert code == 0
    out = capsys.readouterr().out
    assert "== Varka" in out and "card_reward: 1 offers" in out
