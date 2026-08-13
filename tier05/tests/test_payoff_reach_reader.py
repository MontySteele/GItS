"""The payoff-reach sprint's two owed builds: the generic reader and `blind`.

Both are named in `review/active/payoff-reach-reregistration.md` §6.4 / §6.5
as owed BEFORE the run and after the predictions commit (R186). Neither may
move a drafter pick, so the pins here are about arithmetic and about rng
seams, never about a measured number: no figure from a live sheet is asserted,
because a sheet edit is allowed to move one and this file must not become the
thing that freezes content.
"""

from __future__ import annotations

import random
from types import SimpleNamespace

import pytest

from tier0 import constants as C
from tier0.engine.state import Card
from tier05 import cells, draft, exp_payoff_reach as reach, model


# --- the static leg, on a fixture pool ------------------------------------

def _card(cid: str, rarity: str, role: str, archetypes: list[str]) -> Card:
    return Card(id=cid, name=cid, cost=1, type="skill", rarity=rarity,
                role=role, archetypes=archetypes)


def _fixture_pool() -> dict[str, list[Card]]:
    """A hand-counted pool: 10 commons, 5 uncommons, 2 rares.

    `plan` holds one uncommon payoff and one rare payoff; the commons carry
    enablers and an off-plan payoff, so a reader that forgot either predicate
    (role or archetype) reads a different number.
    """
    return {
        "common": ([_card(f"c{i}", "common", "enabler", ["plan"])
                    for i in range(4)]
                   + [_card("c_off", "common", "payoff", ["other"])]
                   + [_card(f"g{i}", "common", "glue", []) for i in range(5)]),
        "uncommon": ([_card("u_pay", "uncommon", "payoff", ["plan"])]
                     + [_card(f"u{i}", "uncommon", "glue", [])
                        for i in range(4)]),
        "rare": [_card("r_pay", "rare", "payoff", ["plan"]),
                 _card("r_off", "rare", "payoff", ["other"])],
    }


def test_static_leg_counts_supply_by_role_and_archetype_together():
    s = reach.static_leg("fixture", "plan", pool=_fixture_pool())
    # Two payoffs on plan: the uncommon and the rare. The common payoff is
    # off-plan, the common enablers are not payoffs.
    assert s["supply"] == 2
    assert s["payoffs_at"] == {"common": 0, "uncommon": 1, "rare": 1}
    assert s["sizes"] == {"common": 10, "uncommon": 5, "rare": 2}


def test_static_leg_offer_is_the_census_r7_sum():
    s = reach.static_leg("fixture", "plan", pool=_fixture_pool())
    expected = (C.RARITY_ODDS["uncommon"] * 1 / 5
                + C.RARITY_ODDS["rare"] * 1 / 2)
    assert s["offer"] == pytest.approx(expected)


def test_static_leg_offer_matches_the_census_tools_own_function():
    """Same arithmetic as `tools/payoff_census.offer_reach`, not a lookalike.

    The bands were derived through that function; a reader that computed the
    figure a second way would be grading GItS sheets on a scale the canonical
    space was never measured on.
    """
    census = pytest.importorskip("tools.payoff_census")
    pool = _fixture_pool()
    flat = [{"rarity": r} for r, cards in pool.items() for _ in cards]
    payoffs = [{"rarity": r} for r, cards in pool.items()
               for c in cards if c.role == "payoff" and "plan" in c.archetypes]
    s = reach.static_leg("fixture", "plan", pool=pool)
    assert s["offer"] == pytest.approx(census.offer_reach(payoffs, flat))


def test_counterfactual_relabels_payoffs_and_moves_the_pool_sizes_with_them():
    """Q-B (B-ii): same COUNT, sitting at the favoured rarity.

    Both payoffs land in common, so common grows by two and the other two
    tiers shrink by one each. A counterfactual that moved the payoffs but
    froze the sizes would price them against a pool they had already left.
    """
    s = reach.static_leg("fixture", "plan", pool=_fixture_pool())
    assert reach.FAVOURED_RARITY == "common"
    expected = C.RARITY_ODDS["common"] * 2 / 12
    assert s["cf_offer"] == pytest.approx(expected)
    assert s["cf_delta"] == pytest.approx(expected - s["offer"])
    assert s["cf_delta"] > 0            # the prize, for this fixture


def test_an_archetype_with_no_payoffs_reads_zero_and_trips_t4():
    s = reach.static_leg("fixture", "absent", pool=_fixture_pool())
    assert (s["supply"], s["offer"], s["cf_offer"]) == (0, 0.0, 0.0)
    fired = reach.tripwires(reach.BASE, s, None)
    assert any(f.startswith("T4") for f in fired)


def _sim(reach_mean: float, max_reach: int, decksize: float = 20.0) -> dict:
    """The three sim-leg keys `tripwires` reads. Nothing live."""
    return {"decksize": decksize, "reach": reach_mean, "max_reach": max_reach,
            "n": 20, "on_plan": reach_mean, "reach_sd": 0.0,
            "held_none": 0.0, "win": 0.0}


