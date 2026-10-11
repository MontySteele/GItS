"""The Klee whole-run round (2026-10-11): the review's no-approval fixes.

1. "Nothing to amplify" prints only on an element-only application
   (`test_seat_fixes_w9b_2026_10_01.py` pins the C# gate).
2. A row's hits and "Put" lines print in play order where the ledger
   stamped them, and in the old order where it did not.
3. The Mine tip says a Mine waits on a turn its enemy does not attack.
4. A Klee card that reads "your largest Bomb" says which enemy's.
5. The `Written:` note names the power on you that moved the number.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from understudy import blindplay, blindplay_faces, blindplay_shape
from understudy.blindplay_board import resolutions
from understudy.blindplay_notes import ARM_KEYWORDS
from understudy.blindplay_render import _resolution_lines

REPO = Path(__file__).resolve().parents[2]
RECORDED_COMBAT = (REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                   / "observed.json")


@pytest.fixture(autouse=True)
def _fresh(tmp_path, monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", tmp_path)
    monkeypatch.setattr(blindplay_faces, "_FIGHT_STORE_DIR", tmp_path)
    monkeypatch.setenv("GITS_LANE", "9")


# ---- 2. play order ----------------------------------------------------------

def _fire_fire(seq: bool) -> list[str]:
    hit = {"target": "Toadpole", "amount": 15, "blocked": 0,
           "combat_id": "2"}
    put = {"target": "Toadpole", "power": "Bomb", "amount": 7,
           "combat_id": "2"}
    if seq:
        put["seq"] = 101
        hit["seq"] = 102
    rows = resolutions({"resolutions": [
        {"card_id": "proto_ko_fire_fire", "card": "Fire! Fire!",
         "hits": [hit], "applied": [put]}]})
    return _resolution_lines(rows)


def test_fire_fire_reads_put_then_hit_in_play_order():
    lines = _fire_fire(seq=True)
    put = next(i for i, ln in enumerate(lines) if "Put **Bomb 7**" in ln)
    hit = next(i for i, ln in enumerate(lines) if "-- 15" in ln)
    assert put < hit
    assert lines[hit].strip().startswith("1.")


def test_an_older_mod_with_no_seq_keeps_hits_then_puts():
    lines = _fire_fire(seq=False)
    put = next(i for i, ln in enumerate(lines) if "Put **Bomb 7**" in ln)
    hit = next(i for i, ln in enumerate(lines) if "-- 15" in ln)
    assert hit < put


# ---- 3. the Mine tip --------------------------------------------------------

MINE = ("A Bomb that also goes off when its enemy attacks you. If it does "
        "not attack, the Mine waits. Any Set off spends it too.")


def test_the_mine_tip_says_it_waits_without_an_attack():
    assert ARM_KEYWORDS["Mine"] == MINE
    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "ArmKeywordTips.cs").read_text(encoding="utf-8")
    assert "If it does not attack, the Mine waits." in src.replace(
        '"\n          + "', "")
    assert len(MINE) <= 135


# ---- 4. "your largest Bomb" ------------------------------------------------

@pytest.mark.parametrize("cls", [
    "ProtoKoStokeTheFuse", "ProtoKoSparksNSplash", "ProtoKoOneMoreCharge",
    "ProtoKoTreasureMap", "ProtoKoHalfAMountain", "ProtoKoFavoniusEscort",
    "ProtoKoHideHere", "ProtoMcAlbedoDustOfPurification"])
def test_a_board_wide_largest_bomb_says_on_any_enemy(cls):
    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "Generated" / f"{cls}.cs").read_text(encoding="utf-8")
    assert "on any enemy" in src


def test_stoke_the_fuse_keeps_its_number_and_its_spend():
    src = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "Generated" / "ProtoKoStokeTheFuse.cs").read_text(encoding="utf-8")
    assert ('"Spend all your remaining [gold]Sparks[/gold]. Your largest '
            '[gold]Bomb[/gold], on any enemy, grows by {Grow:diff()} per '
            '[gold]Spark[/gold] spent."') in src


def test_the_largest_bomb_lint_fires_on_a_face_that_does_not_say_where():
    from tools import lint_text_conventions as lint
    bad = lint.Row("card", "fx", "Your largest [gold]Bomb[/gold] grows by 3.",
                   "fixture")
    ok = lint.Row("card", "fx_ok", "[gold]Set off[/gold] only your largest "
                  "[gold]Bomb[/gold] on the enemy.", "fixture")
    found = lint.findings_for([bad, ok], {}, gate=False)
    assert any("largest-bomb-where" in f and "[fx]" in f for f in found)
    assert not any("[fx_ok]" in f for f in found)


# ---- 5. the Written note names the power ------------------------------------

def _shrunk_attack(powers: list[dict]) -> dict:
    state = json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))["state"]
    state = copy.deepcopy(state)
    state["player"]["hand"] = [
        {"id": "KLEEMOD-PROTO_KK_CORAL_BULWARK", "name": "Coral Bulwark",
         "type": "Skill", "cost": "1", "can_play": True, "index": 0,
         "target_type": "Self", "is_upgraded": False, "keywords": [],
         "description": "Gain 6 Block."}]
    state["player"]["status"] = list(state["player"].get("status") or []) \
        + powers
    return state


def _power(name: str, amount: int, debuff: bool = True) -> dict:
    return {"id": name.upper() + "_POWER", "name": name, "amount": amount,
            "is_debuff": debuff, "description": f"{name}."}


def test_the_written_note_names_the_block_power_on_you():
    page = blindplay.observe(_shrunk_attack([_power("Frail", 2)]))
    assert "Written: Gain 8 Block." in page
    assert "the difference is the board's: your **Frail**.)" in page


def test_a_damage_power_is_not_named_on_a_block_face():
    page = blindplay.observe(_shrunk_attack([_power("Shrink", 1)]))
    assert "Written: Gain 8 Block." in page
    assert "the difference is the board's.)" in page
    assert "your **Shrink**" not in page


def test_the_written_note_names_shrink_on_a_damage_face():
    """Lane 5 read Shrink's smaller number as Weak's."""
    state = _shrunk_attack([_power("Shrink", 1), _power("Frail", 1)])
    state["player"]["hand"] = [
        {"id": "KLEEMOD-PROTO_KO_POCKET_MATCH", "name": "Pocket Match",
         "type": "Attack", "cost": "0", "can_play": True, "index": 0,
         "target_type": "AnyEnemy", "is_upgraded": False, "keywords": [],
         "description": "[gold]Set off[/gold] only your largest "
                        "[gold]Bomb[/gold] on the enemy. Deal 4 "
                        "[gold]Pyro[/gold] damage."}]
    page = blindplay.observe(state)
    assert "Written: Set off only your largest Bomb on the enemy. Deal 6 " \
        "Pyro damage." in page
    assert "the difference is the board's: your **Shrink**.)" in page
