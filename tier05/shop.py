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


@dataclass
class ShopOutcome:
    deck_ids: list[str]
    gold: int
    removal_uses: int
    purchases: list[dict] = field(default_factory=list)   # buy log


def visit_shop(rng: random.Random, character: str, deck_ids: list[str],
               gold: int, archetype: str, policy: DraftPolicy,
               removal_uses: int = 0,
               n_offers: int = C.SHOP_CARD_OFFERS) -> ShopOutcome:
    """Resolve one shop visit. Returns the mutated deck, remaining gold, the
    running removal count and a per-purchase log.

    CARDS FIRST, then removal (deterministic order so gold-limited runs are
    replayable). Cards are bought best-first by asking the DRAFT POLICY to
    pick from the shelf; we buy its pick when affordable and re-ask on the
    shrunken shelf until it skips or gold can't cover the next card. Removal
    is bought once if a known-dead card is present and the rising price is
    affordable."""
    deck_ids = list(deck_ids)
    deck_cards = [loader.get_card(cid) for cid in deck_ids]
    purchases: list[dict] = []

    # --- cards: reuse the draft policy's valuation verbatim (§5) ---
    shelf = shop_offer(rng, character, n_offers)
    while shelf and gold >= C.SHOP_CARD_PRICE:
        pick = policy(rng, deck_cards, shelf, archetype)
        if pick is None:                 # policy would skip the shelf -> stop
            break
        gold -= C.SHOP_CARD_PRICE
        deck_ids.append(pick.id)
        deck_cards.append(pick)
        purchases.append({"buy": "card", "id": pick.id,
                          "price": C.SHOP_CARD_PRICE})
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
                       removal_uses=removal_uses, purchases=purchases)


# --- Treasure relic slot: STUB (§1, §5). Relics are NOT modeled this pass.
# The treasure node grants gold (model.run_one) and calls this no-op so the
# hook exists exactly where a relic would be granted -- do NOT invent a relic
# here; that is a separate, unratified stream.
def grant_treasure_relic(character: str, deck_ids: list[str]) -> None:
    """No-op relic slot. Intentionally does nothing (relics unmodeled, §1)."""
    return None
