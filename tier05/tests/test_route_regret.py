"""`run_metrics.route_regret` -- the research doc's third route countermeasure
(§4.2: "a `route_regret` instrument analogous to `draft_regret`"), built for
BACKLOG EB-16 after `route.py`'s header advertised it for a fortnight without
it existing.

What these tests pin is the CONSTRUCTION, not a calibrated number:

  - in the deciding state the sampler must read exactly zero, because the
    planner takes the argmax there -- if this ever goes positive the planner
    and the re-scorer have drifted apart, which is the failure mode that
    makes the instrument lie in the direction of "the policy is bad";
  - a road genuinely better than the one walked must show up, at its exact
    value gap, so the magnitude means something in an A/B;
  - and the whole thing replays on a seed, because the route A/B is a seeded
    comparison and an instrument that wanders is not a countermeasure.
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier05 import draft, maps, model, route, run_metrics
from tier05.maps import ELITE, NORMAL, SHOP, TREASURE, ActMap, Room

SEED = 42


def _state(hp: int, elites_taken: int = 0) -> route.RouteState:
    return route.RouteState(hp=hp, max_hp=80, gold=0, deck_size=15, floor=0,
                            act=0, elites_taken=elites_taken, rests_taken=0)


HEALTHY, HURT = _state(80), _state(20)


def _two_lane_map() -> ActMap:
    """Lane 0 is the rich one: normal + elite + shop + treasure. Lane 1 is
    four plain normals. The lanes never merge, so floor 1 is the only real
    choice on the board and every gap the sampler reports is that one
    decision, arithmetic a reader can do by hand."""
    return ActMap(act=0, floors=[
        [Room(0, 0, NORMAL, out=[0]), Room(0, 1, NORMAL, out=[1])],
        [Room(1, 0, ELITE, out=[0]), Room(1, 1, NORMAL, out=[1])],
        [Room(2, 0, SHOP, out=[0]), Room(2, 1, NORMAL, out=[1])],
        [Room(3, 0, TREASURE, out=[]), Room(3, 1, NORMAL, out=[])],
    ])


def _decisions(m, policy, st):
    return route.walk_decisions(random.Random(0), m, policy, lambda: st)


# --- zero when the policy picked the argmax ---------------------------------

def test_no_regret_when_the_sampler_looks_back_from_the_deciding_state():
    """Re-scored in the very state it chose in, `hunter` cannot regret: the
    planner already maximised over these path values. Zero here is the
    instrument's calibration, not a lucky map."""
    m = _two_lane_map()
    got = run_metrics.route_regret(random.Random(0), m,
                                   _decisions(m, route.hunter, HEALTHY),
                                   HEALTHY, "hunter")
    assert got["sampled"] == 1                  # one forked floor on this map
    assert got["forced"] == 3
    assert got["max_regret"] == 0.0
    assert got["regretted"] == 0


def test_no_regret_on_a_generated_map_for_either_policy():
    """The same claim where the map has real forks all the way up: over sixty
    seeded maps, neither policy regrets a single decision it made in the state
    it is being judged in. The `sampled` assertion is there so a sampler that
    silently measured nothing could not pass this."""
    for name, policy in route.POLICIES.items():
        total = 0
        for seed in range(60):
            m = maps.generate(random.Random(seed), 0)
            got = run_metrics.route_regret(random.Random(seed), m,
                                           _decisions(m, policy, HEALTHY),
                                           HEALTHY, name)
            assert got["max_regret"] == 0.0, (name, seed)
            total += got["sampled"]
        assert total > 100, name


# --- positive when a better path existed ------------------------------------

def test_a_policy_that_walks_the_poorer_lane_regrets_by_the_exact_gap():
    """Regret is a MAGNITUDE, and it is the difference between the two path
    values the planner would have quoted. A stub policy that always takes the
    right-hand room walks the plain lane (2+2+2+2 = 8) past the rich one
    (2+10+5+5 = 22), so the gap is 14.0 -- and it lands on the one floor that
    was actually a fork."""
    m = _two_lane_map()
    rightmost = lambda rng, act_map, options, st: options[-1]   # noqa: E731

    got = run_metrics.route_regret(random.Random(0), m,
                                   _decisions(m, rightmost, HEALTHY),
                                   HEALTHY, "hunter")

    assert got["sampled"] == 1
    assert got["max_regret"] == 14.0
    assert got["mean_regret"] == 14.0
    assert got["p50_regret"] == 14.0
    assert got["regretted"] == 1
    assert got["regret_rate"] == 1.0


