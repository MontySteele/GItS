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


@lru_cache(maxsize=1)
def _pool() -> dict:
    return yaml.safe_load(_POOL_PATH.read_text()) or {}


def _act_key(act: int) -> str:
    return f"act{act + 1}"


def pool_for(act: int) -> list[dict]:
    """Events reachable in this act: its own plus the all-acts set, minus the
    hidden escalation stages (reachable only by `escalate`)."""
    raw = _pool()
    out = [e for e in (raw.get(_act_key(act)) or []) if not e.get("hidden")]
    out += [e for e in (raw.get("all") or []) if not e.get("hidden")]
    return out


def get_event(event_id: str) -> dict:
    for section in _pool().values():
        for e in section:
            if e["id"] == event_id:
                return e
    raise ValueError(f"unknown event {event_id!r}")


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

GOLD_PER_HP = 4.0      # a shop card is 60 gold; ~15 HP of value. OPEN NUMBER.
CARD_HP = 8.0          # one drafted card
REMOVE_HP = 6.0        # deck-thinning is real but smaller than a good add
UPGRADE_HP = 5.0
RELIC_HP = 20.0        # relics are the reason to fight elites
POTION_HP = 6.0
CURSE_HP = -14.0       # a permanent dead card; deliberately painful


def option_value(opt: dict, st: EventState) -> float:
    """What this option is worth, in HP. Positive is good."""
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
    if opt.get("pick_cards"):
        v += CARD_HP * opt["pick_cards"]["take"]
    v += REMOVE_HP * (opt.get("remove", 0) + opt.get("remove_random", 0) * 0.5)
    v += UPGRADE_HP * (opt.get("upgrade", 0) + opt.get("upgrade_random", 0) * 0.7)
    v += 2.0 * opt.get("transform", 0)       # a coin flip on a card, not a gain
    v += CURSE_HP if opt.get("curse") else 0.0
    v += RELIC_HP if opt.get("relic") else 0.0
    v += POTION_HP * opt.get("potion", 0)
    if opt.get("spend_potion"):
        v -= POTION_HP
    return v


def available(event: dict, st: EventState) -> list[dict]:
    out = []
    for opt in event["options"]:
        if opt.get("requires_gold", 0) > st.gold:
            continue
        if opt.get("spend_potion") and not st.potions:
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


def choose(rng: random.Random, event: dict, st: EventState) -> dict | None:
    """Greedy on `option_value`, ties by declaration order. None if the event
    left nothing legal (possible on a nearly-dead run)."""
    opts = available(event, st)
    if not opts:
        return None
    return max(opts, key=lambda o: (option_value(o, st),
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
        st.potions.pop(rng.randrange(len(st.potions)))

    # --- deck ---
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
    if opt.get("card_reward"):
        offers = _random_pool_cards(rng, st, opt["card_reward"])
        if opt.get("upgraded"):
            offers = [loader.peek_card(c.id + upgrades.SUFFIX)
                      if upgrades.has_upgrade(c.id) else c for c in offers]
        deck = [loader.peek_card(cid) for cid in st.deck_ids]
        pick = (policy or draft.assigned_policy)(
            rng, deck, offers, st.archetype)
        if pick is not None:
            st.deck_ids.append(pick.id)

    # --- grants ---
    if opt.get("relic") and held is not None:
        from tier05 import relics as relic_pool
        rid = relic_pool.roll_relic_reward(rng, held, st.character)
        if rid is not None:
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
        opt = choose(rng, event, st)
        if opt is None:
            return
        resolve(rng, event, opt, st, held=held, bag=bag, policy=policy)
        nxt = opt.get("escalate")
        if not nxt or st.hp <= 0:
            return
        event = get_event(nxt)
