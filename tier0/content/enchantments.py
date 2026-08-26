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
}

# Enchantments the seven events name that this module deliberately does NOT
# hold, with the engine surface each one would need. House rule: a gap is
# named, never approximated.
#
#   Slither (Wood Carvings) -- "randomises this card's cost when drawn".
#       The ENGINE half is no longer the blocker: EB-83 built the per-draw
#       card hook (`Card.on_draw_randomise_cost` / `cost_set_this_combat`,
#       read in `refpowers.randomise_cost_on_draw`) as unused machinery, and
#       a CATALOG row for Slither would now be expressible. It stays out
#       anyway, on this module's own rule: the row exists to serve a granting
#       event, and Wood Carvings is not converted yet. Its colorless blocker
#       is RULED -- R184 chose reskin, so Peck and Toric Toughness are
#       replaced by equivalent-function companion/Teyvat content and LAW's
#       colorless clause holds. THE ENGINE IS NO LONGER SHORT EITHER: the
#       Peck half was always expressible (1-cost Attack, 2 damage x3), and
#       the TORIC TOUGHNESS half -- "Block at the start of your next 2
#       turns", which `block_next_turn`'s one-shot bank could not say -- now
#       has `block_at_turn_start`, the duration-scoped repeating Block power
#       (EB-83, 2026-08-26; atlas tier0-engine §7), also built as unused
#       machinery. What remains is [USER]'s, not engineering's: the RT window
#       for the conversion and the S4-G11-pattern name eye-read. Until it
#       converts no event grants Slither, so this row stays.
#       An enchantment nobody grants is a name with no caller.
#
#       When it does land it needs a companion row in the parity lint:
#       tools/lint_enchant_parity.GAME_RULES has no `slither` entry and would
#       report UNMAPPED, and the card fact its CanEnchant reads is NOT on the
#       wiki's Enchantments page (Slither is absent from that list) -- the
#       citation has to come from the decompile.
UNEXPRESSED = {
    "slither": ("randomises cost on DRAW -- the engine hook exists (EB-83); "
                "no event grants it, because the Wood Carvings reskin is "
                "blocked on Toric Toughness's 2-turn Block power (R184)"),
}


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
    `enchant_damage_mult` multiplies; everything else is a set-or-add by the
    field's own kind. Deliberately dumb: the whole mechanic is the CATALOG
    row, and nothing downstream ever asks a card which enchantment it holds.
    """
    for field, value in CATALOG[name].rider(amount).items():
        current = getattr(card, field)
        if isinstance(value, list):
            setattr(card, field, list(current) + list(value))
        elif isinstance(value, bool):
            setattr(card, field, value)
        elif field == "enchant_damage_mult":
            card.enchant_damage_mult = current * value
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
