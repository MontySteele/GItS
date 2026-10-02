"""Sheet pass 4 Q1a: the Fanfare saturation metrics.

These pin the REGISTERED definitions (docs/archive/furina-sheet-pass-4-plan.md).
A metric that quietly changes shape mid-pass would invalidate every cell
measured before the change, so the definitions are tests, not comments.
"""

from __future__ import annotations

from tier05 import fanfare_telemetry as ft
import pytest



def test_time_at_cap_counts_turn_snapshots_not_events():
    # Registered definition: the fraction of PLAYER TURNS whose start-of-turn
    # snapshot sits at the cap. Gain events must not vote.
    log = [
        {"event": "fanfare_turn", "total": 10, "cap": 20, "at_cap": False},
        {"event": "gain_fanfare", "amount": 0, "total": 20,
         "requested": 5, "wasted": 5, "source": "x"},
        {"event": "fanfare_turn", "total": 20, "cap": 20, "at_cap": True},
        {"event": "fanfare_spent", "amount": 6, "total": 14},
    ]
    tr = ft.trace(log)

    assert tr.turns == 2
    assert tr.time_at_cap == 0.5
    assert tr.overflow == 1.0
    assert (tr.spend_events, tr.spent) == (1, 6)
    assert tr.peak == 20


def test_pre_pass4_logs_are_unmeasured_not_healthy():
    # A log without requested/wasted keys must not read as "zero waste",
    # which would look like a healthy world in an archive comparison.
    log = [{"event": "gain_fanfare", "amount": 3, "total": 3, "source": "x"},
           {"event": "fanfare_turn", "total": 3, "cap": 20, "at_cap": False}]
    tr = ft.trace(log)
    assert tr.requested == 0
    assert tr.overflow == 0.0        # 0/0 -> reported as no denominator
    assert ft.aggregate([tr])["requested"] == 0


def test_read_time_saturation_is_measured_separately_from_turn_start():
    """"The Tide Turns" gate (2). Pass 4 measured both and they disagreed by
    25 points: the turn-start snapshot can look healthy while every read
    still lands on a pinned meter, because the pool refills mid-turn."""
    log = [
        {"event": "fanfare_turn", "total": 10, "cap": 30, "floor": 0,
         "at_cap": False, "at_floor": False},
        {"event": "gain_fanfare", "amount": 20, "total": 30,
         "requested": 20, "wasted": 0, "source": "x"},
        {"event": "fanfare_read", "kind": "bonus_formula", "total": 30,
         "cap": 30, "floor": 0, "at_cap": True, "at_floor": False},
        {"event": "fanfare_read", "kind": "threshold", "total": 30,
         "cap": 30, "floor": 0, "at_cap": True, "at_floor": False},
    ]
    tr = ft.trace(log)

    assert tr.time_at_cap == 0.0      # the turn-start sample says "healthy"
    assert tr.read_at_cap == 1.0      # every actual read says "pinned"
    assert tr.mean_at_read == 30


def test_a_floor_pinned_meter_is_visible_even_though_it_never_reads_at_cap():
    """The blind spot the added metric exists to close: a grant raises the
    cap ALONGSIDE the floor, so floor < cap always -- a meter resting on its
    floor is fully saturated in play and reads at-cap exactly never."""
    log = [
        {"event": "fanfare_floor_granted", "amount": 15, "source": "p",
         "floor": 15, "cap": 45, "total": 15},
        {"event": "fanfare_turn", "total": 15, "cap": 45, "floor": 15,
         "at_cap": False, "at_floor": True},
        {"event": "fanfare_read", "kind": "salon_focus", "total": 15,
         "cap": 45, "floor": 15, "at_cap": False, "at_floor": True},
    ]
    tr = ft.trace(log)

    assert tr.read_at_cap == 0.0, "at-cap is blind to this failure by design"
    assert tr.read_at_floor == 1.0
    assert tr.read_empty == 0.0
    assert tr.time_at_floor == 1.0
    assert (tr.floor_grants, tr.floor_granted) == (1, 15)


def test_floor_rates_are_per_combat_and_per_run_is_derived_explicitly():
    """Gate (3) is written per RUN; every rate in aggregate() is per COMBAT,
    because `live` is one trace per fight. Conflating them understates the
    per-run figure by the combats-per-run factor (~9x) and reads as a gate
    failure where there is none -- which is exactly what happened once."""
    traces = [ft.FanfareTrace(turns=3, cap=30, held=[5, 5, 5],
                              floor_grants=1, floor_granted=8)
              for _ in range(18)]           # 18 combats from 2 runs
    agg = ft.aggregate(traces)
    assert agg["floor_granted_per_combat"] == 8
    assert agg["combats_counted"] == 18

    pr = ft.per_run(agg, runs=2)
    assert pr["combats_per_run"] == 9
    assert pr["floor_granted_per_run"] == 72     # NOT 8
    assert pr["floor_grants_per_run"] == 9


def test_an_empty_meter_is_not_reported_as_a_built_floor():
    """Before any grant the floor is 0, so `at_floor` fires on an EMPTY
    meter too -- opposite diagnosis, same flag. Act 1 is dominated by this
    case, so conflating them would read a dead stat as successful
    floor-building."""
    log = [
        {"event": "fanfare_turn", "total": 0, "cap": 30, "floor": 0,
         "at_cap": False, "at_floor": True},
        {"event": "fanfare_read", "kind": "bonus_formula", "total": 0,
         "cap": 30, "floor": 0, "at_cap": False, "at_floor": True},
    ]
    tr = ft.trace(log)

    assert tr.read_empty == 1.0
    assert tr.read_at_floor == 0.0, "an empty meter is not a floor pin"
    assert ft.aggregate([tr])["read_at_floor"] == 0.0


def test_a_deck_that_never_reads_is_not_reported_as_healthy():
    log = [{"event": "fanfare_turn", "total": 3, "cap": 30, "floor": 0,
            "at_cap": False, "at_floor": False}]
    agg = ft.aggregate([ft.trace(log)])
    assert agg["reads"] == 0
    assert agg["read_at_cap"] == 0.0    # 0/0 -- read alongside `reads`


def test_aggregate_pools_ratios_instead_of_averaging_them():
    # A 1-turn combat must not weigh as much as a 9-turn one.
    short = ft.FanfareTrace(turns=1, turns_at_cap=1, cap=20, held=[20])
    long_ = ft.FanfareTrace(turns=9, turns_at_cap=0, cap=20, held=[0] * 9)
    agg = ft.aggregate([short, long_])

    assert agg["turns"] == 10
    assert agg["time_at_cap"] == 0.1     # pooled, not (1.0 + 0.0) / 2
