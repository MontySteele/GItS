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

from tier05 import aura_telemetry, encore_telemetry, fanfare_telemetry

_FIXTURES = (pathlib.Path(__file__).resolve().parents[2]
             / "review" / "redteam" / "fixtures" / "track_o"
             / "s07-partial-fights.json")


def _log(name: str) -> list[dict]:
    return json.loads(_FIXTURES.read_text(encoding="utf-8"))[name]["log"]


def _fanfare_turns(turns: int, held: int, cap: int) -> list[dict]:
    return [{"turn": t, "event": "fanfare_turn", "total": held, "cap": cap,
             "floor": 0, "at_cap": held >= cap, "at_floor": held == 0}
            for t in range(1, turns + 1)]


# --- encore: the fight that ends mid-upkeep -------------------------------
#
# encore_telemetry.py:50-55 registers this explicitly: `salon_tick` is emitted
# per member inside a loop that breaks when the fight ends (effects.py:2423),
# so an upkeep short of its member count is the fight ending, not a dry stage,
# and it must stay out of the all-ticked denominator.

def test_upkeep_truncated_by_death_is_excluded_from_all_ticked() -> None:
    t = encore_telemetry.trace(_log("encore_death_mid_upkeep"))
    assert t.upkeeps == 1
    assert t.upkeeps_truncated == 1
    assert t.upkeeps_complete == 0
    assert t.upkeeps_all_ticked == 0
    agg = encore_telemetry.aggregate([t])
    assert agg["truncated_upkeeps"] == 1
    # 0/0, not 0/1: the lethal-blow turn is not an Encore failure.
    assert agg["all_ticked_rate"] == 0.0


def test_complete_upkeep_is_scored_all_ticked() -> None:
    t = encore_telemetry.trace(_log("encore_complete_upkeep"))
    assert (t.upkeeps_complete, t.upkeeps_truncated) == (1, 0)
    assert encore_telemetry.aggregate([t])["all_ticked_rate"] == 1.0


def test_truncated_upkeep_still_contributes_its_arrival_snapshot() -> None:
    """The snapshot is taken BEFORE the first member spends (effects.py:2415-
    2419), so an upkeep the fight cut short is still a valid reading of what
    the stage arrived holding."""
    agg = encore_telemetry.aggregate(
        [encore_telemetry.trace(_log("encore_death_mid_upkeep"))])
    assert agg["upkeeps"] == 1
    assert agg["full_rate"] == 1.0        # arrived with 9 against a bill of 3
    assert agg["mean_held"] == 9.0
    assert agg["mean_surplus"] == 6.0


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


# --- fanfare: the columns that really are pooled --------------------------
#
# fanfare_telemetry.py:181-183 states the rule: pool the numerator and the
# denominator, so a two-turn combat cannot weigh as much as a twenty-turn one.
# time_at_cap and overflow obey it. (mean_held_fraction and peak_fraction do
# not -- slice-07 finding S07-03 -- and are deliberately not pinned.)

def test_time_at_cap_is_pooled_over_turns_not_averaged_over_combats() -> None:
    long_fight = fanfare_telemetry.trace(_fanfare_turns(20, 10, 10))
    short_deaths = [fanfare_telemetry.trace(_fanfare_turns(1, 0, 10))
                    for _ in range(9)]
    agg = fanfare_telemetry.aggregate([long_fight] + short_deaths)
    assert agg["turns"] == 29
    assert agg["time_at_cap"] == 20 / 29
    # The per-combat average of the same quantity would be 1/10.
    assert agg["time_at_cap"] != 0.1
