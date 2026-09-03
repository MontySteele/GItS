"""Named enchantments: the vocabulary, and how one rides a deck-list id.

R82 REOPENED ([USER], 2026-08-10, M7 -- "let's reopen r82 and get it done").
R82 clause (2) had closed the enchantment scope at the per-INSTANCE rider
that ships in `engine/state.Card` (`enchant_damage` / `enchant_effects`,
attached at creation by the `enchant:` block on `add_card`). That rider is
enough for Blade Of Ink, which enchants tokens it makes inside a combat, and
it is not enough for an EVENT, which enchants a card that already sits in the
run's deck and must stay enchanted for the rest of the run. This module is
the reopened half, and it is deliberately still not a subsystem:

  * there is no enchantment ECONOMY (no grant screens, no enchanting relics,
    no ~20-type model hierarchy). The base game has one; we do not, and that
    refusal is still recorded in `engine/state.Card`'s rider comment.
  * the vocabulary below holds EXACTLY the enchantments the converted events
    grant, no more. An enchantment nobody grants is a name with no caller.

HOW IT RIDES A DECK LIST. A tier05 deck is a list of id STRINGS, and the run
layer's one existing per-instance decoration is the upgrade suffix (`<id>+`,
resolved in `loader._card_prototype`). An enchantment decorates the same way
rather than growing a parallel structure the deck mutations would have to
keep in step:

    klee_sparkly_bomb@sharp-2        base card, Sharp 2
    klee_sparkly_bomb@sharp-2+       the same card, upgraded

The mark sits BEFORE the upgrade suffix on purpose: every `endswith(SUFFIX)`
read in the repo keeps working unchanged, and only two functions learn about
the mark at all (`loader._card_prototype` builds the enchanted prototype,
`upgrades.has_upgrade` looks past it to the plain id). No id in any sheet
contains `@`, so every existing deck list resolves down the untouched path.

WHAT AN ENCHANTMENT IS ALLOWED TO BE. A row here maps a NAME to concrete
per-instance card fields and nothing else -- there is no hook, no registry,
no combat-side lookup by name. Two of the eight need fields the shipped rider
lacked; those extensions are listed in ENGINE_EXTENSIONS below and are inert
(0 / False / 1.0 / []) on every card that carries no enchantment, so the
frozen battery is byte-identical.

Effect text is the wiki's, verbatim, and the amounts are the granting event's.
"""

from __future__ import annotations

MARK = "@"

# Rider fields added to Card for this pass, and who needed them. Kept as data
# so the docs and the tests can both read the list rather than restate it.
ENGINE_EXTENSIONS = {
    "enchant_block": "Nimble -- the shipped rider folded damage, not Block",
    "enchant_damage_mult": "Corrupted -- a multiplier, not a flat rider",
    "enchant_first_play_damage": "Vigorous -- flat damage, first play only",
    "enchant_first_play_effects": "Sown / Swift -- effects, first play only",
    "enchant_top_of_draw": "Perfect Fit -- a SHUFFLE placement, not a play",
    "enchant_played_this_combat": "the per-instance first-play gate itself",
    # EB-83, and the one field that landed BEFORE its enchantment rather than
    # with it: the per-draw hook was built alone in the 2026-08-26 window on
    # EB-82's admission rule (an engine surface is never invented inline inside
    # a conversion), sat inert while Wood Carvings was blocked, and is armed by
    # the Slither row below. `cost_set_this_combat` is the absolute cost that
    # hook WRITES and is deliberately not listed: it is combat state on the
    # instance (`EnergyCost.SetThisCombat`), never a rider the CATALOG sets.
    "on_draw_randomise_cost": "Slither -- the per-draw cost randomiser",
}


class Enchantment:
    """One named enchantment: its published text, its rider, its targets."""

    __slots__ = ("name", "label", "text", "eligible", "_rider")

    def __init__(self, name, label, text, eligible, rider):
        self.name = name
        self.label = label
        self.text = text
        self.eligible = eligible      # (card) -> bool, BEFORE the shared rules
        self._rider = rider           # (amount) -> {card field: value}

    def rider(self, amount: int | None) -> dict:
        return self._rider(amount)


