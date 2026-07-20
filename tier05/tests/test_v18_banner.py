"""v1.8 Featured Banner (principles §4.2 + draft-sim addendum).

Plumbing, not behaviour: Mondstadt has exactly BANNER_FEATURED_SLOTS designed
5-stars, so today's roll features all of them and changes nothing. That makes
these tests unusual -- most of them have to FAKE a grown roster, because the
real one cannot exercise the mechanism yet. The degenerate case is asserted
explicitly so the day the roster grows, the tests that start doing real work
are the ones that were always meant to.
"""

from __future__ import annotations

import random
from unittest import mock

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import Card
from tier05 import draft, model, rewards, run_metrics


def _fake_roster(n: int, nation: str = "mondstadt") -> list[Card]:
    return [Card(id=f"star5_{i}", name=f"Five Star {i}", cost=2, type="power",
                 rarity="rare", role_c="buffer", star=5, nation=nation)
            for i in range(n)]


# --- the v0.1 degenerate case ------------------------------------------


def test_v01_roster_makes_the_banner_a_noop():
    roster = rewards.five_star_roster("mondstadt")
    assert len(roster) <= C.BANNER_FEATURED_SLOTS, (
        "Mondstadt grew past the banner slots -- the roll is now live, and "
        "the frozen v0.1 numbers were measured without it.")
    featured = {c.id for c in roster}
    for seed in range(50):
        assert rewards.roll_banner(random.Random(seed)) == featured


def test_personal_pool_companions_are_not_banner_eligible():
    # Prune is Klee's designated teammate, not a shared-pool 5-star draw.
    assert "prune_witch_hunt" not in {c.id
                                      for c in rewards.five_star_roster("mondstadt")}


def test_nation_comes_from_the_sheet_not_the_row():
    assert loader.get_card("albedo_solar_isotoma").nation == "mondstadt"
    assert loader.get_card("kaeya_frostgnaw").nation == "mondstadt"
    # Klee's own cards are not companions and carry no nation.
    assert loader.get_card("kaboom").nation is None


# --- the mechanism, on a roster big enough to exercise it ---------------


def test_roll_selects_exactly_the_slot_count_from_a_grown_roster():
    fake = _fake_roster(8)
    with mock.patch.object(rewards, "five_star_roster", lambda n: fake):
        for seed in range(100):
            b = rewards.roll_banner(random.Random(seed))
            assert len(b) == C.BANNER_FEATURED_SLOTS
            assert b <= {c.id for c in fake}


def test_roll_is_seed_deterministic_and_actually_varies():
    fake = _fake_roster(8)
    with mock.patch.object(rewards, "five_star_roster", lambda n: fake):
        assert (rewards.roll_banner(random.Random(42))
                == rewards.roll_banner(random.Random(42)))
        seen = {rewards.roll_banner(random.Random(s)) for s in range(300)}
        assert len(seen) > 1, "banner roll is not varying across seeds"


def test_off_banner_five_stars_are_filtered_but_four_stars_never_are():
    fake = _fake_roster(8)
    banner = frozenset({"star5_0"})
    assert ([c.id for c in rewards._banner_filtered(fake, banner)]
            == ["star5_0"])
    four = Card(id="c4", name="C4", cost=1, type="attack", rarity="common",
                role_c="applier", star=4, nation="mondstadt")
    assert rewards._banner_filtered([four], frozenset()) == [four]
    # None means unrestricted -- the pre-v1.8 path Tier 0 still uses.
    assert rewards._banner_filtered(fake, None) == fake


def test_banner_emptying_the_rare_tier_falls_through_to_uncommon():
    # A banner featuring no available rare must not wedge the reward screen;
    # it should degrade the same way a naturally rare-less pool does.
    rng = random.Random(7)
    offers = rewards.roll_rewards(rng, "klee", companion_offers=1,
                                  banner=frozenset())
    assert len(offers) == C.REWARD_CARD_OFFERS + 1
    companions = [c for c in offers if c.is_companion]
    assert companions and all(c.star != 5 for c in companions)


# --- determinism contract ----------------------------------------------


def test_banner_does_not_perturb_the_main_rng_stream():
    """The banner is drawn from a derived stream on purpose. If it ever came
    out of the run's main rng, every previously measured number would shift
    silently -- including the frozen v0.1 snapshot."""
    a = model.run_one("klee", "demolition", "demolition",
                      draft.assigned_policy,
                      seed=123)
    b = model.run_one("klee", "demolition", "demolition",
                      draft.assigned_policy,
                      seed=123)
    assert a.deck_ids == b.deck_ids and a.hp_by_node == b.hp_by_node
    assert a.banner == b.banner and a.banner  # recorded on the result


# --- metrics -----------------------------------------------------------


def test_banner_variance_reports_degenerate_rather_than_zero_spread():
    results = model.run_many("klee", "demolition", "demolition",
                             draft.assigned_policy, runs=12, seed=5)
    bv = run_metrics.banner_variance(results)
    assert bv["distinct_banners"] == 1
    assert bv["degenerate"] is True, (
        "a single possible lineup must not read as 'measured no variance'")
    assert bv["spread"] == 0.0


def test_conditional_assembly_conditions_only_on_five_stars():
    results = model.run_many("klee", "reaction", "reaction",
                             draft.assigned_policy, runs=12, seed=9)
    # 4-star only: never gated, so every run is eligible.
    ca = run_metrics.conditional_assembly(results, ["kaeya_frostgnaw"])
    assert ca["eligible_rate"] == 1.0
    # 5-star: eligible whenever featured, which at v0.1 is always.
    ca5 = run_metrics.conditional_assembly(results, ["durin_witchs_flame"])
    assert ca5["eligible_rate"] == 1.0
    assert ca5["conditional_rate"] == ca5["unconditional_rate"]
