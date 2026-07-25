"""v1.8 Featured Banner (principles §4.2 + draft-sim addendum).

BEHAVIOUR NOW, NOT PLUMBING. Until 2026-07-25 this file's own docstring said
"Plumbing, not behaviour": every nation had at most BANNER_FEATURED_SLOTS
designed 5-stars, so the roll featured all of them and changed nothing, and
most tests here had to FAKE a grown roster to exercise the mechanism at all.

R64 gave Fontaine four Rares against three slots. The banner is selective for
the first time, on the real roster, and the assertions below are the ones the
old file said were "always meant to" start doing work:

  - exactly BANNER_FEATURED_SLOTS featured when a roster exceeds the cap;
  - the excluded Rare never reaches that run's reward slot or shop slot 1;
  - two seeds produce different banners.

The old `roster <= cap` invariant is RETIRED. It was a tripwire for exactly
this day, and keeping it would now assert the sprint had not happened.
"""

from __future__ import annotations

import random
from unittest import mock

from tier0 import constants as C
from tier0.content import loader
from tier0.engine.state import Card
from tier05 import draft, model, rewards, run_metrics, shop

MONDSTADT = ("mondstadt",)


def _fake_roster(n: int, nation: str = "mondstadt") -> list[Card]:
    return [Card(id=f"star5_{i}", name=f"Five Star {i}", cost=2, type="power",
                 rarity="rare", role_c="buffer", star=5, nation=nation)
            for i in range(n)]


# --- which nations the roll covers -------------------------------------


def test_designed_nations_is_derived_not_listed():
    """The regression that motivated R64's call-site audit.

    roll_banner's `nations` used to default to the literal ("mondstadt",), and
    the run model's single call site passed no argument. Every run of every
    character therefore rolled a Mondstadt-only banner, and _banner_filtered
    dropped every other nation's 5-stars from the reward slot AND the shop.
    Measured before the fix: 400 Kokomi seeds offered Albedo/Durin/Nicole and
    never Itto or Raiden -- Inazuma's own Rares, unreachable in Inazuma runs.
    """
    nations = rewards.designed_nations()
    assert set(nations) >= {"mondstadt", "inazuma", "fontaine"}
    for nation in nations:
        assert rewards.five_star_roster(nation), nation
    # Derived from the sheets: a nation with 5-stars cannot be left out by
    # someone forgetting to edit a tuple.
    from_sheets = {c.nation for c in loader._card_index().values()
                   if c.is_companion and c.star == 5 and c.nation
                   and c.personal_pool is None and not c.guest_star}
    assert set(nations) == from_sheets


def test_a_run_banner_covers_every_nation_not_just_home():
    """§4.2 is "3 limited 5-stars per nation". A banner that omits a nation
    does not thin it -- it deletes it, because the reward slot's uniform half
    and the shop's wildcard slot both offer off-nation 5-stars."""
    banner = rewards.roll_banner(random.Random(4))
    for nation in rewards.designed_nations():
        roster = {c.id for c in rewards.five_star_roster(nation)}
        assert roster & banner, f"{nation} is absent from the banner entirely"


def test_inazuma_five_stars_are_reachable_in_an_inazuma_run():
    """The concrete half of the regression above, on the character it hurt."""
    seen: set[str] = set()
    for s in range(400):
        banner = rewards.roll_banner(random.Random(s + 2 * 10 ** 9))
        offers = rewards.roll_rewards(random.Random(s), "kokomi", banner=banner)
        seen |= {c.id for c in offers if c.star == 5}
    assert {"itto_superlative_superstrength",
            "raiden_musou_no_hitotachi"} & seen, (
        "Inazuma's own 5-stars never surfaced in 400 Kokomi runs")


# --- selectivity, on the REAL roster ------------------------------------


def test_fontaine_roster_exceeds_the_cap_so_the_roll_is_live():
    roster = rewards.five_star_roster("fontaine")
    assert len(roster) > C.BANNER_FEATURED_SLOTS, (
        "R64's premise is gone: Fontaine no longer exceeds the banner cap, so "
        "the selectivity assertions below are vacuous again")


def test_exactly_the_slot_count_is_featured_per_nation():
    roster = {c.id for c in rewards.five_star_roster("fontaine")}
    for seed in range(200):
        b = rewards.roll_banner(random.Random(seed), nations=("fontaine",))
        assert len(b) == C.BANNER_FEATURED_SLOTS
        assert b < roster, "featured set must be a STRICT subset"


def test_exactly_one_fontaine_rare_is_excluded_and_all_four_get_excluded():
    """Selectivity has to be real in both directions: every run drops one, and
    no card is permanently benched by a biased sample."""
    roster = {c.id for c in rewards.five_star_roster("fontaine")}
    excluded_ever: set[str] = set()
    for seed in range(300):
        b = rewards.roll_banner(random.Random(seed), nations=("fontaine",))
        missing = roster - b
        assert len(missing) == 1
        excluded_ever |= missing
    assert excluded_ever == roster, (
        f"never excluded: {sorted(roster - excluded_ever)} -- these would be "
        "permanently featured, which is not a banner")