def _is_attack(c) -> bool:
    return c.type == "attack"


# `block_next_turn` is deliberately NOT here -- see _grants_block. Neither is
# EB-83's `block_at_turn_start`, for the identical reason and by the identical
# mechanism: this is an ALLOWLIST, so a delayed-Block op is excluded by
# construction rather than by remembering to exclude it. Said out loud anyway,
# because "the new op is absent" and "the new op was forgotten" look the same
# on a line that lists one op.
_BLOCK_OPS = ("block",)


def _grants_block(effects) -> bool:
    """Does this effect tree contain a Block-granting op, at any depth?

    `conditional` is the one op that nests further effect lists (`then` /
    `else` -- see engine.effects._op_conditional), so the walk is over those
    two keys and nothing else.

    `block_next_turn` DOES NOT COUNT (EB-85 divergence 4). It is the sim's
    mirror of `BlockNextTurnPower`, whose payout is

        await CreatureCmd.GainBlock(base.Owner, base.Amount,
                                    ValueProp.Unpowered, null);

    in `AfterBlockCleared`. That trailing argument is the `CardPlay`, and
    `GainBlock` derives the card source from it (`cardPlay?.Card`), so a null
    `CardPlay` means a null `cardSource`: `Hook.ModifyBlock` finds no
    `cardSource.Enchantment` and Nimble is never paid on that Block. The mod's cards say the same thing from the
    other side: `TidelineWatch` declares no `BlockVar` and no `GainsBlock`
    override, so `CardModel.GainsBlock` is its inherited `false` and
    `Nimble.CanEnchant` refuses the card outright. A card whose ONLY Block
    arrives this way is not a Nimble target in game (base game: Prolong);
    tier0 offered it one and then paid a rider the game does not pay.
    """
    for fx in effects or ():
        if fx.get("op") in _BLOCK_OPS:
            return True
        if fx.get("op") == "conditional":
            if _grants_block(fx.get("then")) or _grants_block(fx.get("else")):
                return True
    return False


def _gains_block(c) -> bool:
    """Nimble's target: any card that actually GAINS Block.

    CARD TYPE IS NOT PART OF THE RULE (EB-85 divergence 1, fixed in this
    window). The game's `MegaCrit.Sts2.Core.Models.Enchantments.Nimble`
    declares no `CanEnchantCardType` override at all, and its whole gate is

        public override bool CanEnchant(CardModel card)
        {
            if (base.CanEnchant(card)) { return card.GainsBlock; }
            return false;
        }

    so a Block-granting ATTACK is Nimble-eligible in the game. tier0 required
    `type == "skill"` on top of that and refused those cards; the base game
    ships four such Attacks itself (IronWave, Dash, BoneShards, Fisticuffs)
    and this repo's mod cards declare `GainsBlock` the same way.

    The Block half of the predicate stays, and it is the game's own
    (`card.GainsBlock`): 83 of this repo's 134 skills grant no Block at all,
    and the event picker (tier05.events._enchant_targets) chooses the
    drafter's best LEGAL card rather than its best BLOCK card -- so a
    type-only predicate welds Nimble onto cards where its one printed effect
    could never fire, silently.
    """
    return _grants_block(c.effects) or _grants_block(c.enchant_effects)


def _exhausts(c) -> bool:
    return bool(c.exhaust)


def _fixed_cost(c) -> bool:
    """Slither's target: a card whose cost is a NUMBER (EB-83).

    The game's `Models.Enchantments.Slither.CanEnchant` (sts2.dll v0.111.0)
    is

        if (base.CanEnchant(card) && !card.Keywords.Contains(
                CardKeyword.Unplayable)) {
            return !card.EnergyCost.CostsX;
        }
        return false;

    -- two clauses on top of base CanEnchant, and only one of them is a fact
    tier0 can state. `CostsX` is `cost: X` on a sheet row, and the enchantment
    is refused there because a randomised cost and an X cost are the same
    field: writing one erases the other, so the game refuses rather than
    deciding which wins. Two shipped rows are X-cost (`controlled_demolition`,
    `fish_blasting`) and both are therefore illegal targets.

    The Unplayable clause has NO tier0 twin and needs none: the base game's
    own `CanEnchant` already refuses an Unplayable card sitting in the Deck
    pile, Slither's repeat of it only widens the refusal to the piles a deck
    event can never reach, and no card in any sheet here carries the keyword
    (`CardKeyword.Unplayable` appears nowhere in klee-mod). The nearest thing
    the sim has is `type == "status"`, which `eligible` already refuses for
    every enchantment.
    """
    return str(c.cost) != "X"


