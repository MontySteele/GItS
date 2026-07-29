"""C2: the elite columns.

The instrument's value is that "act-1 clear moved" decomposes. A low clear rate
and a low ATTEMPT rate produce similar act-clear symptoms and want opposite
fixes, and nothing in the report could tell them apart.

R14: these pin the MEASUREMENT, not a target. No threshold is asserted here and
none should be added.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tier0 import constants as C
from tier05 import elite_blitz as eb


@dataclass
class FakeFight:
    won: bool = True
    hp_start: int = 80
    hp_end: int = 60


@dataclass
class FakeRun:
    node_kinds: list = field(default_factory=list)
    fight_stats: list = field(default_factory=list)
    relics_by_act: list = field(default_factory=list)
    kurage_traces: list = field(default_factory=list)


def _one_act(kinds):
    """Pad a kind sequence out to one full act so floor//MAP_FLOORS is 0."""
    return list(kinds) + ["R"] * (C.MAP_FLOORS - len(kinds))


def test_only_elite_nodes_are_counted():
    run = FakeRun(node_kinds=_one_act(["N", "E", "N", "E"]),
                  fight_stats=[FakeFight(), FakeFight(),
                               FakeFight(), FakeFight()])
    act = eb.aggregate([run])[0]
    assert act["attempted"] == 2
    assert act["cleared"] == 2


def test_non_fight_nodes_do_not_shift_the_fight_alignment():
    """Rests, shops and events sit in node_kinds and run no fight. If they
    were not filtered out, every elite after the first rest would be scored
    against some other fight's stats -- quietly, and in the wrong act."""
    run = FakeRun(
        node_kinds=_one_act(["R", "$", "N", "R", "E"]),
        # Two fights only: the N and the E, in that order.
        fight_stats=[FakeFight(won=True, hp_start=80, hp_end=79),
                     FakeFight(won=True, hp_start=79, hp_end=40)],
    )
    act = eb.aggregate([run])[0]
    assert act["attempted"] == 1
    assert act["mean_hp_cost"] == 39


def test_a_lost_elite_is_attempted_but_not_cleared():
    run = FakeRun(node_kinds=_one_act(["E"]),
                  fight_stats=[FakeFight(won=False, hp_start=50, hp_end=0)])
    act = eb.aggregate([run])[0]
    assert (act["attempted"], act["cleared"]) == (1, 0)
    assert act["clear_rate"] == 0.0


def test_a_death_does_not_drag_the_hp_cost_mean():
    """A death costs all remaining HP. Folding it into the mean would report
    'elites cost about your whole bar', which is true and useless -- the
    question the column exists for is what a SURVIVED elite takes out of you."""
    runs = [FakeRun(node_kinds=_one_act(["E"]),
                    fight_stats=[FakeFight(won=True, hp_start=80, hp_end=70)]),
            FakeRun(node_kinds=_one_act(["E"]),
                    fight_stats=[FakeFight(won=False, hp_start=80, hp_end=0)])]
    act = eb.aggregate(runs)[0]
    assert act["attempted"] == 2
    assert act["mean_hp_cost"] == 10
    assert act["max_hp_cost"] == 10


def test_attempts_per_run_separates_ducking_from_losing():
    """Two cohorts with the same act-clear symptom and opposite diseases:
    one loses the elites it takes, the other routes around them."""
    losing = [FakeRun(node_kinds=_one_act(["E"]),
                      fight_stats=[FakeFight(won=False)]) for _ in range(4)]
    ducking = [FakeRun(node_kinds=_one_act(["N"]),
                       fight_stats=[FakeFight(won=True)]) for _ in range(4)]
    a_lose = eb.aggregate(losing)[0]
    assert (a_lose["attempts_per_run"], a_lose["clear_rate"]) == (1.0, 0.0)
    assert eb.aggregate(ducking) == {}


def test_acts_are_split_on_the_map_floor_boundary():
    kinds = _one_act(["E"]) + _one_act(["N", "E"])
    run = FakeRun(node_kinds=kinds,
                  fight_stats=[FakeFight(), FakeFight(), FakeFight()])
    agg = eb.aggregate([run])
    assert agg[0]["attempted"] == 1
    assert agg[1]["attempted"] == 1


def test_relic_counts_are_per_act_boundary():
    runs = [FakeRun(node_kinds=_one_act(["E"]),
                    fight_stats=[FakeFight()], relics_by_act=[3, 7]),
            FakeRun(node_kinds=_one_act(["E"]),
                    fight_stats=[FakeFight()], relics_by_act=[5])]
    agg = eb.aggregate(runs)
    assert agg[0]["mean_relics"] == 4.0 and agg[0]["boundary_runs"] == 2
    # An act nobody finished contributes no entry, rather than a zero that
    # would read as "arrived with no relics".
    assert agg[1]["mean_relics"] == 7.0 and agg[1]["boundary_runs"] == 1


def test_the_pool_separates_total_hp_from_the_largest_body():
    """A 4-body swarm and a single fat elite can share a total. The pulse is
    single-target, so only the largest body is the right denominator for it."""
    pool = eb.elite_hp_pool(0)
    assert pool["encounters"] >= 3
    # Act 1 holds both shapes: BYGONE EFFIGY (one 127 body) and PHANTASMAL
    # GARDENER x4 (four ~28s). The largest body must come from the former.
    assert pool["largest_body"] > pool["smallest_body"] * 2
    assert pool["max_total"] >= pool["largest_body"]


def test_p95_over_body_is_the_reader_hierarchy_as_a_number():
    from tier05 import kurage_telemetry as kt
    trace = kt.KurageTrace(amounts=[10] * 19 + [100], charges=[5] * 20)
    run = FakeRun(node_kinds=_one_act(["E"]), fight_stats=[FakeFight()],
                  kurage_traces=[(0, trace)])
    act = eb.aggregate([run])[0]
    # RE-HOMED, sim-hygiene sprint 2026-07-29: same correction as
    # test_kurage_telemetry -- elite_blitz priced its tail nearest-rank under a
    # docstring claiming it matched run_metrics. The repo now has ONE
    # percentile (tier05.stats, linear), so p95 of these 20 pulses interpolates
    # (14.5) instead of snapping to the single 100. The RELATION this test is
    # about -- p95 divided by the act's largest single body -- is untouched.
    assert round(act["p95_pulse"], 1) == 14.5
    assert (act["p95_over_largest_body"]
            == act["p95_pulse"] / act["pool"]["largest_body"])


def test_a_cohort_that_meets_no_elite_prints_nothing():
    runs = [FakeRun(node_kinds=_one_act(["N"]), fight_stats=[FakeFight()])]
    assert eb.format_block(eb.aggregate(runs)) == ""


def test_no_results_is_an_empty_aggregate_not_a_crash():
    assert eb.aggregate([]) == {}
    assert eb.format_block({}) == ""
