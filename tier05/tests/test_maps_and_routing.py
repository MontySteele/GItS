"""Act maps + route policies (§11).

The load-bearing test in this file is
`test_hunter_hits_the_player_behaviour_target`. Everything else guards the
generator's shape; that one guards the only calibration claim the map layer
makes, and it is calibrated against PLAYER BEHAVIOUR (a competent player
fights ~2.5 elites an act) rather than against a winrate. That distinction is
deliberate: an earlier attempt in this branch tuned enemy strength to hit a
winrate target and had to be retracted.
"""

from __future__ import annotations

import collections
import random
import statistics

import pytest

from tier0 import constants as C
from tier05 import maps, route

SEEDS = 400


def _maps(n=SEEDS, act=0):
    return [maps.generate(random.Random(s), act) for s in range(n)]


# --- generator shape -------------------------------------------------------

def test_fixed_floors_are_fixed():
    for m in _maps(60):
        assert all(r.kind == maps.NORMAL for r in m.floors[0])
        assert all(r.kind == maps.TREASURE
                   for r in m.floors[C.MAP_TREASURE_FLOOR])
        assert all(r.kind == maps.REST for r in m.floors[C.MAP_REST_FLOOR])
        assert [r.kind for r in m.floors[C.MAP_BOSS_FLOOR]] == [maps.BOSS]
        assert len(m.floors) == C.MAP_FLOORS


def test_every_room_reaches_the_boss_and_has_at_most_three_edges():
    """A room with no way up would be a dead end the walker could enter."""
    for m in _maps(60):
        for f, rooms in enumerate(m.floors[:-1]):
            for r in rooms:
                assert r.out, f"dead end at floor {f} index {r.index}"
                assert len(r.out) <= C.MAP_MAX_EDGES
                assert all(0 <= i < len(m.floors[f + 1]) for i in r.out)


def test_every_room_is_reachable_from_the_first_floor():
    for m in _maps(60):
        seen = {r.id for r in m.floors[0]}
        for f in range(len(m.floors) - 1):
            for r in m.floors[f]:
                if r.id in seen:
                    seen |= {s.id for s in m.successors(r)}
        assert seen == {r.id for fl in m.floors for r in fl}


def test_floors_are_at_most_six_wide():
    for m in _maps(60):
        assert max(len(f) for f in m.floors) <= C.MAP_MAX_FLOOR_WIDTH


def test_generation_is_seed_deterministic():
    a = maps.generate(random.Random(11), 0)
    b = maps.generate(random.Random(11), 0)
    assert [[r.kind for r in f] for f in a.floors] == \
           [[r.kind for r in f] for f in b.floors]
    assert [[r.out for r in f] for f in a.floors] == \
           [[r.out for r in f] for f in b.floors]


def test_room_odds_land_near_the_wiki_table():
    """Wiki-real: N 53 / ? 22 / R 12 / E 8 / $ 5, on non-fixed floors."""
    tally = collections.Counter()
    fixed = {0, C.MAP_TREASURE_FLOOR, C.MAP_REST_FLOOR, C.MAP_BOSS_FLOOR}
    for m in _maps():
        for f, rooms in enumerate(m.floors):
            if f not in fixed:
                tally.update(r.kind for r in rooms)
    n = sum(tally.values())
    for kind, want in C.MAP_ROOM_ODDS:
        assert tally[kind] / n == pytest.approx(want, abs=0.02), kind


# --- Unknown rooms ---------------------------------------------------------

def test_unknown_resolves_and_runs_a_pity_table():
    """Chosen kind resets to baseline, the others climb. Wiki-real RULE; the
    numbers themselves are stamped OPEN in constants."""
    w = maps.fresh_unknown_weights()
    assert w == C.MAP_UNKNOWN_BASE and w is not C.MAP_UNKNOWN_BASE
    rng = random.Random(3)
    seen = collections.Counter()
    for _ in range(400):
        before = dict(w)
        got = maps.resolve_unknown(rng, w)
        seen[got] += 1
        assert w[got] == C.MAP_UNKNOWN_BASE[got]
        for other in w:
            if other != got:
                assert w[other] == before[other] + C.MAP_UNKNOWN_STEP[other]
    assert set(seen) == set(C.MAP_UNKNOWN_BASE)     # every kind is reachable


# --- routing: the calibration target --------------------------------------

def _run_route(m, pol, hp_frac_at, rng):
    st = {"e": 0, "r": 0, "f": 0}

    def state_for():
        return route.RouteState(
            hp=int(80 * hp_frac_at(st["f"])), max_hp=80, gold=99,
            deck_size=15, floor=st["f"], act=0, elites_taken=st["e"],
            rests_taken=st["r"])

    cur = pol(rng, m, m.rooms_on(0), state_for())
    kinds = []
    while True:
        kinds.append(cur.kind)
        st["e"] += cur.kind == maps.ELITE
        st["r"] += cur.kind == maps.REST
        st["f"] += 1
        nxt = m.successors(cur)
        if not nxt:
            return kinds
        cur = pol(rng, m, nxt, state_for())


