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


_BLOCK_OPS = ("block", "block_next_turn")


def _grants_block(effects) -> bool:
    """Does this effect tree contain a Block-granting op, at any depth?

    `conditional` is the one op that nests further effect lists (`then` /
    `else` -- see engine.effects._op_conditional), so the walk is over those
    two keys and nothing else.
    """
    for fx in effects or ():
        if fx.get("op") in _BLOCK_OPS:
            return True
        if fx.get("op") == "conditional":
            if _grants_block(fx.get("then")) or _grants_block(fx.get("else")):
                return True
    return False


def _is_block_skill(c) -> bool:
    """Nimble's target: a Skill that actually GAINS Block.

    The loose predicate was `type == "skill"`, but 83 of this repo's 134
    skills grant no Block at all, and the event picker
    (tier05.events._enchant_targets) chooses the drafter's best LEGAL card
    rather than its best BLOCK card -- so Nimble routinely welded itself onto
    a card where its one printed effect could never fire, silently. The
    tighter predicate is the published text read literally ("Block gained
    from this card"), and the event targeting follows it for free.
    """
    return c.type == "skill" and (_grants_block(c.effects)
                                  or _grants_block(c.enchant_effects))


def _is_power(c) -> bool:
    return c.type == "power"


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
        # NOTE, recorded rather than averaged: mobalytics publishes "lose 3
        # HP" for this enchantment; slaythespire.wiki.gg publishes 2, and the
        # wiki is this repo's authority everywhere else in the event layer,
        # so 2 it is.
        lambda x: {"enchant_damage_mult": 1.5,
                   "enchant_effects": [{"op": "damage", "target": "self",
                                        "amount": 2}]}),

    # --- needed a minimal rider extension (ENGINE_EXTENSIONS) -------------
    "nimble": Enchantment(
        "nimble", "Nimble",
        "Increases Block gained from this card by X.",
        _is_block_skill,
        lambda x: {"enchant_block": x}),

    "swift": Enchantment(
        "swift", "Swift",
        "The first time you play this card, draw X cards.",
        _is_power,
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
        lambda x: {"enchant_top_of_draw": True}),
}

# Enchantments the seven events name that this module deliberately does NOT
# hold, with the engine surface each one would need. House rule: a gap is
# named, never approximated.
#
#   Slither (Wood Carvings) -- "randomises this card's cost when drawn".
#       Needs a per-DRAW hook on the card instance; `state.draw` has no
#       per-card callback and cost is read at play time from `card_cost`,
#       so this is new machinery rather than a rider. Wood Carvings is
#       blocked on two further things anyway (Peck and Toric Toughness are
#       named base-game colorless cards the mod's pools do not contain), so
#       it stays in the skip list rather than shipping two of three options.
UNEXPRESSED = {
    "slither": "randomises cost on DRAW -- no per-draw card hook exists",
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
