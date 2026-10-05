"""Track O slice 3 -- pins on the `player.resources` reader's UNSEEN discipline.

These lock only the behaviours whose correct answer is unambiguous from the
instrument's own declarations:

  understudy/soak.py:585-601   -1 is UNSEEN, never a zero; a pre-P1.5 bridge
                               (no `resources` key) must keep saying "unseen"
  understudy/soak.py:641-643   the resource is AUTHORITATIVE over the badge

(The replay half -- `replay._apply_meters`, `_meters_at`, `_encore_unseen` --
left with `meters_by_turn`, 2026-10-04.)

The known SILENT-LIEs found in this slice (partial degradation writing a hard
0 into the Encore column; `_encore_unseen` defeated by an intermittently
degraded column; the fanfare floor/cap resources dropped on the wire) are NOT
pinned here -- a pin asserting the right answer on those paths would fail, and
a red test does not belong in the suite. They live in the slice-03 report.

Fixtures: review/redteam/fixtures/track_o/s03-*.json
"""

import json
import os

import pytest

from understudy import soak

FIX = os.path.join(os.path.dirname(__file__), "..", "..",
                   "review", "redteam", "fixtures", "track_o")


def _wire(case):
    with open(os.path.join(FIX, "s03-resources-wire.json"), encoding="utf-8") as fh:
        return {"player": json.load(fh)[case]["player"]}


def test_healthy_resource_map_is_read_and_beats_the_badge():
    """A full map supplies both meters; Fanfare comes from the resource."""
    fanfare, salon, cap, encore = soak._meters(_wire("healthy"))
    assert (fanfare, salon, cap, encore) == (7, 2, soak.SALON_PRINTED_CAP, 4)


def test_absent_resources_key_keeps_encore_unseen():
    """Pre-P1.5 bridge: no `resources` key at all -> UNSEEN, not zero."""
    assert soak._meters(_wire("old_bridge"))[3] == soak.METER_UNSEEN


def test_present_but_unparseable_encore_stays_unseen():
    """A key that is there but does not coerce must not become a zero."""
    assert soak._meters(_wire("null_amounts"))[3] == soak.METER_UNSEEN


def test_non_dict_resources_blob_degrades_to_unseen():
    """A `resources` value of the wrong shape must not fabricate a meter."""
    assert soak._meters(_wire("resources_not_a_map"))[3] == soak.METER_UNSEEN


@pytest.mark.parametrize("case", ["healthy", "old_bridge", "declared_empty",
                                  "partial_drop_encore", "coerce_string",
                                  "null_amounts", "resources_not_a_map"])
def test_reader_never_raises_on_any_wire_shape(case):
    """GitsResources.cs:104-107 -- a state read must never throw."""
    out = soak._meters(_wire(case))
    assert len(out) == 4 and all(isinstance(v, int) for v in out)
