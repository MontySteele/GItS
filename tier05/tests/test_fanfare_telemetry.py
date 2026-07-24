"""Sheet pass 4 Q1a: the Fanfare saturation metrics.

These pin the REGISTERED definitions (docs/furina-sheet-pass-4-plan.md).
A metric that quietly changes shape mid-pass would invalidate every cell
measured before the change, so the definitions are tests, not comments.
"""

from __future__ import annotations

import random

from tier0.content import loader
from tier0.engine import resources
from tier0.engine.state import CombatState, Enemy
from tier05 import fanfare_telemetry as ft


def _furina_state(fanfare: int = 0) -> CombatState:
    player = loader.build_player("furina")
    state = CombatState(player=player,
                        enemies=[Enemy(hp=300, max_hp=300, name="dummy",
                                       intents=[{"kind": "attack",
                                                 "amount": 5}])],
                        rng=random.Random(1))
    state.player.fanfare = fanfare
    return state


def test_gain_emits_the_overflow_the_clamp_used_to_swallow():
    # Before pass 4 a gain that hit the cap emitted only what LANDED, so
    # wasted generation left no trace -- the reason no earlier cap sweep
    # could see saturation.
    state = _furina_state()
    cap = state.player.fanfare_cap
    assert cap > 0
    state.player.fanfare = cap - 2
    state.log.clear()
    resources.gain_fanfare(state, 10, "test")

    ev = next(e for e in state.log if e["event"] == "gain_fanfare")
    assert ev["amount"] == 2          # what landed
    assert ev["requested"] == 10      # what was asked for
    assert ev["wasted"] == 8          # what the cap ate
    assert state.player.fanfare == cap


def test_a_fully_wasted_gain_still_reports():
    # The case that matters most: at the cap, the old code emitted NOTHING.
    state = _furina_state()
    state.player.fanfare = state.player.fanfare_cap
    state.log.clear()
    resources.gain_fanfare(state, 7, "test")

    ev = next(e for e in state.log if e["event"] == "gain_fanfare")
    assert (ev["amount"], ev["requested"], ev["wasted"]) == (0, 7, 7)


def test_characters_without_the_resource_emit_nothing():
    state = _furina_state()
    state.player.fanfare_cap = 0            # e.g. Klee
    state.log.clear()
    resources.gain_fanfare(state, 5, "test")
    assert not [e for e in state.log if e["event"] == "gain_fanfare"]


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
