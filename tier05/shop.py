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
    R116/NC-10, slot-2 floor RESTORED by [USER] 2026-08-10).

    Slot 1 draws the character's HOME NATION at an Uncommon floor -- the
    targeted "buy your dream support" slot. Slot 2 draws ANY NATION at the
    SAME Uncommon floor. The two slots differ by nation and by nothing else.

    THE FLOOR ON SLOT 2 CAME BACK ON 2026-08-10. R116/NC-10 had removed it
    ("any companion card"), which let slot 2 roll the full reward odds and
    sell a Common at the 50-gold band. [USER] closed the S4-G10 agenda item
    "should slot 2 carry a rarity floor at all?" by restoring R59's reading:
    the paid premium channel does not sell Commons. Both engines moved
    together and the shop world bumped to CONSTANTS_VERSION 9, so no §4.7
    number measured before that date is comparable with one measured after.
    Returns ``(card, price)`` pairs because the two slots are priced by DRAWN RARITY,
    which is the whole balance story: §4.7 lets the paid channel roll
    payoff-grade 5-stars precisely because gold, not a stat nerf, is the
    governor.

    EMPTY-DRAW LADDER (Track D). A slot that cannot be filled must be a
    decision, never a crash. The ladder widens the NATION before it drops the
    RARITY, because R59 ratified the floor while §4.7 only ever described the
    nation as falling through:

        home nation @ rarity -> any nation @ rarity -> any nation @ the other
        rarity -> the slot is OMITTED.

    THE LAST RUNG NO LONGER DIVERGES ([USER] 2026-08-10). It used to: the C#
    side fell back to one base colorless card for that slot, while tier 0.5 --
    which models no base colorless pool at all -- dropped the slot. The
    divergence was unreachable (it needs a rarity with no companion at ANY
    nation), but an unreachable divergence is still two different games on
    paper, so it was ruled shut in the SIM'S favour: the mod now omits the
    slot too. See `MerchantCompanionSlots.AddSlot` for how the mod omits it
    without ever handing `MerchantCardEntry.Populate` a no-card path.

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
        # ONE TABLE, TWO NATIONS ([USER] 2026-08-10, CONSTANTS_VERSION 9).
        # Slot 1 is "Uncommon or higher from the home region"; slot 2 is
        # "Uncommon or higher from any region". The slots differ in the NATION
        # filter only, so they read the same conditioned odds -- which is why
        # `odds` is no longer a per-slot choice.
        #
        # WHAT MOVED. R116/NC-10 had slot 2 on RARITY_ODDS itself (no floor,
        # Commons drawable at the 50-gold band); [USER] restored R59's floor
        # on 2026-08-10 and slot 2 came back to this table. The conditioning
        # inside the table is still Q16's ruled reading (R118, verbatim
        # "Condition."); that ruling is untouched here, only its scope grew
        # back to both slots.
        nation = home if slot == 0 else None
        odds = C.SHOP_COMPANION_RARITY_ODDS
        rarity = _roll_companion_rarity(rng, odds)
        cards = eligible(rarity, nation, taken)
        if not cards and nation is not None:
            cards = eligible(rarity, None, taken)
        if not cards:
            # The rarity rung: try the table's OWN remaining rarities, in the
            # table's order. Order is the odds table's, not a preference of
            # this function's -- picking a "best" fallback rarity would be a
            # balance choice hiding in an error path. Since the floor came
            # back to slot 2 the table is two-entry again for both slots, so
            # this rung can no longer drop a slot below Uncommon.
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

    NC-10 (R116) gave the two slots different tables and made the table an
    argument rather than a constant this function reads. [USER]'s 2026-08-10
    floor restoration put both slots back on one table, but the argument
    STAYS an argument: a per-slot table is the shape a future stated split
    would need (see tier0/constants.py), and re-hardcoding the read would
    have to be undone to get there. The fallback returns the table's FIRST
    key, the table's own commonest rarity; it is only reachable on float slop.
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
    # price, visit, gold_at_visit, affordable}. The buy log alone cannot grade
    # P1, because a slot that was never offered and a slot that was offered
    # and declined are the same absence in it -- and the difference is exactly
    # what a buy RATE means.
    #
    # `visit` IS THE JOIN KEY (added 2026-08-10). Both lists are flattened
    # onto the RunResult across every shop the run walks into, and until this
    # field existed there was no way to say which offer a purchase answered:
    # the P1 instrument matched on slot alone and therefore credited a buy at
    # shop 3 to the offers at shops 1 and 2 as well. `gold_at_visit` and
    # `affordable` are the money read AT THE DOOR -- whether the purse could
    # have reached this offer at the moment the visit began.
    companion_offers: list[dict] = field(default_factory=list)
    # Everything the purse could NOT reach, at the moment it could not reach
    # it (added 2026-08-11). `companion_offers.affordable` is measured at the
    # door and therefore cannot see a card that went out of reach DURING the
    # visit; both such exits used to be silent. Two kinds, distinguished by
    # `residual`:
    #
    #   residual=False -- the buy loop's PREFERRED PICK. The policy named this
    #       card and gold could not cover it, so the entry was dropped and the
    #       policy re-asked. `spent_before` is the gold already committed this
    #       visit: 0 means the card was never affordable here at all, >0 means
    #       earlier purchases in THIS visit priced it out.
    #   residual=True -- STILL ON THE SHELF and out of reach when the loop
    #       ended. The loop guard exits the moment gold falls below the
    #       cheapest remaining entry, so on that exit every survivor was
    #       stranded; on a policy-skip exit only the survivors that were also
    #       unaffordable are logged. `exit` says which ("guard" / "skip").
    #
    # Shape: {visit, id, price, rarity, channel, slot, gold_now,
    #         gold_at_visit, spent_before, residual, exit}. `channel` is
    # "companion" or "character"; `slot` is the companion slot index or None;
    # `exit` is "pick" on a preferred-pick record and "guard"/"skip" on a
    # residual one, naming how the buy loop ended.
    # Nothing reads these to decide anything and appending them draws no rng
    # (see the module docstring), so the run plays out identically either way.
    priced_out: list[dict] = field(default_factory=list)


