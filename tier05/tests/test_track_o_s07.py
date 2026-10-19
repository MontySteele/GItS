"""Track O red-team, slice 7: Track D telemetry writers under PARTIAL fights.

These are PINS, not findings. Each one fixes a behaviour that is unambiguous
from the module's own registered metric definitions, so that the fixes the
slice-07 report proposes cannot quietly change the half that is already
right while repairing the half that is not.

The fixtures live in review/redteam/fixtures/track_o/s07-partial-fights.json;
the same file drives the reproducer for the findings, which are deliberately
NOT pinned here.
"""

from __future__ import annotations

import json
import pathlib

from tier05 import aura_telemetry

_FIXTURES = (pathlib.Path(__file__).resolve().parents[2]
             / "review" / "redteam" / "fixtures" / "track_o"
             / "s07-partial-fights.json")


def _log(name: str) -> list[dict]:
    return json.loads(_FIXTURES.read_text(encoding="utf-8"))[name]["log"]


# --- aura: the intervals that DO close ------------------------------------
#
# aura_telemetry.py:9-11 registers the three closers. The reaction and expiry
# legs are pinned here; the missing enemy-death leg is a slice-07 finding and
# is not pinned.

def test_aura_interval_closes_on_expiry() -> None:
    t = aura_telemetry.trace(_log("aura_enemy_survives_aura_expires"))
    assert t.turns == 20
    assert t.applications == 1
    assert t.hydro_turns == 3           # applied t2, wasted t4 -> t2, t3, t4
    assert t.uptime == 0.15


def test_aura_interval_closes_on_a_reaction_consuming_it() -> None:
    t = aura_telemetry.trace(_log("aura_complete_fight"))
    assert t.applications == 2
    # t3-t4 and t6-t7 -> four distinct turns out of ten.
    assert t.hydro_turns == 4
    assert t.uptime == 0.4


def test_aura_traces_do_not_leak_across_fights() -> None:
    """Every trace is built from one fight's log (model.py:563-597). Two
    fights reduced in sequence must not see each other's intervals."""
    first = aura_telemetry.trace(_log("aura_complete_fight"))
    second = aura_telemetry.trace(_log("aura_partial_fight_death_turn_1"))
    again = aura_telemetry.trace(_log("aura_complete_fight"))
    assert (second.applications, second.hydro_turns) == (0, 0)
    assert (again.applications, again.hydro_turns) == (first.applications,
                                                       first.hydro_turns)