def _anything(c) -> bool:
    return True


CATALOG: dict[str, Enchantment] = {
    # --- expressible in the SHIPPED rider ---------------------------------
    "sharp": Enchantment(
        "sharp", "Sharp",
        "Increases damage on this card by X.",
        _is_attack,
        lambda x: {"enchant_damage": x}),

    "souls_power": Enchantment(
        "souls_power", "Soul's Power",
        "This card loses Exhaust.",
        _exhausts,
        # Not a rider at all: it un-sets a printed card field, which is the
        # honest expression and needs no engine surface whatsoever.
        lambda x: {"exhaust": False}),

    "corrupted": Enchantment(
        "corrupted", "Corrupted",
        "Deal 50% more damage, but lose 2 HP.",
        _is_attack,
        # The HP loss is the SHIPPED `enchant_effects` list, resolved after
        # the card's own effects -- the same pipe Inky's Weak rides. The
        # damage half needs a multiplier the flat rider could not carry.
        # BOTH NUMBERS ARE THE BINARY'S, confirmed by the EB-84 sweep and
        # re-read for EB-85 (sts2.dll v0.107.1,
        # `Models.Enchantments.Corrupted`): `private const decimal
        # _damageAmount = 2m` with `CreatureCmd.Damage(..., 2m, ...)` in
        # OnPlay, and `EnchantDamageMultiplicative` returning `1.5m`. The
        # sources had disagreed -- mobalytics publishes "lose 3 HP",
        # slaythespire.wiki.gg publishes 2 -- and the wiki-over-mobalytics
        # call this row made was right. The DLL is the citation now.
        #
        # The multiplier is gated `if (!props.IsPoweredAttack()) return 1m;`,
        # i.e. it applies to powered Move damage only, which is why the
        # engine applies it inside the `card.type == "attack"` branch and NOT
        # to the self-damage row below -- that row is dealt Unblockable |
        # Unpowered | Move in game, so it fails the same gate.
        lambda x: {"enchant_damage_mult": 1.5,
                   "enchant_effects": [{"op": "damage", "target": "self",
                                        "amount": 2}]}),

    # --- needed a minimal rider extension (ENGINE_EXTENSIONS) -------------
    "nimble": Enchantment(
        "nimble", "Nimble",
        "Increases Block gained from this card by X.",
        _gains_block,
        lambda x: {"enchant_block": x}),

    "swift": Enchantment(
        "swift", "Swift",
        "The first time you play this card, draw X cards.",
        # EB-85 divergence 2: NO card-level restriction. The game's `Swift`
        # overrides `HasExtraCardText`, `ShowAmount` and `OnPlay` and nothing
        # else -- no `CanEnchant`, no `CanEnchantCardType` -- so base
        # CanEnchant (Status / Curse / Quest / already-enchanted) is the whole
        # gate and any card may take it. tier0 took `_is_power`, a narrowing
        # inherited from the granting event's flavor text rather than the
        # game. This is the widest of the five: it changes what an enchant
        # event may target on every character.
        _anything,
        lambda x: {"enchant_first_play_effects": [{"op": "draw",
                                                   "amount": x}]}),

    "sown": Enchantment(
        "sown", "Sown",
        "The first time you play this card each combat, gain Energy.",
        _anything,
        # The wiki states no amount on the card; the published value is 1
        # Energy, so the row carries 1 rather than taking an event amount.
        lambda x: {"enchant_first_play_effects": [{"op": "energy",
                                                   "amount": 1}]}),

    "vigorous": Enchantment(
        "vigorous", "Vigorous",
        "The first time this card is played, it deals X additional damage.",
        _is_attack,
        lambda x: {"enchant_first_play_damage": x}),

    "perfect_fit": Enchantment(
        "perfect_fit", "Perfect Fit",
        "Whenever this would be shuffled into your Draw Pile, place it on "
        "the top instead.",
        _anything,
        # The printed text says "whenever"; the implementation does not. It
        # is a MID-COMBAT reshuffle placement only -- `ModifyShuffleOrder`
        # opens `if (!isInitialShuffle && ...)` and refuses the opening
        # shuffle, so this is not an Innate (EB-85 divergence 5). The one
        # reading site is state.shuffle_discard_into_draw.
        lambda x: {"enchant_top_of_draw": True}),

    "slither": Enchantment(
        "slither", "Slither",
        "Randomizes this card's cost when drawn.",
        _fixed_cost,
        # THE TEXT IS THE DECOMPILE'S, not the wiki's, and that is deliberate:
        # Slither is absent from slaythespire.wiki.gg's Enchantments page
        # altogether, which is why the gallery entry (dossiers/content/
        # event-conversion-gallery.md) said this row's citation would have to
        # come from the binary. `Models.Enchantments.Slither`, sts2.dll
        # v0.111.0, read 2026-09-02:
        #
        #     public override Task AfterCardDrawn(..., CardModel card, bool
        #                                         fromHandDraw) {
        #         if (card != base.Card) return Task.CompletedTask;
        #         if (base.Card.Pile.Type != PileType.Hand)
        #             return Task.CompletedTask;
        #         base.Card.EnergyCost.SetThisCombat(NextEnergyCost());
        #         ...
        #     private int NextEnergyCost() => ...
        #         base.Card.Owner.RunState.Rng.CombatEnergyCosts.NextInt(4);
        #
        # THE RIDER IS THE ROLL'S EXCLUSIVE BOUND, 4 -- i.e. 0..3 inclusive,
        # which is `NextInt(4)` verbatim -- and it IGNORES the event amount,
        # exactly as Sown's 1 Energy does: Wood Carvings grants it with
        # `CardCmd.Enchant<Slither>(cardModel, 1m)`, but nothing in the class
        # reads that amount, so a number in the deck-list id would be a
        # number nothing spends. The hook that consumes this field is
        # `refpowers.randomise_cost_on_draw`, which carries the game's
        # in-hand gate and the per-instance identity check with it.
        lambda x: {"on_draw_randomise_cost": 4}),
}

