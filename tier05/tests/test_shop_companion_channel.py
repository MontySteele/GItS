"""§4.7 shop companion channel -- Track D invariants (R59/R60/R61).

THE CLASS THIS FILE EXISTS TO PREVENT is the empty draw: asking a filtered
pool for a card it cannot supply. It softlocked Dusty Tome once already
(`tools/lint_ancient_coverage.py` is the scar), and the shop is a second
instance -- `MerchantCardEntry.Populate` ends in `Rng.NextItem` over a
rarity-and-nation-filtered list, and the merchant's slot layout is
load-bearing UI with no "no card" path.

So the corners below are not hypothetical hygiene. Two of them are live
today: Fontaine designs ZERO Rare companions, and every nation's Uncommon
tier is small enough that two slots can exhaust a nation between them.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft, rewards, shop

CHARACTERS = ["klee", "furina", "kokomi"]


# --- the offer itself ------------------------------------------------------

@pytest.mark.parametrize("character", CHARACTERS)
def test_both_slots_fill_for_every_character(character):
    """Across many seeds every character gets SHOP_COMPANION_SLOTS offers.

    A dropped slot is legal (the ladder's last rung) but must never happen on
    the live roster -- if this fails, a nation has gone thin and the shop is
    quietly offering less than it advertises."""
    for seed in range(200):
        offers = shop.companion_shop_offer(random.Random(seed), character)
        assert len(offers) == C.SHOP_COMPANION_SLOTS, (
            f"{character} seed {seed} filled {len(offers)} of "
            f"{C.SHOP_COMPANION_SLOTS} companion slots")


@pytest.mark.parametrize("character", CHARACTERS)
def test_the_floor_is_slot_ones_and_the_home_region_is_too(character):
    """NC-10 (R116, Errata Batch 2 item 6) -- the spec, verbatim: "Slot 1
    should be 'Uncommon or higher from the home region'; slot 2 should be
    'any companion card'."

    This REPLACES the old `test_uncommon_floor_holds`, which asserted R59's
    floor across BOTH slots. R116 respecified the channel and the floor is
    now slot 1's alone; the old assertion is not weakened, it is relocated.
    Slot 2's own invariant is below: it must actually reach the rarities the
    absence of a filter admits, or "unrestricted" is a comment rather than a
    behaviour.
    """
    for seed in range(200):
        offers = shop.companion_shop_offer(random.Random(seed), character)
        if not offers:
            continue
        card, _ = offers[0]
        assert card.rarity in ("uncommon", "rare"), (
            f"{character} was offered {card.id} ({card.rarity}) in SLOT 1 -- "
            "the Uncommon-or-higher floor is broken")
        assert card.nation == loader.character_nation(character), (
            f"{character} was offered off-region {card.id} in SLOT 1")


@pytest.mark.parametrize("character", CHARACTERS)
def test_slot_two_is_unrestricted_in_both_filters(character):
    """The other half of the same spec. "Any companion card" has to be
    observable: over enough seeds slot 2 offers Commons, and it offers cards
    from outside the home region."""
    rarities = set()
    nations = set()
    for seed in range(400):
        offers = shop.companion_shop_offer(random.Random(seed), character)
        if len(offers) < 2:
            continue
        card, _ = offers[1]
        rarities.add(card.rarity)
        nations.add(card.nation)
    assert "common" in rarities, (
        f"{character}'s slot 2 never offered a Common -- R116 removed the "
        "floor from this slot, and a floor that survives in the code is the "
        "defect NC-10 named")
    assert rarities >= {"common", "uncommon", "rare"}
    assert len(nations) > 1


@pytest.mark.parametrize("character", CHARACTERS)
def test_price_matches_drawn_rarity(character):
    """§4.7's governor: gold, not a stat nerf. A companion priced off-band is
    the balance lever silently disconnected."""
    for seed in range(100):
        for card, price in shop.companion_shop_offer(random.Random(seed), character):
            assert price == C.SHOP_COMPANION_PRICE[card.rarity]


@pytest.mark.parametrize("character", CHARACTERS)
def test_only_offerable_companions_appear(character):
    """Never another character's personal-pool card, never a guest star, and
    never a non-companion. `companion_pool` already excludes guest stars; this
    is the assertion that the shop reads the same door the reward slot does."""
    for seed in range(100):
        for card, _ in shop.companion_shop_offer(random.Random(seed), character):
            assert card.is_companion
            assert not card.guest_star
            assert card.personal_pool in (None, character)


def test_slot_one_is_home_nation_when_the_nation_can_supply_it():
    """Slot 1 is the TARGETED slot -- that is the whole reason it is priced as
    the premium buy. Klee's Mondstadt covers both rarities, so her slot 1 must
    be Mondstadt every time. (Furina is deliberately not asserted here: see
    the Fontaine test below.)"""
    home = loader.character_nation("klee")
    for seed in range(200):
        offers = shop.companion_shop_offer(random.Random(seed), "klee")
        assert offers[0][0].nation == home, (
            f"seed {seed}: slot 1 offered {offers[0][0].id} from "
            f"{offers[0][0].nation}, not {home}")


# --- the empty-draw corners (the reason this file exists) ------------------

def test_furinas_slot_one_now_answers_a_rare_roll_from_her_own_nation():
    """SUCCESSOR to test_fontaine_has_no_rare_companion_so_furinas_slot_one_widens.

    That test asserted the opposite fact and carried its own retirement
    instructions: "the tripwire for the day Fontaine gains a Rare -- the fix is
    to delete it, not to re-widen the ladder." R64 (2026-07-25) shipped four
    Fontaine Rares, so it was deleted and this took its place.

    What flipped: Furina's home-nation slot can now honour a Rare roll from
    Fontaine itself, which means the nation-widening rung STOPS being her
    normal path. It is not gone -- the banner can still thin her Rare tier, and
    slot 2 can still take the last Fontaine card first -- but it is now a
    corner rather than the everyday case.
    """
    pool = rewards.companion_pool()
    fontaine_rares = [c for c in pool.get("rare", []) if c.nation == "fontaine"]
    assert fontaine_rares, "R64's roster is gone; this test's premise with it"

    saw_fontaine_rare = False
    for seed in range(300):
        offers = shop.companion_shop_offer(random.Random(seed), "furina")
        assert len(offers) == C.SHOP_COMPANION_SLOTS
        for card, _ in offers:
            if card.rarity == "rare" and card.nation == "fontaine":
                saw_fontaine_rare = True
    assert saw_fontaine_rare, (
        "Furina never saw a Fontaine Rare across 300 seeds -- the roster gap "
        "this sprint closed is still closed in the sheet but not in the shop")


def test_the_widening_rung_still_works_when_the_banner_thins_her_tier():
    """The rung the test above stopped exercising, exercised deliberately.

    A banner that features NO Fontaine Rare is now a reachable run state (four
    Rares, three slots, and slot 1 draws home nation). The ladder must widen
    the nation rather than drop the rarity or crash -- the R59 floor.
    """
    empty = frozenset()          # nothing featured at all: the hardest case
    for seed in range(100):
        offers = shop.companion_shop_offer(random.Random(seed), "furina", empty)
        assert len(offers) == C.SHOP_COMPANION_SLOTS
        for card, _ in offers:
            assert card.star != 5, "an off-banner 5-star reached the shop"


def test_a_nation_with_no_companions_at_all_still_fills_both_slots():
    """The ladder's middle rungs, forced. A character whose nation supplies
    nothing must still get a full shop off the wildcard rungs rather than a
    silently short one."""
    offers = shop.companion_shop_offer(random.Random(0), "klee")
    assert len(offers) == C.SHOP_COMPANION_SLOTS

    # Klee, but pretending Mondstadt does not exist.
    original = loader.character_nation

    class _Nowhere:
        def __call__(self, cid):
            return "atlantis" if cid == "klee" else original(cid)

    loader.character_nation = _Nowhere()          # type: ignore[assignment]
    try:
        for seed in range(100):
            got = shop.companion_shop_offer(random.Random(seed), "klee")
            assert len(got) == C.SHOP_COMPANION_SLOTS, (
                "a character from a nation with no companions lost a shop slot")
    finally:
        loader.character_nation = original        # type: ignore[assignment]


def test_the_two_slots_never_offer_the_same_card():
    """Base `MerchantCardEntry.Populate` excludes already-stocked cards via
    `Except`; the sim must not be laxer, or a thin nation shows you the same
    companion twice and the second slot is worthless."""
    for character in CHARACTERS:
        for seed in range(200):
            offers = shop.companion_shop_offer(random.Random(seed), character)
            ids = [c.id for c, _ in offers]
            assert len(ids) == len(set(ids)), (
                f"{character} seed {seed} offered {ids} -- duplicate slot")


def test_an_empty_roster_drops_slots_instead_of_raising():
    """The last rung. tier 0.5 has no base colorless pool to fall back on
    (that rung is C#-only, R60), so it OMITS the slot -- but it must omit it
    deliberately, not by throwing out of a shop visit mid-run."""
    original = rewards.companion_pool
    rewards.companion_pool = lambda: {}           # type: ignore[assignment]
    try:
        assert shop.companion_shop_offer(random.Random(0), "klee") == []
    finally:
        rewards.companion_pool = original         # type: ignore[assignment]


# --- integration with the buy loop ----------------------------------------

def test_channel_off_is_the_archived_shop():
    """The flag is a real off switch: with companions disabled the visit is
    byte-identical to the pre-channel shop, which is what lets every archived
    number stay comparable."""
    deck = loader.starting_deck("klee")
    off = shop.visit_shop(random.Random(7), "klee", deck, 300, "demolition",
                          draft.assigned_policy, companions=False)
    assert all(p["price"] == C.SHOP_CARD_PRICE
               for p in off.purchases if p["buy"] == "card")
    assert all(not loader.peek_card(p["id"]).is_companion
               for p in off.purchases if p["buy"] == "card")


def test_the_drafter_can_actually_buy_a_companion():
    """R61's point: an unmeasured governor is a design claim with no
    instrument. If the drafter never buys one, the channel is modelled but
    dead, and the P1 buy-rate would be measuring nothing."""
    bought = 0
    for seed in range(60):
        out = shop.visit_shop(random.Random(seed), "klee",
                              loader.starting_deck("klee"), 400, "demolition",
                              draft.assigned_policy)
        bought += sum(1 for p in out.purchases
                      if p["buy"] == "card"
                      and loader.peek_card(p["id"]).is_companion)
    assert bought > 0, "the drafter never bought a companion in 60 flush shops"


def test_gold_is_conserved_across_a_mixed_price_shelf():
    """Mixed prices are new; the accounting must still close exactly. A
    per-card price map is easy to get subtly wrong (charging the flat price
    for a Rare would hand the drafter a 90-gold discount and quietly break the
    only balance lever the channel has)."""
    for seed in range(60):
        start = 400
        out = shop.visit_shop(random.Random(seed), "klee",
                              loader.starting_deck("klee"), start,
                              "demolition", draft.assigned_policy)
        assert out.gold == start - sum(p["price"] for p in out.purchases)
        assert out.gold >= 0


def test_an_unaffordable_companion_does_not_end_the_shop():
    """The regression this guards: 'the policy wants a card it cannot afford'
    must drop that ONE entry and re-ask, not break the loop. Break it and a
    150-gold Rare on the shelf would block every affordable purchase behind
    it -- a silent, seed-dependent loss of the whole character shelf."""
    rare_price = C.SHOP_COMPANION_PRICE["rare"]
    saw_purchase_after_unaffordable = 0
    for seed in range(200):
        gold = rare_price - 1            # can afford anything BUT a Rare
        out = shop.visit_shop(random.Random(seed), "klee",
                              loader.starting_deck("klee"), gold,
                              "demolition", draft.assigned_policy)
        if any(p["price"] < rare_price for p in out.purchases):
            saw_purchase_after_unaffordable += 1
    assert saw_purchase_after_unaffordable > 0, (
        "no shop ever bought a cheaper card while a Rare sat unaffordable on "
        "the shelf -- the re-ask path is not being exercised")