HEALTHY = lambda f: 1.0                                   # noqa: E731
DEGRADING = lambda f: 1.0 - 0.6 * f / 15                  # noqa: E731


@pytest.mark.battery
def test_hunter_hits_the_player_behaviour_target():
    """THE calibration claim. Domain ground truth (research §1.3): a competent
    player fights a median ~2.5 elites per act, realistic range 1-4, because
    elites are where relics come from.

    Measured on a healthy run, which is the ceiling the target describes.
    """
    counts = [sum(k == maps.ELITE for k in
                  _run_route(m, route.hunter, HEALTHY, random.Random(i)))
              for i, m in enumerate(_maps())]
    assert statistics.mean(counts) == pytest.approx(2.5, abs=0.35)
    dist = collections.Counter(counts)
    # 1-4 is the realistic band; the tails must be genuinely rare.
    assert sum(dist[k] for k in (1, 2, 3, 4)) / len(counts) > 0.90
    assert dist[0] / len(counts) < 0.06, \
        "a path-hunter should nearly always find at least one"


@pytest.mark.battery
def test_elite_count_responds_to_run_state():
    """The clause that makes the target meaningful. A policy that always takes
    exactly two hits the median and is still wrong -- a real player takes the
    third elite when healthy and ducks to one when hurt."""
    healthy = [sum(k == maps.ELITE for k in
                   _run_route(m, route.hunter, HEALTHY, random.Random(i)))
               for i, m in enumerate(_maps(200))]
    hurt = [sum(k == maps.ELITE for k in
                _run_route(m, route.hunter, DEGRADING, random.Random(i)))
            for i, m in enumerate(_maps(200))]
    assert statistics.mean(hurt) < statistics.mean(healthy) - 0.5

    # ...and the HP it does not spend on elites goes into rests.
    rests_healthy = statistics.mean(
        sum(k == maps.REST for k in
            _run_route(m, route.hunter, HEALTHY, random.Random(i)))
        for i, m in enumerate(_maps(200)))
    rests_hurt = statistics.mean(
        sum(k == maps.REST for k in
            _run_route(m, route.hunter, DEGRADING, random.Random(i)))
        for i, m in enumerate(_maps(200)))
    assert rests_hurt > rests_healthy + 0.5


@pytest.mark.battery
def test_the_two_policies_are_structurally_different():
    """The A/B is only worth running if the poles actually differ. `cautious`
    deliberately brackets BELOW the realistic floor -- it is not a model of a
    cautious player, it is the other end of the confounder check."""
    hunter_e = statistics.mean(
        sum(k == maps.ELITE for k in
            _run_route(m, route.hunter, HEALTHY, random.Random(i)))
        for i, m in enumerate(_maps(200)))
    cautious_e = statistics.mean(
        sum(k == maps.ELITE for k in
            _run_route(m, route.cautious, HEALTHY, random.Random(i)))
        for i, m in enumerate(_maps(200)))
    assert cautious_e < 1.0 < hunter_e


def test_planning_beats_greedy_at_finding_elites():
    """Regression on the actual bug this module was rewritten for.

    A next-room-only policy cannot route toward an elite three columns away;
    it reached zero elites on ~23% of maps. Whole-map planning is the fix, so
    pin that the planner beats a greedy stand-in by a wide margin.
    """
    def greedy(rng, act_map, options, st):
        want = {maps.ELITE: 10.0, maps.SHOP: 5.0, maps.TREASURE: 5.0,
                maps.UNKNOWN: 4.0, maps.REST: 6.0, maps.NORMAL: 2.0}
        return max(options, key=lambda r: (want.get(r.kind, 0.0), -r.index))

    ms = _maps(200)
    planned = statistics.mean(
        sum(k == maps.ELITE for k in
            _run_route(m, route.hunter, HEALTHY, random.Random(i)))
        for i, m in enumerate(ms))
    greedily = statistics.mean(
        sum(k == maps.ELITE for k in
            _run_route(m, greedy, HEALTHY, random.Random(i)))
        for i, m in enumerate(ms))
    assert planned > greedily + 0.75


def test_every_route_ends_on_the_boss_and_visits_one_room_per_floor():
    for i, m in enumerate(_maps(60)):
        for pol in route.POLICIES.values():
            kinds = _run_route(m, pol, HEALTHY, random.Random(i))
            assert len(kinds) == C.MAP_FLOORS
            assert kinds[-1] == maps.BOSS
            assert kinds[0] == maps.NORMAL
            assert kinds[C.MAP_TREASURE_FLOOR] == maps.TREASURE
            assert kinds[C.MAP_REST_FLOOR] == maps.REST
