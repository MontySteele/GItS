"""C4: the carry-card overlap watch.

The instrument's whole value is that it can see TWO cards at once. Playtest two
was carried by a pair, and every column the sim owned was per-card or per-run,
so the pair was invisible until a hand reported it. These pin the join.

R14: these pin the MEASUREMENT, not a target. No threshold is asserted here and
none should be added -- MIN_CELL is a rendering rule (refuse to print a rate
built on too few runs), not an acceptance bar.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tier05 import overlap_telemetry as ot


@dataclass
class FakeRun:
    """The three fields aggregate() joins on, and nothing else."""

    won: bool = False
    deck_ids: list = field(default_factory=list)
    overlap_traces: list = field(default_factory=list)


def _fight(**plays):
    return (0, ot.OverlapTrace(plays=dict(plays)))


def test_a_play_is_counted_from_the_log():
    log = [{"event": "play", "card": "honor_guard"},
           {"event": "play", "card": "waters_edge"},
           {"event": "play", "card": "honor_guard"},
           {"event": "damage", "card": "honor_guard"}]
    assert ot.trace(log).plays == {"honor_guard": 2}


def test_unwatched_cards_leave_no_trace():
    """Silence for the rest of the roster is the point: a Klee run must not
    carry an empty Kokomi column through every fight of every cell."""
    log = [{"event": "play", "card": "kaboom"} for _ in range(20)]
    assert ot.trace(log).plays == {}
    assert ot.trace(log).total == 0


def test_copies_are_counted_not_just_presence():
    """G2 ratified before_sun_and_moon STACKING over an objection. A draft
    rate cannot grade that -- 0/1/2 collapses to 'held' -- so the copies
    column is the entire reason this card is on the watch."""
    runs = [FakeRun(deck_ids=["before_sun_and_moon"]),
            FakeRun(deck_ids=["before_sun_and_moon", "before_sun_and_moon"]),
            FakeRun(deck_ids=["waters_edge"])]
    card = ot.aggregate(runs)["cards"]["before_sun_and_moon"]
    assert card["drafted_runs"] == 2
    assert card["max_copies"] == 2
    assert card["multi_copy_runs"] == 1
    assert card["mean_copies"] == 1.5


def test_lift_is_one_when_the_pair_is_independent():
    """The raw co-draft rate of two commonly drafted cards is arithmetic, not
    a finding. Lift is what separates 'both are popular' from 'decks seek the
    pair', and it must read 1.0 on an independent draw."""
    a, b = "before_sun_and_moon", "honor_guard"
    # 4 runs: each card in exactly half, overlapping in exactly one quarter.
    runs = [FakeRun(deck_ids=[a, b]), FakeRun(deck_ids=[a]),
            FakeRun(deck_ids=[b]), FakeRun(deck_ids=[])]
    pair = ot.aggregate(runs)["pairs"][(a, b)]
    assert pair["co_draft_rate"] == 0.25
    assert abs(pair["lift"] - 1.0) < 1e-9


def test_lift_rises_when_the_pair_is_sought():
    a, b = "before_sun_and_moon", "honor_guard"
    # Same marginal rates as above (half each), but they never appear apart.
    runs = [FakeRun(deck_ids=[a, b]), FakeRun(deck_ids=[a, b]),
            FakeRun(deck_ids=[]), FakeRun(deck_ids=[])]
    pair = ot.aggregate(runs)["pairs"][(a, b)]
    assert pair["co_draft_rate"] == 0.5
    assert pair["lift"] == 2.0


def test_the_three_win_cells_are_reported_separately():
    """'Both is strong' means nothing without what ONE is worth. The pair
    that carried playtest two would have looked identical to two independently
    good cards if only win-when-both had been reported."""
    a, b = "before_sun_and_moon", "honor_guard"
    runs = [FakeRun(won=True, deck_ids=[a, b]),
            FakeRun(won=True, deck_ids=[a, b]),
            FakeRun(won=False, deck_ids=[a]),
            FakeRun(won=False, deck_ids=[])]
    pair = ot.aggregate(runs)["pairs"][(a, b)]
    assert (pair["win_both"], pair["n_both"]) == (1.0, 2)
    assert (pair["win_one"], pair["n_one"]) == (0.0, 1)
    assert (pair["win_neither"], pair["n_neither"]) == (0.0, 1)


def test_the_drafted_but_never_cast_gap_is_visible():
    """R75 made honor_guard a 0-cost Rare. A 0-cost card never competes for a
    turn, so its drafted-vs-cast gap is the question -- and the deck alone
    cannot answer it, which is why the trace half of the module exists."""
    runs = [FakeRun(deck_ids=["honor_guard"],
                    overlap_traces=[_fight(honor_guard=3)]),
            FakeRun(deck_ids=["honor_guard"], overlap_traces=[_fight()]),
            FakeRun(deck_ids=["honor_guard"], overlap_traces=[_fight()])]
    card = ot.aggregate(runs)["cards"]["honor_guard"]
    assert card["never_played_runs"] == 2
    assert card["mean_plays"] == 1.0


def test_plays_accumulate_across_the_fights_of_a_run():
    runs = [FakeRun(deck_ids=["honor_guard"],
                    overlap_traces=[_fight(honor_guard=1),
                                    _fight(honor_guard=2),
                                    _fight()])]
    assert ot.aggregate(runs)["cards"]["honor_guard"]["mean_plays"] == 3.0


def test_a_thin_cell_is_withheld_rather_than_printed():
    """A win rate over a handful of runs is noise wearing a percent sign, and
    a printed number gets quoted. Withholding is not a gate (R14) -- it is a
    refusal to render something that would be read as one."""
    runs = ([FakeRun(won=True, deck_ids=["honor_guard"])]
            + [FakeRun(won=False) for _ in range(50)])
    block = ot.format_block(ot.aggregate(runs))
    assert f"n<{ot.MIN_CELL}" in block
    # The 1-run 100% must not appear anywhere in the rendering.
    assert "100.0" not in block


def test_a_roster_that_drafts_none_of_them_prints_nothing():
    runs = [FakeRun(deck_ids=["kaboom", "waters_edge"]) for _ in range(50)]
    assert ot.format_block(ot.aggregate(runs)) == ""


def test_no_results_is_an_empty_aggregate_not_a_crash():
    assert ot.aggregate([]) == {}
    assert ot.format_block({}) == ""