# Enchantments the seven events name that this module deliberately does NOT
# hold, with the engine surface each one would need. House rule: a gap is
# named, never approximated.
#
# THE TABLE IS EMPTY as of EB-83 (2026-09-02), and empty is a RESULT rather
# than a table nobody filled in. It held exactly one row for the whole of its
# life -- Slither, the Wood Carvings enchantment -- and that row left because
# the event converted, which is the only exit this dict has ever had: the
# module's rule is that a CATALOG row serves a granting event, so an
# unexpressed name is one an unconverted event would grant. Every enchantment
# the seven events name is now in CATALOG above.
#
# Slither's history, kept because it is the shape of the next gap rather than
# a fact about this one: the ENGINE half stopped being the blocker on
# 2026-08-26, when EB-83 built the per-draw card hook
# (`Card.on_draw_randomise_cost` / `cost_set_this_combat`, read in
# `refpowers.randomise_cost_on_draw`) as unused machinery. The row still
# stayed out for six days after that, on this module's own rule, because
# Wood Carvings was still blocked -- on R184's colorless call, then on the
# R231 name eye-read, then on the `RT` window. An enchantment nobody grants is
# a name with no caller, and the engine being ready is not the same fact.
#
# A ROW ADDED HERE IN FUTURE owes what Slither's owed and paid: the enchantment
# the event names, the engine surface it would need, and -- the part that is
# easy to forget -- a companion row in `tools/lint_enchant_parity.GAME_RULES`
# on the day it moves into CATALOG, because a CATALOG name with no rule there
# reports UNMAPPED and a rule there with no CATALOG name reports STALE.
UNEXPRESSED: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Deck-list ids.
# ---------------------------------------------------------------------------

