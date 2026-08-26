"""R68: the canonical cell object and the mandatory run stamp.

The defect these pin is not a crash -- it is two numbers that look
comparable and are not. Twelve experiment scripts hand-rolled five different
seeds, three carried copied argument parsers around drifted `_arm()` bodies,
and no report printed the world it came from. Every one of those failures is
silent at the report and only shows up months later when someone puts two
rows in the same table.
"""

from __future__ import annotations

import dataclasses

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier05 import cells, draft, run_metrics, runner


def test_the_canonical_cell_is_the_ratified_configuration():
    """600 runs, seed 11, hunter, realistic -- the sprint-doc sentence."""
    c = cells.CANONICAL
    assert c.runs == 600
    assert c.seed == 11
    assert c.route == "hunter"
    assert c.realistic is True
    assert c.policy == "assigned"


def test_version_fields_are_read_live_not_stored():
    """The whole point of not storing them.

    A stored stamp goes stale silently at the next bump, which is exactly
    what the ghost check did to itself one bump after it was written. When
    the R66 epoch landing moves POLICY_VERSION to 3, the canonical cell has
    to follow with nobody editing a literal.
    """
    before = cells.CANONICAL.stamp()
    original = draft.POLICY_VERSION
    try:
        draft.POLICY_VERSION = 99
        assert "P99" in cells.CANONICAL.stamp()
    finally:
        draft.POLICY_VERSION = original
    assert cells.CANONICAL.stamp() == before

    # And nothing is cached on the instance itself.
    assert "versions" not in {f.name for f in
                              dataclasses.fields(cells.CANONICAL)}


def test_the_stamp_names_every_axis_a_reader_needs():
    stamp = cells.CANONICAL.stamp()
    assert stamp == (f"cell=canonical seed=11 runs=600 "
                     f"RT{C.RUNTEMPLATE_VERSION}/D{C.DRAFTER_VERSION}"
                     f"/P{draft.POLICY_VERSION}/C{C.CONSTANTS_VERSION}")


def test_a_cell_is_frozen():
    """A cell that mutates mid-experiment stamps half its own rows wrong."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        cells.CANONICAL.runs = 1


def test_a_derived_cell_stops_claiming_to_be_the_canonical_one():
    """`but()` forces the divergence into the name.

    Without this a script could run 20 runs off CANONICAL and stamp the
    output `cell=canonical`, which is worse than an unstamped report: it
    asserts a provenance that is false.
    """
    derived = cells.CANONICAL.but(runs=20)
    assert derived.name != "canonical"
    assert "runs=20" in derived.name
    assert "cell=canonical " not in derived.stamp()


def test_an_explicit_name_survives_derivation():
    derived = cells.CANONICAL.but(name="ghostcheck", runs=200)
    assert derived.name == "ghostcheck"


def test_a_cell_cannot_name_a_plan_its_character_does_not_have():
    """resolve_plan is the ONLY path to a pilot (R68), and it fails loudly.

    Scripts used to pass the archetype string as its own pilot id, which
    worked right up until a plan's pilot differed from its name -- a
    silently wrong pilot is a run measuring a different deck.
    """
    with pytest.raises(ValueError, match="no archetype"):
        cells.Cell(name="bad", character="klee", archetype="salon")
    with pytest.raises(ValueError, match="unsupported character"):
        cells.Cell(name="bad", character="nobody", archetype="generic")


def test_the_pilot_comes_from_resolve_plan():
    for character, plans in runner.CHARACTER_PLANS.items():
        for archetype, expected_pilot in plans.items():
            try:
                c = cells.Cell(name="t", character=character,
                               archetype=archetype)
            except loader.MissingReferenceLayer:
                # BACKLOG EB-128 (4). The `real_*` arms read the gitignored
                # `game_ref/` tree, which is absent on a fresh clone and in
                # every worktree by construction. Constructing one there now
                # REFUSES at the door instead of building a cell that would
                # die by traceback mid-run -- so this is the pass, not a hole
                # in the sweep, and it is asserted rather than skipped past.
                assert character in loader.REFERENCE_LAYER_SHEETS
                assert not (loader.GAME_REF_DIR /
                            loader.REFERENCE_LAYER_SHEETS[character]).exists()
                continue
            assert c.pilot == expected_pilot


def test_an_unknown_policy_is_refused():
    with pytest.raises(ValueError, match="unknown policy"):
        cells.CANONICAL.but(policy="vibes")


def test_but_refuses_a_field_that_does_not_exist():
    """A typo'd delta would otherwise be silently dropped, and the cell
    would run the base configuration while its name claimed otherwise."""
    with pytest.raises(TypeError, match="no field"):
        cells.CANONICAL.but(runz=10)


def test_print_run_report_requires_a_stamp(capsys):
    """R68: a report without a stamp is not citable, so omitting one is a
    TypeError at the call site rather than a thinner report."""
    summary = {
        "runs": 1, "wins": 0, "winrate": 0.0, "winrate_wilson95": (0.0, 1.0),
        "avg_final_deck": 10.0, "pick_rate": 0.5, "regretted_decisions": 0,
        "median_time_to_online": 1, "online_rate": 1.0,
        "hp_bands": [None], "death_heatmap": {},
    }
    with pytest.raises(TypeError):
        run_metrics.print_run_report("furina", "salon", summary, ["fight"])

    run_metrics.print_run_report("furina", "salon", summary, ["fight"],
                                 stamp=cells.CANONICAL.stamp())
    assert "cell=canonical" in capsys.readouterr().out


def test_the_shared_parser_replaces_the_copied_ones():
    base = cells.CANONICAL
    cell, rest = cells.parse_overrides(
        ["--runs", "50", "--seed", "7", "--route", "cautious",
         "--jobs", "2", "leftover"], base)
    assert (cell.runs, cell.seed, cell.route, cell.jobs) == (50, 7,
                                                             "cautious", 2)
    assert rest == ["leftover"]
    # Untouched fields still come from the ratified cell.
    assert cell.realistic is base.realistic


def test_parse_overrides_with_no_flags_returns_the_base_unchanged():
    cell, rest = cells.parse_overrides([], cells.CANONICAL)
    assert cell is cells.CANONICAL
    assert rest == []


def test_a_multi_arm_header_does_not_contradict_its_own_rows():
    """A base cell holds ONE character and ONE policy; a sweep over either
    must not print the base's value as if it described the table."""
    line = cells.CANONICAL.describe(subject="7 arms", varying=("policy",))
    assert line.startswith("7 arms")
    assert "policy (swept)" in line
    assert "furina/salon" not in line
