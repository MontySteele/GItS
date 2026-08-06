"""Shop node ($) economy (run-model rework §5, Economy phase).

The smallest closed loop that makes the shop mean something. A shop visit:

  1. Offers SHOP_CARD_OFFERS cards rolled from the character's OWN draft pool
     -- `rewards.character_pool`, which is ownership-REQUIRED and companion-
     free. The shop can therefore NEVER offer another character's cards or a
     companion (§5): it reuses the exact ownership filter the reward screen
     uses, so the two doors admit the same cards.
  2. Offers ONE card removal, priced SHOP_REMOVAL_PRICE rising by
     SHOP_REMOVAL_PRICE_STEP per removal already bought this run.

Buy policy (§5) REUSES the draft policy's valuation rather than inventing a
second one:

  - CARDS: the policy is asked to draft from the offered cards exactly as it
    would at a reward screen. It picks its best; we buy it iff gold allows,
    then ask again on the shrunken shelf with the bought card now in the deck,
    until the policy skips (its own skip threshold) or gold runs out. "Buy a
    card iff the policy would draft it AND gold allows" -- verbatim.
  - REMOVAL: bought iff a KNOWN-DEAD card (a curse, or unupgradable basic
    filler) is in the deck and the rising price is affordable. Klee's basics
    are all upgradable, so this branch stays inert on her clean deck -- it
    fires only against a genuinely dead card, which is the point.

All randomness flows through the run's single `random.Random`, same
determinism contract as the rest of tier0.5. The draft policies do not
consume rng (they sort), so evaluating buys never perturbs the run stream.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Optional

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine.state import Card
from tier05 import rewards

# Same callable shape as tier05.model.DraftPolicy.
DraftPolicy = Callable[[random.Random, list[Card], list[Card], str],
                       Optional[Card]]


def is_known_dead(card: Card) -> bool:
    """A removal target (§5): a curse, or unupgradable basic filler.

    'curse' is a tag we do not ship yet -- the branch exists so the mechanism
    is correct the moment a curse card appears, never faked. 'Unupgradable
    filler' is a basic-rarity glue card (a plain strike/defend) with no
    upgrade path: it will never scale and is the classic thing you pay to
    thin. An ALREADY-upgraded basic (`kaboom+`) is excluded -- it lost its
    upgrade because it was spent, not because it is filler."""
    if "curse" in card.tags:
        return True
    return (card.rarity == "basic" and card.role == "glue"
            and not card.id.endswith(upgrades.SUFFIX)
            and not upgrades.has_upgrade(card.id))


def known_dead_card(deck_cards: list[Card]) -> Optional[Card]:
    """The first known-dead card in the deck, or None. Deck order is the
    run's deck order, so this is deterministic."""
    for c in deck_cards:
        if is_known_dead(c):
            return c
    return None


def removal_price(removal_uses: int) -> int:
    """Rising removal price: base + step per removal already bought (§5)."""
    return C.SHOP_REMOVAL_PRICE + C.SHOP_REMOVAL_PRICE_STEP * removal_uses


def shop_offer(rng: random.Random, character: str,
               n: int = C.SHOP_CARD_OFFERS) -> list[Card]:
    """Roll `n` cards from the character's OWN draft pool for sale.

    Reuses `rewards.character_pool` (ownership-required, companion-free) and
    the same rarity roll the reward screen uses, so shop stock is drawn from
    exactly the cards the character could otherwise be offered -- never a
    companion, never another character's card."""
    pool = rewards.character_pool(character)
    if not pool:
        raise ValueError(
            f"no shop stock for character {character!r} -- character_pool is "
            "empty (every shop card must be owned by the character).")
    offers: list[Card] = []
    for _ in range(n):
        rarity = rewards._roll_rarity(rng)
        while rarity not in pool:                 # ref pool may lack a rarity
            rarity = {"rare": "uncommon", "uncommon": "common"}[rarity]
        offers.append(loader.get_card(rng.choice(pool[rarity]).id))
    return offers