def test_t3_grades_the_arms_realized_reach_and_not_the_per_run_maximum():
    """§6.5 T3 reads "any arm's realized reach", which is the per-ARM figure
    §6.4 leg 2 defines and the printer grades -- the mean. A per-run maximum
    is one deck, and one deck is not an arm: reading it halted the sprint on
    ordinary data, because a deck holding four on-plan payoffs is ordinary
    against sheets that print 3-14 per archetype.

    Pinned in both directions so a future edit cannot quietly swap the
    statistic back.
    """
    s = reach.static_leg("fixture", "plan", pool=_fixture_pool())
    assert reach.REACH_CEILING == 3

    # A mean inside the ceiling does NOT fire, however high one deck ran.
    inside = reach.tripwires(reach.BASE, s, _sim(2.12, 11))
    assert not any(f.startswith("T3") for f in inside), inside

    # A mean above the ceiling DOES fire, even with no outlier deck at all.
    over = reach.tripwires(reach.BASE, s, _sim(3.5, 4))
    t3 = [f for f in over if f.startswith("T3")]
    assert len(t3) == 1, over
    assert "3.50" in t3[0]              # the mean, printed as a mean


def test_two_arms_at_the_same_number_report_as_two_fired_tripwires():
    """The fired list used to be de-duplicated by exact message text. That is
    correct for T1 -- one live stamp read nine times -- and wrong for the
    per-arm tripwires, whose messages carried a number and no arm name: two
    arms at the same reach emitted byte-identical strings and printed as one
    line, so the report under-counted the arms that fired.

    Asserted on the COUNT and on both arm names, which is what a reader
    following §6.5 needs and what the collapse destroyed.
    """
    a = reach.static_leg("alpha", "plan", pool=_fixture_pool())
    b = reach.static_leg("beta", "plan", pool=_fixture_pool())
    fired = (reach.tripwires(reach.BASE, a, _sim(5.0, 5))
             + reach.tripwires(reach.BASE, b, _sim(5.0, 5)))
    fired = reach.dedupe_fired(fired)

    t3 = [f for f in fired if f.startswith("T3")]
    assert len(t3) == 2, fired
    assert any("alpha/plan" in f for f in t3)
    assert any("beta/plan" in f for f in t3)


def test_the_arm_independent_stamp_tripwire_is_still_reported_once():
    """The other half of the same rule: T1 reads one live stamp, so nine arms
    firing it is one stop, not nine lines burying the arm-specific ones."""
    stale = SimpleNamespace(versions={"RT": 1, "D": 14, "P": 7, "C": 9})
    s = reach.static_leg("fixture", "plan", pool=_fixture_pool())
    fired = reach.dedupe_fired(
        reach.tripwires(stale, s, _sim(1.0, 1))
        + reach.tripwires(stale, s, _sim(1.0, 1)))
    assert len([f for f in fired if f.startswith("T1")]) == 1, fired


# --- the band-hit criterion (P5) ------------------------------------------

def test_supply_grade_is_the_band_ceiling_plus_or_minus_one_card():
    assert [reach.grade_supply(n, "LOW") for n in (0, 1, 2, 3)] == \
        [True, True, True, False]
    assert [reach.grade_supply(n, "HIGH") for n in (0, 1, 2, 3, 4)] == \
        [False, True, True, True, False]


def test_offer_grade_is_the_half_open_interval_between_neighbouring_bands():
    lo, med, high, top = (reach.BANDS[b][0]
                          for b in ("LOW", "MEDIUM", "HIGH", "TOP"))
    assert reach.grade_offer(lo, "LOW")            # below MEDIUM's figure
    assert not reach.grade_offer(med, "LOW")       # the interval is half-open
    assert reach.grade_offer(med, "MEDIUM")
    assert not reach.grade_offer(high, "MEDIUM")
    assert reach.grade_offer(high, "HIGH")
    assert reach.grade_offer(top, "HIGH")          # HIGH closes at TOP
    assert not reach.grade_offer(top * 2, "HIGH")


def test_band_of_reports_where_a_missed_offer_actually_landed():
    assert reach.band_of(0.0) == "LOW"
    assert reach.band_of(reach.BANDS["MEDIUM"][0]) == "MEDIUM"
    assert reach.band_of(reach.BANDS["HIGH"][0]) == "HIGH"
    assert reach.band_of(1.0) == "TOP+"


def test_the_nine_arms_and_the_ruled_aims_agree_and_are_three_of_each():
    assert set(reach.ARMS) == set(reach.AIMS)
    counts = {b: sum(1 for v in reach.AIMS.values() if v == b)
              for b in ("LOW", "MEDIUM", "HIGH")}
    assert counts == {"LOW": 3, "MEDIUM": 3, "HIGH": 3}
    assert all(cells.CANONICAL.but(character=c, archetype=a)
               for c, a in reach.ARMS)         # every arm is a legal cell


# --- the sim leg's reach column -------------------------------------------

def test_deck_reach_is_generic_core_counts_and_not_a_second_classifier():
    deck = [_card("p1", "common", "payoff", ["plan"]),
            _card("e1", "common", "enabler", ["plan"]),
            _card("p2", "rare", "payoff", ["other"]),
            _card("g1", "common", "glue", [])]
    assert reach.deck_reach(deck, "plan") == \
        draft._generic_core_counts(deck, "plan") == (2, 1)


