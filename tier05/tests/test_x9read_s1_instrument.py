"""`X9READ-S1`'s RUNNER: the registered cell, and the observer seam.

Nothing here reads a number off a run. It pins the cell §4 registers (so the
record's header and the registration cannot quietly disagree) and proves the
one monkeypatch is restored even when the run underneath it raises — a leaked
patch would silently attach this experiment's observer to whatever ran next in
the same process.
"""

from __future__ import annotations

import pytest

from tier05 import exp_x9read_s1 as exp, model


def test_the_cell_is_the_one_section_four_registers():
    cell = exp.CELL
    assert cell.character == "kokomi"        # the bank is hers
    assert cell.runs == 600                  # §4's n, countersigned R233
    assert cell.seed == 11                   # §4's standing seed
    assert cell.jobs == 1                    # the seam lives in this process
    assert cell.route == "hunter"
    assert cell.policy == "assigned"
    assert cell.realistic is True
    assert cell.n_acts is None
    assert exp.ARCHETYPES == ("priest", "commander", "assist")


def test_the_observer_seam_is_restored_when_the_run_raises():
    before = model._RunCtx._record_traces

    class _Boom(Exception):
        pass

    class _Cell:
        def run(self):
            raise _Boom()

    with pytest.raises(_Boom):
        exp._observe(_Cell())
    assert model._RunCtx._record_traces is before