def companion_shop_offer(
        rng: random.Random, character: str,
        banner: frozenset[str] | None = None) -> list[tuple[Card, int]]:
    """The §4.7 companion channel: TWO priced slots (R59/R61, respecified by
    R116/NC-10).

    Slot 1 draws the character's HOME NATION at an Uncommon floor -- the
    targeted "buy your dream support" slot. Slot 2 is "any companion card":
    no nation and NO FLOOR, so it rolls the full reward odds and can offer a
    Common at the Common band. That is R116's spec and it supersedes R59's
    reading of the floor as covering both slots; the shop is now a real Rare
    source in slot 1's math and a real Common source in slot 2's, which is
    cross-noted to the companion-pricing docket because it moves the
    acquisition assumptions that docket prices against. Returns
    ``(card, price)`` pairs because the two slots are priced by DRAWN RARITY,
    which is the whole balance story: §4.7 lets the paid channel roll
    payoff-grade 5-stars precisely because gold, not a stat nerf, is the
    governor.

    EMPTY-DRAW LADDER (Track D). A slot that cannot be filled must be a
    decision, never a crash. The ladder widens the NATION before it drops the
    RARITY, because R59 ratified the floor while §4.7 only ever described the
    nation as falling through:

        home nation @ rarity -> any nation @ rarity -> any nation @ the other
        rarity -> the slot is OMITTED.

    THE LAST RUNG DIVERGES FROM THE MOD, deliberately and it is recorded here
    rather than faked: the C# side falls back to one base colorless card for
    that slot (R60 keeps ColorlessCardPool populated exactly so that rung
    exists). tier 0.5 models no base colorless pool at all, so it drops the
    slot instead. The divergence is unreachable today -- it needs a rarity with
    no companion at ANY nation -- and inventing a base-colorless surrogate to
    match would be faking content the sim does not have.

    Live corner worth knowing (UPDATED 2026-07-25, R64): Fontaine used to
    design ZERO Rare companions, so Furina's slot 1 could never roll one and
    took the nation-widening rung as its everyday path. It now designs four, so
    her slot 1 answers a Rare roll from her own nation. The rung is still
    reachable and still load-bearing -- it is now the BANNER that can empty her
    Rare tier (four Fontaine Rares against three featured slots), rather than
    the roster being empty by construction. That is the first time the rung has
    had a stochastic trigger instead of a structural one.
    """
    home = loader.character_nation(character)
    pool = rewards.companion_pool()

    def eligible(rarity: str, nation: str | None,
                 taken: list[Card]) -> list[Card]:
        taken_ids = {c.id for c in taken}
        cards = rewards._banner_filtered(pool.get(rarity, []), banner)
        return [c for c in cards
                if c.personal_pool in (None, character)
                and c.id not in taken_ids
                and (nation is None or c.nation == nation)]

    offers: list[tuple[Card, int]] = []
    taken: list[Card] = []
    for slot in range(C.SHOP_COMPANION_SLOTS):
        # NC-10 (R116, Errata Batch 2 item 6): slot 1 is "Uncommon or higher
        # from the home region"; slot 2 is "any companion card" -- no nation
        # and no floor. The two slots differ in BOTH filters, so they read
        # different odds tables: slot 1 the floor's conditioned odds, slot 2
        # RARITY_ODDS itself. See tier0/constants.py for the conditioning and
        # for the stated-split reading that was surfaced and not chosen.
        # RESOLVED BY Q16, 2026-08-06 (R117 rider / R118, verbatim
        # "Condition."): the conditioning shipped here IS the ruled reading;
        # the stated-split alternative was declined. No value changed.
        nation = home if slot == 0 else None
        odds = C.SHOP_COMPANION_RARITY_ODDS if slot == 0 else C.RARITY_ODDS
        rarity = _roll_companion_rarity(rng, odds)
        cards = eligible(rarity, nation, taken)
        if not cards and nation is not None:
            cards = eligible(rarity, None, taken)
        if not cards:
            # The rarity rung, generalized because slot 2's table now has
            # three entries instead of two: try the slot's OWN remaining
            # rarities, in the table's order. Order is the odds table's, not
            # a preference of this function's -- picking a "best" fallback
            # rarity would be a balance choice hiding in an error path.
            for other in odds:
                if other == rarity:
                    continue
                cards = eligible(other, None, taken)
                if cards:
                    rarity = other
                    break
        if not cards:
            continue                      # slot omitted -- see the docstring
        pick = rng.choice(cards)
        taken.append(pick)
        offers.append((loader.get_card(pick.id), C.SHOP_COMPANION_PRICE[rarity]))
    return offers


def _roll_companion_rarity(rng: random.Random, odds: dict) -> str:
    """One draw from a rarity table.

    NC-10 (R116) gave the two slots different tables -- slot 1 the reward
    odds conditioned on >= Uncommon, slot 2 the reward odds themselves -- so
    the table is an argument now rather than a constant this function reads.
    The fallback returns the table's FIRST key, which is the table's own
    commonest rarity in both cases; it is only reachable on float slop.
    """
    roll = rng.random()
    acc = 0.0
    for rarity, weight in odds.items():
        acc += weight
        if roll < acc:
            return rarity
    return next(iter(odds))


@dataclass
class ShopOutcome:
    deck_ids: list[str]
    gold: int
    removal_uses: int
    purchases: list[dict] = field(default_factory=list)   # buy log
    # What the companion channel OFFERED this visit: {slot, id, rarity,
    # price}. The buy log alone cannot grade P1, because a slot that was never
    # offered and a slot that was offered and declined are the same absence in
    # it -- and the difference is exactly what a buy RATE means.
    companion_offers: list[dict] = field(default_factory=list)