def test_hindsight_turns_the_elite_lane_into_a_regret():
    """THE instrument, doing the job §4.2 asked for. `hunter` at full HP takes
    the elite lane and is right to. Judged from a run that arrived at 20 HP,
    the elite is repellent (-8.0) instead of a prize (+10.0), the rich lane is
    worth 4.0 against the plain lane's 8.0, and the decision reads as 4.0 of
    regret. Nothing about the policy changed -- only what the run turned out
    to be able to afford."""
    m = _two_lane_map()
    decisions = _decisions(m, route.hunter, HEALTHY)
    assert decisions[0]["picked"].index == 0            # took the rich lane

    got = run_metrics.route_regret(random.Random(0), m, decisions,
                                   HURT, "hunter")
    assert got["max_regret"] == 4.0
    assert got["regretted"] == 1

    # And the gap is a property of the hindsight state, not of the sampler:
    # `cautious`, which never wanted the elite, prices the same road-not-taken
    # differently (plain lane 3*3 + 3 = 12 against 3 + 1 + 4 + 5 = 13 healthy,
    # so it regrets nothing until the elite turns repellent).
    assert run_metrics.route_regret(random.Random(0), m, decisions,
                                    HEALTHY, "cautious")["max_regret"] == 0.0


def test_forced_floors_are_not_counted_as_decisions():
    """A one-room-per-floor map is a corridor: four floors walked, zero
    choices, and the rate is 0.0 rather than a division by nothing."""
    m = maps.linear([NORMAL, ELITE, SHOP, TREASURE])
    got = run_metrics.route_regret(random.Random(0), m,
                                   _decisions(m, route.hunter, HEALTHY),
                                   HEALTHY, "hunter")
    assert (got["decisions"], got["forced"], got["sampled"]) == (4, 4, 0)
    assert got["regret_rate"] == got["mean_regret"] == 0.0
    assert got["p50_regret"] == got["max_regret"] == 0.0


# --- determinism ------------------------------------------------------------

def test_route_regret_replays_identically_on_a_seeded_map():
    """Same map seed, same walk, same sampler seed -> the same dict, including
    when the sample rate is throttled and the rng actually decides which
    decisions get re-scored. Two DIFFERENT sampler seeds are allowed to
    disagree on the sample; that they do is what makes the first assertion
    worth making."""
    def run(map_seed: int, rng_seed: int, sample: float) -> dict:
        m = maps.generate(random.Random(map_seed), 0)
        return run_metrics.route_regret(
            random.Random(rng_seed), m,
            _decisions(m, route.hunter, HEALTHY), HURT, "hunter",
            sample=sample)

    assert run(11, 3, 1.0) == run(11, 3, 1.0)
    assert run(11, 3, 0.4) == run(11, 3, 0.4)

    full = run(11, 3, 1.0)
    assert full["sampled"] > 0
    thrown = [run(11, s, 0.4)["sampled"] for s in range(12)]
    assert min(thrown) < full["sampled"]        # the throttle actually throttles
    assert max(thrown) <= full["sampled"]


# --- the live wiring (EB-16w) -----------------------------------------------
#
# Everything above tests the sampler on a pure map. These test that a REAL run
# feeds it -- the half EB-16 left open, where `model.run_one` walked
# incrementally and wrote none of it down.

def _live(runs: int = 6, seed: int = SEED, **kw) -> list:
    return model.run_many("klee", "spark", "spark", draft.assigned_policy,
                          runs, seed, **kw)


def test_the_live_run_records_the_walk_it_actually_walked():
    """One `route_decisions` entry per act, and inside it the same records
    `walk_decisions` would have written: consecutive floors from 0, options
    drawn from the map's own floor, and every pick a successor of the last.
    The pure-map helper cannot produce these -- it has no fights to resolve --
    so the live walk has to record them itself, and this is what pins that the
    two walks are the same walk."""
    r = _live(runs=1)[0]
    assert r.route_decisions                       # not an empty instrument
    for act_i, w in enumerate(r.route_decisions):
        assert w["act"] == act_i
        recs = w["decisions"]
        assert [d["floor"] for d in recs] == list(range(len(recs)))
        assert recs[0]["options"] == w["map"].rooms_on(0)
        for d in recs:
            assert d["picked"] in d["options"]
        for prev, nxt in zip(recs, recs[1:]):
            assert nxt["picked"] in w["map"].successors(prev["picked"])
            assert nxt["options"] == w["map"].successors(prev["picked"])
    # A run that survived walked every floor of every act.
    if r.won:
        assert all(len(w["decisions"]) == C.MAP_FLOORS
                   for w in r.route_decisions)


def test_the_run_ends_holding_the_hindsight_state_the_sampler_needs():
    """`route_hindsight` is the route twin of the final deck: without it there
    is nothing to re-price against, and a death exit needs it as much as a win
    does (that is the run whose road-not-taken is most interesting)."""
    results = _live(runs=12)
    assert any(not r.won for r in results), "fixture no longer covers deaths"
    for r in results:
        st = r.route_hindsight
        assert st is not None
        assert st.hp <= st.max_hp
        # It is the END state, not a mid-run snapshot: a death carries the
        # killing blow's overkill (hp can be negative, exactly as the run
        # loop left it -- `hp_by_node` is the clamped view, this is not), a
        # survivor is alive. The valuation only reads hp_frac through a
        # min(1.0, ...) clip, so overkill is harmless and clamping it here
        # would be inventing a state the run never had.
        # (A loss can still hold HP -- the fight loop calls a stall-out a loss
        # -- so only the survivor direction is an invariant.)
        if r.won:
            assert st.hp > 0


