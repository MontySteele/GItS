"""R67: the sweep harness refuses to sweep a knob nothing reads.

The negative test the ruling asks for, plus the positive control it needs
to be worth anything -- "the gate fails" is only evidence if the same
harness passes a live knob under the same conditions.

Why a gate and not a reviewer: an instrument that reads nothing and a knob
that genuinely does nothing print the SAME flat table. Three times now
(R33's selector circularity, SPOTLIGHT_SELF_MULT, FANFARE_DECAY_PER_TURN)
that table was read as a null result about the knob. Nobody caught it at
review, because there was nothing to catch at review.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.engine import effects
from tier05 import sweeps


# A knob planted for this test alone: no engine code reads it, which is
# precisely the property under test. Registered here rather than in
# constants.py so nothing can grow a reader for it by accident.
DEAD_KNOB = "_TEST_KNOB_NOTHING_READS"


@pytest.fixture(autouse=True)
def _plant_dead_knob():
    setattr(C, DEAD_KNOB, 1.0)
    yield
    if hasattr(C, DEAD_KNOB):
        delattr(C, DEAD_KNOB)
    C._SWEPT.pop(DEAD_KNOB, None)


def test_sweeping_a_dead_knob_is_refused_on_the_first_cell():
    """The ruling's negative test.

    Refusal lands on cell ONE, not after the grid: a dead-knob sweep can be
    an hour of compute and there is nothing to learn from finishing it.
    """
    cells_run = []

    with pytest.raises(sweeps.DeadKnobError) as excinfo:
        list(sweeps.sweep(DEAD_KNOB, (1.0, 2.0, 3.0), cells_run.append))

    assert len(cells_run) == 1, "the gate must fire before cell two"
    msg = str(excinfo.value)
    # The message has to stop the reader from "fixing" this the wrong way.
    assert "instrument error" in msg
    assert "R33" in msg


def test_the_gate_passes_a_knob_the_engine_really_reads():
    """Positive control: the same harness, a live knob, no refusal.

    Without this, a gate that refused EVERYTHING would look identical to a
    working one from the negative test alone.
    """
    seen = []

    def cell(value):
        # A real read on the real path -- module attribute access, which is
        # what every consumer in this repo does.
        seen.append(C.FANFARE_DECAY_FRACTION)
        return value

    out = list(sweeps.sweep("FANFARE_DECAY_FRACTION", (0.1, 0.2), cell))

    assert [v for v, _ in out] == [0.1, 0.2]
    assert seen == [0.1, 0.2], "each cell must see its own armed value"


def test_the_stamped_default_is_restored_after_a_sweep():
    """A sweep must not leave the world edited for whatever runs next."""
    before = C.FANFARE_DECAY_FRACTION

    list(sweeps.sweep("FANFARE_DECAY_FRACTION", (0.4,),
                      lambda v: C.FANFARE_DECAY_FRACTION))

    assert C.FANFARE_DECAY_FRACTION == before
    assert "FANFARE_DECAY_FRACTION" not in C._SWEPT


def test_the_default_is_restored_even_when_a_cell_raises():
    """The failure path is the one that matters: a sweep that dies holding
    an armed knob would silently contaminate every later measurement in the
    same process."""
    before = C.FANFARE_DECAY_FRACTION

    def exploding_cell(value):
        raise ValueError("boom")

    with pytest.raises(ValueError):
        list(sweeps.sweep("FANFARE_DECAY_FRACTION", (0.4,), exploding_cell))

    assert C.FANFARE_DECAY_FRACTION == before
    assert "FANFARE_DECAY_FRACTION" not in C._SWEPT


def test_the_gate_refuses_a_knob_that_does_not_exist():
    """A typo'd knob name sweeps nothing and would report a clean null --
    the same defect wearing a different hat."""
    with pytest.raises(AttributeError):
        list(sweeps.sweep("FANFARE_DECAY_FRACTOIN", (0.1,), lambda v: v))


def test_multi_knob_sweeps_require_every_axis_to_be_live():
    """The R7 rest-economy sweep shape: two axes, one of them applied by
    nothing (NORMAL_ATTRITION_SCALE, deleted by R67). A 2D grid with a dead
    second axis is half an experiment reported as a whole one."""
    def cell(frac, dead):
        return C.FANFARE_DECAY_FRACTION

    with pytest.raises(sweeps.DeadKnobError) as excinfo:
        list(sweeps.sweep_pairs(("FANFARE_DECAY_FRACTION", DEAD_KNOB),
                                [(0.1, 1.0)], cell))

    assert DEAD_KNOB in str(excinfo.value)
    # And the live axis is not blamed for the dead one's failure.
    assert "FANFARE_DECAY_FRACTION" not in str(excinfo.value).split(
        "without reading")[0].replace(DEAD_KNOB, "")


def test_multi_knob_sweeps_restore_every_knob():
    before = (C.FANFARE_DECAY_FRACTION, C.FANFARE_CAP_FRACTION)

    def cell(frac, cap):
        return (C.FANFARE_DECAY_FRACTION, C.FANFARE_CAP_FRACTION)

    out = list(sweeps.sweep_pairs(
        ("FANFARE_DECAY_FRACTION", "FANFARE_CAP_FRACTION"),
        [(0.1, 0.25), (0.3, 0.75)], cell))

    assert [r for _, r in out] == [(0.1, 0.25), (0.3, 0.75)]
    assert (C.FANFARE_DECAY_FRACTION, C.FANFARE_CAP_FRACTION) == before


def test_reads_do_not_leak_between_cells():
    """Per-cell reset is what makes the count mean "this cell read it".
    Without it, cell one's reads would vouch for every later cell."""
    calls = []

    def cell(value):
        # Only the first cell reads the knob.
        if not calls:
            calls.append(C.FANFARE_DECAY_FRACTION)
        return value

    with pytest.raises(sweeps.DeadKnobError):
        list(sweeps.sweep("FANFARE_DECAY_FRACTION", (0.1, 0.2), cell))

    assert len(calls) == 1, "cell two must be judged on its own reads"


def test_the_deleted_knobs_are_actually_gone():
    """R67's deletion list, pinned. A DEAD-KNOB comment was the audit's
    halfway step; an unreadable knob left in the file invites exactly the
    false-evidence sweeps the ruling deleted."""
    for knob in ("PROGRESSION_GAP_COMPENSATOR", "SPOTLIGHT_SELF_MULT",
                 "FANFARE_DECAY_PER_TURN", "SPOTLIGHT_SELECTOR_VERSION",
                 "PILOT_REGRET_SAMPLE_RATE", "ATTRITION_LITE_HP",
                 "PUNISHER_LITE_SCALE", "NORMAL_POOL_WEIGHTS",
                 "NORMAL_ATTRITION_SCALE"):
        assert not hasattr(C, knob), f"{knob} was deleted by R67"


def test_knob_reads_survives_as_the_engines_own_counter():
    """The gate reuses KNOB_READS rather than inventing a parallel
    mechanism, so the hand-instrumented counters must still work."""
    effects.reset_knob_reads()
    assert effects.KNOB_READS == {}
