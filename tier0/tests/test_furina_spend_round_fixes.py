"""THE SPEND ROUND'S "CLAUDE SHIPS" CHANGES, sim and page side (2026-10-10).

`review/records/furina-spend-round-2026-10-10.md`, "What changes" and
"Defects to fix": High Stakes reads the net Drained counter (1 damage a hit
for every 5 [4] HP drained and not Repaid); A Five-Century Act's past-line
return is said on the page; the curtain call says what did not come back;
every fixed-Drain refusal says "it would take you to 0 HP"; Bubble Aria's
chooser label names its Block; a calculated Block face folds Frail and
Dexterity (`FoldedCalculatedBlockVar`); and the telemetry report reads the
new keys. The C# twin is
`klee-mod/KleeTests/Prototype/FurinaSpendRoundFixesTests.cs`.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from tier0.content import loader
from tier0.engine import combat, effects, furina_stage as FS, furina_tide as T
from tier0.tests.conftest import make_enemy, make_state
from tools import gen_klee_cards, telemetry_report
from understudy import blindplay_board, blindplay_render

REPO = Path(__file__).resolve().parents[2]
GENERATED = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"


def _card(cid):
    return copy.deepcopy(loader.get_card(cid))


def _furina(hp=78, max_hp=78):
    st = make_state(enemies=[make_enemy(hp=300)], hp=max_hp)
    st.player.character_id = "furina"
    st.player.hp = hp
    st.in_player_turn = True
    st.turn = 1
    FS.reset_for_combat(st.player)
    st.player.energy = 9
    return st


def _play(st, card):
    st.player.hand.append(card)
    combat.play_card(st, card)


# ---- 1. High Stakes ------------------------------------------------------------

def test_high_stakes_constants_mirror_the_card():
    row = loader.get_card("proto_fs_high_stakes")
    assert row.effects[0]["amount"] == FS.HIGH_STAKES_EVERY == 4
    up = loader.get_card("proto_fs_high_stakes+")
    assert up.effects[0]["amount"] == FS.HIGH_STAKES_EVERY_UPGRADED == 3
    assert (row.cost, row.rarity) == (1, "uncommon")


def test_high_stakes_reads_the_drained_this_combat():
    """Round 2 (2026-10-10) made the count gross: Repay no longer lowers it
    (`test_furina_spend_round_2.py`)."""
    st = _furina()
    _play(st, _card("proto_fs_high_stakes"))
    assert st.player.ftd.high_stakes_every == [4]
    assert FS.high_stakes_bonus(st) == 0
    st.player.ftd.drained_this_combat = 14       # past the line counts too
    assert FS.high_stakes_bonus(st) == 3         # 14 // 4


def test_high_stakes_copies_add_their_own_bonus():
    st = _furina()
    _play(st, _card("proto_fs_high_stakes"))
    _play(st, _card("proto_fs_high_stakes+"))
    assert st.player.ftd.high_stakes_every == [4, 3]
    st.player.ftd.drained_this_combat = 9
    assert FS.high_stakes_bonus(st) == 2 + 3     # 9 // 4 + 9 // 3


def test_high_stakes_no_longer_reads_the_line():
    st = _furina(hp=40)                          # within 5 of the line (39)
    _play(st, _card("proto_fs_high_stakes"))
    assert FS.high_stakes_bonus(st) == 0         # nothing drained


def test_high_stakes_adds_to_every_attack_hit():
    st = _furina()
    _play(st, _card("proto_fs_high_stakes"))
    st.player.ftd.drained_this_combat = 10
    strike = _card("strike")
    assert effects.flat_attack_bonus(st, strike, 1) >= 2


def test_a_pin_that_sets_the_power_directly_reads_one_copy():
    st = _furina()
    st.player.powers[FS.HIGH_STAKES] = 4
    st.player.ftd.drained_this_combat = 8
    assert FS.high_stakes_bonus(st) == 2


# ---- 2 and 3. The page: A Five-Century Act and the curtain call ----------------

def _wire(**extra) -> dict:
    raw = {"live": True, "fanfare": 4, "drained": 12, "drain_line": 39,
           "drain_line_why": "", "entry_hp": 78, "entry_max_hp": 78,
           "seats": [], "log": []}
    raw.update(extra)
    return raw


def _drain_line(raw: dict) -> str:
    stage = blindplay_board.furina_stage({"furina_stage": raw})
    lines = blindplay_render._render_stage(
        stage, {"block": 0, "hp": 40, "max_hp": 78})
    return next(ln for ln in lines if ln.startswith("- Drained "))


def test_under_a_five_century_act_the_counter_drops_lost_unless_you_repay():
    line = _drain_line(_wire(drained_past=4, past_returns=True))
    assert line.startswith(
        "- Drained 12 HP (4 past your line). Drained HP returns after "
        "combat, past your line too. Drain line 39 HP")
    assert "lost unless" not in line
    # Without it, as before.
    assert "lost unless you Repay" in _drain_line(_wire(drained_past=4))
    # A build that sends none reads False.
    assert blindplay_board.furina_stage(
        {"furina_stage": _wire()})["past_returns"] is False


def _ev(amount=0, lost=0, past=0) -> dict:
    return {"kind": "curtain", "card": "", "target": "Furina", "power": "",
            "source": "", "on_player": True, "amount": amount, "lost": lost,
            "past": past}


def test_the_curtain_call_says_what_was_lost():
    assert blindplay_render._event_phrases("curtain", [_ev(2, lost=6)]) == [
        "Drained 2 HP returned; 6 past your line lost (the fight ended)"]
    # Nothing returned but something lost is still said.
    assert blindplay_render._event_phrases("curtain", [_ev(0, lost=6)]) == [
        "Drained 0 HP returned; 6 past your line lost (the fight ended)"]


def test_under_a_five_century_act_the_curtain_call_names_the_past_part():
    assert blindplay_render._event_phrases(
        "curtain", [_ev(14, past=6)]) == [
        "Drained 14 HP returned, 6 of it past your line"]


def test_a_plain_curtain_call_reads_as_before():
    assert blindplay_render._event_phrases("curtain", [_ev(12)]) == [
        "Drained 12 HP returned (the fight ended)"]
    assert blindplay_render._event_phrases("curtain", [_ev(0)]) == []


def test_the_board_reads_lost_and_past_off_the_wire():
    player = {"resolutions": [{"card": "", "events": [
        {"kind": "curtain", "amount": 2, "lost": 6, "past": 0, "seq": 1}]}]}
    ev = blindplay_board.page_events(player)[0]
    assert (ev["amount"], ev["lost"], ev["past"]) == (2, 6, 0)


# ---- 4. The refusal --------------------------------------------------------------

def test_every_fixed_drain_refusal_says_zero_hp():
    texts = [p.read_text(encoding="utf-8")
             for p in GENERATED.glob("ProtoFs*.cs")]
    assert not [t for t in texts if "below your Drain line" in t]
    assert sum(': "it would take you to 0 HP";' in t for t in texts) >= 11


# ---- 5. Bubble Aria ------------------------------------------------------------

def test_bubble_arias_spend_mode_names_its_block():
    src = (GENERATED / "ProtoFsBubbleAria.cs").read_text(encoding="utf-8")
    assert ('"Gain 6 [gold]Block[/gold]. [gold]Spend[/gold] 3: draw 2 '
            'cards."') in src
    assert ('"Gain 8 [gold]Block[/gold]. [gold]Spend[/gold] 3: draw 2 '
            'cards."') in src


# ---- 6. The calculated Block face --------------------------------------------

def test_a_proto_calculated_block_face_is_the_folding_var():
    assert gen_klee_cards.calculated_block_var_type(
        {"id": "proto_fs_the_show_must_go_on"}) == "FoldedCalculatedBlockVar"
    assert gen_klee_cards.calculated_block_var_type(
        {"id": "klee_shipped_row"}) == "CalculatedBlockVar"
    leftover = [p.name for p in GENERATED.glob("Proto*.cs")
                if "new CalculatedBlockVar(" in p.read_text(encoding="utf-8")]
    assert leftover == []


# ---- 7. The telemetry report -------------------------------------------------

def _row(**extra) -> dict:
    row = {"record": "fight", "character": "Furina", "act": 1,
           "kind": "monster", "turns": 4, "hp_start": 60, "hp_end": 40,
           "hp_lost": 20, "max_hp": 80, "damage_dealt": 40, "seats": 1,
           "outcome": "won"}
    row.update(extra)
    return row


def test_the_report_reads_hp_after_the_return():
    assert telemetry_report.hp_net_pct(_row(hp_after_return=56)) == 5.0
    assert telemetry_report.hp_net_pct(_row(hp_after_return=-1)) is None
    assert telemetry_report.hp_net_pct(_row()) is None
    cell = telemetry_report.cell("Furina", 1, "monster",
                                 [_row(hp_after_return=56)])
    assert cell.hp_lost_pct == 25.0 and cell.hp_net_pct == 5.0


def test_the_report_reads_her_fanfare():
    rows = [_row(fanfare_peak=30, fanfare_end=12, fanfare_spends=[
                {"card": "Hydro Lance", "spent": 4, "before": 30, "cap": -1},
                {"card": "Tidal Flourish+", "spent": 10, "before": 26,
                 "cap": 12}]),
            _row(fanfare_peak=20, fanfare_end=20, fanfare_spends=[],
                 outcome="died"),
            _row()]
    s = telemetry_report.fanfare_summary("Furina", rows)
    assert s["fights"] == 3 and s["fights_with_keys"] == 2
    assert s["peak"] == 25 and s["end"] == 16 and s["end_on_death"] == 20
    assert s["spends"] == 2 and s["up_to_share"] == 0.5
    assert s["spent_per_spend"] == 7 and s["before_per_spend"] == 28
    lines = telemetry_report.render_fanfare([s])
    assert any(line.startswith("Furina") for line in lines)


def test_the_report_cli_takes_fanfare(tmp_path, capsys):
    path = tmp_path / "play-1.jsonl"
    path.write_text(json.dumps(_row(fanfare_peak=9, fanfare_end=3,
                                    fanfare_spends=[], hp_after_return=50,
                                    ts=1.0)) + "\n", encoding="utf-8")
    assert telemetry_report.main(["--dir", str(tmp_path), "--fanfare",
                                  "--character", "Furina"]) == 0
    out = capsys.readouterr().out
    assert "FANFARE" in out and "net%" in out
