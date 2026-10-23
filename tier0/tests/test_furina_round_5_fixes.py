"""FURINA WHOLE-RUN ROUND 5 (2026-10-11): the review's no-approval changes.

None moves a rule or a number:

1. Freminet's act logs as Block on the seat page, as the mod does it
   (`FurinaStage.CueOf`: `StageCueKind.Block`), not "N Cryo damage".
2. A line of 0 on a buffer build reads in the buffer's words; the old
   line-first zero sentence is kept for a build that sends no buffer.
3. Lyney: his badge says the Drain buffer is 10 HP larger, and his face
   names the act's Drain 2.
4. Telemetry: the Spend cards in hand at each turn start by name, and the
   enemies alive as each Spend card is played; the report reads both.

The C# twin is `klee-mod/KleeTests/Prototype/FurinaRound5FixesTests.cs`.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from understudy import blindplay_board, blindplay_render
from tools import telemetry_report

from tier0.tests.test_furina_round_3_page import _row, _wire

REPO = Path(__file__).resolve().parents[2]


def _stage(raw: dict) -> dict:
    stage = blindplay_board.furina_stage({"furina_stage": raw})
    assert stage is not None
    return stage


def _drain_line(raw: dict) -> str:
    lines = blindplay_render._render_stage(
        _stage(raw), {"block": 0, "hp": 74, "max_hp": 78})
    return next(ln for ln in lines
                if ln.startswith(("- Drained ", "- Drain buffer")))


# ---- 1. Freminet's act is Block ------------------------------------------------

def _act(member: str, moved: int) -> dict:
    return {"event": "act", "member": member, "name": member.capitalize(),
            "seat": 0, "seat_key": 1, "fanfare": 4, "moved": moved}


def test_freminets_act_logs_as_block():
    log = blindplay_render._render_stage_log(
        _stage(_wire(log=[_act("freminet", 9)])))
    assert log == ["  - **Freminet** acted: Furina gains 9 Block."]


def test_freminet_has_no_damage_element():
    assert blindplay_render.STAGE_MEMBER_KINDS["freminet"] == "block"
    assert "freminet" not in blindplay_render.STAGE_MEMBER_ELEMENTS
    # The damage acts keep theirs.
    assert blindplay_render.STAGE_MEMBER_ELEMENTS["escoffier"] == "Cryo"


def test_the_page_matches_the_mods_cue_kind():
    cs = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
          / "FurinaStage.cs").read_text(encoding="utf-8")
    cue = cs[cs.index("StagePerformer.Freminet => new(seat.Who"):]
    assert cue.split(")", 1)[0].count("StageCueKind.Block") == 1


# ---- 2. the zero line on a buffer build ------------------------------------------

def test_a_zero_line_reads_in_buffer_words():
    line = _drain_line(_wire(drain_line=0, drain_buffer=19,
                             drain_buffer_left=13))
    assert line == (
        "- Drain buffer: 13 HP left. Your HP is inside it, so all your "
        "Drain returns after combat.")
    assert "your HP minus" not in line


def test_the_zero_line_wins_over_five_century_act_on_a_buffer_build():
    line = _drain_line(_wire(drain_line=0, past_returns=True))
    assert line.startswith("- Drain buffer: 13 HP left. Your HP is "
                           "inside it")


def test_a_non_zero_buffer_line_is_unchanged():
    assert _drain_line(_wire()) == (
        "- Drain buffer: 13 HP left. Drain inside it returns after combat; "
        "past it (past your line), only Repay returns.")


# ---- 3. Lyney ----------------------------------------------------------------

def _sheet_row(card_id: str) -> dict:
    sheet = yaml.safe_load((REPO / "docs" / "prototype-surface.yaml")
                           .read_text(encoding="utf-8"))
    rows = sheet["cards"] if isinstance(sheet, dict) else sheet
    return next(r for r in rows if r.get("id") == card_id)


def test_lyneys_face_names_the_acts_drain():
    face = _sheet_row("proto_fs_guest_star_lyney")["description"]
    assert ("Act: [gold]Drain[/gold] 2, deal {GuestAct:diff()} "
            "[gold]Pyro[/gold] damage to ALL enemies.") in face


def test_lyneys_badge_speaks_of_the_buffer():
    # The badge's keyed rows since the localization census (2026-10-23).
    from tools import lint_text_conventions as ltc
    line, act = ltc._guest_halves()["Lyney"]
    assert line == "Your [gold]Drain[/gold] buffer is {LineDrop} HP larger."
    assert act.startswith("Act: ")
    assert "HP lower" not in line + act


# ---- 4. telemetry ----------------------------------------------------------------

def test_the_report_reads_spend_card_plays_and_names():
    rows = [_row(fanfare_peak=9, fanfare_end=3, fanfare_spends=[],
                 spend_card_plays=[[1, "Standing Ovation", 4],
                                   [3, "Bravura+", 1]],
                 spend_card_names_turn_start=[
                     [1, ["Standing Ovation", "Spirited Aria"]],
                     [2, ["Standing Ovation"]], [3, []]]),
            _row(fanfare_peak=9, fanfare_end=3, fanfare_spends=[],
                 spend_card_plays=[[2, "Standing Ovation", 2]],
                 spend_card_names_turn_start=[[1, ["Bravura+"]]]),
            _row()]
    s = telemetry_report.fanfare_summary("Furina", rows)
    assert s["spend_card_plays"] == 3
    assert s["alive_per_spend_play"] == 2
    assert s["spend_cards_held"] == {"Standing Ovation": 2,
                                     "Spirited Aria": 1, "Bravura+": 1}
    lines = telemetry_report.render_fanfare([s])
    assert any(ln.strip().startswith("Standing Ovation") for ln in lines)
    bare = telemetry_report.fanfare_summary("Furina", [_row()])
    assert bare["spend_card_plays"] is None
    assert bare["alive_per_spend_play"] is None
    assert bare["spend_cards_held"] == {}


def test_the_schema_names_the_new_keys():
    readme = (REPO / "understudy" / "README.md").read_text(encoding="utf-8")
    cs = (REPO / "klee-mod" / "KleeCode" / "Diagnostics" / "PlayTelemetry.cs"
          ).read_text(encoding="utf-8")
    for key in ("spend_card_names_turn_start", "spend_card_plays"):
        assert f"`{key}`" in readme, key
        assert f'\\"{key}\\":' in cs, key
    # What `damage_by_source` measures is written down, in both places.
    assert "OVERKILL IS NOT COUNTED" in cs
    assert "overkill is not counted" in readme
