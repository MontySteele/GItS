"""The gated sweep harness (R67, 2026-07-26).

Every constant sweep in this repo runs through `sweep()`. That is a rule,
not a convenience: R67 made the KNOB_READS exercise counter a GATE after the
read-nothing instrument class showed up for the third time.

The class, for anyone who finds this later and wonders why the ceremony:

  R33   `SPOTLIGHT_BASE_MULT` was swept across cells in which the companion
        branch was structurally unreachable. Every cell was identical, and
        the pass-2 record read it as "MEASURED 1.0 -- the knob is dead".
  §2.1  `SPOTLIGHT_SELF_MULT` had zero readers at all; `spotlight_mult()`
        hard-codes its early return. Three swept cells, three identical rows.
  §2.1  `FANFARE_DECAY_PER_TURN` sat behind a branch the 20% proportional
        ruling made permanently unreachable. Five swept cells, five
        identical rows, read as a null about decay magnitude.

All three produced numbers. None of them measured anything. The failure is
invisible at the report -- an instrument that reads nothing and a knob that
genuinely does nothing print the same flat table -- which is why it needs a
gate rather than a reviewer.

What the gate asserts: while a cell ran, the swept knob was READ at least
once. `tier0.constants` counts those reads itself, at the real attribute
access on the real read path (see the instrumentation block at the foot of
that module). R33's law carries over verbatim: the gate may NOT be satisfied
by adding artificial reads. If a knob records zero, wire it or delete it --
do not teach anything to touch it so the sweep goes green.

Usage:

    from tier05 import sweeps

    for value, result in sweeps.sweep("FANFARE_CAP_FRACTION",
                                      (0.25, 0.5, 0.75), run_cell):
        print(value, result["winrate"])

`run_cell` is called once per value and receives that value. Anything it
returns is handed back untouched.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from typing import Any

from tier0 import constants as C
from tier0.engine import effects


class DeadKnobError(RuntimeError):
    """A swept knob was never read while its cell ran.

    The sweep's rows are not a null result about that knob -- they are
    instrument error, and citing them is citing nothing.
    """


@contextmanager
def armed(knob: str, value) -> Iterator[None]:
    """Hold `knob` at `value` for the duration, restoring it after.

    Restoration happens on the way out of any exception too: a sweep that
    dies mid-cell must not leave the stamped default overwritten for
    whatever runs next in the same process.
    """
    original = C._arm_knob(knob, value)
    try:
        yield
    finally:
        C._disarm_knob(knob, original)


def sweep(knob: str, values: Iterable, run_cell: Callable[[Any], Any],
          *, label: str | None = None) -> Iterator[tuple[Any, Any]]:
    """Run `run_cell` once per value of `knob`, gated on KNOB_READS.

    Yields (value, result) per cell so callers can print as they go rather
    than waiting out the whole grid.

    Raises DeadKnobError the FIRST time a cell records zero reads. Failing
    on cell one rather than collecting the grid and complaining at the end
    is deliberate: a dead-knob sweep can be an hour of compute, and there is
    nothing to learn from finishing it.
    """
    name = label or knob
    for value in values:
        effects.reset_knob_reads()
        with armed(knob, value):
            result = run_cell(value)
        reads = effects.KNOB_READS.get(knob, 0)
        if reads == 0:
            raise DeadKnobError(
                f"{name} = {value!r}: the cell ran and never read {knob}. "
                f"Every row of this sweep would be identical, and identical "
                f"rows here mean instrument error, NOT 'the knob does not "
                f"matter'. Wire the knob to the code path under test or "
                f"delete it (R67); do not add a read to satisfy this gate "
                f"(R33 exercise-counter law).")
        yield value, result


def sweep_pairs(knobs: tuple[str, ...], value_rows: Iterable[tuple],
                run_cell: Callable[..., Any]) -> Iterator[tuple[tuple, Any]]:
    """`sweep()` for cells that move more than one knob at once.

    Each row of `value_rows` supplies one value per knob, positionally, and
    `run_cell` receives them as separate arguments. EVERY knob in the tuple
    must be read in EVERY cell -- a 2D sweep whose second axis is dead is
    the R7 rest-economy sweep, whose NORMAL_ATTRITION_SCALE axis was applied
    by nothing and which R67 deleted rather than fixed.
    """
    for row in value_rows:
        if len(row) != len(knobs):
            raise ValueError(f"row {row!r} does not supply one value per "
                             f"knob {knobs!r}")
        effects.reset_knob_reads()
        originals = []
        try:
            for knob, value in zip(knobs, row):
                originals.append((knob, C._arm_knob(knob, value)))
            result = run_cell(*row)
        finally:
            for knob, original in reversed(originals):
                C._disarm_knob(knob, original)
        dead = [k for k in knobs if effects.KNOB_READS.get(k, 0) == 0]
        if dead:
            raise DeadKnobError(
                f"cell {row!r}: swept {', '.join(dead)} without reading "
                f"{'them' if len(dead) > 1 else 'it'}. See sweep() -- this "
                f"is instrument error, not a null result.")
        yield row, result
