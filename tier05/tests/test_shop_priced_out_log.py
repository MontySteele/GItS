"""The priced-out log: the two shop exits that used to record nothing.

WHAT WAS MISSING. `ShopOutcome.companion_offers` carries an `affordable` flag,
but it is measured AT THE DOOR -- against the gold held when the visit began,
before the character shelf has spent anything. Two ways a card can go out of
reach DURING a visit were therefore invisible:

  1. the buy loop's PREFERRED PICK. The policy names a card, gold no longer
     covers it because of an earlier purchase at this same shop, the entry is
     dropped and the policy is re-asked. Nothing was written down.
  2. the LOOP GUARD. It ends the visit the instant gold falls below the
     cheapest remaining shelf entry; everything still on the shelf at that
     moment was priced out, and nothing was written down.

The instrument printed "gold was never the constraint" whenever no offer was
unaffordable on arrival, which either of these could falsify. `priced_out`
records both, and these tests hold the two exits and their boundary open.

The shelf is constructed rather than rolled: both exits need a MIXED-PRICE
shelf and a specific spend order, which a rolled shop reaches only by seed
luck. `_order_policy` stands in for the draft policy -- it consumes no rng,
exactly like the real policies (which sort), so nothing here perturbs a run.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft, shop

CARD_PRICE = C.SHOP_CARD_PRICE
RARE_PRICE = C.SHOP_COMPANION_PRICE["rare"]


def _order_policy(order: list[str]):
    """A draft policy that wants `order`'s ids, best first. Draws no rng."""

    def policy(rng, deck_cards, shelf, archetype):
        for cid in order:
            for card in shelf:
                if card.id == cid:
                    return card
        return None

    return policy


def _fixed_shop(monkeypatch, character_ids: list[str],
                companion_ids: list[str]):
    """Pin the shelf: `character_ids` at the flat price, `companion_ids` in
    the companion slots at their true rarity price."""
    monkeypatch.setattr(
        shop, "shop_offer",
        lambda rng, character, n=None: [loader.get_card(c)
                                        for c in character_ids])
    monkeypatch.setattr(
        shop, "companion_shop_offer",
        lambda rng, character, banner=None: [
            (loader.get_card(c), C.SHOP_COMPANION_PRICE[
                loader.peek_card(c).rarity])
            for c in companion_ids])


def _a_rare_companion() -> str:
    from tier05 import rewards
    rares = sorted(c.id for c in rewards.companion_pool().get("rare", []))
    assert rares, "no Rare companion exists; this file's premise is gone"
    return rares[0]


def _two_character_cards() -> list[str]:
    from tier05 import rewards
    pool = rewards.character_pool("klee")
    ids = sorted(c.id for tier in pool.values() for c in tier)
    assert len(ids) >= 2
    return ids[:2]


# --- exit 1: the preferred pick, priced out by an earlier buy --------------

def test_a_preferred_pick_priced_out_by_an_earlier_buy_is_logged(monkeypatch):
    """The line the shop's own comment called "the difference between 'too
    expensive' and 'shop over'". The rare is affordable at the door; the
    cheap card bought first takes it out of reach. `spent_before` > 0 is what
    makes that case readable at all -- it is precisely the case the door-time
    `affordable` flag cannot see."""
    cheap_a, cheap_b = _two_character_cards()
    rare = _a_rare_companion()
    _fixed_shop(monkeypatch, [cheap_a, cheap_b], [rare])

    gold = CARD_PRICE + RARE_PRICE - 1        # the rare fits ONLY at the door
    out = shop.visit_shop(random.Random(0), "klee",
                          loader.starting_deck("klee"), gold, "demolition",
                          _order_policy([cheap_a, rare, cheap_b]), visit=2)

    picks = [e for e in out.priced_out if not e["residual"]]
    assert len(picks) == 1, out.priced_out
    ev = picks[0]
    assert ev["id"] == rare
    assert ev["visit"] == 2
    assert ev["price"] == RARE_PRICE
    assert ev["rarity"] == "rare"
    assert ev["channel"] == "companion"
    assert ev["slot"] == 1
    assert ev["exit"] == "pick"
    assert ev["gold_at_visit"] == gold
    assert ev["gold_now"] == gold - CARD_PRICE
    assert ev["spent_before"] == CARD_PRICE, (
        "spent_before is the whole point: 0 would mean 'never affordable "
        "here', and this card WAS affordable when the visit began")
    # It was affordable on arrival, which is exactly why the offer log's
    # flag cannot report this event.
    offer = next(o for o in out.companion_offers if o["id"] == rare)
    assert offer["affordable"] is True

    # The re-ask still happens: dropping the pick must not end the shop.
    assert [p["id"] for p in out.purchases if p["buy"] == "card"] == [
        cheap_a, cheap_b]


