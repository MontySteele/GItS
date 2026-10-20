"""FURINA'S HP LEGIBILITY PASS (2026-10-19,
`review/active/furina-hp-legibility-2026-10-19.md`, all picks (a)).

The Python half: the seat page's "HP A -> B" line lists what moved her HP
(Drain, Repay, the refund after a fight, the rest), so it agrees with the
header; and the telemetry report counts the Rising Applause Spends made
with another Spend card in hand. No rule or number moves. Fanfare's tip
(change 5) is not built: the text lint allows no parentheses in a tip.

The C# twin is `klee-mod/KleeTests/Prototype/FurinaHpLegibilityTests.cs`.
"""

from __future__ import annotations

from pathlib import Path

from tools import telemetry_report
from understudy import blindplay_faces, blindplay_render

from tier0.tests.test_furina_round_3_page import _row

REPO = Path(__file__).resolve().parents[2]


def _player(hp: int, drained: int | None = None, repaid: int = 0,
            events: list[dict] | None = None) -> dict:
    player: dict = {"hp": hp, "max_hp": 78}
    if drained is not None:
        player["furina_stage"] = {"live": True,
                                  "drained_this_combat": drained,
                                  "repaid_this_combat": repaid}
    if events is not None:
        player["resolutions"] = [{"card": "", "events": events}]
    return player


def _snap(player: dict, floor: int = 3) -> dict:
    snap = {"hp": player["hp"], "floor": floor}
    snap.update(blindplay_faces._hp_ledger_snapshot(player))
    return snap


# ---- the HP-change line ----------------------------------------------------------

def test_a_fight_turn_lists_drain_repay_and_the_rest():
    # Lane 2's case: header 30, then 27 after Regina's Drain 3, Lyney's
    # Drain 2 and Salon Solitaire's Repay 1, and a 1 HP hit.
    before = _snap(_player(30, drained=10, repaid=2, events=[]))
    here = _snap(_player(25, drained=15, repaid=3, events=[]))
    parts = blindplay_faces._hp_parts(before, here)
    assert parts == {"drained": 5, "repaid": 1, "other": -1}
    assert (blindplay_render._hp_parts_clause(parts)
            == " (Drain −5, Repay +1, hits and other changes −1)")


def test_the_fight_end_names_the_refund():
    # Lane 1's case: "HP 49 -> 50, up 1" after "Drained 3 HP returned".
    before = _snap(_player(49, drained=8, events=[
        {"kind": "drawn", "seq": 40}]))
    here = _snap(_player(50, events=[
        {"kind": "curtain", "seq": 41, "amount": 3}]), floor=3)
    parts = blindplay_faces._hp_parts(before, here)
    assert parts["returned"] == 3
    assert parts["other"] == -2
    lines = blindplay_render._render_run_change(
        {"hp": [49, 50], "max_hp": 78, "room_changed": True,
         "hp_settled": True, "hp_parts": parts})
    assert ("- HP 49 → 50 (of 78), up 1 (returned after the fight +3, "
            "hits and other changes −2)") in lines


def test_a_curtain_already_read_is_not_counted_twice():
    curtain = [{"kind": "curtain", "seq": 41, "amount": 3}]
    before = _snap(_player(50, events=curtain))
    here = _snap(_player(44, events=curtain))
    assert blindplay_faces._hp_parts(before, here) == {}


def test_another_seat_reads_as_before():
    before = _snap({"hp": 40, "max_hp": 70})
    here = _snap({"hp": 35, "max_hp": 70})
    assert blindplay_faces._hp_parts(before, here) == {}
    assert blindplay_render._hp_parts_clause({}) == ""
    lines = blindplay_render._render_run_change(
        {"hp": [40, 35], "max_hp": 70, "room_changed": True,
         "hp_settled": True})
    assert "- HP 40 → 35 (of 70), down 5" in lines


def test_the_wire_sends_the_gross_counts():
    cs = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
          / "FurinaStageLedger.cs").read_text(encoding="utf-8")
    assert 'snapshot["drained_this_combat"] = ledger.DrainedThisCombat;' in cs
    assert 'snapshot["repaid_this_combat"] = ledger.RepaidThisCombat;' in cs


# ---- telemetry --------------------------------------------------------------------

def test_the_report_counts_rising_applause_spends_with_another_in_hand():
    rows = [_row(fanfare_peak=9, fanfare_end=0, fanfare_spends=[],
                 rising_applause_plays=[
                     [1, 12, ["Bravura", "Bring the House Down+"]],
                     [2, 6, []],
                     [3, 0, ["Bravura"]]]),          # no bank: not a Spend
            _row(fanfare_peak=9, fanfare_end=0, fanfare_spends=[],
                 rising_applause_plays=[[2, 20, ["Bravura"]]]),
            _row()]
    s = telemetry_report.fanfare_summary("Furina", rows)
    assert s["rising_applause_spends"] == 3
    assert s["rising_applause_with_other"] == 2
    assert s["rising_applause_others"] == {"Bravura": 2,
                                           "Bring the House Down+": 1}
    lines = telemetry_report.render_fanfare([s])
    assert any("Rising Applause Spends 3, with another Spend card in hand 2"
               in ln for ln in lines)
    bare = telemetry_report.fanfare_summary("Furina", [_row()])
    assert bare["rising_applause_spends"] is None


def test_the_schema_names_the_new_key():
    readme = (REPO / "understudy" / "README.md").read_text(encoding="utf-8")
    cs = (REPO / "klee-mod" / "KleeCode" / "Diagnostics" / "PlayTelemetry.cs"
          ).read_text(encoding="utf-8")
    assert "`rising_applause_plays`" in readme
    assert '\\"rising_applause_plays\\":' in cs
