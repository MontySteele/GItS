"""THE "LOST FOR GOOD" COUNTER on the seat page (2026-10-10).

`review/records/furina-quarter-line-round-2026-10-10.md`, "What to change"
1: seats learned the cost of draining past the Drain line only by losing
the HP. The stage's Drain line now names the part past the line in one
phrase, "Drained 12 HP (4 past your line: lost unless you Repay)", and
reads as before when nothing is past it. The C# twin (the Drained counter's
hover) is `klee-mod/KleeTests/Prototype/FurinaDrainLostCounterTests.cs`.
"""

from __future__ import annotations

from understudy import blindplay_board, blindplay_render


def _wire(**extra) -> dict:
    raw = {"live": True, "fanfare": 4, "drained": 12, "drain_line": 39,
           "drain_line_why": "the HP you started this fight with, minus 1/4 "
                             "of your Max HP",
           "entry_hp": 78, "entry_max_hp": 78, "seats": [], "log": []}
    raw.update(extra)
    return raw


def _drain_line(raw: dict) -> str:
    stage = blindplay_board.furina_stage({"furina_stage": raw})
    assert stage is not None
    lines = blindplay_render._render_stage(
        stage, {"block": 0, "hp": 40, "max_hp": 78})
    return next(ln for ln in lines if ln.startswith("- Drained "))


def test_the_board_reads_the_past_line_part_off_the_wire():
    stage = blindplay_board.furina_stage(
        {"furina_stage": _wire(drained_past=4)})
    assert stage["drained"] == 12 and stage["drained_past"] == 4
    # A build that sends none reads 0.
    assert blindplay_board.furina_stage(
        {"furina_stage": _wire()})["drained_past"] == 0


def test_the_drain_line_names_what_is_past_the_line():
    line = _drain_line(_wire(drained_past=4))
    assert line.startswith(
        "- Drained 12 HP (4 past your line: lost unless you Repay). "
        "Drained HP above your line returns after combat.")
    assert "Drain line 39 HP (the HP you started this fight with" in line


def test_nothing_past_the_line_reads_as_before():
    for raw in (_wire(drained_past=0), _wire()):
        line = _drain_line(raw)
        assert line.startswith("- Drained 12 HP. Drained HP above your line")
        assert "past your line:" not in line


def test_the_phrase_matches_the_game_hover():
    # The same words as `DrainedCounter.DrainedPhrase`, BBCode aside.
    assert blindplay_render.STAGE_DRAIN_PAST.format(past=4) == (
        " (4 past your line: lost unless you Repay)")