def visit_shop(rng: random.Random, character: str, deck_ids: list[str],
               gold: int, archetype: str, policy: DraftPolicy,
               removal_uses: int = 0,
               n_offers: int = C.SHOP_CARD_OFFERS,
               companions: bool = True,
               banner: frozenset[str] | None = None,
               visit: int = 0) -> ShopOutcome:
    """Resolve one shop visit. Returns the mutated deck, remaining gold, the
    running removal count, a per-purchase log, the companion offer log and a
    PRICED-OUT log (see ShopOutcome) recording what gold could not reach, at
    the moment it could not reach it -- both the preferred pick the policy
    named and could not pay for, and whatever was still on the shelf when the
    purse ran dry. Together those are the honest answer to "was a preferred
    purchase ever priced out"; the offer log's `affordable` flag answers only
    the narrower question of what the purse could reach ON ARRIVAL.

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
    channel-off arm identical to every archived shop number.

    ``visit`` is this shop's INDEX WITHIN THE RUN (0-based), stamped onto
    every record this call emits. It is pure bookkeeping -- nothing reads it
    to decide anything, and it consumes no rng -- but without it the run-level
    offer and purchase logs cannot be joined, which is the defect that made
    the P1 buy rate wrong (see ShopOutcome.companion_offers). Callers that do
    not care may leave it at 0."""
    deck_ids = list(deck_ids)
    gold_at_visit = gold
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
    priced_out: list[dict] = []
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
            companion_offers.append(
                {"slot": slot, "id": card.id, "rarity": card.rarity,
                 "price": price, "visit": visit,
                 # Money at the door, and whether THIS offer was inside it.
                 # Measured at visit START, before the character shelf spends
                 # anything: "could the player have had it" is the question,
                 # and by the time the companion slots are evaluated the purse
                 # has already been narrowed by choices the player made with
                 # this offer visible.
                 "gold_at_visit": gold_at_visit,
                 "affordable": price <= gold_at_visit})

    def _out_of_reach(card: Card, residual: bool, how: str) -> dict:
        """One priced-out record. Pure bookkeeping: no rng, no state."""
        return {"visit": visit, "id": card.id, "price": price_of[id(card)],
                "rarity": card.rarity,
                "channel": "companion" if id(card) in slot_of else "character",
                "slot": slot_of.get(id(card)),
                "gold_now": gold, "gold_at_visit": gold_at_visit,
                "spent_before": gold_at_visit - gold,
                "residual": residual, "exit": how}

    # How the buy loop ended, for the log. "guard" is the default because the
    # guard is also what stops the loop from starting: walking into a shop too
    # poor for anything on the shelf is the same exit as running dry inside it.
    how = "guard"
    while shelf and gold >= min(price_of[id(c)] for c in shelf):
        pick = policy(rng, deck_cards, shelf, archetype)
        if pick is None:                 # policy would skip the shelf -> stop
            how = "skip"
            break
        price = price_of[id(pick)]
        if price > gold:
            # The policy wants a card it cannot afford. Drop that ONE entry
            # and re-ask: with a flat shelf this branch is unreachable (the
            # loop guard already proved affordability), so every archived
            # flat-price run is bit-identical. With the companion channel it
            # is the difference between "too expensive" and "shop over" -- and
            # that difference is now WRITTEN DOWN rather than merely commented
            # on. `spent_before` separates "never affordable at this shop"
            # (0) from "priced out by what this visit already bought" (>0),
            # which is the only place the second case is visible at all.
            priced_out.append(_out_of_reach(pick, residual=False, how="pick"))
            shelf.remove(pick)
            continue
        gold -= price
        deck_ids.append(pick.id)
        deck_cards.append(pick)
        record = {"buy": "card", "id": pick.id, "price": price,
                  "visit": visit}
        if id(pick) in slot_of:
            record["channel"] = "companion"
            record["slot"] = slot_of[id(pick)]
            # TRUE rarity, logged rather than inferred. The instrument used
            # to recover slot-2 rarity from the price band with a two-way
            # `>= 150 ? rare : uncommon` split, which silently folded every
            # Common purchase into the "uncommon" bucket for as long as slot 2
            # could sell Commons. A price band is not a rarity; the card knows
            # its own.
            record["rarity"] = pick.rarity
        purchases.append(record)
        shelf.remove(pick)

    # THE SILENT EXIT, LOGGED (2026-08-11). The loop guard above stops the
    # moment gold falls below the CHEAPEST remaining entry, and everything
    # still on the shelf at that instant was priced out -- including companion
    # slots that were affordable at the door and stopped being affordable
    # because this visit bought something else. That is exactly the case the
    # door-time `affordable` flag cannot see, and until now nothing recorded
    # it. On a policy-skip exit the survivors are NOT all stranded (the policy
    # simply stopped wanting them), so only the ones gold could not have
    # covered anyway are logged; `exit` keeps the two kinds apart.
    for card in shelf:
        if price_of[id(card)] > gold:
            priced_out.append(_out_of_reach(card, residual=True, how=how))

    # --- removal: only a known-dead card, only if affordable (§5) ---
    dead = known_dead_card(deck_cards)
    price = removal_price(removal_uses)
    if dead is not None and gold >= price:
        gold -= price
        deck_ids.remove(dead.id)
        removal_uses += 1
        purchases.append({"buy": "removal", "id": dead.id, "price": price,
                          "visit": visit})

    return ShopOutcome(deck_ids=deck_ids, gold=gold,
                       removal_uses=removal_uses, purchases=purchases,
                       companion_offers=companion_offers,
                       priced_out=priced_out)


# --- Treasure relic slot: STUB (§1, §5). Relics are NOT modeled this pass.
# The treasure node grants gold (model.run_one) and calls this no-op so the
# hook exists exactly where a relic would be granted -- do NOT invent a relic
# here; that is a separate, unratified stream.
def grant_treasure_relic(character: str, deck_ids: list[str]) -> None:
    """No-op relic slot. Intentionally does nothing (relics unmodeled, §1)."""
    return None
