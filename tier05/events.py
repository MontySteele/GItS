"""Event rooms (§11): the pool, the option policy, and the resolver.

An Unknown room resolves to an event 55% of the time (maps.resolve_unknown),
so this is the single biggest new source of run variance -- and the reason the
map pass cannot ship without it. Content and the curation rule live in
`content/events.yaml`; this module is only the grammar's interpreter plus the
policy that chooses an option.

THE POLICY IS A CONFOUNDER, same as the drafter and the router. An event
policy that is unusually good at valuing "lose 18 HP for 150 gold" moves every
run number. It is deliberately simple and explicit here -- one valuation
function, in HP-equivalent units, that anyone can read and disagree with --
rather than tuned, and `run_metrics` reports the option split so a policy that
always takes the same side is visible rather than invisible.

Everything mutates a small dataclass rather than the run's locals, so the
resolver stays pure enough to unit-test without building a whole run.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from tier0 import constants as C, roster
from tier0.content import enchantments, loader, upgrades
from tier05 import draft, potions as potion_pool, rewards

_POOL_PATH = Path(__file__).parent / "content" / "events.yaml"


# --- content-boundary allowlists (audit sec.5) -----------------------------
# This file and the act pools are the two largest content files in the repo and
# were the two that read every key through `.get()`. The two SMALLEST (potions,
# relics) validate loudly -- the inversion the audit names. A typo'd key here
# does not fail: it silently does nothing, so `is_bos: true` makes a non-boss
# boss and a misspelled `heal_frac` makes a heal option worth zero, both with
# every gate green.
#
# Same shape as tier05/potions.py's engine-vocabulary guard: the allowlist is
# the grammar this file's own header documents, and anything outside it is a
# loud error at load rather than a silent no-op at play.
#
# The rule for extending these: adding a key to the grammar means adding it
# BOTH to the reader and to the set below. That is the point -- a key nothing
# reads is exactly the defect being caught.
EVENT_KEYS = frozenset({
    "id", "name", "options",
    "hidden",        # reachable only via `escalate`, never rolled directly
    "also_acts",     # ALSO appears in these (1-based) acts
    "variants",      # one authored event with several rolled bodies
})

OPTION_KEYS = frozenset({
    "label",
    # health / economy
    "heal", "heal_frac", "hp", "max_hp", "gold", "gold_all",
    # deck
    "card_reward", "card_screens", "pick_cards", "add_card", "random_card",
    "remove", "remove_random", "upgrade", "upgrade_random", "downgrade_random",
    "duplicate_deck", "transform", "curse", "upgraded",
    # The Dusty Tome (R127 / EB-30m): add THIS character's Ancient, upgraded.
    # A key rather than an `add_card` id because the card is per-character and
    # the option cannot name one; `roster.ANCIENTS` is the lookup. Carrying it
    # also GATES the event -- see `pool_for`.
    "add_ancient",
    # R82 reopened (2026-08-10): attach a NAMED enchantment to a card in the
    # DECK, permanently. `{name, amount}` -- see `_enchant_targets`.
    "enchant",
    # objects
    "relic", "relic_id", "potion", "spend_potion",
    # gating / structure
    "requires_gold", "escalate",
    # Self-Help Book's null branch: offered ONLY when every other option on
    # the event is locked for want of a legal enchant target. The wiki states
    # it as an availability rule on the option, so it is one here too.
    "if_no_enchant_target",
})


def _validate_pool(raw: dict) -> dict:
    for act_key, events in (raw or {}).items():
        for event in events or []:
            unknown = set(event) - EVENT_KEYS
            if unknown:
                raise ValueError(
                    f"event {event.get('id', '?')!r} in {act_key!r}: unknown "
                    f"key(s) {sorted(unknown)} -- not in events.EVENT_KEYS. A "
                    "key nothing reads is a silent no-op, never a tolerance.")
            bodies = event.get("variants") or [event]
            for body in bodies:
                for opt in body.get("options") or []:
                    unknown = set(opt) - OPTION_KEYS
                    if unknown:
                        raise ValueError(
                            f"event {event.get('id', '?')!r} option "
                            f"{opt.get('label', '?')!r}: unknown key(s) "
                            f"{sorted(unknown)} -- not in events.OPTION_KEYS.")
    return raw


@lru_cache(maxsize=1)
def _pool() -> dict:
    return _validate_pool(yaml.safe_load(_POOL_PATH.read_text(encoding="utf-8")) or {})


def _act_key(act: int) -> str:
    return f"act{act + 1}"


def _needs_an_ancient(event: dict) -> bool:
    """Does any of this event's options grant the character's Ancient?

    The first CHARACTER-conditional availability in the pool. Every other
    gate in this module is per-option and lives in `available` (gold, potions,
    an empty filtered draw), because every other option is offerable to
    somebody. This one is not: `add_ancient` reads `roster.ANCIENTS`, the
    reference anchors (ref_ironclad, real_*) are not roster characters and
    have no Ancient, and an event whose payout does not exist for you must
    not consume one of the run's Unknown rooms.
    """
    return any(o.get("add_ancient") for o in options_of(event))


def pool_for(act: int, character: str | None = None) -> list[dict]:
    """Events reachable in this act: its own, the all-acts set, and anything
    from another act that declares this one in `also_acts` -- minus the hidden
    escalation stages (reachable only by `escalate`).

    `also_acts` exists because several real events span acts without being
    all-acts events (Brain Leech and Room Full of Cheese are Overgrowth +
    Underdocks + Hive; Symbiote and Ranwid are Hive + Glory). Filing those
    under `all` would leak them into acts the wiki says they never appear in,
    and duplicating the entry would let the two copies drift. Acts are 1-BASED
    here, matching the section names.

    `character` is OPTIONAL and omitting it means "every event this act can
    hold", which is what the content sweeps want. A run passes it, and gets
    the events that character can actually meet -- today that is the Ancient
    gate above and nothing else.
    """
    raw = _pool()
    want = act + 1
    out = []
    for key, section in raw.items():
        if key == "all":
            continue
        for e in section:
            if e.get("hidden"):
                continue
            if key == _act_key(act) or want in (e.get("also_acts") or ()):
                out.append(e)
    out += [e for e in (raw.get("all") or []) if not e.get("hidden")]
    if character is not None and character not in roster.ANCIENTS:
        out = [e for e in out if not _needs_an_ancient(e)]
    return out


def get_event(event_id: str) -> dict:
    for section in _pool().values():
        for e in section:
            if e["id"] == event_id:
                return e
    raise ValueError(f"unknown event {event_id!r}")


def options_of(event: dict) -> list[dict]:
    """Every option an event can present, variants flattened.

    For a plain event this is just `options`. For a VARIANT event (The Trial)
    it is the union across variants -- correct for valuation and validation,
    but never for play: `materialize` picks the one variant a visit sees.
    """
    if "variants" in event:
        return [o for v in event["variants"] for o in v["options"]]
    return event["options"]


def materialize(rng: random.Random, event: dict) -> dict:
    """Collapse a variant event down to the single variant this visit rolls.

    The Trial is one event that randomly selects one of three sub-trials, each
    with its own two verdicts. Modeling the three as three separate events
    would be wrong twice over: a run could meet all three, and each would
    consume its own Unknown room. So the roll happens here, inside the visit,
    and the returned dict is an ordinary event as far as every other function
    is concerned.
    """
    if "variants" not in event:
        return event
    v = event["variants"][rng.randrange(len(event["variants"]))]
    return {**event, "options": v["options"],
            "id": event["id"], "variant": v.get("name", "?")}


def roll_event(rng: random.Random, act: int, seen: set[str],
               character: str | None = None) -> dict | None:
    """Draw an unseen event for this act; None once the pool is exhausted
    (the real game does not repeat an event within a run either).

    `character` is forwarded to `pool_for`, so an event this character cannot
    meet is never rolled and never lands in `seen`."""
    choices = [e for e in pool_for(act, character) if e["id"] not in seen]
    if not choices:
        return None
    return choices[rng.randrange(len(choices))]


# ---------------------------------------------------------------------------
# Run state the resolver is allowed to touch.
# ---------------------------------------------------------------------------

@dataclass
class EventState:
    character: str
    archetype: str          # the plan to draft/remove/upgrade TOWARD. For an
    #                         adaptive run this is the deck's EMERGENT shape,
    #                         never the assigned label -- same contract as
    #                         rest-site smithing and shop buying. Passing the
    #                         label here would reintroduce exactly the leak
    #                         test_m7 pins.
    hp: int
    max_hp: int
    gold: int
    deck_ids: list[str]
    # `potions` is a SNAPSHOT of the bag, for options that read or spend one.
    # There is deliberately no `potion_slots` mirror: capacity questions go to
    # the real PotionBag handed to `resolve` as `bag`, which derives its slot
    # count on read. A snapshotted count was write-only here and could only
    # ever be a second, staler answer to what the bag already answers.
    potions: list[str] = field(default_factory=list)
    relics_granted: list[str] = field(default_factory=list)
    log: list[dict] = field(default_factory=list)
    # EB-111: how many cards this visit ADDED to the deck. The run layer
    # hands the total to `HeldRelics.note_cards_added` so Book of Five Rings
    # ticks on event adds, which it never did. Counted at each add site
    # rather than diffed off `len(deck_ids)`, because a net diff undercounts
    # an option that removes N and adds M -- the game counts M.
    cards_added: int = 0

    def note_add(self, n: int = 1) -> None:
        """One door for every event site that puts a card into the deck."""
        if n > 0:
            self.cards_added += n


# ---------------------------------------------------------------------------
# Option valuation. HP-EQUIVALENT units throughout, so the tradeoffs the
# events are actually made of ("18 HP for 150 gold") are comparable at all.
# ---------------------------------------------------------------------------

# GOLD_PER_HP is DERIVED, not chosen. The shop is the game's own published
# exchange rate, and two of its three prices agree exactly:
#     SHOP_CARD_PRICE  60 / CARD_HP  8  = 7.5
#     SHOP_RELIC_PRICE 150 / RELIC_HP 20 = 7.5
# (SHOP_REMOVAL_PRICE 75 / REMOVE_HP 6 implies 12.5 -- recorded, not averaged
# in: 75 is a BASE that rises 25 per use, so it is not a clean read.)
# This shipped at 4.0 with a comment deriving it from "a shop card is 60 gold;
# ~15 HP of value" -- a card worth 15 HP, which contradicts CARD_HP = 8.0 four
# lines below it. Gold was therefore worth roughly double what the same file
# said it was, and every "pay HP for gold" option in the pool was mispriced in
# the same direction. Corrected to the derivation, not to a target.
GOLD_PER_HP = 7.5
CARD_HP = 8.0          # one drafted card
RANDOM_CARD_HP = 5.0   # a FORCED random card: same body, none of the choice
REMOVE_HP = 6.0        # deck-thinning is real but smaller than a good add
UPGRADE_HP = 5.0
RELIC_HP = 20.0        # relics are the reason to fight elites
POTION_HP = 6.0
CURSE_HP = -14.0       # a permanent dead card; deliberately painful

_LOOKAHEAD_DEPTH = 8   # ladders are 4 deep; this is a cycle guard, not a tune

# Rarities a `transform:` option may not consume. Deliberately narrower than
# C.ACQUISITION_ONLY_RARITIES: a curse or a basic really is transformable in
# the real game, and only Ancient is filtered out of transform generation on
# the C# side. See the citation at the transform branch.
_NEVER_TRANSFORMED = frozenset({"ancient"})


def _filtered_pool(st: EventState, spec: dict) -> list:
    """Character pool cards matching a `random_card` filter (type and/or
    cost). Empty is a real answer -- `available` drops the option."""
    pool = rewards.character_pool(st.character)
    out = [c for cs in pool.values() for c in cs]
    if "type" in spec:
        out = [c for c in out if c.type == spec["type"]]
    if "cost" in spec:
        out = [c for c in out if c.cost == spec["cost"]]
    return out


ENCHANT_HP = UPGRADE_HP    # see _enchant_targets' docstring for why


def _enchant_targets(opt: dict, st: EventState) -> list[int]:
    """Deck INDICES this option's enchantment may legally land on.

    The selection rule is the enchantment's own eligibility (Sharp wants an
    Attack, Soul's Power wants a card that Exhausts, Sown wants anything)
    plus the base game's two universal rules: a card holds exactly one
    enchantment and it can never be replaced, and curses/statuses/kit cards
    are not enchantable at all. Both live in `content/enchantments.eligible`
    / `.decorate` so this function cannot drift from the tier-0 side.

    EMPTY IS A REAL ANSWER, and it is the reason this returns indices rather
    than a bool: `available` drops an option with no legal target, which is
    the lock the wiki states verbatim on Grave of the Forgotten, Wood
    Carvings and every branch of Self-Help Book.

    On VALUATION, which is `ENCHANT_HP` above: an enchantment is priced at
    exactly one upgrade. That is a statement, not a tune. The valuation
    already refuses to tell one NAMED card from another (`add_card` rides a
    flat CARD_HP -- see the Bugslayer note in events.yaml), and pricing
    Vigorous 8 above Nimble 2 here would be inventing a per-enchantment
    number with no measurement behind it. An enchantment is the same SHAPE
    as an upgrade -- a permanent buff to one card the player picks -- so it
    carries the same price and no free parameter enters the policy.
    """
    spec = opt["enchant"]
    name = spec["name"]
    out = []
    for i, cid in enumerate(st.deck_ids):
        if enchantments.enchantment_of(cid) is not None:
            continue
        if enchantments.eligible(loader.peek_card(cid), name):
            out.append(i)
    return out


def _adds_of(opt: dict, st: EventState) -> int:
    """How many cards this option would put INTO THE DECK.

    The forecast half of `EventState.note_add`: every site `resolve` ticks
    the door at has a line here and no site has two. Written against the same
    option keys the valuation below already reads, so a key that gains a
    value term and forgets its add count is visible as a diff of one function
    against its neighbour rather than as a silent under-credit.

    It is an UPPER BOUND in exactly one place, and only for one reason: a
    card screen adds nothing when the drafter skips every offer
    (`DRAFT_SKIP_THRESHOLD`). Every other site is exact -- the emptiness
    cases that make an add fail (`random_card` with no legal pool,
    `pick_cards` with a short offer list, a `transform` with no legal victim)
    are counted here the same way `resolve` counts them.
    """
    n = 0
    if opt.get("duplicate_deck"):
        n += len(st.deck_ids)
    if opt.get("transform"):
        # `_worst_cards` picks victims from the non-excluded deck, so the
        # count of legal victims is the count of replacements that arrive.
        legal = sum(1 for cid in st.deck_ids
                    if loader.peek_card(cid).rarity not in _NEVER_TRANSFORMED)
        n += min(opt["transform"], legal)
    n += 1 if opt.get("curse") else 0
    n += 1 if opt.get("add_card") else 0
    n += 1 if opt.get("add_ancient") else 0
    if opt.get("random_card"):
        spec = opt["random_card"]
        if _filtered_pool(st, spec):
            n += spec.get("n", 1)
    if opt.get("pick_cards"):
        spec = opt["pick_cards"]
        pool = rewards.character_pool(st.character)
        if any(cs for cs in pool.values()):
            n += min(spec["take"], spec["of"])
    n += 1 if opt.get("card_reward") else 0
    n += opt.get("card_screens", 0)
    return n


def _book_credit(opt: dict, st: EventState, held) -> float:
    """HP this option is worth THROUGH Book of Five Rings (EB-129 / R205).

    The relic pays 20 HP every fifth card that enters the master deck, and
    `EB-111` made event adds count toward that -- but only on the paying
    side. The pilot still scored the fifth card exactly like the first, so a
    run holding the Book at 4-of-5 could walk past a free card and take the
    other branch. This is the seeing side.

    THE VALUE IS THE REALIZED HEAL, CLIPPED TO MISSING HP, and both halves
    are the ruling's:

      * realized -- the chunk arithmetic is not re-derived here. `held`
        is asked (`book_heal_for`), so a batch that crosses no boundary is
        worth nothing and a batch that crosses two is worth two heals.
        `st.cards_added` is added in because the ledger is in two pieces
        mid-visit: the run layer hands the visit's tally to
        `note_cards_added` only when the visit ENDS, so an earlier rung of
        an escalation ladder has already moved the pending count without
        `held` knowing it yet.
      * clipped -- a heal cannot restore HP that is not missing. Without the
        clip a full-HP run would pay real costs for a heal it cannot bank.

    NO NEW WEIGHT ENTERS, and none is owed: option value is already
    HP-denominated, so the relic's own printed 20 is the price.

    Its one honest approximation is the same one every term here makes: the
    missing HP is read BEFORE this option's own HP moves, so an option that
    also costs HP is credited slightly low and one that also heals slightly
    high. `resolve` applies costs first and heals last, and reproducing that
    order here would be a second copy of it.
    """
    if held is None:
        return 0.0
    adds = _adds_of(opt, st)
    if adds <= 0:
        return 0.0
    pending = st.cards_added
    raw = held.book_heal_for(pending + adds) - held.book_heal_for(pending)
    if raw <= 0:
        return 0.0
    return float(min(raw, max(0, st.max_hp - st.hp)))


def option_value(opt: dict, st: EventState, _depth: int = 0,
                 held=None) -> float:
    """What this option is worth, in HP. Positive is good.

    ESCALATION IS VALUED THROUGH, not at face value. An option that only opens
    the next rung of a ladder (Colossal Flower's "Reach Deeper": lose 5 HP,
    gain nothing) scores as a pure cost in isolation, so a myopic policy never
    climbs and the whole ladder is dead content the run can never reach. The
    value of continuing is therefore the immediate effect PLUS the best
    reachable value of the next stage -- which is what a player who can read
    the next screen actually computes, and it has no free parameter to tune.
    Tablet of Truth had the same latent bug: with lookahead it climbs one rung
    and stops, which is where the max-HP price overtakes the upgrade.

    `held` is the run's relic holder, or None for a bare run and for every
    caller that only wants the content's own value. It is read by exactly one
    term -- `_book_credit` -- and a run without the Book scores identically
    whether it is passed or not.
    """
    v = 0.0
    v += opt.get("hp", 0)
    v += opt.get("heal", 0) if st.hp < st.max_hp else 0.0
    if opt.get("heal_frac"):
        v += opt["heal_frac"] * (st.max_hp - st.hp)
    v += opt.get("max_hp", 0) * 1.2          # max HP outlives the heal
    if opt.get("gold"):
        lo, hi = opt["gold"]
        v += ((lo + hi) / 2) / GOLD_PER_HP
    if opt.get("gold_all"):
        v -= st.gold / GOLD_PER_HP
    v += CARD_HP * opt.get("card_reward", 0) / 3.0
    v += CARD_HP * opt.get("card_screens", 0)
    if opt.get("pick_cards"):
        v += CARD_HP * opt["pick_cards"]["take"]
    if opt.get("add_card") or opt.get("add_ancient"):
        # The Ancient rides `add_card`'s flat CARD_HP rather than getting a
        # rarity premium. Same known limitation the Bugslayer comment names
        # (events.yaml): the valuation cannot tell one named card from
        # another, and inventing a number for "an upgraded Ancient" here
        # would be a tuning decision wearing a pricing function's clothes.
        # It does not change the pick -- the Tome's other option is a
        # walk-away worth 0 -- but it is stated rather than assumed.
        v += CARD_HP
    if opt.get("random_card"):
        v += RANDOM_CARD_HP * opt["random_card"].get("n", 1)
    if opt.get("duplicate_deck"):
        # Doubling the deck is not doubling its power: every good card is
        # matched by a copy of every bad one, and the draw is diluted. Valued
        # as the copies of the cards the drafter would have KEPT, minus the
        # dilution -- i.e. a wash on average, which is why the curse attached
        # to it decides the option. Deliberately NOT a tuned number.
        v += 0.0
    v += REMOVE_HP * (opt.get("remove", 0) + opt.get("remove_random", 0) * 0.5)
    v += UPGRADE_HP * (opt.get("upgrade", 0) + opt.get("upgrade_random", 0) * 0.7)
    v -= UPGRADE_HP * opt.get("downgrade_random", 0) * 0.7
    if opt.get("enchant"):
        v += ENCHANT_HP
    v += 2.0 * opt.get("transform", 0)       # a coin flip on a card, not a gain
    v += CURSE_HP if opt.get("curse") else 0.0
    v += RELIC_HP * int(opt.get("relic") or 0)      # `relic: true` -> 1
    v += RELIC_HP if opt.get("relic_id") else 0.0
    v += POTION_HP * opt.get("potion", 0)
    if opt.get("spend_potion"):
        v -= POTION_HP
    # EB-129 (R205): the cards this option adds are ALSO worth whatever Book
    # of Five Rings pays for crossing its next chunk boundary. Beside the
    # other HP terms because it IS one -- see `_book_credit`.
    v += _book_credit(opt, st, held)
    nxt = opt.get("escalate")
    if nxt and _depth < _LOOKAHEAD_DEPTH:
        stages = options_of(get_event(nxt))
        # The next rung is valued against the ledger as it stands NOW: the
        # lookahead has never applied this stage's effects before valuing the
        # one after it (the deck, HP and gold it reads are this stage's too),
        # and the Book credit inherits that limit rather than inventing a
        # second, half-applied state to read.
        v += max(option_value(o, st, _depth + 1, held=held) for o in stages)
    return v


def available(event: dict, st: EventState) -> list[dict]:
    # Self-Help Book's null branch is offered ONLY when nothing else is:
    # "Move On is only available if you have no valid cards". Computed once
    # over the whole event rather than per option, because that is what the
    # rule is about -- the state of the OFFER, not of this option.
    any_target = any(_enchant_targets(o, st)
                     for o in event["options"] if o.get("enchant"))
    out = []
    for opt in event["options"]:
        if opt.get("if_no_enchant_target") and any_target:
            continue
        if opt.get("enchant") and not _enchant_targets(opt, st):
            continue
        if opt.get("requires_gold", 0) > st.gold:
            continue
        if opt.get("spend_potion") and not st.potions:
            continue
        # A filtered draw with nothing to draw is not an option. The real game
        # locks these too ("only available if you have a valid card").
        if opt.get("random_card") and not _filtered_pool(st, opt["random_card"]):
            continue
        # A lethal option stays legal in the real game; ours refuses, because
        # nothing in the run model can survive it (no Lizard Tail) and a
        # policy that suicides is noise, not agency.
        if st.hp + min(0, opt.get("hp", 0)) <= 0:
            continue
        if st.max_hp + min(0, opt.get("max_hp", 0)) <= 0:
            continue
        out.append(opt)
    return out


def _fit(opt: dict, st: EventState) -> float:
    """Drafter's opinion of a NAMED card an option adds. Used only to break
    ties between options the HP valuation cannot separate (Bugslayer offers
    two colorless cards, so both score a flat CARD_HP). Not a second currency:
    it never outranks `option_value`."""
    cid = opt.get("add_card")
    if not cid:
        return 0.0
    deck = [loader.peek_card(c) for c in st.deck_ids]
    return draft.score_offer(loader.peek_card(cid), deck, st.archetype)


def choose(rng: random.Random, event: dict, st: EventState,
           held=None) -> dict | None:
    """Greedy on `option_value`, then on card fit, ties by declaration order.
    None if the event left nothing legal (possible on a nearly-dead run).

    `held` is forwarded to the valuation and nothing else; a bare run passes
    None and picks exactly as it always did.
    """
    opts = available(event, st)
    if not opts:
        return None
    return max(opts, key=lambda o: (option_value(o, st, held=held),
                                    _fit(o, st),
                                    -event["options"].index(o)))


# ---------------------------------------------------------------------------
# Resolution.
# ---------------------------------------------------------------------------

def _worst_cards(st: EventState, n: int,
                 exclude_rarities: frozenset[str] = frozenset()) -> list[str]:
    """The n cards the DRAFTER would least want, curses first. Reuses the
    draft valuation so removal policy and draft policy cannot disagree.

    `exclude_rarities` holds cards out of the CANDIDATE set entirely rather
    than down-ranking them, so an excluded card can never be picked however
    badly it scores. Only the transform branch passes it -- removal has no
    such exclusion, because giving an Ancient up is a real choice.
    """
    cards = [loader.peek_card(cid) for cid in st.deck_ids]
    scored = []
    for i, c in enumerate(cards):
        if c.rarity in exclude_rarities:
            continue
        if c.rarity == "curse":
            scored.append((-1000.0, i, c.id))
            continue
        scored.append((draft.score_offer(c, cards, st.archetype), i, c.id))
    scored.sort()
    return [cid for _, _, cid in scored[:n]]


def _random_pool_cards(rng: random.Random, st: EventState, n: int) -> list:
    pool = rewards.character_pool(st.character)
    flat = [c for cs in pool.values() for c in cs]
    if not flat:
        return []
    return [flat[rng.randrange(len(flat))] for _ in range(n)]


def resolve(rng: random.Random, event: dict, opt: dict, st: EventState,
            held=None, bag=None, policy=None, policy_rng=None) -> None:
    """Apply one option. Mutates `st` (and `held`/`bag` when relics/potions
    are granted). Order is fixed so a seed replays: costs, then gains."""
    entry = {"event": event["id"], "option": opt.get("label", "?")}
    if event.get("variant"):
        entry["variant"] = event["variant"]

    # --- costs ---
    if opt.get("hp"):
        st.hp = max(0, st.hp + opt["hp"])
    if opt.get("max_hp"):
        st.max_hp = max(1, st.max_hp + opt["max_hp"])
        st.hp = min(st.hp, st.max_hp)
    if opt.get("gold_all"):
        st.gold = 0
    if opt.get("gold"):
        lo, hi = opt["gold"]
        st.gold = max(0, st.gold + rng.randint(min(lo, hi), max(lo, hi)))
    if opt.get("spend_potion") and st.potions:
        # NC-8 (R116, Errata Batch 2 item 2): the potion is ACTUALLY consumed.
        # `st.potions` is a snapshot -- `model.py` builds EventState with
        # `list(bag.potions)` because the event layer is pure over the run's
        # holdings -- so popping it alone spent nothing: "The Future of
        # Potions?" granted its reward AND left the potion in the bag. The
        # snapshot is still popped (it is what the rest of this resolve and
        # the next option read), and the same potion now leaves the real bag.
        spent = st.potions.pop(rng.randrange(len(st.potions)))
        if bag is not None and spent in bag.potions:
            bag.potions.remove(spent)

    # --- deck ---
    # BEFORE any add: "Duplicate your entire Deck. Add Bad Luck" copies the
    # deck as it stands, then hands you ONE curse, not two.
    if opt.get("duplicate_deck"):
        st.note_add(len(st.deck_ids))
        st.deck_ids.extend(list(st.deck_ids))
    for cid in _worst_cards(st, opt.get("remove", 0)):
        st.deck_ids.remove(cid)
    for _ in range(opt.get("remove_random", 0)):
        if st.deck_ids:
            st.deck_ids.pop(rng.randrange(len(st.deck_ids)))
    if opt.get("transform"):
        # Remove the drafter's worst, add a random pool card of that rarity.
        #
        # ANCIENTS ARE NEVER TRANSFORMED (R127 / EB-30m), mirroring the
        # decompiled CardFactory, where transform generation filters
        # CardRarity.Ancient out upstream exactly as reward and shop
        # generation do. Without the exclusion this is a one-way leak: an
        # Ancient's rarity has no row in `rewards.character_pool`, so the
        # `.get(rarity) or <whole pool>` fallback below would take the run's
        # single once-per-run card and hand back a random draftable common.
        for cid in _worst_cards(st, opt["transform"], _NEVER_TRANSFORMED):
            rarity = loader.peek_card(cid).rarity
            st.deck_ids.remove(cid)
            same = rewards.character_pool(st.character).get(rarity) \
                or [c for cs in rewards.character_pool(st.character).values()
                    for c in cs]
            if same:
                st.deck_ids.append(same[rng.randrange(len(same))].id)
                st.note_add()
    if opt.get("curse"):
        st.deck_ids.append(opt["curse"])
        st.note_add()
    if opt.get("add_card"):
        st.deck_ids.append(opt["add_card"])
        st.note_add()
    if opt.get("add_ancient"):
        # The Dusty Tome grants the card ALREADY UPGRADED (C#
        # DustyTome.AfterObtained), which is why ANCIENT_WITNESS pins these
        # three at their upgraded numbers.
        try:
            ancient = roster.ANCIENTS[st.character]
        except KeyError:
            # Unreachable through `visit`: `pool_for` hides an add_ancient
            # event from a character with no entry. Loud rather than a
            # silent no-grant, because reaching it means that gate was
            # bypassed and the run would otherwise carry on looking fine.
            raise KeyError(
                f"{st.character!r} has no Ancient card, so the Dusty Tome "
                "has nothing to grant. Registered: "
                f"{', '.join(roster.ANCIENTS)}. Adding one means a row in "
                "tier0/roster.ANCIENTS and a card in "
                "tier0/content/cards/ancients.yaml (EB-30m / R127)."
            ) from None
        st.deck_ids.append(ancient + upgrades.SUFFIX)
        st.note_add()
    if opt.get("random_card"):
        spec = opt["random_card"]
        pool = _filtered_pool(st, spec)
        for _ in range(spec.get("n", 1)):
            if pool:
                st.deck_ids.append(pool[rng.randrange(len(pool))].id)
                st.note_add()

    # Downgrades resolve BEFORE upgrades, the order Reflections states them
    # in -- so a card knocked down here can be picked back up by the upgrade
    # that follows, which is the real event's behaviour.
    for _ in range(opt.get("downgrade_random", 0)):
        cand = [i for i, cid in enumerate(st.deck_ids)
                if cid.endswith(upgrades.SUFFIX)]
        if cand:
            i = cand[rng.randrange(len(cand))]
            st.deck_ids[i] = st.deck_ids[i][:-len(upgrades.SUFFIX)]

    n_up = opt.get("upgrade", 0)
    if n_up:
        cards = [loader.peek_card(cid) for cid in st.deck_ids]
        # R125: behavioural tag read -- same widened shield as the smith.
        on_plan = [c for c in cards if upgrades.has_upgrade(c.id)
                   and st.archetype in draft.behavioural_archetypes(c)]
        rest = [c for c in cards if upgrades.has_upgrade(c.id)
                and c not in on_plan]
        for c in (on_plan + rest)[:n_up]:
            st.deck_ids[st.deck_ids.index(c.id)] = c.id + upgrades.SUFFIX
    for _ in range(opt.get("upgrade_random", 0)):
        cand = [i for i, cid in enumerate(st.deck_ids)
                if upgrades.has_upgrade(cid)]
        if cand:
            i = cand[rng.randrange(len(cand))]
            st.deck_ids[i] = st.deck_ids[i] + upgrades.SUFFIX

    # R82 reopened: attach a named enchantment to ONE deck card, for the rest
    # of the run. The attachment is a decoration on the deck-list id
    # (`<id>@<name>-<amount>`), so it survives every later deck operation and
    # every fight for free -- the run layer rebuilds the player from
    # `deck_ids` each combat, and `loader` resolves the mark.
    #
    # THE SELECTION RULE IS THE PLAYER'S, and the events state it as "choose
    # a card": the pick is the drafter's HIGHEST-valued legal target, the
    # mirror image of `_worst_cards`, so enchant policy and draft policy
    # cannot disagree any more than removal policy can. Ties break to the
    # earliest deck slot, which is the declaration-order rule `choose` uses.
    if opt.get("enchant"):
        idxs = _enchant_targets(opt, st)
        if idxs:
            cards = [loader.peek_card(cid) for cid in st.deck_ids]
            best = max(idxs, key=lambda i: (
                draft.score_offer(cards[i], cards, st.archetype), -i))
            st.deck_ids[best] = enchantments.decorate(
                st.deck_ids[best], opt["enchant"]["name"],
                opt["enchant"].get("amount"))
            entry["enchanted"] = st.deck_ids[best]

    if opt.get("pick_cards"):
        spec = opt["pick_cards"]
        offers = _random_pool_cards(rng, st, spec["of"])
        deck = [loader.peek_card(cid) for cid in st.deck_ids]
        for _ in range(spec["take"]):
            if not offers:
                break
            pick = (policy or draft.assigned_policy)(
                policy_rng or rng, deck, offers, st.archetype) or offers[0]
            st.deck_ids.append(pick.id)
            st.note_add()
            offers.remove(pick)
    # `card_reward: N` is one screen of N offers; `card_screens: N` is N
    # INDEPENDENT screens ("Gain 2 card rewards"), each the standard width.
    screens = ([opt["card_reward"]] if opt.get("card_reward") else [])
    screens += [C.REWARD_CARD_OFFERS] * opt.get("card_screens", 0)
    for width in screens:
        # EB-112: a card screen is a REWARD SCREEN -- the rarity is rolled
        # per offer through C.RARITY_ODDS (60/35/5) and only then is a card
        # picked inside that tier. These built their offers by flattening
        # the whole character pool and drawing uniformly with replacement,
        # which made Rare 14/71 = 19.7% per offer and let one screen show
        # the same card twice. `_random_pool_cards` stays for the ops that
        # genuinely declare a uniform pool draw (`pick_cards`).
        offers = rewards.roll_card_offers(rng, st.character, width,
                                          distinct=True)
        if opt.get("upgraded"):
            offers = [loader.peek_card(c.id + upgrades.SUFFIX)
                      if upgrades.has_upgrade(c.id) else c for c in offers]
        deck = [loader.peek_card(cid) for cid in st.deck_ids]
        pick = (policy or draft.assigned_policy)(
            policy_rng or rng, deck, offers, st.archetype)
        if pick is not None:
            st.deck_ids.append(pick.id)
            st.note_add()

    # --- grants ---
    from tier05 import relics as relic_pool
    if opt.get("relic") and held is not None:
        for _ in range(int(opt["relic"])):      # `relic: true` -> one roll
            rid = relic_pool.roll_relic_reward(rng, held, st.character)
            if rid is None:
                break                           # pool exhausted, grant nothing
            st.hp, st.max_hp, st.gold = held.add(
                rid, st.character, st.hp, st.max_hp, st.gold, st.deck_ids, rng)
            st.relics_granted.append(rid)
    # A NAMED event relic (§11.2). Never rolled, never substituted: an event
    # that hands out a relic we cannot express exactly is skipped instead.
    if opt.get("relic_id") and held is not None:
        rid = opt["relic_id"]
        if rid not in held.ids:
            st.hp, st.max_hp, st.gold = held.add(
                rid, st.character, st.hp, st.max_hp, st.gold, st.deck_ids, rng)
            st.relics_granted.append(rid)
    if opt.get("potion") and bag is not None:
        for _ in range(opt["potion"]):
            if not bag.full():
                bag.add(potion_pool.roll_potion(rng))

    # --- heals last: a max-HP change earlier must not clip them ---
    if opt.get("heal"):
        st.hp = min(st.max_hp, st.hp + opt["heal"])
    if opt.get("heal_frac"):
        # Fractional heals truncate, same as the rest site (EB-110).
        st.hp = min(st.max_hp,
                    st.hp + int(opt["heal_frac"] * (st.max_hp - st.hp)))

    st.log.append(entry)


def visit(rng: random.Random, act: int, st: EventState, seen: set[str],
          held=None, bag=None, policy=None, policy_rng=None) -> None:
    """One Unknown-room-turned-event, escalation ladders included."""
    event = roll_event(rng, act, seen, st.character)
    if event is None:
        return
    while True:
        seen.add(event["id"])
        event = materialize(rng, event)
        opt = choose(rng, event, st, held=held)
        if opt is None:
            return
        resolve(rng, event, opt, st, held=held, bag=bag, policy=policy,
                policy_rng=policy_rng)
        nxt = opt.get("escalate")
        if not nxt or st.hp <= 0:
            return
        event = get_event(nxt)
