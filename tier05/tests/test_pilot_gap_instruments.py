"""The three instrument changes the pilot-gap sprint makes (2026-07-28).

Same standard as the sprint before it: an instrument that quietly reports the
wrong number is worse than no instrument, because the sprint after this one
will make a ruling out of it. Each test below is written against a specific
way the change could have been wrong, not against the implementation.

The three:
  1. `encore_telemetry` gains a RUNWAY rate -- the sim analogue of the bar a
     playtester reads as "I am not going to run out".
  2. `fanfare_telemetry` gains a per-SOURCE reduction, so a realistic drafted
     run can be asked where its Fanfare came from. The fight log does not
     survive onto a RunResult, so before this the question was answerable
     only of a hand-built deck.
  3. `cells.Cell` gains `pilot_override`, which lands in `stamp()` -- the
     brief's "never quote a stoker row against a greedy row without both
     labels" rule, enforced by the mandatory stamp line rather than by
     discipline.
"""

from __future__ import annotations

import pytest

from tier05 import cells, encore_telemetry, fanfare_telemetry


def _upkeep(members: int, encore: int, cost: int = 1) -> dict:
    return {"event": "salon_upkeep", "members": members, "encore": encore,
            "cost": cost * members}


def _turn(total: int = 10, cap: int = 40) -> dict:
    return {"event": "fanfare_turn", "total": total, "cap": cap,
            "at_cap": False, "at_floor": False}


def _gain(source: str, requested: int, total: int = 10) -> dict:
    return {"event": "gain_fanfare", "source": source, "requested": requested,
            "wasted": 0, "total": total}


# --- 1. the runway rate -------------------------------------------------

def test_the_runway_rate_measures_turns_of_bill_not_a_single_turn():
    """A three-member stage holding 3 can tick THIS turn and is broke the
    next. Full rate says yes to it; the runway rate is the column that says
    what a playtester actually sees, and conflating the two is what let the
    sim call a bar 'full' that nobody would describe that way."""
    turns = encore_telemetry.RUNWAY_SATURATED_TURNS
    barely = encore_telemetry.trace([_upkeep(3, 3)])
    saturated = encore_telemetry.trace([_upkeep(3, 3 * turns)])

    assert barely.full_rate == 1.0
    assert barely.runway_rate == 0.0
    assert saturated.full_rate == 1.0
    assert saturated.runway_rate == 1.0


def test_the_runway_threshold_is_the_whole_stage_bill_not_one_member():
    """Scaling with the stage is the point: five members cost five times
    what one does, so the same held Encore is a shorter runway. A threshold
    read off a single member's cost would report a big stage as MORE
    saturated than a small one on identical Encore."""
    turns = encore_telemetry.RUNWAY_SATURATED_TURNS
    held = 3 * turns
    assert encore_telemetry.trace([_upkeep(3, held)]).runway_rate == 1.0
    assert encore_telemetry.trace([_upkeep(5, held)]).runway_rate == 0.0


def test_the_runway_rate_survives_pooling():
    agg = encore_telemetry.aggregate([
        encore_telemetry.trace([_upkeep(1, 99), _upkeep(1, 0)]),
    ])
    assert agg["runway_rate"] == pytest.approx(0.5)
    assert f"runway{encore_telemetry.RUNWAY_SATURATED_TURNS}+" in \
        encore_telemetry.format_row("probe", agg)


# --- 2. the per-source reduction ----------------------------------------

def test_fanfare_is_attributed_to_the_source_that_generated_it():
    tr = fanfare_telemetry.trace([
        _gain("encore_gained", 3), _gain("center_stage", 2),
        _gain("encore_gained", 1),
    ])
    assert tr.by_source == {"encore_gained": 4, "center_stage": 2}
    assert tr.requested == 6


def test_sources_are_credited_by_request_not_by_what_survived_the_cap():
    """Crediting a source with only the part that fit under the ceiling
    would re-attribute overflow to whichever source happened to be measured
    while there was room -- a fact about ORDER, not about sources. The pair
    below generates the same amount and one of them spills."""
    tr = fanfare_telemetry.trace([
        {"event": "gain_fanfare", "source": "hp_lost", "requested": 5,
         "wasted": 4, "total": 30},
        {"event": "gain_fanfare", "source": "center_stage", "requested": 5,
         "wasted": 0, "total": 30},
    ])
    assert tr.by_source == {"hp_lost": 5, "center_stage": 5}


def test_a_prepass4_log_without_requested_is_not_credited_to_anyone():
    """The existing `requested` leg skips those events as UNMEASURED rather
    than as zero. The source map has to skip the same ones or the two
    numbers stop adding up -- shares against a total they do not sum to."""
    tr = fanfare_telemetry.trace([
        {"event": "gain_fanfare", "source": "hp_lost", "total": 4},
        _gain("center_stage", 2),
    ])
    assert tr.by_source == {"center_stage": 2}
    assert sum(tr.by_source.values()) == tr.requested


def test_pooled_sources_come_back_descending_and_summed():
    # `_turn()` is required, not decoration: `aggregate` has always pooled
    # only traces with turns on them, so a combat that never emitted a
    # fanfare_state is not in the denominator of ANY of its columns. The
    # source map inherits that rule rather than inventing a second one.
    agg = fanfare_telemetry.aggregate([
        fanfare_telemetry.trace([_turn(), _gain("encore_gained", 2)]),
        fanfare_telemetry.trace([_turn(), _gain("encore_gained", 3),
                                 _gain("center_stage", 9)]),
    ])
    assert list(agg["by_source"]) == ["center_stage", "encore_gained"]
    assert agg["by_source"] == {"center_stage": 9, "encore_gained": 5}


# --- 3. the pilot override ----------------------------------------------

def test_an_overridden_pilot_is_named_in_the_stamp():
    """The brief's labelling rule, made structural. A stoker table that did
    not say so would be indistinguishable from every greedy Furina row on
    record -- and those rows are what the next nerf gets priced against."""
    cell = cells.CANONICAL.but(character="furina", archetype="salon",
                               pilot_override="salon_stoker")
    assert cell.pilot == "salon_stoker"
    assert "pilot=salon_stoker" in cell.stamp()
    assert "pilot salon_stoker" in cell.describe()


def test_the_ratified_cells_stamp_is_untouched():
    """Naming the pilot unconditionally would rewrite every stamp on record
    and stop the canonical line matching the sprint docs that cite it. It is
    named only where a reader has to be warned."""
    assert "pilot=" not in cells.CANONICAL.stamp()
    assert cells.CANONICAL.pilot == "salon"


def test_an_unknown_pilot_fails_at_construction_not_inside_a_worker():
    """Otherwise a typo surfaces as a KeyError deep in a subprocess,
    halfway through a batch that has already cost minutes."""
    with pytest.raises(KeyError):
        cells.CANONICAL.but(pilot_override="salon_stokker")
