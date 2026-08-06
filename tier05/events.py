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

from tier0 import constants as C
from tier0.content import loader, upgrades
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
    # objects
    "relic", "relic_id", "potion", "spend_potion",
    # gating / structure
    "requires_gold", "escalate",
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


def pool_for(act: int) -> list[dict]:
    """Events reachable in this act: its own, the all-acts set, and anything
    from another act that declares this one in `also_acts` -- minus the hidden
    escalation stages (reachable only by `escalate`).

    `also_acts` exists because several real events span acts without being
    all-acts events (Brain Leech and Room Full of Cheese are Overgrowth +
    Underdocks + Hive; Symbiote and Ranwid are Hive + Glory). Filing those
    under `all` would leak them into acts the wiki says they never appear in,
    and duplicating the entry would let the two copies drift. Acts are 1-BASED
    here, matching the section names.
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


def roll_event(rng: random.Random, act: int, seen: set[str]) -> dict | None:
    """Draw an unseen event for this act; None once the pool is exhausted
    (the real game does not repeat an event within a run either)."""
    choices = [e for e in pool_for(act) if e["id"] not in seen]
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
    potions: list[str] = field(default_factory=list)
    potion_slots: int = 0
    relics_granted: list[str] = field(default_factory=list)
    log: list[dict] = field(default_factory=list)


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


def option_value(opt: dict, st: EventState, _depth: int = 0) -> float:
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
    if opt.get("add_card"):
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
    v += 2.0 * opt.get("transform", 0)       # a coin flip on a card, not a gain
    v += CURSE_HP if opt.get("curse") else 0.0
    v += RELIC_HP * int(opt.get("relic") or 0)      # `relic: true` -> 1
    v += RELIC_HP if opt.get("relic_id") else 0.0
    v += POTION_HP * opt.get("potion", 0)
    if opt.get("spend_potion"):
        v -= POTION_HP
    nxt = opt.get("escalate")
    if nxt and _depth < _LOOKAHEAD_DEPTH:
        stages = options_of(get_event(nxt))
        v += max(option_value(o, st, _depth + 1) for o in stages)
    return v


def available(event: dict, st: EventState) -> list[dict]:
    out = []
    for opt in event["options"]:
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


def choose(rng: random.Random, event: dict, st: EventState) -> dict | None:
    """Greedy on `option_value`, then on card fit, ties by declaration order.
    None if the event left nothing legal (possible on a nearly-dead run)."""
    opts = available(event, st)
    if not opts:
        return None
    return max(opts, key=lambda o: (option_value(o, st), _fit(o, st),
                                    -event["options"].index(o)))


# ---------------------------------------------------------------------------
# Resolution.
# ---------------------------------------------------------------------------

def _worst_cards(st: EventState, n: int) -> list[str]:
    """The n cards the DRAFTER would least want, curses first. Reuses the
    draft valuation so removal policy and draft policy cannot disagree."""
    cards = [loader.peek_card(cid) for cid in st.deck_ids]
    scored = []
    for i, c in enumerate(cards):
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
            held=None, bag=None, policy=None) -> None:
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
        st.deck_ids.extend(list(st.deck_ids))
    for cid in _worst_cards(st, opt.get("remove", 0)):
        st.deck_ids.remove(cid)
    for _ in range(opt.get("remove_random", 0)):
        if st.deck_ids:
            st.deck_ids.pop(rng.randrange(len(st.deck_ids)))
    if opt.get("transform"):
        # Remove the drafter's worst, add a random pool card of that rarity.
        for cid in _worst_cards(st, opt["transform"]):
            rarity = loader.peek_card(cid).rarity
            st.deck_ids.remove(cid)
            same = rewards.character_pool(st.character).get(rarity) \
                or [c for cs in rewards.character_pool(st.character).values()
                    for c in cs]
            if same:
                st.deck_ids.append(same[rng.randrange(len(same))].id)
    if opt.get("curse"):
        st.deck_ids.append(opt["curse"])
    if opt.get("add_card"):
        st.deck_ids.append(opt["add_card"])
    if opt.get("random_card"):
        spec = opt["random_card"]
        pool = _filtered_pool(st, spec)
        for _ in range(spec.get("n", 1)):
            if pool:
                st.deck_ids.append(pool[rng.randrange(len(pool))].id)

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
        on_plan = [c for c in cards if upgrades.has_upgrade(c.id)
                   and st.archetype in c.archetypes]
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

    if opt.get("pick_cards"):
        spec = opt["pick_cards"]
        offers = _random_pool_cards(rng, st, spec["of"])
        deck = [loader.peek_card(cid) for cid in st.deck_ids]
        for _ in range(spec["take"]):
            if not offers:
                break
            pick = (policy or draft.assigned_policy)(
                rng, deck, offers, st.archetype) or offers[0]
            st.deck_ids.append(pick.id)
            offers.remove(pick)
    # `card_reward: N` is one screen of N offers; `card_screens: N` is N
    # INDEPENDENT screens ("Gain 2 card rewards"), each the standard width.
    screens = ([opt["card_reward"]] if opt.get("card_reward") else [])
    screens += [C.REWARD_CARD_OFFERS] * opt.get("card_screens", 0)
    for width in screens:
        offers = _random_pool_cards(rng, st, width)
        if opt.get("upgraded"):
            offers = [loader.peek_card(c.id + upgrades.SUFFIX)
                      if upgrades.has_upgrade(c.id) else c for c in offers]
        deck = [loader.peek_card(cid) for cid in st.deck_ids]
        pick = (policy or draft.assigned_policy)(
            rng, deck, offers, st.archetype)
        if pick is not None:
            st.deck_ids.append(pick.id)

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
        st.hp = min(st.max_hp,
                    st.hp + round(opt["heal_frac"] * (st.max_hp - st.hp)))

    st.log.append(entry)


def visit(rng: random.Random, act: int, st: EventState, seen: set[str],
          held=None, bag=None, policy=None) -> None:
    """One Unknown-room-turned-event, escalation ladders included."""
    event = roll_event(rng, act, seen)
    if event is None:
        return
    while True:
        seen.add(event["id"])
        event = materialize(rng, event)
        opt = choose(rng, event, st)
        if opt is None:
            return
        resolve(rng, event, opt, st, held=held, bag=bag, policy=policy)
        nxt = opt.get("escalate")
        if not nxt or st.hp <= 0:
            return
        event = get_event(nxt)
