"""FURINA WHOLE-RUN ROUND 3 (2026-10-11): the seat page and the telemetry.

The review's proposed changes 1-5, none of which moves a rule or a number:

1. The Drain counter leads with the buffer and prints the line as a derived
   number; the zero-line sentence stays.
2. A Repay act's log line and forecast name the Repay floor's Block, as the
   card face does ("(Repays 0, +2 Block)").
3. The incoming fold says what "first" means: before the enemies act, and
   Block takes it.
4. One hand note where an enemy wears Vulnerable or Slow: the faces leave
   them out until a card is aimed.
5. The telemetry report reads the new keys: the Drain buffer left at the
   close, the Guest Star evictions and repeat acts, and Block per card play.

The C# twin is `klee-mod/KleeTests/Prototype/FurinaRound3TelemetryTests.cs`.
"""

from __future__ import annotations

import copy
from pathlib import Path

from understudy import blindplay, blindplay_board, blindplay_render
from tools import telemetry_report

from tier0.tests.test_understudy_blindplay import combat_state

REPO = Path(__file__).resolve().parents[2]


def _wire(**extra) -> dict:
    raw = {"live": True, "fanfare": 4, "drained": 6, "drain_line": 61,
           "drain_line_why": "your HP minus your Drain buffer: 1/4 of your "
                             "Max HP, less what you have drained",
           "entry_hp": 78, "entry_max_hp": 78, "drain_buffer": 19,
           "drain_buffer_left": 13, "seats": [], "log": []}
    raw.update(extra)
    return raw


def _stage(raw: dict, hp: int = 74, max_hp: int = 78) -> list[str]:
    stage = blindplay_board.furina_stage({"furina_stage": raw})
    assert stage is not None
    return blindplay_render._render_stage(
        stage, {"block": 0, "hp": hp, "max_hp": max_hp})


def _drain_line(raw: dict) -> str:
    return next(ln for ln in _stage(raw) if ln.startswith("- Drained "))


# ---- 1. the buffer leads ------------------------------------------------------

def test_the_drain_counter_leads_with_the_buffer():
    assert _drain_line(_wire()) == (
        "- Drained 6 HP. Drain buffer 13 of 19 left: Drain inside it returns "
        "after combat; past it, only Repay returns. Drain line 61 HP.")


def test_the_board_reads_the_buffer_off_the_wire():
    stage = blindplay_board.furina_stage({"furina_stage": _wire()})
    assert stage["buffer"] == 19 and stage["buffer_left"] == 13
    old = _wire()
    del old["drain_buffer"], old["drain_buffer_left"]
    stage = blindplay_board.furina_stage({"furina_stage": old})
    assert stage["buffer"] is None and stage["buffer_left"] is None


def test_the_past_part_still_says_what_it_costs():
    line = _drain_line(_wire(drained=25, drained_past=6,
                             drain_buffer_left=0, drain_line=49))
    assert line == (
        "- Drained 25 HP (6 past your line: lost unless you Repay). Drain "
        "buffer 0 of 19 left: Drain inside it returns after combat; past it, "
        "only Repay returns. Drain line 49 HP.")


def test_a_five_century_act_returns_the_past_part_too():
    line = _drain_line(_wire(drained=25, drained_past=6, past_returns=True,
                             drain_buffer_left=0, drain_line=49))
    assert line == (
        "- Drained 25 HP (6 past your line). Drain buffer 0 of 19 left: all "
        "your Drain returns after combat, past it too. Drain line 49 HP.")


def test_the_zero_line_sentence_stays():
    # On a build that sends no buffer. Furina round 5 (2026-10-11): a buffer
    # build at a line of 0 reads in the buffer's words
    # (`test_furina_round_5_fixes.py`).
    old = _wire(drain_line=0)
    del old["drain_buffer"], old["drain_buffer_left"]
    line = _drain_line(old)
    assert line.startswith("- Drained 6 HP. Drain line 0 HP")
    assert line.endswith(": all your Drain returns after combat.")


def test_an_older_build_keeps_the_line_first_sentence():
    old = _wire()
    del old["drain_buffer"], old["drain_buffer_left"]
    assert _drain_line(old).startswith(
        "- Drained 6 HP. Drained HP above your line returns after combat.")


