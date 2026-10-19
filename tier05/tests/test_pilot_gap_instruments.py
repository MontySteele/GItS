"""The three instrument changes the pilot-gap sprint makes (2026-07-28).

Same standard as the sprint before it: an instrument that quietly reports the
wrong number is worse than no instrument, because the sprint after this one
will make a ruling out of it. Each test below is written against a specific
way the change could have been wrong, not against the implementation.

The three:
  1. `encore_telemetry` gained a RUNWAY rate (its reader left with the
     shipped Encore buffer, 2026-10-13; its tests went with it).
  2. `fanfare_telemetry` gained a per-SOURCE reduction (its reader left with
     the shipped Fanfare meter, 2026-10-19; its tests went with it).
  3. `cells.Cell` gains `pilot_override`, which lands in `stamp()` -- the
     brief's "never quote a stoker row against a greedy row without both
     labels" rule, enforced by the mandatory stamp line rather than by
     discipline.
"""

from __future__ import annotations

import pytest

from tier05 import cells


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