def test_two_seeds_produce_different_banners():
    seen = {rewards.roll_banner(random.Random(s), nations=("fontaine",))
            for s in range(300)}
    assert len(seen) > 1, "banner roll is not varying across seeds"
    assert (rewards.roll_banner(random.Random(42))
            == rewards.roll_banner(random.Random(42))), "not seed-deterministic"


def test_the_excluded_rare_never_reaches_the_reward_slot():
    for seed in range(120):
        banner = rewards.roll_banner(random.Random(seed + 2 * 10 ** 9))
        offers = rewards.roll_rewards(random.Random(seed), "furina",
                                      banner=banner)
        for c in offers:
            if c.star == 5:
                assert c.id in banner, (
                    f"seed {seed}: off-banner 5-star {c.id} was offered")


def test_the_excluded_rare_never_reaches_shop_slot_one():
    """§4.7 slot 1 is the home-nation draw, and Furina's home nation is the
    one with a selective banner -- so this is the surface where exclusion is
    most likely to leak."""
    checked = 0
    for seed in range(200):
        banner = rewards.roll_banner(random.Random(seed + 2 * 10 ** 9))
        offers = shop.companion_shop_offer(random.Random(seed), "furina",
                                           banner)
        for card, _price in offers:
            if card.star == 5:
                checked += 1
                assert card.id in banner, (
                    f"seed {seed}: shop offered off-banner {card.id}")
    assert checked, "no 5-star ever reached the shop; the assertion is vacuous"


# --- the degenerate case, where it still exists -------------------------


def test_mondstadt_alone_is_still_degenerate():
    """Mondstadt sits at exactly the cap, so ITS slice features everyone. Kept
    because it is the control for the Fontaine assertions above -- selectivity
    should be a property of roster size, not of the code path."""
    roster = rewards.five_star_roster("mondstadt")
    assert len(roster) <= C.BANNER_FEATURED_SLOTS
    featured = {c.id for c in roster}
    for seed in range(50):
        assert rewards.roll_banner(random.Random(seed),
                                   nations=MONDSTADT) == featured


def test_personal_pool_companions_are_not_banner_eligible():
    # Prune is Klee's designated teammate, not a shared-pool 5-star draw.
    assert "prune_witch_hunt" not in {c.id
                                      for c in rewards.five_star_roster("mondstadt")}


def test_nation_comes_from_the_sheet_not_the_row():
    assert loader.get_card("albedo_solar_isotoma").nation == "mondstadt"
    assert loader.get_card("kaeya_frostgnaw").nation == "mondstadt"
    # Klee's own cards are not companions and carry no nation.
    assert loader.get_card("kaboom").nation is None


# --- the mechanism on a synthetic roster (kept: sizes the real one cannot) --


def test_roll_selects_exactly_the_slot_count_from_a_grown_roster():
    fake = _fake_roster(8)
    with mock.patch.object(rewards, "five_star_roster", lambda n: fake):
        for seed in range(100):
            b = rewards.roll_banner(random.Random(seed), nations=MONDSTADT)
            assert len(b) == C.BANNER_FEATURED_SLOTS
            assert b <= {c.id for c in fake}


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


def test_banner_variance_now_measures_real_variance():
    """RETIRES test_banner_variance_reports_degenerate_rather_than_zero_spread.

    That test asserted `distinct_banners == 1` and `degenerate is True` for a
    Klee run, which was true only because no nation exceeded the cap. Fontaine
    now does, and a Klee run's banner covers Fontaine too (that is the point of
    designed_nations), so Klee runs see multiple lineups as well. The metric's
    `degenerate` flag is still worth having -- it just no longer describes the
    live roster.
    """
    results = model.run_many("klee", "demolition", "demolition",
                             draft.assigned_policy, runs=12, seed=5)
    bv = run_metrics.banner_variance(results)
    assert bv["distinct_banners"] > 1
    assert bv["degenerate"] is False
    assert bv["spread"] >= 0.0


def test_conditional_assembly_conditions_only_on_five_stars():
    results = model.run_many("klee", "reaction", "reaction",
                             draft.assigned_policy, runs=12, seed=9)
    # 4-star only: never gated, so every run is eligible.
    ca = run_metrics.conditional_assembly(results, ["kaeya_frostgnaw"])
    assert ca["eligible_rate"] == 1.0
    # 5-star: eligible whenever featured. Durin is Mondstadt, which is still at
    # the cap, so he is featured in every run -- the assertion holds for the
    # same reason it always did, not by accident of the Fontaine change.
    ca5 = run_metrics.conditional_assembly(results, ["durin_witchs_flame"])
    assert ca5["eligible_rate"] == 1.0
    assert ca5["conditional_rate"] == ca5["unconditional_rate"]