def visit_shop(rng: random.Random, character: str, deck_ids: list[str],
               gold: int, archetype: str, policy: DraftPolicy,
               removal_uses: int = 0,
               n_offers: int = C.SHOP_CARD_OFFERS,
               companions: bool = True,
               banner: frozenset[str] | None = None) -> ShopOutcome:
    """Resolve one shop visit. Returns the mutated deck, remaining gold, the
    running removal count and a per-purchase log.

    CARDS FIRST, then removal (deterministic order so gold-limited runs are
    replayable). Cards are bought best-first by asking the DRAFT POLICY to
    pick from the shelf; we buy its pick when affordable and re-ask on the
    shrunken shelf until it skips or gold can't cover the next card. Removal
    is bought once if a known-dead card is present and the rising price is
    affordable.

    ``companions`` is the §4.7 channel (R61). It is a PARAMETER rather than a
    constant so P2 can be measured as a paired-seed on/off comparison; note
    that turning it on also consumes rng, so the two arms diverge downstream
    rather than being strictly paired. Character-card offers are rolled FIRST
    so their draw sequence is untouched by the flag, which is what keeps the
    channel-off arm identical to every archived shop number."""
    deck_ids = list(deck_ids)
    # Read-only: the policy only SCORES the held deck (a bought card is
    # appended by id), so the shared prototypes are safe here.
    deck_cards = [loader.peek_card(cid) for cid in deck_ids]
    purchases: list[dict] = []

    # --- cards: reuse the draft policy's valuation verbatim (§5) ---
    # Character cards first (see the flag note above), then the two companion
    # slots. Price is per-card because the channels charge differently: the
    # character shelf is the flat §5 price, companions are priced by drawn
    # rarity. `id()` keys are safe -- loader.get_card returns a fresh copy per
    # call, so two copies of one card id are still distinct shelf entries.
    shelf = shop_offer(rng, character, n_offers)
    price_of: dict[int, int] = {id(c): C.SHOP_CARD_PRICE for c in shelf}
    # Which companion slot an entry came from. Needed because P1 and P3 are
    # SLOT-level predictions -- "did the premium home-region slot get bought"
    # is a different question from "did a companion get bought", and only the
    # first one grades the §4.7 thesis. Character-shelf entries stay out of
    # this map so their purchase records keep their original shape.
    slot_of: dict[int, int] = {}
    companion_offers: list[dict] = []
    if companions:
        for slot, (card, price) in enumerate(
                companion_shop_offer(rng, character, banner), start=1):
            shelf.append(card)
            price_of[id(card)] = price
            slot_of[id(card)] = slot
            companion_offers.append({"slot": slot, "id": card.id,
                                     "rarity": card.rarity, "price": price})

    while shelf and gold >= min(price_of[id(c)] for c in shelf):
        pick = policy(rng, deck_cards, shelf, archetype)
        if pick is None:                 # policy would skip the shelf -> stop
            break
        price = price_of[id(pick)]
        if price > gold:
            # The policy wants a card it cannot afford. Drop that ONE entry
            # and re-ask: with a flat shelf this branch is unreachable (the
            # loop guard already proved affordability), so every archived
            # flat-price run is bit-identical. With the companion channel it
            # is the difference between "too expensive" and "shop over".
            shelf.remove(pick)
            continue
        gold -= price
        deck_ids.append(pick.id)
        deck_cards.append(pick)
        record = {"buy": "card", "id": pick.id, "price": price}
        if id(pick) in slot_of:
            record["channel"] = "companion"
            record["slot"] = slot_of[id(pick)]
        purchases.append(record)
        shelf.remove(pick)

    # --- removal: only a known-dead card, only if affordable (§5) ---
    dead = known_dead_card(deck_cards)
    price = removal_price(removal_uses)
    if dead is not None and gold >= price:
        gold -= price
        deck_ids.remove(dead.id)
        removal_uses += 1
        purchases.append({"buy": "removal", "id": dead.id, "price": price})

    return ShopOutcome(deck_ids=deck_ids, gold=gold,
                       removal_uses=removal_uses, purchases=purchases,
                       companion_offers=companion_offers)


# --- Treasure relic slot: STUB (§1, §5). Relics are NOT modeled this pass.
# The treasure node grants gold (model.run_one) and calls this no-op so the
# hook exists exactly where a relic would be granted -- do NOT invent a relic
# here; that is a separate, unratified stream.
def grant_treasure_relic(character: str, deck_ids: list[str]) -> None:
    """No-op relic slot. Intentionally does nothing (relics unmodeled, §1)."""
    return None