# ---- 2. the Repay floor -------------------------------------------------------

def _act(member: str, moved: int, floor: int | None) -> dict:
    row = {"event": "act", "member": member, "name": member.capitalize(),
           "seat": 0, "seat_key": 1, "fanfare": 4, "moved": moved}
    if floor is not None:
        row["floor"] = floor
    return row


def _log(*rows) -> list[str]:
    stage = blindplay_board.furina_stage(
        {"furina_stage": _wire(log=list(rows))})
    return blindplay_render._render_stage_log(stage)


def test_charlottes_act_names_the_floor_it_gave():
    assert _log(_act("charlotte", 0, 2)) == [
        "  - **Charlotte** acted: you Repay 0, +2 Block."]
    assert _log(_act("sigewinne", 1, 3)) == [
        "  - **Sigewinne** acted: you Repay 1, +3 Block."]


def test_a_full_repay_or_an_older_build_reads_as_before():
    assert _log(_act("charlotte", 2, 0)) == [
        "  - **Charlotte** acted: you Repay 2."]
    assert _log(_act("charlotte", 0, None)) == [
        "  - **Charlotte** acted: you Repay 0."]


def _forecast(drained: int, hp: int, *amounts: int) -> list[str]:
    acts = [{"member": "charlotte", "name": "Charlotte", "seat_key": n + 1,
             "kind": "repay", "amount": a, "element": "", "target": "",
             "times": 1, "price": 0, "skips": False}
            for n, a in enumerate(amounts)]
    seats = [{"member": "charlotte", "name": "Charlotte", "seat": n,
              "seat_key": n + 1, "guest": True} for n in range(len(amounts))]
    raw = _wire(drained=drained, seats=seats,
                forecast={"fanfare_after": 4, "block": 0, "acts": acts})
    return [ln for ln in _stage(raw, hp=hp) if ln.startswith("  - **")]


def test_the_forecast_names_the_floor_the_face_way():
    # Nothing drained: Repay 2 returns 0, +2 Block.
    assert _forecast(0, 78, 2) == [
        "  - **Charlotte**: Repay 2 (repays 0, +2 Block)"]
    # Drained 1: it returns 1, +1 Block.
    assert _forecast(1, 70, 2) == [
        "  - **Charlotte**: Repay 2 (repays 1, +1 Block)"]
    # Enough drained: the plain words.
    assert _forecast(6, 70, 2) == ["  - **Charlotte**: Repay 2"]
    # Never past her Max HP: 6 drained but 1 HP of room.
    assert _forecast(6, 77, 2) == [
        "  - **Charlotte**: Repay 2 (repays 1, +1 Block)"]


def test_the_forecast_walks_two_repays_front_to_back():
    assert _forecast(3, 70, 2, 2) == [
        "  - **Charlotte**: Repay 2",
        "  - **Charlotte**: Repay 2 (repays 1, +1 Block)"]


# ---- 3. "first" ----------------------------------------------------------------

def test_the_self_hit_fold_says_before_the_enemies_act():
    assert blindplay_render.FOLD_SELF_HIT.format(
        who="Wither x3", verb="hit", n=36) == (
        "Wither x3 hit you for 36 before the enemies act, and your Block "
        "takes it")
    assert " first" not in blindplay_render.FOLD_SELF_HIT


# ---- 4. the Vulnerable and Slow note -------------------------------------------

def _board_with(status: list[dict]) -> dict:
    state = copy.deepcopy(combat_state())
    for enemy in state["battle"]["enemies"]:
        enemy["status"] = copy.deepcopy(status)
    return state


VULNERABLE = {"id": "VULNERABLE_POWER", "name": "Vulnerable", "amount": 2,
              "type": "Debuff",
              "description": "Takes 50% more damage from attacks."}
SLOW = {"id": "SLOW_POWER", "name": "Slow", "amount": 3, "type": "Debuff",
        "description": "Whenever you play a card, this enemy receives 10% "
                       "more damage from attacks this turn."}