def test_a_pick_unaffordable_from_the_door_reads_spent_before_zero(monkeypatch):
    """The other side of the same field. Nothing was bought first, so the
    rare was out of reach on arrival -- and `spent_before` says so."""
    cheap_a, cheap_b = _two_character_cards()
    rare = _a_rare_companion()
    _fixed_shop(monkeypatch, [cheap_a, cheap_b], [rare])

    gold = RARE_PRICE - 1
    out = shop.visit_shop(random.Random(0), "klee",
                          loader.starting_deck("klee"), gold, "demolition",
                          _order_policy([rare, cheap_a, cheap_b]))
    picks = [e for e in out.priced_out if not e["residual"]]
    assert len(picks) == 1 and picks[0]["id"] == rare
    assert picks[0]["spent_before"] == 0
    assert picks[0]["gold_now"] == gold


# --- exit 2: the loop guard, stranding the shelf ---------------------------

def test_the_loop_guard_logs_what_it_strands(monkeypatch):
    """The silent exit. After the cheap card is bought, only the rare is left
    and gold is below it, so the guard ends the visit without the policy ever
    being asked again. The rare was affordable at the door and is stranded --
    an event with no record at all before this log existed."""
    cheap_a, _ = _two_character_cards()
    rare = _a_rare_companion()
    _fixed_shop(monkeypatch, [cheap_a], [rare])

    gold = CARD_PRICE + RARE_PRICE - 1
    out = shop.visit_shop(random.Random(0), "klee",
                          loader.starting_deck("klee"), gold, "demolition",
                          _order_policy([cheap_a, rare]), visit=1)

    assert not [e for e in out.priced_out if not e["residual"]], (
        "the guard fired, so the pick branch must never have run")
    residual = [e for e in out.priced_out if e["residual"]]
    assert len(residual) == 1, out.priced_out
    ev = residual[0]
    assert ev["id"] == rare
    assert ev["visit"] == 1
    assert ev["exit"] == "guard"
    assert ev["channel"] == "companion" and ev["slot"] == 1
    assert ev["gold_now"] == gold - CARD_PRICE
    assert ev["spent_before"] == CARD_PRICE


def test_a_policy_skip_does_not_strand_what_it_could_still_afford(monkeypatch):
    """The boundary between the two exits. When the policy simply stops
    wanting the shelf, the survivors were NOT priced out -- the purse could
    still reach them. Only survivors gold could not have covered are logged,
    which is what keeps "stranded" an honest word."""
    cheap_a, cheap_b = _two_character_cards()
    rare = _a_rare_companion()
    _fixed_shop(monkeypatch, [cheap_a, cheap_b], [rare])

    gold = CARD_PRICE + 1                 # affords one card, never the rare
    out = shop.visit_shop(random.Random(0), "klee",
                          loader.starting_deck("klee"), gold, "demolition",
                          _order_policy([]),      # wants nothing at all
                          visit=0)
    assert not out.purchases
    logged = {e["id"] for e in out.priced_out}
    assert logged == {rare}, (
        "the two affordable character cards were declined, not priced out; "
        f"got {sorted(logged)}")
    ev = next(iter(out.priced_out))
    assert ev["residual"] is True and ev["exit"] == "skip"


# --- the flat shelf: the branch the comment says is unreachable ------------

def test_a_flat_price_shelf_never_prices_out_a_preferred_pick():
    """PINNED because an archived-number claim rests on it. `visit_shop`'s
    comment says the pick branch is unreachable with a flat shelf -- the loop
    guard has already proved the cheapest entry affordable, and with one price
    every entry is the cheapest -- which is why every archived flat-price run
    is bit-identical. If a mixed price ever leaks into the character shelf,
    that claim quietly stops holding and this test is where it surfaces.

    Residual records are allowed here and expected: running out of gold with
    cards left on a flat shelf is the ordinary guard exit."""
    for seed in range(120):
        for gold in (0, 45, 60, 130, 400):
            out = shop.visit_shop(random.Random(seed), "klee",
                                  loader.starting_deck("klee"), gold,
                                  "demolition", draft.assigned_policy,
                                  companions=False)
            assert not [e for e in out.priced_out if not e["residual"]], (
                f"seed {seed} gold {gold}: the pick branch fired on a "
                "flat-price shelf")
            assert all(e["channel"] == "character" and e["slot"] is None
                       for e in out.priced_out)


# --- shape invariants ------------------------------------------------------

@pytest.mark.parametrize("character", ["klee", "furina", "kokomi"])
def test_every_priced_out_record_is_actually_out_of_reach(character):
    """The log must never claim an affordable card was priced out: every
    record's price exceeds the gold held at the moment it was written."""
    seen = 0
    for seed in range(120):
        for gold in (0, 70, 140, 220):
            out = shop.visit_shop(random.Random(seed), character,
                                  loader.starting_deck(character), gold,
                                  "demolition", draft.assigned_policy)
            for ev in out.priced_out:
                seen += 1
                assert ev["price"] > ev["gold_now"]
                assert ev["gold_at_visit"] == gold
                assert ev["spent_before"] == gold - ev["gold_now"] >= 0
                assert ev["exit"] in ("pick", "guard", "skip")
                assert (ev["channel"] == "companion") is (ev["slot"] is not None)
    assert seen, "no priced-out event in any of these shops -- test is inert"
