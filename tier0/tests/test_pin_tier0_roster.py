"""Pin tests for the two roster-layer facts nothing else reads back.

Both are DECLARATIONS rather than derivations: the index of the act map's
fixed Treasure floor, and the order the shipped characters are registered in.
Every existing test reads each of them back out of the thing that declares it
(`C.MAP_TREASURE_FLOOR`, `roster.ROSTER`), so either can be moved to any other
value and stay self-consistent -- while the run-layer economy shifts under the
map, and every roster-ordered report and roster.IDS-parametrized sweep quietly
permutes.
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier0 import roster
from tier05 import maps


# --- the act map's fixed Treasure floor ----------------------------------

def test_treasure_floor_is_map_index_eight():
    """The all-Treasure floor sits at 0-based map index 8 -- wiki floor 9,
    the midpoint of the 16 modelled floors. Its index is a layout fact, not a
    free parameter: the freely-typed floor budget (wiki 2-8 below it and 10-14
    above it) and the spacing against the Rest floor at 14 and the Boss floor
    at 15 are all counted off it.
    """
    assert C.MAP_TREASURE_FLOOR == 8


def test_generated_maps_put_every_treasure_room_on_floor_eight():
    """A generated act map carries its Treasure rooms on exactly one floor,
    index 8, and Treasure appears nowhere else: no other floor is fixed to
    Treasure and no room rolls it, because Treasure is not among the room
    odds. Sliding the fixed floor one step would move an entire floor's worth
    of reward off index 8 and onto its neighbour.
    """
    for seed in range(20):
        m = maps.generate(random.Random(seed), act=0)
        assert all(r.kind == maps.TREASURE for r in m.floors[8])
        for floor, rooms in enumerate(m.floors):
            if floor == 8:
                continue
            assert all(r.kind != maps.TREASURE for r in rooms), floor


# --- the roster's declared ship order ------------------------------------

def test_roster_ids_are_declaration_order_not_alphabetical():
    """`roster.IDS` is the ROSTER tuple's own order, position for position --
    ship order, which is klee then furina then kokomi. It is documented as
    stable and meaningful ("Append; never reorder") because reports print the
    roster in it and sweeps are parametrized over it, so it must never be
    re-derived by sorting: alphabetical order would move furina ahead of klee.
    """
    assert roster.IDS == tuple(c.id for c in roster.ROSTER)
    assert roster.IDS[:3] == ("klee", "furina", "kokomi")
    assert roster.IDS != tuple(sorted(roster.IDS))
