"""Route policies: which room does the run walk into next (§11).

THE CONFOUNDER WARNING, up front. Draft-policy quality was pre-registered as
tier 0.5's central confounder (spec §0) precisely because a bad drafter makes
every card finding unreadable. Pathing adds a SECOND policy with the same
hazard: a route policy that is unusually good or bad at ducking elites moves
every run-level number, and "runs got better" then says nothing about cards,
characters or rosters. So the same countermeasures apply and are not optional:

  - two structurally DIFFERENT policies ship together (`hunter` and `cautious`
    below), and
  - every headline finding must survive the A/B across them.
  (The research doc's third countermeasure, a `route_regret` sampler
  analogous to draft_regret, was NEVER BUILT -- see
  docs/archive/missed-requirements.md §2.1. This header used to claim it existed.)

THE ACCEPTANCE TARGET (research doc §1.3, user domain authority): a competent
player fights a median of ~2.5 elites per act, range 1-4, because elites are
where relics come from. Critically the count must RESPOND TO RUN STATE -- a
healthy deck takes the third elite, a run at 20 HP ducks to one. A policy that
always takes exactly 2 hits the median and is still wrong, so
`run_metrics.route_profile` reports the distribution and its correlation with
arrival HP, never just the mean.

Do NOT calibrate these policies against the winrate. That is how the enemy
difficulty dial went wrong earlier in this branch.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from tier05.maps import ELITE, NORMAL, REST, SHOP, TREASURE, UNKNOWN, Room


@dataclass
class RouteState:
    """What a routing decision is allowed to see. Deliberately small: run
    state a real player can read off their screen, nothing about the map
    beyond the rooms actually on offer."""
    hp: int
    max_hp: int
    gold: int
    deck_size: int
    floor: int
    act: int
    elites_taken: int               # this act
    rests_taken: int                # this act

    @property
    def hp_frac(self) -> float:
        return self.hp / max(1, self.max_hp)


# --- planning ------------------------------------------------------------
#
# Routing is a WHOLE-MAP plan, not a one-floor choice. That distinction is the
# single most important thing in this module, and it was learned the hard way:
# a greedy next-room policy reached ZERO elites on 23% of maps and a median of
# 1, against a target median of 2.5. Not because elites were scarce -- there
# are ~4 on every map -- but because an elite three columns away is invisible
# to a policy that can only see one floor ahead. "Path-hunting" is precisely
# the act of reading the map and committing to a lane several floors early, so
# a model of it has to look that far.
#
# Implementation: value every room, then take the maximum-value path through
# the DAG by backward induction (rooms are layered by floor, so one reverse
# pass is exact). Re-plan at every floor, because the room values depend on
# live run state -- which is what makes the elite count respond to HP instead
# of being a constant.


def _plan(act_map, start: Room, value) -> tuple[float, list[Room]]:
    """Best (value, path) from `start` to the boss. Exact, not greedy."""
    best: dict[tuple[int, int], tuple[float, list[Room]]] = {}
    for floor in range(len(act_map.floors) - 1, -1, -1):
        for room in act_map.floors[floor]:
            succ = act_map.successors(room)
            if not succ:
                best[room.id] = (value(room), [room])
                continue
            # Ties break on room index so a seed replays identically.
            sv, sp = max((best[s.id] + (-s.index,) for s in succ),
                         key=lambda t: (t[0], t[2]))[:2]
            best[room.id] = (value(room) + sv, [room] + sp)
    return best[start.id]


def _make_value(want: dict[str, float], st: RouteState, elite_ok: bool):
    """Room -> value, under this policy's preferences and the CURRENT state.

    `elite_ok` False makes elites actively repellent rather than merely
    unattractive, so a hurt run routes AROUND them instead of tolerating one
    on the way to something it likes.
    """
    def value(room: Room) -> float:
        v = want.get(room.kind, 0.0)
        if room.kind == ELITE and not elite_ok:
            return -8.0
        if room.kind == REST:
            # A rest is worth what it heals; at full HP it is worth almost
            # nothing, which is why a healthy run walks past one.
            return want[REST] * min(1.0, 2.0 * (1.0 - st.hp_frac))
        return v
    return value


def _route(act_map, st: RouteState, options: list[Room],
           want: dict[str, float], elite_ok: bool) -> Room:
    scored = [(_plan(act_map, r, _make_value(want, st, elite_ok))[0], -r.index, r)
              for r in options]
    return max(scored, key=lambda t: t[:2])[2]


def hunter(rng: random.Random, act_map, options: list[Room],
           st: RouteState) -> Room:
    """Value-seeking: elites are relics, and relics win runs.

    Plans toward elites and keeps taking them, but the HP bar RISES with each
    one already taken this act (55% / 70% / 85%), so the third is a real
    decision rather than a reflex and a bruised run stops hunting. Sits at the
    top of the realistic 1-4 range.
    """
    want = {ELITE: 10.0, SHOP: 5.0, TREASURE: 5.0, UNKNOWN: 4.0,
            REST: 6.0, NORMAL: 2.0}
    bar = 0.55 + 0.15 * st.elites_taken
    elite_ok = st.hp_frac >= bar and st.elites_taken < 4
    return _route(act_map, st, options, want, elite_ok)


def cautious(rng: random.Random, act_map, options: list[Room],
             st: RouteState) -> Room:
    """Survival-seeking: HP is the resource, elites are a tax.

    Routes around elites unless nearly full. Sits at the bottom of the range.
    It is NOT meant to be the better policy -- it is the other end of the A/B,
    and if it wins outright that is itself a finding (elite relics underpriced).
    """
    want = {REST: 8.0, UNKNOWN: 6.0, TREASURE: 5.0, SHOP: 4.0,
            NORMAL: 3.0, ELITE: 1.0}
    return _route(act_map, st, options, want, st.hp_frac >= 0.9)


POLICIES = {"hunter": hunter, "cautious": cautious}


def walk(rng: random.Random, act_map, policy, state_for) -> list[Room]:
    """Walk floor 1 -> boss, re-planning at every floor.

    `state_for()` returns the CURRENT RouteState and is called fresh each
    floor rather than passed once, because the whole point is that routing
    responds to run state as the run degrades.

    This pure-map version is for tests and the route-regret sampler; the live
    run walks incrementally in model.run_one so fights resolve between
    decisions.
    """
    path = [policy(rng, act_map, act_map.rooms_on(0), state_for())]
    while True:
        nxt = act_map.successors(path[-1])
        if not nxt:
            return path
        path.append(policy(rng, act_map, nxt, state_for()))