def test_run_many_calls_the_sampler_on_every_act_of_a_real_run():
    """The wiring itself: `route_regret` carries one sampler summary per act,
    filled at the same site the drafter's `regret_samples` is."""
    for r in _live(runs=6):
        assert len(r.route_regret) == len(r.route_decisions)
        for d, w in zip(r.route_regret, r.route_decisions):
            assert d["policy"] == r.route
            assert d["decisions"] == len(w["decisions"])
            assert d["forced"] + d["sampled"] == d["decisions"]
            assert d["max_regret"] >= 0.0


def test_live_route_regret_is_deterministic():
    """The drafter's pin (test_m5.test_draft_regret_deterministic), one layer
    out: the sampler runs on a DEDICATED stream, so the same seed gives the
    same regret and -- because that stream is dedicated -- the same run."""
    a, b = _live(runs=8), _live(runs=8)
    assert [x.route_regret for x in a] == [x.route_regret for x in b]
    assert [x.hp_by_node for x in a] == [x.hp_by_node for x in b]


def test_recording_the_walk_draws_no_rng_of_its_own():
    """The recording must be free. If it consumed a draw, or if the sampler
    reached into the run stream, every seeded number in the repo would
    renumber -- so the run under the parallel path (a different process, same
    seeds) has to stay element-for-element identical to the serial one."""
    serial = _live(runs=4, jobs=1)
    parallel = _live(runs=4, jobs=2)
    for x, y in zip(serial, parallel):
        assert (x.hp_by_node, x.deck_ids, x.node_kinds) == \
               (y.hp_by_node, y.deck_ids, y.node_kinds)
        assert x.route_regret == y.route_regret


def test_pooled_route_regret_reports_the_run_layer_totals():
    """`run_metrics.route_profile` carries the pooled read, which is where a
    route A/B (the "elite relics are underpriced" comparison, research §3.7.5)
    picks it up. Counts add; the mean is sample-weighted; no pooled
    percentiles are invented."""
    results = _live(runs=6)
    pooled = run_metrics.route_profile(results)["regret"]
    per_act = [d for r in results for d in r.route_regret]
    assert pooled["acts_sampled"] == len(per_act)
    assert pooled["sampled"] == sum(d["sampled"] for d in per_act)
    assert pooled["forced"] == sum(d["forced"] for d in per_act)
    assert pooled["max_regret"] == max(d["max_regret"] for d in per_act)
    assert "p50_regret" not in pooled and "p90_regret" not in pooled
    assert pooled["margin"] == run_metrics.ROUTE_REGRET_MARGIN


def test_the_sample_rate_is_homed_in_constants_beside_its_draft_twin():
    """EB-16w: the rate is a tier0 constant now, not a module literal, and it
    is the sampler's default. 1.0 against the drafter's 0.10 is deliberate --
    see the constant's comment. The MARGIN deliberately stays 1.0 and
    UNCALIBRATED: the drafter's own margin is a hardcoded literal with no
    measured provenance, so there is no procedure to copy, and moving this
    number is a measurement or a [USER] ruling, not a code change."""
    assert C.ROUTE_REGRET_SAMPLE == 1.0
    assert run_metrics.ROUTE_REGRET_SAMPLE is C.ROUTE_REGRET_SAMPLE
    assert run_metrics.ROUTE_REGRET_MARGIN == 1.0

    m = maps.generate(random.Random(5), 0)
    decisions = _decisions(m, route.hunter, HEALTHY)
    default = run_metrics.route_regret(random.Random(0), m, decisions,
                                       HURT, "hunter")
    explicit = run_metrics.route_regret(random.Random(0), m, decisions,
                                        HURT, "hunter",
                                        sample=C.ROUTE_REGRET_SAMPLE)
    assert default == explicit


def test_walk_decisions_agrees_with_walk():
    """The recording walk and the plain one must be the same walk -- the
    sampler is only honest if the option sets it re-prices are the ones the
    live path was chosen from."""
    for seed in range(20):
        m = maps.generate(random.Random(seed), 0)
        path = route.walk(random.Random(0), m, route.hunter, lambda: HEALTHY)
        rec = route.walk_decisions(random.Random(0), m, route.hunter,
                                   lambda: HEALTHY)
        assert [r.id for r in path] == [d["picked"].id for d in rec]
        assert [d["floor"] for d in rec] == list(range(len(path)))
        assert rec[0]["options"] == m.rooms_on(0)
