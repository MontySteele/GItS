"""M6: adaptive policy, divergence / relevance / achievability, A/B harness.

The regression that matters most here is test_starting_deck_does_not_
precommit_the_shape. Measured with basics counted, adaptive drafting
"converged" on demolition in 100% of runs -- which was Klee's starting deck
being read back as a pool finding. That confound is the reason this metric
exists at all, so it gets a test rather than a comment.
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier0.content import loader
from tier05 import ab, draft, model


def _cards(*ids):
    return [loader.get_card(i) for i in ids]


# --- the confound ------------------------------------------------------


def test_starting_deck_does_not_precommit_the_shape():
    starter = _cards(*loader.starting_deck("klee"))
    # Jumpy Dumpty and Pop are demolition-tagged, but they are basics and
    # were never drafted. Commitment must be measured over drafted cards.
    assert any("demolition" in c.archetypes for c in starter), (
        "premise changed: the starter no longer carries archetype tags, so "
        "this regression can no longer occur -- re-derive the exclusion.")
    assert draft.archetype_shares(starter) == {"demolition": 0.0,
                                               "spark": 0.0,
                                               "reaction": 0.0}
    assert draft.dominant_archetype(starter) == "goodstuff"


def test_basics_are_never_draftable_so_the_exclusion_is_exact():
    from tier05 import rewards
    assert "basic" not in rewards.character_pool("klee")


def test_companions_feed_scoring_but_not_commitment():
    """Companions are reaction fuel, not evidence of a plan.

    They now carry a derived `reaction` tag so the adaptive scorer can value
    Burst and amp payoffs in a deck full of appliers -- that bootstrap was
    genuinely broken. But the reward screen has a GUARANTEED companion slot, so
    every deck is offered one every screen and taking them signals nothing
    about commitment. Counting them for classification put 65.6% of decks in
    'reaction' while only 3.5% of those had an online reaction core.
    """
    starter = _cards(*loader.starting_deck("klee"))
    comps = [c for c in loader._card_index().values()
             if c.is_companion and "reaction" in c.archetypes][:4]
    assert comps, "premise: some companions must derive a reaction tag"
    deck = starter + comps

    # Scoring sees them...
    assert draft.archetype_shares(deck)["reaction"] > 0.0
    # ...commitment does not.
    assert draft.archetype_shares(deck, companions=False)["reaction"] == 0.0
    assert draft.dominant_archetype(deck) == "goodstuff"


def test_companion_tag_is_derived_from_effects_not_hand_written():
    """The tag must follow what the card does, or it drifts."""
    idx = loader._card_index()
    fuel = idx["dahlia_sacramental_shower"]      # applies_element
    swirl = idx["sucrose_gust"]                  # swirl IS a reaction
    plain = idx["barbara_melody"]                # heal only
    assert "reaction" in fuel.archetypes
    assert "reaction" in swirl.archetypes
    assert "reaction" not in plain.archetypes


# --- adaptive policy ---------------------------------------------------


def test_adaptive_ignores_the_assigned_archetype():
    """The A/B is meaningless if adaptive peeks at the target."""
    deck = _cards(*loader.starting_deck("klee"))
    offers = _cards("mine_toss", "crackle", "sizzle")
    picks = {draft.adaptive_policy(random.Random(0), deck, offers, a).id
             for a in ("demolition", "spark", "reaction", "generic")}
    assert len(picks) == 1


def test_commitment_emerges_from_what_was_drafted():
    starter = _cards(*loader.starting_deck("klee"))
    spark_deck = starter + _cards("crackle", "pocket_fireworks",
                                  "sparkly_treasure")
    shares = draft.archetype_shares(spark_deck)
    assert shares["spark"] > shares["demolition"]
    assert draft.dominant_archetype(spark_deck) == "spark"


def test_adaptive_payoffs_ramp_rather_than_gate():
    """Assigned gates payoffs on the core being online. Adaptive has no core,
    so a hard gate would make payoffs permanently unpickable and no shape
    could ever finish -- the same deadlock shape as the M5 amp-payoff bug."""
    starter = _cards(*loader.starting_deck("klee"))
    payoff = next(c for c in loader._card_index().values()
                  if c.role == "payoff" and "spark" in c.archetypes)
    bare = draft.adaptive_score(payoff, starter)
    committed = draft.adaptive_score(
        payoff, starter + _cards("crackle", "pocket_fireworks",
                                 "sparkly_treasure"))
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
    offers = _cards("crackle", "mine_toss", "sizzle")
    assert not draft.core_complete(starter, "reaction")

    done = starter + [c for c in loader._card_index().values()
                      if draft._is_applier(c)][:2]
    done += [c for c in loader._card_index().values()
             if draft._is_amp_payoff(c)][:1]
    done += [c for c in loader._card_index().values() if "burst" in c.tags][:1]
    assert draft.core_complete(done, "reaction"), "premise: core must be online"
    assert not draft.offer_advances_plan(offers, done, "reaction")


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
        assert x.node_kinds == y.node_kinds
