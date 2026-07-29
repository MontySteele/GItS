"""Encore + conditional telemetry (salon UI sprint, Tracks 3 and 4).

Instruments get tests for the same reason gates do: a metric that quietly
reports the wrong number is worse than no metric, because the sprint after
this one will make a ruling out of it. Every case below is one the real run
actually produced.
"""

from __future__ import annotations

from tier0.engine.combat import run_fight
from tier0.content import loader
from tier0.pilot.policy import make_pilot
from tier05 import conditional_telemetry, encore_telemetry


def _upkeep(members: int, encore: int, cost: int = 1) -> dict:
    return {"event": "salon_upkeep", "members": members, "encore": encore,
            "cost": cost * members}


def _tick(paid: bool, member: str = "usher") -> dict:
    return {"event": "salon_tick", "member": member, "paid": paid}


def test_a_stage_that_arrives_fully_funded_reads_full_and_all_ticked():
    tr = encore_telemetry.trace([
        _upkeep(3, 5), _tick(True), _tick(True), _tick(True),
    ])
    assert tr.upkeeps == 1
    assert tr.full_rate == 1.0
    assert tr.dry_rate == 0.0
    assert tr.all_ticked_rate == 1.0
    assert tr.mean_surplus == 2.0


def test_an_underfunded_stage_is_not_full_and_not_all_ticked():
    """Two members, one point: the first pays and the second goes dry. The
    stage is NOT dry by the metric's definition -- dry means it could not
    afford even one member -- and this distinction is the whole reason the
    two rates are reported separately."""
    tr = encore_telemetry.trace([
        _upkeep(2, 1), _tick(True), _tick(False),
    ])
    assert tr.dry_rate == 0.0
    assert tr.full_rate == 0.0
    assert tr.all_ticked_rate == 0.0
    assert tr.mean_surplus == -1.0


def test_an_empty_meter_reads_dry():
    tr = encore_telemetry.trace([_upkeep(2, 0), _tick(False), _tick(False)])
    assert tr.dry_rate == 1.0
    assert tr.paid_rate == 0.0


def test_a_fight_that_ends_mid_upkeep_is_excluded_not_counted_as_a_failure():
    """The upkeep loop breaks when the last enemy dies, so the lethal turn
    emits fewer ticks than it has members. Counting that as "not all ticked"
    would report the winning turn as an Encore failure."""
    tr = encore_telemetry.trace([
        _upkeep(3, 9), _tick(True), _tick(True),      # third never resolves
    ])
    assert tr.upkeeps_truncated == 1
    assert tr.upkeeps_complete == 0
    assert tr.all_ticked_rate == 0.0        # 0/0, and complete==0 says why


def test_absorption_counts_as_drain_or_the_ratio_inverts():
    """The bug this test exists for: the first run reported gained/spent 3.07
    against a mean end level of 4.0, numbers that cannot both be true. The
    missing sink was absorption -- points the buffer ATE, which is the thing
    the buffer is FOR, being reported as points wasted."""
    log = [
        {"event": "gain_encore", "amount": 10, "total": 10},
        {"event": "encore_spent", "amount": 2},
        {"event": "encore_absorb", "amount": 5},
        {"event": "encore_end", "encore": 3, "members": 0, "won": True},
    ]
    agg = encore_telemetry.aggregate([encore_telemetry.trace(log)])
    assert agg["drained_per_combat"] == 7.0
    assert agg["gain_drain_ratio"] == 10 / 7
    # The arithmetic that makes it credible: gained - drained == end level.
    assert (agg["gained_per_combat"] - agg["drained_per_combat"]
            == agg["mean_end_encore"])


def test_a_meter_that_was_never_used_reports_none_not_zero():
    """Reporting the most saturated case as the ratio's minimum would print
    the strongest finding as the weakest number."""
    agg = encore_telemetry.aggregate([encore_telemetry.trace([
        {"event": "gain_encore", "amount": 6, "total": 6},
        {"event": "encore_end", "encore": 6, "members": 0, "won": True},
    ])])
    assert agg["gain_drain_ratio"] is None
    assert encore_telemetry.format_row("x", agg).count("NEVER USED") == 1


