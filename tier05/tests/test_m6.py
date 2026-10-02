"""M6: adaptive policy, divergence / relevance / achievability, A/B harness.

The regression that mattered most here was test_starting_deck_does_not_
precommit_the_shape: measured with basics counted, adaptive drafting
"converged" on demolition in 100% of runs -- Klee's starting deck read back
as a pool finding. Its premise (a starter carrying archetype tags) left with
the shipped kits at legacy cleanup stage 6, and the test with it; the basics
exclusion it guarded is still pinned below.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier05 import ab, draft, model

def _cards(*ids):
    return [loader.get_card(i) for i in ids]


def _tagged(cid, role, plan):
    """A synthetic row carrying the role and plan tag the drafter reads. No
    current row carries an archetype tag (the shipped kits' tagged rows left
    with their sheets at legacy cleanup stage 6), so the drafter's
    tag-driven claims are pinned on these."""
    from tier0.engine.state import Card
    return Card(id=cid, name=cid, cost=1, type="skill", rarity="common",
                role=role, archetypes=[plan])


# --- the confound ------------------------------------------------------


def test_basics_are_never_draftable_so_the_exclusion_is_exact():
    from tier05 import rewards
    assert "basic" not in rewards.character_pool("klee")


def test_kit_burst_never_draftable():
    """v1.9: Bursts are kit, not loot. The sheet's kit_card flag is the
    pool exclusion; if it stops working the Burst quietly re-enters the
    rare tier and every acquisition number reverts to measuring odds."""
    from tier05 import rewards
    pool = rewards.character_pool("klee")
    assert all(not c.kit_card for cs in pool.values() for c in cs)
    assert not any(c.id == "sparks_n_splash"
                   for cs in pool.values() for c in cs)


def test_adaptive_ignores_the_assigned_archetype():
    """The A/B is meaningless if adaptive peeks at the target."""
    deck = _cards(*loader.starting_deck("klee"))
    offers = _cards("proto_ko_fish_blasting", "proto_ko_bombs_away",
                    "proto_mc_kaeya_frostgnaw")
    picks = {draft.adaptive_policy(random.Random(0), deck, offers, a).id
             for a in ("demolition", "spark", "reaction", "generic")}
    assert len(picks) == 1


def test_commitment_emerges_from_what_was_drafted():
    starter = _cards(*loader.starting_deck("klee"))
    spark_deck = starter + [_tagged(f"s{i}", "enabler", "spark")
                            for i in range(3)]
    shares = draft.archetype_shares(spark_deck)
    assert shares["spark"] > shares["demolition"]
    assert draft.dominant_archetype(spark_deck) == "spark"


def test_adaptive_payoffs_ramp_rather_than_gate():
    """Assigned gates payoffs on the core being online. Adaptive has no core,
    so a hard gate would make payoffs permanently unpickable and no shape
    could ever finish -- the same deadlock shape as the M5 amp-payoff bug."""
    starter = _cards(*loader.starting_deck("klee"))
    payoff = _tagged("p", "payoff", "spark")
    bare = draft.adaptive_score(payoff, starter)
    committed = draft.adaptive_score(
        payoff, starter + [_tagged(f"s{i}", "enabler", "spark")
                           for i in range(3)])
    assert committed > bare, "payoff value must rise with its enablers"


# --- metrics -----------------------------------------------------------


def test_divergence_reports_underpowered_samples():
    rs = model.run_many("klee", "demolition", "demolition",
                        draft.adaptive_policy, runs=20, seed=3)
    d = ab.divergence(rs)
    assert d["underpowered_sample"] is True, (
        "spec asks for >=1000 runs before divergence alarms are readable; "
        "a small sample must say so rather than report a clean verdict")
    assert abs(sum(d["distribution"].values()) - 1.0) < 1e-9


def test_goodstuff_is_excluded_from_the_starvation_check():
    """Starvation is a claim about archetypes; goodstuff is the absence of
    one, so it must not be able to trigger an archetype alarm."""
    rs = model.run_many("klee", "demolition", "demolition",
                        draft.adaptive_policy, runs=20, seed=3)
    d = ab.divergence(rs)
    assert "goodstuff" not in d["starved_archetypes"]


def test_relevance_is_judged_before_the_pick_lands():
    rs = model.run_many("klee", "demolition", "demolition",
                        draft.assigned_policy, runs=10, seed=4)
    for r in rs:
        for d in r.decisions:
            assert "advanced_plan" in d
    rel = ab.relevance(rs)
    assert 0.0 <= rel["relevance"] <= 1.0
    assert rel["screens"] == sum(len(r.decisions) for r in rs)


@pytest.mark.battery
def test_relevance_measures_the_pool_not_the_policy():
    """Same seeds, different policy: the FIRST screen is offered before any
    pick diverges, so its relevance must match regardless of policy.

    Parameterized on REACTION deliberately. On demolition this test was
    vacuous: `offer_advances_plan` there is a pure function of the offers, so
    every screen matched by construction and the assertion would have held even
    if relevance were badly broken. Reaction is the one archetype whose core
    progress moves on cards that carry no archetype tag (appliers, Burst), so
    it is the only place the deck genuinely enters the answer -- and therefore
    the only place this invariant can fail.
    """
    common = ("klee", "reaction", "reaction")
    a = model.run_many(*common, draft.assigned_policy, runs=25, seed=8)
    b = model.run_many(*common, draft.adaptive_policy, runs=25, seed=8)
    first_a = [r.decisions[0]["advanced_plan"] for r in a if r.decisions]
    first_b = [r.decisions[0]["advanced_plan"] for r in b if r.decisions]
    assert first_a and first_a == first_b


def test_relevance_is_deck_sensitive_for_reaction():
    """The guard that would have caught the subsumption bug.

    A completed reaction core cannot be advanced further, so a screen that
    advances an empty deck's plan must NOT advance a finished one. Under the
    old two-clause definition this failed: any reaction-tagged enabler counted
    as advancing a plan that was already complete.
    """
    starter = _cards(*loader.starting_deck("klee"))
    offers = _cards("proto_mc_kaeya_frostgnaw", "proto_ko_fish_blasting",
                    "proto_ko_kapow")
    assert not draft.core_complete(starter, "reaction")

    done = starter + [c for c in loader.prototype_cards()
                      if draft._is_applier(c)][:2]
    done += [_tagged("amp", "payoff", "reaction")]      # no current amp row
    assert draft.core_complete(done, "reaction"), "premise: core must be online"
    assert not draft.offer_advances_plan(offers, done, "reaction")


@pytest.mark.battery
def test_achievability_alarm_threshold():
    rs = model.run_many("klee", "demolition", "demolition",
                        draft.assigned_policy, runs=40, seed=6)
    ach = ab.achievability(rs)
    med = ach["median_time_to_online"]
    assert ach["alarm"] == (med is not None
                            and med > C.ACHIEVABILITY_ALARM_FIGHTS)
    assert 0.0 <= ach["never_online_share"] <= 1.0


# --- harness -----------------------------------------------------------


def test_ab_runs_both_policies_over_identical_seeds():
    out = ab.run_ab("klee", "demolition", "demolition", runs=15, seed=2)
    assert set(out) == {"assigned", "adaptive"}
    for name in out:
        assert len(out[name]["results"]) == 15
    # Same seeds => same banner and same node layout per run index.
    for x, y in zip(out["assigned"]["results"], out["adaptive"]["results"]):
        assert x.seed == y.seed
        assert x.banner == y.banner
        # §11: NOT node_kinds. Both policies get the same generated map for
        # act 1 (same seed, same rng prefix), but a different deck means
        # different fight outcomes, different HP, and therefore a different
        # ROUTE through it -- which is the map layer working, not a seed leak.
        assert x.n_acts == y.n_acts


def test_ab_threads_realistic_run_layers(monkeypatch):
    calls = []

    def fake_run_many(*args, **kwargs):
        calls.append(kwargs)
        return []

    monkeypatch.setattr(ab.model, "run_many", fake_run_many)
    out = ab.run_ab("klee", "demolition", "demolition", runs=1, seed=2,
                    grant_relics=True, grant_potions=True)
    assert set(out) == {"assigned", "adaptive"}
    assert calls == [
        {"grant_relics": True, "grant_potions": True, "n_acts": None,
         "jobs": 1, "route_name": "hunter"},
        {"grant_relics": True, "grant_potions": True, "n_acts": None,
         "jobs": 1, "route_name": "hunter"},
    ]
