"""Track O slice 3 -- pins on the `player.resources` reader's UNSEEN discipline.

These lock only the behaviours whose correct answer is unambiguous from the
instrument's own declarations:

  understudy/soak.py:585-601   -1 is UNSEEN, never a zero; a pre-P1.5 bridge
                               (no `resources` key) must keep saying "unseen"
  understudy/soak.py:641-643   the resource is AUTHORITATIVE over the badge
  understudy/replay.py:301-307 `encore == -1` leaves the sim's own value alone
                               and suppresses that turn's comparison
  understudy/replay.py:677-686 an all-zero Encore column is reading corruption

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

from understudy import replay, soak

FIX = os.path.join(os.path.dirname(__file__), "..", "..",
                   "review", "redteam", "fixtures", "track_o")


def _wire(case):
    with open(os.path.join(FIX, "s03-resources-wire.json"), encoding="utf-8") as fh:
        return {"player": json.load(fh)[case]["player"]}


def _fight(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return json.load(fh)


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


def test_unseen_encore_leaves_the_sim_value_alone():
    """replay.py:301-307 -- -1 must not be loaded onto the player."""
    player = replay._fresh_player("furina", 60, 70, 0, {})
    player.encore = 5
    replay._apply_meters(player, {"fanfare": 7, "salon_members": 1,
                                  "salon_cap": 3, "encore": -1})
    assert player.encore == 5


def test_seen_encore_is_loaded_onto_the_sim_player():
    player = replay._fresh_player("furina", 60, 70, 0, {})
    player.encore = 5
    replay._apply_meters(player, {"fanfare": 7, "salon_members": 1,
                                  "salon_cap": 3, "encore": 4})
    assert player.encore == 4


def test_all_zero_encore_column_is_flagged_as_corruption():
    """replay.py:677-686 -- the sentinel wearing a zero, fight-wide."""
    assert replay._encore_unseen(_fight("s03-allzero-fight.json")) is True


def test_a_column_with_real_reads_is_not_flagged():
    """Sanity companion: a column carrying non-zero reads is not corruption."""
    fight = {"meters_by_turn": [[1, 5, 1, 3, 4], [2, 7, 1, 3, 6]]}
    assert replay._encore_unseen(fight) is False


def test_meters_at_defaults_encore_to_unseen_on_a_short_row():
    """A row written by a pre-P1.5 soak has no 5th column."""
    fight = {"meters_by_turn": [[1, 5, 1, 3]]}
    assert replay._meters_at(fight, 1)["encore"] == -1