def test_pooling_is_by_upkeep_not_by_combat():
    """A 1-upkeep combat must not weigh as much as a 9-upkeep one."""
    short = encore_telemetry.trace([_upkeep(1, 0), _tick(False)])
    long = encore_telemetry.trace(
        [ev for _ in range(9) for ev in (_upkeep(1, 5), _tick(True))])
    agg = encore_telemetry.aggregate([short, long])
    assert agg["upkeeps"] == 10
    assert agg["dry_rate"] == 0.1


def test_conditional_fire_rate_is_per_card_and_predicate():
    tr = conditional_telemetry.trace([
        {"event": "conditional", "card": "graceful_retreat",
         "predicate": "hp_lost_this_turn", "fired": False},
        {"event": "conditional", "card": "graceful_retreat",
         "predicate": "hp_lost_this_turn", "fired": True},
        {"event": "conditional", "card": "showstopper",
         "predicate": "killed_target", "fired": True},
    ])
    agg = conditional_telemetry.aggregate([tr])
    assert agg[("graceful_retreat", "hp_lost_this_turn")]["rate"] == 0.5
    assert agg[("showstopper", "killed_target")]["rate"] == 1.0
    rows = conditional_telemetry.format_rows(agg, "graceful_retreat")
    assert len(rows) == 1 and "50.0%" in rows[0]


def test_the_dead_riders_sort_to_the_top():
    """The finding is the rider that never pays, so it must not be buried
    under the ones that work."""
    agg = {("a", "p"): {"evaluated": 10, "fired": 9, "rate": 0.9},
           ("b", "q"): {"evaluated": 10, "fired": 0, "rate": 0.0}}
    assert conditional_telemetry.format_rows(agg)[0].startswith("  b")


def test_the_engine_actually_emits_what_the_instruments_read():
    """The instruments above are fed synthetic logs, which proves they do
    arithmetic and not that the events exist. This runs a real Furina fight
    and asserts the event names and keys are the ones tier05 reads -- the
    join between the two halves, which is where a rename would break the
    measurement silently."""
    # The starter deck holds no conditional and no deploy, so the join would
    # be untested on exactly the two events this sprint added. Both are
    # named into the deck instead.
    #
    # `many_waters_melody` replaced `graceful_retreat` here (Fanfare rework
    # Track C.1, 2026-07-28): Slip Backstage was rewritten into a flat
    # Encore->Block spender and no longer holds a conditional at all, so it
    # stopped supplying the event this test names it for. Its replacement
    # gates on `has_salon_members`, which the crabaletta deploys below
    # actually satisfy -- so the conditional is both EVALUATED and FIRED,
    # which is a slightly stronger join than the one it replaces.
    deck = (loader.starting_deck("furina")
            + ["many_waters_melody"] * 6 + ["mademoiselle_crabaletta"] * 3)
    player = loader.build_player_from_ids("furina", deck)
    pilot = make_pilot(loader.pilot_weights("salon"))
    state = run_fight(player, loader.build_encounter("punisher"), pilot,
                      seed=20260728)

    kinds = {ev["event"] for ev in state.log}
    assert "conditional" in kinds, "no conditional was ever evaluated"
    assert "salon_upkeep" in kinds, "no salon upkeep snapshot was emitted"
    assert "salon_tick" in kinds, "no per-member tick was emitted"
    assert "encore_end" in kinds, "the end-of-combat Encore level is not emitted"

    tr = encore_telemetry.trace(state.log)
    assert tr.end_encore is not None
    if tr.upkeeps:
        # Every upkeep must be paired with its ticks or the rates are lies.
        assert tr.upkeeps_complete + tr.upkeeps_truncated == tr.upkeeps

    cond = conditional_telemetry.trace(state.log)
    assert cond.total > 0
    assert all(isinstance(k, tuple) and len(k) == 2 for k in cond.evaluated)