def split(card_id: str) -> tuple[str, str | None, int | None]:
    """`<plain id>, <enchantment name>, <amount>` for a deck-list id.

    The plain id KEEPS its upgrade suffix, because the suffix is the other
    decoration and the two are independent: `x@sharp-2+` splits to
    `("x+", "sharp", 2)`. An undecorated id round-trips as `(id, None, None)`,
    which is the branch every existing deck list takes.
    """
    if MARK not in card_id:
        return card_id, None, None
    base, _, tail = card_id.partition(MARK)
    from tier0.content import upgrades          # late: upgrades imports us not
    suffix = ""
    if tail.endswith(upgrades.SUFFIX):
        tail, suffix = tail[:-len(upgrades.SUFFIX)], upgrades.SUFFIX
    name, dash, raw = tail.rpartition("-")
    if not dash:                                # no amount: `@perfect_fit`
        name, raw = tail, ""
    amount = int(raw) if raw else None
    if name not in CATALOG:
        raise ValueError(
            f"{card_id!r}: unknown enchantment {name!r}. Registered: "
            f"{', '.join(sorted(CATALOG))}. Adding one means a row in "
            "tier0/content/enchantments.CATALOG (R82, reopened 2026-08-10).")
    return base + suffix, name, amount


def decorate(card_id: str, name: str, amount: int | None = None) -> str:
    """Attach an enchantment to a deck-list id, upgrade suffix preserved.

    Refuses a card that already carries one: the base game's rule is that a
    card holds exactly one enchantment and it can neither be removed nor
    replaced, and the event layer's eligibility filter depends on that being
    enforced here rather than remembered at every call site.
    """
    if name not in CATALOG:
        raise ValueError(f"unknown enchantment {name!r}")
    plain, held, _ = split(card_id)
    if held is not None:
        raise ValueError(
            f"{card_id!r} already carries {held!r}; a card holds exactly one "
            "enchantment and it cannot be replaced")
    from tier0.content import upgrades
    suffix = ""
    if plain.endswith(upgrades.SUFFIX):
        plain, suffix = plain[:-len(upgrades.SUFFIX)], upgrades.SUFFIX
    tag = name if amount is None else f"{name}-{amount}"
    return f"{plain}{MARK}{tag}{suffix}"


def enchantment_of(card_id: str) -> str | None:
    return split(card_id)[1]


def apply(card, name: str, amount: int | None) -> None:
    """Write one enchantment's rider onto a card instance, in place.

    List-valued rider fields APPEND (a card could in principle already carry
    an `enchant_effects` row from the creation-time `enchant:` block);
    `enchant_damage_mult` multiplies; a field whose current value is `None`
    is SET, because `None` is this engine's spelling of "this card does not
    have one of these at all" and there is nothing to add to; everything else
    is a set-or-add by the field's own kind. Deliberately dumb: the whole
    mechanic is the CATALOG row, and nothing downstream ever asks a card which
    enchantment it holds.

    The `None` branch arrived with EB-83's Slither, whose rider writes
    `on_draw_randomise_cost` -- an ABSOLUTE roll bound (`NextInt(4)`), not a
    delta. Adding it to a default of `None` raised; adding it to a default of
    0 would have been worse, because summing two bounds is not what a second
    bound would mean. Nothing can reach the add branch on such a field anyway:
    a card holds exactly one enchantment and `decorate` refuses a second.
    """
    for field, value in CATALOG[name].rider(amount).items():
        current = getattr(card, field)
        if isinstance(value, list):
            setattr(card, field, list(current) + list(value))
        elif isinstance(value, bool):
            setattr(card, field, value)
        elif field == "enchant_damage_mult":
            card.enchant_damage_mult = current * value
        elif current is None:
            setattr(card, field, value)
        else:
            setattr(card, field, current + value)


def eligible(card, name: str) -> bool:
    """May this card take this enchantment, ignoring what it already holds?

    Three shared rules on top of the row's own predicate, all of them the
    base game's: a curse is not an enchantment target, an injected status is
    not a card the player owns, and a kit card never enters a deck at all so
    it can never be the target of a deck-level event.
    """
    if card.rarity == "curse" or card.type == "status" or card.kit_card:
        return False
    return CATALOG[name].eligible(card)
