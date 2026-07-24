"""Act maps: the real StS2 17-floor DAG, generated per act (§11).

Replaces the fixed `RUN_NODE_TEMPLATE` spine. Research and the numbers behind
every constant: `docs/sts2-map-and-events-research.md` §1.

Shape (wiki-real, A0):
  - 17 floors, up to MAX_FLOOR_WIDTH rooms each, 1-3 edges per room to the
    floor above.
  - Fixed floors: 1 = easy-pool monsters, 9 = Treasure, 15 = Rest, 16 = Boss.
    Floor 17 (the boss chest) is folded into the boss reward, not a room.
  - Every other room rolls its own type from ROOM_ODDS.
  - The same elite never appears twice in a row ON A PATH; enforced at walk
    time by the encounter draw, not here.

WHY THE WIDTH MATTERS (§1.1): the 8% elite rate is per ROOM, not per floor.
On a 6-wide map that is 4-6 elite ROOMS per act, and how many the player
actually FIGHTS is a routing outcome (target: median ~2.5, range 1-4) rather
than a map statistic. A one-room-wide map would silently make elite count an
authored constant again, which is the thing this module exists to stop.

Determinism: every roll flows through the caller's `random.Random`, the same
contract as the rest of tier 0.5.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from tier0 import constants as C

# Node kinds, shared with the run model. "?" is an Unknown room: it resolves
# to one of RoomKind at ENTRY (see resolve_unknown), never at generation.
BOSS, TREASURE, REST, SHOP, ELITE, NORMAL, UNKNOWN = "B", "T", "R", "$", "E", "N", "?"


@dataclass
class Room:
    floor: int
    index: int                      # position within its floor, left to right
    kind: str
    out: list[int] = field(default_factory=list)   # room indices on floor+1

    @property
    def id(self) -> tuple[int, int]:
        return (self.floor, self.index)


@dataclass
class ActMap:
    act: int
    floors: list[list[Room]]

    def rooms_on(self, floor: int) -> list[Room]:
        return self.floors[floor]

    def successors(self, room: Room) -> list[Room]:
        if room.floor + 1 >= len(self.floors):
            return []
        nxt = self.floors[room.floor + 1]
        return [nxt[i] for i in room.out]

    def count(self, kind: str) -> int:
        return sum(1 for fl in self.floors for r in fl if r.kind == kind)


def _fixed_kind(floor: int) -> str | None:
    """The guaranteed contents of a fixed floor, or None if it rolls."""
    if floor == 0:
        return NORMAL                       # floor 1: easy-pool monsters
    if floor == C.MAP_TREASURE_FLOOR:
        return TREASURE
    if floor == C.MAP_REST_FLOOR:
        return REST
    if floor == C.MAP_BOSS_FLOOR:
        return BOSS
    return None


def _roll_kind(rng: random.Random) -> str:
    r = rng.random()
    acc = 0.0
    for kind, p in C.MAP_ROOM_ODDS:
        acc += p
        if r < acc:
            return kind
    return C.MAP_ROOM_ODDS[-1][0]


def generate(rng: random.Random, act: int = 0) -> ActMap:
    """One act's map, built the way the real generator builds one.

    PATH CARVING, not per-floor width rolls. `MAP_PATHS` routes are walked
    from the bottom floor to the top, each stepping left / straight / right one
    column per floor; a room EXISTS iff some path visits it, and an edge exists
    iff some path uses it. Floor width and the 1-3 edge fan-out are therefore
    emergent, which is both what the source game does and the only way to get
    a map whose lanes actually merge and cross.

    The first implementation here rolled a width per floor and gave each room a
    contiguous span of forward edges centred on its own column. That produced
    strictly lane-locked maps: a run could not cross the board, so ~9% of
    elite-hunting routes reached ZERO elites and the median sat at 2.0 against
    a target of 2.5 (research §1.3) -- and widening floors did not help, which
    was the tell that connectivity, not room count, was the binding
    constraint. Recorded because "add more of the thing you want" is the
    tempting wrong fix.

    All randomness flows through `rng`.
    """
    grid: dict[tuple[int, int], Room] = {}
    edges: dict[tuple[int, int], set[int]] = {}

    def room_at(f: int, col: int) -> Room:
        if (f, col) not in grid:
            grid[(f, col)] = Room(floor=f, index=col, kind="")
            edges[(f, col)] = set()
        return grid[(f, col)]

    width = C.MAP_MAX_FLOOR_WIDTH
    for p in range(C.MAP_PATHS):
        # Spread the starts so floor 1 is genuinely several rooms wide, then
        # let the walk wander.
        col = rng.randrange(width) if p >= width else p
        room_at(0, col)
        for f in range(C.MAP_FLOORS - 1):
            if f + 1 == C.MAP_BOSS_FLOOR:
                nxt = 0                     # every route converges on the boss
            else:
                steps = [c for c in (col - 1, col, col + 1) if 0 <= c < width]
                nxt = rng.choice(steps)
            room_at(f + 1, nxt)
            edges[(f, col)].add(nxt)
            col = nxt

    # Compact each floor's occupied columns to contiguous indices, so `index`
    # stays a left-to-right position and `out` indexes the floor above.
    floors: list[list[Room]] = []
    remap: list[dict[int, int]] = []
    for f in range(C.MAP_FLOORS):
        cols = sorted(c for (ff, c) in grid if ff == f)
        remap.append({c: i for i, c in enumerate(cols)})
        fixed = _fixed_kind(f)
        floors.append([
            Room(floor=f, index=i, kind=fixed or _roll_kind(rng))
            for i, _ in enumerate(cols)])
    for f in range(C.MAP_FLOORS - 1):
        for col, i in remap[f].items():
            floors[f][i].out = sorted(remap[f + 1][c]
                                      for c in edges[(f, col)])
    return ActMap(act=act, floors=floors)


def resolve_unknown(rng: random.Random, weights: dict[str, float]) -> str:
    """What an Unknown room turns into, rolled AT ENTRY (§1).

    `weights` is the run's live pity table and is MUTATED: the chosen kind
    resets to its baseline, every other kind gains its increment. That is the
    real game's rule; the baselines and increments themselves are an OPEN
    NUMBER (the wiki publishes neither -- §5.1), stamped in constants.
    """
    kinds = list(weights)
    total = sum(weights[k] for k in kinds)
    r, acc = rng.random() * total, 0.0
    chosen = kinds[-1]
    for k in kinds:
        acc += weights[k]
        if r < acc:
            chosen = k
            break
    for k in kinds:
        if k == chosen:
            weights[k] = C.MAP_UNKNOWN_BASE[k]
        else:
            weights[k] += C.MAP_UNKNOWN_STEP[k]
    return chosen


def fresh_unknown_weights() -> dict[str, float]:
    """A run's Unknown pity table, reset per act (the real rule)."""
    return dict(C.MAP_UNKNOWN_BASE)
