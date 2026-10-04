"""Furina, the Stage -- the 2026-09-25 afternoon seat round (0.2.3768).

Two seats: `review/qa/blindplay/20260925-171756/record.md` (Codex) and an Opus
seat on lane 2. This file pins the PAGE, the SHEET and the BRIDGE halves; the
mod halves are `klee-mod/KleeTests/Prototype/FurinaStageSeatRoundBTests.cs`
and the sim's are in `test_furina_stage.py`.

  1. Usher's Bow gives the front performer 4 Fanfare (it was 4 Block, which
     expired unused when a hit made him bow on the enemy's turn).
  2. Let the People Rejoice deals twice the Fanfare it spends.
  3. (The part of a hit that reaches Furina left the stage log with the
     re-founding, 2026-10-04: performers take no hits.)
  4. The Stage badge printed "1": a `Single` power shows no number in game,
     and now none on the page.
  5. The "after the acts" preview read 3 right after Full House, because the
     page was read before the power landed: the board settle now waits while
     the bridge says an action is still running.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from understudy import blindplay
from understudy.blindplay_board import furina_stage
from understudy.blindplay_notes import ARM_KEYWORDS
from understudy.blindplay_render import _render_stage_log

REPO = Path(__file__).resolve().parents[2]
RECORDED_COMBAT = (REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                   / "observed.json")


def _combat_state() -> dict:
    return json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))["state"]


# ---------------------------------------------------------------------------
# 1. USHER'S BOW.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 2. LET THE PEOPLE REJOICE.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 3. THE PART OF A HIT THAT REACHED HER.
# ---------------------------------------------------------------------------

def _wire_stage(*log):
    return {"furina_stage": {"live": True, "seats": [], "log": list(log)}}


def _row(event, member, name, **kw):
    row = {"event": event, "member": member, "name": name, "seat": -1,
           "fanfare": 0, "moved": 0, "reason": "", "target": "",
           "target_id": ""}
    row.update(kw)
    return row


# ---------------------------------------------------------------------------
# 4. THE STAGE BADGE'S "1".
# ---------------------------------------------------------------------------

def _with_status(rows):
    state = _combat_state()
    state["player"]["status"] = rows
    return state


STAGE_BADGE = {"id": "STAGE_SUMMARY_POWER", "name": "The Stage", "amount": 1,
               "type": "Buff", "keywords": [],
               "description": "Up to 3 performers act at the end of your turn."}


def test_a_single_power_prints_no_number():
    page = blindplay.observe(_with_status([dict(STAGE_BADGE, stack="Single")]))
    assert "The Stage (buff) — Up to 3 performers" in page
    assert "The Stage 1" not in page


def test_a_counter_power_and_an_older_bridge_still_print_the_number():
    page = blindplay.observe(_with_status([dict(STAGE_BADGE, stack="Counter")]))
    assert "The Stage 1 (buff)" in page
    page = blindplay.observe(_with_status([dict(STAGE_BADGE)]))
    assert "The Stage 1 (buff)" in page


def test_the_bridge_sends_the_stack_type_and_the_badge_is_single():
    """The re-founding (2026-10-04) retired the Stage summary badge; each
    performer's badge is the `Single` power now."""
    builder = (REPO / "vendor" / "STS2_MCP" / "McpMod.StateBuilder.cs"
               ).read_text(encoding="utf-8")
    assert '["stack"] = power.StackType.ToString(),' in builder
    badges = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
              / "FurinaStageBadges.cs").read_text(encoding="utf-8")
    badge = badges[badges.index("class StagePerformerBadge"):]
    badge = badge[:badge.index("public static string ActText")]
    assert "PowerStackType.Single" in badge


# ---------------------------------------------------------------------------
# 5. THE FULL HOUSE PREVIEW.
# ---------------------------------------------------------------------------

class _PollWire:
    def __init__(self, frames):
        self.frames = list(frames)
        self.reads = 0

    def get_state(self):
        self.reads += 1
        return self.frames[min(self.reads - 1, len(self.frames) - 1)]


def _flight(settled: bool, powers=()):
    state = _combat_state()
    state["player"]["hp_settled"] = settled
    state["player"]["status"] = list(powers)
    return state


FULL_HOUSE = {"id": "FULL_HOUSE_POWER", "name": "Full House", "amount": 1,
              "type": "Buff", "keywords": [], "stack": "Counter",
              "description": "Your performers act 1 more time."}


def test_a_still_board_is_not_at_rest_while_an_action_runs(monkeypatch):
    """Fight 6: two reads agreed while Full House was still resolving, so the
    page printed the board without it and "after the acts: Block 3"."""
    from understudy import blindplay_read
    monkeypatch.setattr(blindplay_read.time, "sleep", lambda _s: None)
    running = _flight(False)
    landed = _flight(True, [FULL_HOUSE])
    wire = _PollWire([_flight(False), landed, landed])
    out = blindplay.settle_board(running, wire, delay=0)
    assert out["player"]["status"] == [FULL_HOUSE]


def test_a_settled_board_still_costs_one_read(monkeypatch):
    from understudy import blindplay_read
    slept: list[float] = []
    monkeypatch.setattr(blindplay_read.time, "sleep", slept.append)
    rest = _flight(True)
    wire = _PollWire([rest, rest])
    assert blindplay.settle_board(rest, wire, delay=9.0) == rest
    assert wire.reads == 1
    assert slept == []


def test_the_brief_records_both_changes():
    brief = (REPO / "review" / "active"
             / "furina-stage-brief-2026-09-08.md").read_text(encoding="utf-8")
    # Draft 3 (2026-09-25) superseded round B's Fanfare Bow: rule 9 is now
    # "the Bow is the performer's act, once more".
    assert "**The Bow is the performer's act, once more**" in brief
    assert "Usher: the front performer gains 4 Fanfare" not in brief
    assert "Usher: Furina gains 4 Block" not in brief
    assert "equal to twice your performers' Fanfare" in brief