def test_the_note_prints_under_the_hand_where_an_enemy_is_vulnerable():
    for status in ([VULNERABLE], [SLOW]):
        page = blindplay.observe(_board_with(status))
        assert blindplay_render.ENEMY_FOLD_NOTE in page
        assert page.count(blindplay_render.ENEMY_FOLD_NOTE) == 1
        hand = page.index("## Your hand")
        assert page.index(blindplay_render.ENEMY_FOLD_NOTE) > hand
    assert blindplay_render.ENEMY_FOLD_NOTE == (
        "*Face numbers leave out the enemy's Vulnerable and Slow until a card "
        "is aimed; the hit lands higher.*")


def test_no_note_without_either_or_without_an_attack_in_hand():
    assert blindplay_render.ENEMY_FOLD_NOTE not in blindplay.observe(
        _board_with([]))
    enemies = [{"name": "A", "hp": 10, "powers": [
        {"name": "Vulnerable", "stacks": 2}]}]
    skill = [{"kind": "Skill", "text": "Gain 5 Block."}]
    attack = [{"kind": "Attack", "text": "Deal 6 damage."}]
    assert blindplay_render._enemy_fold_note(enemies, skill) == []
    assert blindplay_render._enemy_fold_note(enemies, attack) == [
        "", blindplay_render.ENEMY_FOLD_NOTE]
    dead = [dict(enemies[0], hp=0)]
    assert blindplay_render._enemy_fold_note(dead, attack) == []


# ---- 5. the telemetry report reads the new keys ---------------------------------

def _row(**extra) -> dict:
    row = {"record": "fight", "character": "Furina", "act": 1,
           "kind": "monster", "turns": 4, "hp_start": 60, "hp_end": 40,
           "hp_lost": 20, "max_hp": 80, "damage_dealt": 40, "seats": 1,
           "outcome": "won"}
    row.update(extra)
    return row


def test_the_report_reads_the_buffer_and_the_guest_counts():
    rows = [_row(fanfare_peak=9, fanfare_end=3, fanfare_spends=[],
                 drain_buffer=20, drain_buffer_left=14, guest_evictions=1,
                 guest_repeat_acts=2),
            _row(fanfare_peak=9, fanfare_end=3, fanfare_spends=[],
                 drain_buffer=20, drain_buffer_left=0, guest_evictions=0,
                 guest_repeat_acts=1),
            _row()]
    s = telemetry_report.fanfare_summary("Furina", rows)
    assert s["fights_with_buffer"] == 2
    assert s["buffer_left"] == 7 and s["buffer_bound"] == 1
    assert s["guest_evictions"] == 1 and s["guest_repeat_acts"] == 3
    assert any(ln.startswith("Furina")
               for ln in telemetry_report.render_fanfare([s]))
    bare = telemetry_report.fanfare_summary("Furina", [_row()])
    assert bare["buffer_left"] is None and bare["guest_evictions"] is None


def test_the_report_reads_block_per_card_play():
    rows = [_row(cards_played=[[1, "Hymn of Many Waters"], [1, "Strike"],
                               [2, "Defend"]],
                 card_play_block=[9, 0, 5],
                 block_card_turns=1, block_card_turns_no_block=0),
            _row(cards_played=[[1, "Hymn of Many Waters"]],
                 card_play_block=[6]),
            # Misaligned: left out.
            _row(cards_played=[[1, "Defend"]], card_play_block=[5, 5]),
            _row()]
    s = telemetry_report.block_gap_summary("Furina", rows)
    assert s["plays_with_block_key"] == 4
    assert s["block_per_play"] == 5.0
    assert s["block_by_card"] == {"Hymn of Many Waters": (2, 15),
                                  "Defend": (1, 5)}
    lines = telemetry_report.render_block_gap([s])
    assert any("Hymn of Many Waters" in ln for ln in lines)


def test_the_schema_names_the_new_keys():
    readme = (REPO / "understudy" / "README.md").read_text(encoding="utf-8")
    for key in ("drain_buffer_left", "guest_evictions", "guest_repeat_acts",
                "card_play_block"):
        assert f"`{key}`" in readme, key
    cs = (REPO / "klee-mod" / "KleeCode" / "Diagnostics" / "PlayTelemetry.cs"
          ).read_text(encoding="utf-8")
    for key in ("drain_buffer", "drain_buffer_left", "guest_evictions",
                "guest_repeat_acts", "card_play_block"):
        assert f'\\"{key}\\":' in cs, key