def test_sim_leg_reports_realized_reach_over_a_tiny_deterministic_cell():
    cell = cells.CANONICAL.but(name="reader-test", character="klee",
                               archetype="demolition", runs=2, n_acts=1,
                               jobs=1)
    a = reach.sim_leg(cell)
    assert a["n"] == 2
    assert a["reach"] <= a["on_plan"] <= a["decksize"]
    assert a["max_reach"] >= a["reach"]
    assert reach.sim_leg(cell) == a          # a cell is reproducible


# --- the blind control policy (C2) ----------------------------------------

def test_blind_is_registered_as_a_policy_without_disturbing_the_ab_pair():
    assert set(draft.POLICIES) == {"assigned", "adaptive", "blind"}
    assert draft.POLICIES["blind"] is draft.blind_policy
    assert draft.POLICIES["assigned"] is draft.assigned_policy
    assert draft.POLICIES["adaptive"] is draft.adaptive_policy
    assert cells.CANONICAL.but(policy="blind").policy == "blind"


def test_blind_takes_uniformly_from_the_screen_and_never_skips():
    offers = [_card(f"o{i}", "common", "glue", []) for i in range(3)]
    picks = [draft.blind_policy(random.Random(s), [], offers, "demolition")
             for s in range(200)]
    assert all(p in offers for p in picks)          # never a skip
    assert {p.id for p in picks} == {"o0", "o1", "o2"}
    assert draft.blind_policy(random.Random(0), [], [], "demolition") is None


def test_blind_is_deterministic_under_seed():
    kw = dict(grant_relics=True, grant_potions=True, n_acts=1)
    def fp(rs):
        return [(r.seed, tuple(r.deck_ids), r.won, tuple(r.hp_by_node))
                for r in rs]
    a = model.run_many("klee", "demolition", "demolition",
                       draft.POLICIES["blind"], 3, 11, **kw)
    b = model.run_many("klee", "demolition", "demolition",
                       draft.POLICIES["blind"], 3, 11, **kw)
    assert fp(a) == fp(b)


def test_blind_and_assigned_are_different_drafters():
    """Sanity: the control is a control, not a second name for the pilot."""
    kw = dict(grant_relics=True, grant_potions=True, n_acts=1)
    blind = model.run_many("klee", "demolition", "demolition",
                           draft.POLICIES["blind"], 5, 11, **kw)
    assigned = model.run_many("klee", "demolition", "demolition",
                              draft.POLICIES["assigned"], 5, 11, **kw)
    assert [r.deck_ids for r in blind] != [r.deck_ids for r in assigned]


# --- the rng seam: a policy stream is never the run's stream ---------------

SEED = 4242


def _skip(rng, deck, offers, archetype):
    return None


def _skip_after_drawing(rng, deck, offers, archetype):
    for _ in range(5):
        rng.random()
    return None


def test_an_own_rng_policy_is_handed_the_dedicated_stream_not_the_run_rng():
    seen = []

    def probe(rng, deck, offers, archetype):
        seen.append(rng)
        return None
    probe.own_rng = True

    model.run_one("klee", "demolition", "demolition", probe, SEED, n_acts=1,
                  grant_relics=True, grant_potions=True)
    assert seen, "the run showed no reward screen; the seam went untested"
    assert all(r is seen[0] for r in seen)      # one stream for the whole run
    # It drew nothing, so it must still be a fresh Random(seed + 6e9) -- which
    # pins WHICH offset the seam takes (understudy/rng.py's registry).
    assert seen[0].getstate() == random.Random(SEED + 6 * 10 ** 9).getstate()


def _fingerprint(results):
    return [(r.seed, r.won, r.death_node, tuple(r.hp_by_node),
             tuple(r.deck_ids), r.gold, tuple(r.relics), r.acts_completed,
             tuple(k for k in r.node_kinds)) for r in results]


def test_drawing_from_the_dedicated_stream_perturbs_nothing_in_the_run():
    """Non-interference, stated as the two runs a house rule promises.

    Both policies below skip every screen, so the DECKS are identical by
    construction and any difference in the fingerprint is the rng draw leaking
    into the run. On its own stream it cannot leak; on the main stream it
    renumbers every encounter, reward roll and shop after the first screen --
    which is the contrast the second half asserts, so the test fails if the
    seam is ever quietly removed.
    """
    kw = dict(n_acts=1, grant_relics=True, grant_potions=True)
    quiet = model.run_many("klee", "demolition", "demolition", _skip, 4,
                           SEED, **kw)

    drawer = _skip_after_drawing
    drawer.own_rng = True
    try:
        dedicated = model.run_many("klee", "demolition", "demolition",
                                   drawer, 4, SEED, **kw)
        assert _fingerprint(dedicated) == _fingerprint(quiet)
    finally:
        del drawer.own_rng

    shared = model.run_many("klee", "demolition", "demolition", drawer, 4,
                            SEED, **kw)
    assert _fingerprint(shared) != _fingerprint(quiet)
