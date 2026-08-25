"""D1's per-act surface (Last Call track D), pinned.

The run-level half of the reactions share-of-damage instrument. Same fence as
every other R14 diagnostic in this directory: it reports, it does not grade,
and it is silent rather than zero-filled when the cohort never reacted.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier05 import cells, reaction_telemetry


class _FS:
    """The four FightStats fields the aggregator reads, and the two properties
    derived from them. Hand-built so the act arithmetic is testable without
    running a cohort."""

    def __init__(self, all_ops=100, amp=0, splash=0, dot=0, reactions=0):
        self.reaction_damage_amp = amp
        self.reaction_damage_splash = splash
        self.reaction_damage_dot = dot
        self.reactions = reactions
        self._all = all_ops

    @property
    def damage_from_reactions(self):
        return (self.reaction_damage_amp + self.reaction_damage_splash
                + self.reaction_damage_dot)

    @property
    def damage_all_ops(self):
        return self._all


class _Run:
    def __init__(self, node_kinds, fight_stats):
        self.node_kinds = node_kinds
        self.fight_stats = fight_stats


def _run_with_one_fight_per_act(per_act):
    """One fight on floor 0 of each act, so act attribution is unambiguous."""
    kinds, stats = [], []
    for act, fs in enumerate(per_act):
        kinds += ["N"] + ["?"] * (C.MAP_FLOORS - 1)
        stats.append(fs)
    return _Run(kinds, stats)


def test_empty_cohort_is_empty_not_a_division():
    assert reaction_telemetry.aggregate([]) == {}
    assert reaction_telemetry.format_block({}) == ""


def test_acts_are_separated_and_minus_one_is_the_cohort_total():
    run = _run_with_one_fight_per_act([
        _FS(all_ops=100, amp=10, reactions=1),
        _FS(all_ops=200, splash=40, reactions=2),
        _FS(all_ops=100, dot=5, reactions=1),
    ])
    agg = reaction_telemetry.aggregate([run])
    assert sorted(agg) == [-1, 0, 1, 2]
    assert agg[0]["share"] == 10 / 100
    assert agg[1]["share"] == 40 / 200
    assert agg[2]["share"] == 5 / 100
    total = agg[-1]
    assert total["fights"] == 3
    assert total["damage_all_ops"] == 400
    assert total["damage_from_reactions"] == 55
    # POOLED, not the mean of the three per-act shares (which is 0.15).
    assert total["share"] == 55 / 400
    assert total["damage_from_base_ops"] == 345
    assert total["amp"] == 10 and total["splash"] == 40 and total["dot"] == 5


def test_a_cohort_that_never_reacted_prints_nothing():
    run = _run_with_one_fight_per_act([_FS(all_ops=100), _FS(all_ops=100)])
    agg = reaction_telemetry.aggregate([run])
    assert agg[-1]["share"] == 0.0
    assert reaction_telemetry.format_block(agg) == "", (
        "a non-reacting cohort printed a row of zeroes")


def test_a_zero_damage_cohort_does_not_divide_by_zero():
    run = _run_with_one_fight_per_act([_FS(all_ops=0)])
    assert reaction_telemetry.aggregate([run])[-1]["share"] == 0.0


def test_only_fight_nodes_are_zipped_against_fight_stats():
    """Rest/shop/event floors run no fight. If they were counted, every act's
    fights would be mis-attributed by however many non-fight rooms preceded
    them -- the failure elite_blitz's docstring warns about."""
    kinds = ["N", "R", "$", "N"] + ["?"] * (C.MAP_FLOORS - 4)
    run = _Run(kinds, [_FS(all_ops=10, amp=1), _FS(all_ops=10, amp=3)])
    agg = reaction_telemetry.aggregate([run])
    assert list(agg) == [0, -1] or sorted(agg) == [-1, 0]
    assert agg[0]["fights"] == 2 and agg[0]["amp"] == 4


def test_the_block_carries_no_verdict():
    run = _run_with_one_fight_per_act([_FS(all_ops=100, amp=10, reactions=1)])
    block = reaction_telemetry.format_block(
        reaction_telemetry.aggregate([run]))
    assert block
    lowered = block.lower()
    for word in ("pass", "fail", "healthy", "verdict", "target", "band ",
                 "too low", "too high"):
        assert word not in lowered, word
    assert "report-only" in lowered


@pytest.mark.battery
def test_end_to_end_on_a_real_reacting_cohort():
    """The instrument survives a live cohort and the arithmetic closes on it."""
    cell = cells.Cell(name="test", character="klee", archetype="reaction",
                      runs=8, seed=42)
    agg = reaction_telemetry.aggregate(cell.run())
    total = agg[-1]
    assert total["fights"] > 0
    assert total["damage_from_reactions"] == (
        total["amp"] + total["splash"] + total["dot"])
    assert (total["damage_from_base_ops"] + total["damage_from_reactions"]
            == total["damage_all_ops"])
    assert 0.0 < total["share"] < 1.0
    # Per-act fights sum to the cohort total; nothing is double-counted and
    # nothing falls between two acts.
    assert sum(b["fights"] for a, b in agg.items() if a >= 0) == total["fights"]
