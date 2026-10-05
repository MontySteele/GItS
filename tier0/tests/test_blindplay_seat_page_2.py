"""The seat-page pass (2026-10-05): the enemy briefing, the incoming line and
the since-last-page line.

The owner's terms: help a seat decide like an experienced human without
bloating the page, never print a best play, and keep the seat blind to the
mod's design (base-game knowledge -- enemies, their moves, their powers -- is
fair game).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from understudy import (blindplay, blindplay_board, blindplay_brief,
                        blindplay_enemies, blindplay_render, blindplay_shape,
                        qa_packet)

REPO = Path(__file__).resolve().parents[2]
RECORDED_COMBAT = (REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                   / "observed.json")


@pytest.fixture(autouse=True)
def _fresh(tmp_path, monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", tmp_path)
    monkeypatch.setenv("GITS_LANE", "9")
    blindplay.forget_fight()
    blindplay.forget_run()
    yield
    blindplay.forget_fight()
    blindplay.forget_run()


def combat(**battle) -> dict:
    state = json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))["state"]
    state = copy.deepcopy(state)
    state["battle"].update(battle)
    return state


def body(entity_id: str, name: str, combat_id: int, intents=None,
         status=None, hp: int = 40) -> dict:
    return {"entity_id": entity_id, "combat_id": combat_id, "name": name,
            "hp": hp, "max_hp": hp, "block": 0, "status": status or [],
            "intents": intents if intents is not None else [
                {"type": "Attack", "label": "6", "title": "Aggressive",
                 "description": "This enemy intends to Attack for 6 "
                                "damage."}]}


# ------------------------------------------------------ the briefing table --


def test_every_elite_and_boss_body_has_a_briefing():
    missing = sorted(blindplay_enemies.ELITE_AND_BOSS_IDS
                     - set(blindplay_enemies.ENEMY_BRIEFS))
    assert not missing, f"no briefing for {missing}"


@pytest.mark.parametrize("key", sorted(blindplay_enemies.ENEMY_BRIEFS))
def test_a_briefing_is_short_blind_and_never_a_play(key):
    name, text = blindplay_enemies.ENEMY_BRIEFS[key]
    line = f"*{name}* — {text}"
    qa_packet.assert_blind(line)
    # Never a line the brief page's safety net would mistake for an intent,
    # a refusal or a verb: it would turn every round-1 brief page full.
    assert not blindplay_brief.PROTECTED.search(line), line
    assert blindplay_brief.GLOSS_LINE.match(line)
    assert len(text) <= 400, (key, len(text))
    assert text.count(". ") <= 4, key
    for word in ("should", "best", "you want", "kill it first", "save "):
        assert word not in text.casefold(), (key, word)


def test_the_key_drops_the_wire_ordinal():
    assert blindplay_enemies.brief_key("DECIMILLIPEDE_SEGMENT_FRONT_0") == \
        "DECIMILLIPEDE_SEGMENT_FRONT"
    assert blindplay_enemies.enemy_brief("ROCKET_1").startswith("Right arm")
    assert blindplay_enemies.enemy_brief("NIBBIT_0") == ""


# ----------------------------------------------------------- the briefing --


def kaiser(round_: int = 1) -> dict:
    return combat(round=round_, enemies=[
        body("CRUSHER_0", "Crusher", 1),
        body("ROCKET_0", "Rocket", 2)])


def test_round_one_prints_what_each_enemy_does():
    page = blindplay.observe(kaiser())
    assert blindplay_render.BRIEFING_HEADING in page
    assert "*Crusher* — Left arm of the Kaiser Crab" in page
    assert "*Rocket* — Right arm of the Kaiser Crab" in page
    assert "Crab Rage" in page


def test_later_rounds_do_not_print_it():
    page = blindplay.observe(kaiser(round_=2))
    assert blindplay_render.BRIEFING_HEADING not in page


def test_one_row_per_kind_of_enemy():
    state = combat(round=1, enemies=[
        body(f"EXOSKELETON_{n}", "Exoskeleton", n + 1) for n in range(3)])
    page = blindplay.observe(state)
    assert page.count("Hard To Kill 9") == 1
    assert "*Exoskeleton* —" in page


def test_an_enemy_the_table_does_not_know_prints_no_section():
    page = blindplay.observe(combat(round=1))
    assert blindplay_render.BRIEFING_HEADING not in page


def test_the_brief_page_never_trims_the_briefing():
    """Seat page 3: once per FIGHT, by the fight's memory
    (`test_blindplay_seat_page_3`), and never cut as a word the lane saw."""
    seen: set[str] = set()
    first = blindplay_brief.brief(blindplay.observe(kaiser()), seen)
    second = blindplay_brief.brief(blindplay.observe(kaiser()), seen)
    assert "*Crusher* —" in first
    assert blindplay_render.BRIEFING_HEADING in first
    assert "*Crusher* —" in second


def test_define_finds_an_enemy_after_round_one():
    out = blindplay_brief.define(blindplay.observe(kaiser(round_=3)),
                                 "Rocket")
    assert out.startswith("- **Rocket** — Right arm")
    assert blindplay_brief.OFF_SCREEN_MARK in out


# --------------------------------------------------------- the incoming line


def incoming(state: dict) -> str:
    lines = [ln for ln in blindplay.observe(state).splitlines()
             if ln.startswith("- Incoming this turn")]
    assert len(lines) == 1
    return lines[0]


def test_incoming_sums_single_and_multi_hits_against_block():
    state = combat(round=2, enemies=[
        body("CRUSHER_0", "Crusher", 1, intents=[
            {"type": "Attack", "label": "5x2", "title": "Bug Sting"}]),
        body("ROCKET_0", "Rocket", 2, intents=[
            {"type": "Attack", "label": "8", "title": "Precision Beam"},
            {"type": "Buff", "label": "", "title": "Charge Up"}])])
    state["player"]["block"] = 5
    assert incoming(state) == ("- Incoming this turn: 18 (your Block 5): "
                               "you would take 13. You would be at 11/70 HP.")


def test_incoming_reads_the_games_breakdown_first():
    state = combat(round=2, enemies=[
        body("ROCKET_0", "Rocket", 2, intents=[
            {"type": "Attack", "label": "9x3", "title": "Laser",
             "breakdown": {"base_damage": 6, "folded_damage": 9,
                           "repeats": 3, "total_damage": 27,
                           "modifiers": ["Strength"]}}])])
    assert incoming(state) == ("- Incoming this turn: 27 (your Block 0): "
                               "you would take 27. You would be at 0/70 HP.")


def test_incoming_says_unknown_where_the_label_may_not_count_weak():
    state = combat(round=2, enemies=[
        body("ROCKET_0", "Rocket", 2, status=[
            {"id": "WEAK_POWER", "name": "Weak", "amount": 1, "type": "Debuff",
             "description": "Deals 25% less damage."}]),
        body("CRUSHER_0", "Crusher", 1)])
    line = incoming(state)
    assert line.startswith("- Incoming this turn: 6 plus an unknown amount "
                           "from Rocket")
    assert "you would take" not in line


def test_incoming_with_no_attack_says_so():
    state = combat(round=2, enemies=[
        body("ROCKET_0", "Rocket", 2, intents=[
            {"type": "Buff", "label": "", "title": "Charge Up"}])])
    assert incoming(state) == blindplay_render.INCOMING_NONE


def test_the_brief_page_keeps_the_incoming_line():
    page = blindplay_brief.brief(blindplay.observe(kaiser(round_=2)), set())
    assert "- Incoming this turn: 12 (your Block 0)" in page


# ---------------------------------------------------- since the last page --


def ledger(*rows) -> list[dict]:
    return list(rows)


def card_row(card: str, events=()) -> dict:
    return {"card_id": card.upper(), "card": card, "auto_played": False,
            "carried": False, "overflowed": False, "hits": [], "applied": [],
            "summoned": [], "oath": [], "between": False,
            "events": list(events)}


def between_row(events) -> dict:
    row = card_row("", events)
    row.update(card_id="", between=True)
    return row


def ev(kind, seq, card="", target="", power="", combat_id="",
       on_player=False) -> dict:
    return {"kind": kind, "card": card, "target": target, "power": power,
            "combat_id": combat_id, "on_player": on_player, "seq": seq}


def with_events(rows) -> dict:
    state = kaiser(round_=2)
    state["player"]["resolutions"] = rows
    return state


ROWS = [
    card_row("Acrobatics", [ev("drawn", 101, card="Strike"),
                            ev("drawn", 102, card="Strike"),
                            ev("drawn", 103, card="Defend")]),
    between_row([ev("negated", 104, target="Crusher", power="Weak",
                    combat_id="1"),
                 ev("negated", 105, power="Frail", on_player=True)]),
    card_row("Bash", [ev("triggered", 106, target="Rocket",
                         power="Crab Rage", combat_id="2")]),
]


def since(state: dict) -> list[str]:
    return [ln for ln in blindplay.observe(state).splitlines()
            if ln.startswith(blindplay_render.EVENTS_HEAD)]


def test_the_line_names_what_the_page_does_not_show():
    assert since(with_events(ROWS)) == [
        "- Since last page: drew Strike x2 and Defend (Acrobatics); "
        "Artifact negated Weak on Crusher; your Artifact negated Frail; "
        "Rocket's Crab Rage fired."]


def test_a_row_with_no_card_is_not_a_resolution():
    rows = blindplay_board.resolutions({"resolutions": ROWS})
    assert [r["card"] for r in rows] == ["Acrobatics", "Bash"]


def test_no_events_no_line():
    assert since(with_events([card_row("Strike")])) == []
    assert since(kaiser(round_=2)) == []


def test_the_printing_door_prints_only_what_is_new(tmp_path, capsys):
    raw = tmp_path / "state.json"
    raw.write_text(json.dumps(with_events(ROWS[:1])), encoding="utf-8")
    args = blindplay.argparse.Namespace(raw_file=str(raw), brief=True,
                                        define="")
    blindplay.cmd_observe(args)
    first = capsys.readouterr().out
    assert "drew Strike x2 and Defend" in first
    assert blindplay_shape.read_events_seen() == 103

    raw.write_text(json.dumps(with_events(ROWS)), encoding="utf-8")
    blindplay.cmd_observe(args)
    second = capsys.readouterr().out
    assert "drew Strike" not in second
    assert "Rocket's Crab Rage fired" in second

    blindplay.cmd_observe(args)
    assert blindplay_render.EVENTS_HEAD not in capsys.readouterr().out


def test_the_line_is_capped():
    many = [card_row(f"Card {n}", [ev("triggered", 200 + n, target=f"E{n}",
                                      power="Hard To Kill")])
            for n in range(12)]
    (line,) = since(with_events(many))
    assert line.endswith("and 4 more.")
