"""EB-28 / `DRAFTER_VERSION` 18 -- the salon DEPLOY stops pricing at zero.

`apply_power` is priced INLINE by `_static_power`, and until this bump none of
the inline branches named `power: salon_member`. So a printed company scored
exactly 0.0 and Furina's members were invisible to every plan except salon,
where the ARCHETYPE term -- not the static scorer -- was paying for them. That
is the blindness the row names, and the acceptance it asks for is one line:
salon members price non-zero cross-plan.

Two claims are pinned here, and the second is the one that makes the archive
scope of the bump checkable rather than asserted:

  (1) THE NINE ROWS PRICE, to the four decimals the archive quotes, on both
      faces. `STATIC_SALON_MEMBER_VALUE` is a [USER]-held number, so a later
      edit to it must break a test before it can move a shipped offer-screen
      price in silence.
  (2) THE TERM REACHES NOTHING ELSE. Exactly nine cards on any sheet print a
      `salon_member` deploy, and the price a card carries is a pure function
      of what it prints, so "nine rows moved and nothing else did" is a
      statement about the sheet that a test can hold.
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier05 import draft


#: (base, upgraded) drafted price at D18, four decimals. The left-hand value
#: in each comment is the D17 price the bump archives.
D18_PRICES = {
    "dress_rehearsal":           (1.5000, 1.5000),   # was 0.0000 / 0.0000
    "endless_waltz":             (1.5000, 3.0000),   # was 0.0000 / 0.0000
    "full_ensemble":             (2.2500, 4.5000),   # was 0.0000 / 0.0000
    "gentilhomme_usher":         (5.5000, 7.5000),   # was 4.0000 / 6.0000
    "grand_gala":                (3.6000, 4.0500),   # was 0.6000 / 1.0500
    "mademoiselle_crabaletta":   (1.5000, 3.0000),   # was 0.0000 / 0.0000
    "overflowing_hospitality":   (2.2000, 2.5000),   # was 1.4500 / 1.7500
    "salon_debut":               (1.5000, 2.1000),   # was 0.0000 / 0.6000
    "surintendante_chevalmarin": (2.4000, 3.0000),   # was 0.9000 / 1.5000
}


def _price(card_id):
    """(base, upgraded) drafted price, to four decimals. Base FIRST --
    `apply_upgrade` builds off the prototype and the order is not free."""
    card = loader.get_card(card_id)
    base = round(draft._static_power(card), 4)
    up = (round(draft._static_power(upgrades.apply_upgrade(card)), 4)
          if upgrades.has_upgrade(card_id) else None)
    return base, up


def _deploys(card) -> int:
    return sum(fx.get("amount", 1)
               for fx in draft._nested_effects(card.effects)
               if fx.get("op") == "apply_power"
               and fx.get("power") == "salon_member")


# --- (1) the nine rows -----------------------------------------------------

@pytest.mark.parametrize("card_id,expected", sorted(D18_PRICES.items()))
def test_the_archived_price_of_every_salon_deploy(card_id, expected):
    assert _price(card_id) == expected


#: The D17 price of the same nine rows, which is what this bump archives.
#: Reproducible on demand rather than transcribed: the dial is the ONLY thing
#: that changed, so setting it to 0.0 puts the pricer back in D17 for these
#: rows exactly (the generic self-power branch the new one sits above pays
#: `STATIC_POWER_ENGINE_VALUE`, which is itself 0.0).
D17_PRICES = {
    "dress_rehearsal":           (0.0000, 0.0000),
    "endless_waltz":             (0.0000, 0.0000),
    "full_ensemble":             (0.0000, 0.0000),
    "gentilhomme_usher":         (4.0000, 6.0000),
    "grand_gala":                (0.6000, 1.0500),
    "mademoiselle_crabaletta":   (0.0000, 0.0000),
    "overflowing_hospitality":   (1.4500, 1.7500),
    "salon_debut":               (0.0000, 0.6000),
    "surintendante_chevalmarin": (0.9000, 1.5000),
}


def test_the_dial_at_zero_reproduces_the_archived_d17_prices(monkeypatch):
    """The archive, checkable. FIVE of the nine priced 0.0000 on their base
    face and FOUR of those on both faces, which is the row's claim measured
    rather than asserted: cross-plan the members were worth literally
    nothing."""
    monkeypatch.setattr(draft, "STATIC_SALON_MEMBER_VALUE", 0.0)
    assert {cid: _price(cid) for cid in D17_PRICES} == D17_PRICES
    assert sum(1 for b, _ in D17_PRICES.values() if b == 0.0) == 5
    assert sum(1 for b, u in D17_PRICES.values() if (b, u) == (0.0, 0.0)) == 4


@pytest.mark.parametrize("card_id", sorted(D18_PRICES))
def test_the_move_is_the_dial_times_the_printed_count_over_cost(card_id):
    """Not a table of magic numbers. Every price above is the D17 price plus
    `deploys * STATIC_SALON_MEMBER_VALUE / cost`, on both faces -- so reading
    the dial off the diff and reading it off the code give the same number."""
    card = loader.get_card(card_id)
    cost = card.cost if isinstance(card.cost, int) else 2
    term = _deploys(card) * draft.STATIC_SALON_MEMBER_VALUE / max(1, cost)
    assert term > 0.0
    assert round(D18_PRICES[card_id][0] - D17_PRICES[card_id][0], 4) == round(
        term, 4)


def test_endless_waltz_is_not_swallowed_by_the_generic_power_branch():
    """The ordering claim, on the one row it decides. Endless Waltz is
    `type: power`, so the generic self-power branch below the new one would
    price the whole card at `STATIC_POWER_ENGINE_VALUE` (0.0) and the deploy
    would stay invisible on exactly the row that most needs to see it."""
    assert draft.STATIC_POWER_ENGINE_VALUE == 0.0
    assert loader.get_card("endless_waltz").type == "power"
    assert _price("endless_waltz")[0] > 0.0


def test_two_upgrades_that_read_identically_before_now_separate():
    """`endless_waltz` and `mademoiselle_crabaletta` both priced 0.0000 on
    BOTH faces at D17 -- an upgrade the offer screen could not see, which is
    the same defect `take_it_from_the_top` was taken for at D17."""
    for card_id in ("endless_waltz", "mademoiselle_crabaletta"):
        base, up = _price(card_id)
        assert up is not None and up > base


# --- (2) the archive scope -------------------------------------------------

def test_exactly_these_nine_cards_print_a_salon_deploy():
    """The archive scope, as a property of the sheets rather than a claim in a
    commit message. A tenth deploy row landing without this test being edited
    would move a price nobody archived."""
    printed = {cid for cid in loader._card_index()
               if _deploys(loader.get_card(cid))}
    assert printed == set(D18_PRICES)


def test_every_deploy_the_engine_can_see_is_a_self_target():
    """The branch reads `target` defaulting to self, matching its Strength /
    Dexterity siblings. A deploy aimed anywhere else would fall through to
    `_op_price` and price at zero again, silently."""
    for cid in D18_PRICES:
        for fx in draft._nested_effects(loader.get_card(cid).effects):
            if fx.get("power") == "salon_member":
                assert fx.get("target", "self") == "self"


def test_the_dial_is_the_conservative_end_of_its_own_derivation():
    """The value is derived, and the two numbers it is derived against are
    live constants rather than prose: the floor is `salon_perform`'s own
    price for one member tick, and the ceiling route is tick + bow."""
    assert draft.STATIC_SALON_MEMBER_VALUE == draft.STATIC_SALON_PERFORM_VALUE
    assert (draft.STATIC_SALON_MEMBER_VALUE
            < draft.STATIC_SALON_PERFORM_VALUE + draft.STATIC_SALON_BOW_VALUE)


def test_the_bump_is_stamped():
    """A priced-op set that grows IS a `DRAFTER_VERSION` bump (EXPERIMENTS,
    D4). This term grew it."""
    assert C.DRAFTER_VERSION == 18
