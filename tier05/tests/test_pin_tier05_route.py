"""Pin tests for the route/map/cell seam (§11 + R68).

Three things in this seam are load-bearing and were measured only in
aggregate, so their exact values could move without a test noticing:

  - the MAGNITUDE of the elite-avoidance penalty and the top of the hunter's
    per-act elite cap (route.py) -- the existing routing tests bound only the
    mean elite count and the sign of the avoidance, so a hurt or capped run
    could walk a different lane through different shops, rests and unknown
    rooms while the elite count stayed identical;
  - that a generated map actually uses its full board width (maps.py) -- the
    shape tests bound width only from above;
  - the definition of every field in `Cell.arm()` (cells.py), the consolidated
    summary row every exp_*.py script reports its headline numbers from.
"""

from __future__ import annotations

import random
import types

from tier0 import constants as C
from tier05 import cells, maps, route
from tier05.maps import ELITE, NORMAL, SHOP, TREASURE, ActMap, Room


def _state(hp: int, elites_taken: int = 0) -> route.RouteState:
    return route.RouteState(hp=hp, max_hp=80, gold=0, deck_size=15, floor=0,
                            act=0, elites_taken=elites_taken, rests_taken=0)


HUNTER_WANT = {ELITE: 10.0, SHOP: 5.0, TREASURE: 5.0, maps.UNKNOWN: 4.0,
               maps.REST: 6.0, NORMAL: 2.0}


# --- the elite-avoidance penalty (route._make_value) ------------------------

def test_repelled_elite_is_worth_minus_eight_regardless_of_the_policy_want():
    """When `elite_ok` is False an elite room scores exactly -8.0, replacing
    (not merely discounting) whatever the policy's `want` table pays for an
    elite. Every other room kind still scores its `want` value."""
    elite = Room(floor=1, index=0, kind=ELITE)
    normal = Room(floor=1, index=1, kind=NORMAL)

    repelled = route._make_value(HUNTER_WANT, _state(20), False)
    assert repelled(elite) == -8.0
    assert repelled(normal) == 2.0

    # A policy that pays only 1.0 for an elite gets the same -8.0 when hurt,
    # and the full want back when elites are allowed again.
    cautious_want = dict(HUNTER_WANT, **{ELITE: 1.0})
    assert route._make_value(cautious_want, _state(20), False)(elite) == -8.0
    assert route._make_value(HUNTER_WANT, _state(80), True)(elite) == 10.0


def test_elite_repulsion_outweighs_a_shop_and_treasure_on_the_same_lane():
    """The penalty is big enough that a hurt run routes AROUND an elite even
    when the elite's lane also carries the two best non-elite rooms on the
    map: -8.0 for the elite plus 5.0 shop plus 5.0 treasure loses to a lane of
    plain normal rooms."""
    m = ActMap(act=0, floors=[
        [Room(0, 0, NORMAL, out=[0]), Room(0, 1, NORMAL, out=[1])],
        [Room(1, 0, ELITE, out=[0]), Room(1, 1, NORMAL, out=[1])],
        [Room(2, 0, SHOP, out=[0]), Room(2, 1, NORMAL, out=[1])],
        [Room(3, 0, TREASURE, out=[]), Room(3, 1, NORMAL, out=[])],
    ])
    hurt = _state(20)                       # hp_frac 0.25, well under the bar
    value = route._make_value(HUNTER_WANT, hurt, False)
    assert route._plan(m, m.floors[0][0], value)[0] == 4.0      # elite lane
    assert route._plan(m, m.floors[0][1], value)[0] == 8.0      # plain lane

    assert route.hunter(random.Random(0), m, m.rooms_on(0), hurt).index == 1


# --- the hunter's per-act elite cap (route.hunter) --------------------------

def test_hunter_still_takes_a_fourth_elite_at_full_hp_but_never_a_fifth():
    """The declared 1-4 range includes its top. With three elites already
    taken this act, a run at FULL hp clears the 0.55 + 0.15 * taken bar and
    still routes into an elite; with four taken it no longer does."""
    m = ActMap(act=0, floors=[
        [Room(0, 0, NORMAL, out=[0]), Room(0, 1, NORMAL, out=[1])],
        [Room(1, 0, ELITE, out=[]), Room(1, 1, NORMAL, out=[])],
    ])
    rng = random.Random(0)
    for taken in (0, 1, 2, 3):
        assert route.hunter(rng, m, m.rooms_on(0),
                            _state(80, taken)).index == 0, taken
    assert route.hunter(rng, m, m.rooms_on(0), _state(80, 4)).index == 1


# --- the generator uses the whole board (maps.generate) ---------------------

def test_carved_paths_can_occupy_every_column_above_the_first_floor():
    """Path carving may step left / straight / right into ANY column of the
    board, so floors above floor 1 -- whose rooms come only from the carve,
    not from the spread starts -- reach the full MAP_MAX_FLOOR_WIDTH. Clipping
    a lane off the carve would shrink the map silently, since the shape tests
    bound width only from above."""
    seed1 = maps.generate(random.Random(1), 0)
    assert max(len(f) for f in seed1.floors[1:]) == C.MAP_MAX_FLOOR_WIDTH

    full = sum(max(len(f) for f in maps.generate(random.Random(s), 0).floors[1:])
               == C.MAP_MAX_FLOOR_WIDTH
               for s in range(60))
    assert full >= 5, "the top lane of the board is never carved into"


# --- the consolidated summary row (cells.Cell.arm) --------------------------

def _fake_result(won, acts_completed, deck, fights):
    return types.SimpleNamespace(won=won, acts_completed=acts_completed,
                                 deck_ids=list(deck),
                                 fight_stats=[None] * fights)


def test_arm_reduces_results_to_the_standard_summary_row(monkeypatch):
    """`act1` is the share of runs with acts_completed >= 1 -- acts_completed
    counts boss wins, so clearing act 1 IS one completed act, and a run that
    died in act 2 still counts. `win` / `acts` / `decksize` / `fights` are the
    win share and the plain means of acts, final deck size and fights taken,
    over every result; `results` is passed through untouched and `decks` is
    the per-run list of final deck ids."""
    results = [_fake_result(False, 0, "ab", 1),        # died in act 1
               _fake_result(False, 1, "abc", 2),       # cleared act 1, died
               _fake_result(True, 3, "abcd", 3)]       # won
    monkeypatch.setattr(cells.Cell, "run", lambda self: results)

    row = cells.CANONICAL.but(runs=3).arm()

    assert row["act1"] == 2 / 3
    assert row["win"] == 1 / 3
    assert row["acts"] == 4 / 3
    assert row["decksize"] == 3.0
    assert row["fights"] == 2.0
    assert row["results"] is results
    assert row["decks"] == [["a", "b"], ["a", "b", "c"], ["a", "b", "c", "d"]]
