"""The run model (spec §2; run-model rework §3-§5, multi-act §10): the fixed
node template ("NNNRETN$ERB" -- 11 nodes, 7 fights, 2 rests, a treasure T
and a shop $) repeated once per registered act (RUNTEMPLATE_VERSION 5), HP
persistence, rest nodes with smithing (M7), the realistic per-act rosters.

Multi-act (§10.1, RATIFIED 2026-07-23): the run walks every act registered
in constants.RUN_ACTS (or the first `n_acts` of them). A non-final boss win
triggers the act boundary: the reward screen's CARD offers are forced Rare
(§10.1's choice-of-3-Rares boss drop, v5) and the companion slot is forced
Rare too, then the Ancient heals 100% of missing HP and -- on grant_relics
runs -- offers a 1-of-3 Ancient-relic pick. Deck, gold, relics and potions
carry forward; HP resets to max.

Run-layer relics: Burning Blood (heal_after_won_fight) is applied HERE,
after each won fight (run-model rework §2) -- combat.py stays emit-only so
tier0's frozen battery and the anchor lock are untouched. Economy: a gold
field, per-fight income and a treasure lump; the shop is a stub this phase.

All randomness for a run flows through ONE random.Random seeded by the
harness (fight seeds, reward rolls, regret sampling) — determinism at
run granularity, same contract as Tier 0.
"""

from __future__ import annotations

import os
import random
import warnings
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Optional

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine.combat import run_fight
from tier0.engine.state import Card, Enemy
from tier0.harness import metrics as t0_metrics
from tier0.pilot.policy import make_pilot
from tier05 import (acts, aura_telemetry, burst_telemetry, conditional_telemetry,
                    draft, encore_telemetry, events,
                    fanfare_telemetry, kurage_telemetry, overlap_telemetry,
                    maps, potions as potion_pool, rewards, route, shop)
from tier05 import relics as relic_pool

# policy(rng, deck_cards, offers, archetype) -> Card | None
DraftPolicy = Callable[[random.Random, list[Card], list[Card], str],
                       Optional[Card]]

# Run node kind (N/E/B) -> the combat-side node_kind context the potion
# offensive use-policy reads (engine/potions.py). Only fight nodes reach the
# combat builder; "" everywhere else keeps the offensive branch dead.
_NODE_KIND_CTX = {"N": "normal", "E": "elite", "B": "boss"}


def _potion_slots(held: "Optional[relic_pool.HeldRelics]") -> int:
    """The run's held-potion capacity: the POTION_SLOTS default, plus any
    slot-bumping relic bonus (Potion Belt: +2). Recomputed at each use site so
    a Potion Belt granted MID-RUN raises the cap immediately."""
    base = C.POTION_SLOTS
    if held is not None:
        base += held.potion_slot_bonus()
    return base


def _consumed(before: list[str], after: list[str]) -> list[str]:
    """The potions used during a fight: the multiset (before - after), in the
    order they sat in `before`. Combat removes each drunk/spent potion from
    player.potions, so what's missing afterwards is exactly what was used."""
    remaining = list(after)
    used: list[str] = []
    for pid in before:
        if pid in remaining:
            remaining.remove(pid)
        else:
            used.append(pid)
    return used


def build_node_encounter(node_kind: str, rng: random.Random,
                         draw: acts.ActDraw) -> list[Enemy]:
    """Realistic per-act roster (run-model rework §4/§10). `draw` is the
    per-ACT ActDraw: it resolves node kind -> encounter (easy pool for the
    act's first easy_fights N nodes, hard pool for later N, the act's two
    drawn elites for E, the act's drawn boss for B), then `acts.spawn` rolls
    each body's HP within its band via the run rng.

    NO progression-gap compensator: rosters use REAL StS2 numbers (§4),
    so the old battery-calibrated PROGRESSION_GAP_COMPENSATOR does not apply.
    The tier0 battery stays frozen and is no longer read at the run layer."""
    encounter = draw.encounter_for(node_kind, rng)
    return acts.spawn(encounter, rng)


def build_act_map(rng: random.Random, act: int):
    """The act's map. Indirected through a module-level function so tests can
    inject a scripted one (maps.linear) exactly as they already do for
    build_node_encounter -- a generated map is the right default and the wrong
    way to ask a one-node question."""
    return maps.generate(rng, act)


def rest_action(deck_ids: list[str], hp: int, max_hp: int,
                archetype: str = "generic",
                next_fight: bool = False) -> tuple[str, Optional[str]]:
    """Rest policy (spec §2 as amended by M7): heal 30% max HP OR remove 1
    card OR upgrade 1 card (rest-site smithing). Heal when hurt below the
    threshold. Then upgrade an ON-PLAN card -- payoffs before enablers,
    because upgrades are where payoffs traditionally sharpen and that
    late-game scaling is exactly what the pre-M7 sim truncated. Then thin
    a basic (attacks first; basic block only if the defense quota
    survives), then upgrade anything upgradable, then heal.

    Two HP lines, deliberately: below REST_SMITH_DANGER the heal always
    wins; between DANGER and HEAL_THRESHOLD an on-plan smith outranks it
    (the classic rest-vs-smith call). With one line at 0.65 the heal
    swallowed every rest of a bruised run and the third option never
    fired at all.

    DRAFTER_VERSION 5 (b): `next_fight` is the lookahead -- True when the
    node after this rest is an Elite/Boss fight. Both template rests
    directly precede E/B, so under v4 the smith band sent runs into
    guaranteed elites at ~48/80 HP (§10.8.1). With the flag set, the heal
    outranks the smith below REST_PREFIGHT_HEAL_THRESHOLD."""
    if hp < C.REST_SMITH_DANGER * max_hp:
        return "heal", None
    if next_fight and hp < C.REST_PREFIGHT_HEAL_THRESHOLD * max_hp:
        return "heal", None
    deck = [loader.peek_card(cid) for cid in deck_ids]     # read-only scoring
    upgradable = [c for c in deck if upgrades.has_upgrade(c.id)]
    # R125: behavioural tag read -- the anchor's instrumentation tags must
    # not steer the smith (the widened R121 shield).
    on_plan = [c for c in upgradable
               if archetype in draft.behavioural_archetypes(c)]
    if on_plan:
        best = max(on_plan, key=lambda c: (c.role == "payoff",
                                           c.role == "enabler"))
        return "upgrade", best.id
    if hp < C.REST_HEAL_THRESHOLD * max_hp:
        return "heal", None
    basics = [c for c in deck if c.rarity == "basic"]
    atk = [c for c in basics if not any(fx.get("op") == "block"
                                       for fx in c.effects)]
    if atk:
        return "remove", atk[0].id
    blockers = [c for c in basics if c not in atk]
    if blockers:
        n_block = sum(1 for c in deck
                      if any(fx.get("op") == "block" for fx in c.effects))
        if (n_block - 1) / max(1, len(deck) - 1) >= C.DRAFT_BLOCK_DENSITY_MIN:
            return "remove", blockers[0].id
    if upgradable:
        return "upgrade", upgradable[0].id
    return "heal", None


@dataclass
class RunResult:
    seed: int
    won: bool
    death_node: Optional[int]           # node index, None if survived
    hp_by_node: list[int]               # hp AFTER each resolved node
    deck_ids: list[str]                 # final deck
    node_kinds: list[str]
    decisions: list[dict] = field(default_factory=list)   # reward screens
    regret_samples: int = 0
    time_to_online: Optional[int] = None    # fights until core complete
    fight_stats: list = field(default_factory=list)       # t0 FightStats
    rests: list[tuple] = field(default_factory=list)
    banner: frozenset[str] = field(default_factory=frozenset)   # v1.8 featured
    gold: int = 0                       # run-model rework §5: economy state
    shop: list[dict] = field(default_factory=list)   # §5: shop purchase log
    shop_companion_offers: list[dict] = field(default_factory=list)
    #                    §4.7 channel (R61): what the two companion slots
    #                    OFFERED, per visit -- {"slot", "id", "rarity",
    #                    "price", "visit", "gold_at_visit", "affordable"}.
    #                    Deliberately NOT folded into `shop`, which is a
    #                    purchase log that callers sum prices over; an offer is
    #                    not a purchase. The buy RATE needs both -- and it
    #                    needs "visit" to join them, because both lists are
    #                    flattened across every shop the run walked into.
    removal_uses: int = 0               # §5: running removal count (rising price)
    relics: list[str] = field(default_factory=list)  # W2: relics GRANTED this
    #                    run (Neow + treasure + elite + boss + shop + events,
    #                    the last since §11.2), in order; excludes any relics=
    #                    SEED. Empty when grant_relics=False.
    potions_used: list[str] = field(default_factory=list)   # potion pass: ids
    #                    consumed in combat across the run, in order. Empty when
    #                    grant_potions=False (no potions ever held).
    potions_end: list[str] = field(default_factory=list)    # potions still held
    #                    at run end (or at death). Empty when grant_potions=False.
    events: list[dict] = field(default_factory=list)   # §11: event rooms
    #                    visited, in order: {"event": id, "option": label}
    route: str = "hunter"               # §11: the route policy that walked it
    route_decisions: list[dict] = field(default_factory=list)   # EB-16w: the
    #                    ROUTE twin of `decisions` above. One entry per ACT --
    #                    {"act", "map", "decisions", "hindsight"} -- because the
    #                    road not taken is only re-pricable against the map it
    #                    was on, and each act has its own. The inner records are
    #                    exactly `route.walk_decisions`' shape ({"floor",
    #                    "options", "picked", "state"}), written by the live
    #                    incremental walk in run_one rather than by that
    #                    pure-map helper, which cannot resolve fights.
    #                    `hindsight` is THAT ACT'S terminal RouteState (2026-08
    #                    -08): elites_taken / rests_taken are act-local, so this
    #                    is the only state act i's regret may be priced against.
    route_hindsight: Optional[route.RouteState] = None   # EB-16w: the run's
    #                    LAST route state -- at death, or after the final node.
    #                    The run's end, and identical to the final act's
    #                    `route_decisions[-1]["hindsight"]`. NOT the repricing
    #                    input for earlier acts -- see _run_range.
    route_regret: list[dict] = field(default_factory=list)   # EB-16w: one
    #                    `run_metrics.route_regret` summary per act, filled in
    #                    after the run by _run_range (the drafter's
    #                    `regret_samples` is filled at the same site).
    n_acts: int = 1                     # §11: acts this run spans. Every path
    #                    visits exactly one room per floor, so node_kinds is
    #                    always MAP_FLOORS * n_acts long and index == floor
    #                    index -- act boundaries sit at multiples of
    #                    C.MAP_FLOORS.
    acts_completed: int = 0             # §10.1: boss wins (final boss included)
    fanfare_traces: list = field(default_factory=list)   # pass 4 Q1a:
    #                    (act_index, FanfareTrace) per fight, in order.
    #                    Empty traces (turns == 0) for non-Fanfare rosters.
    #                    Under RUNTEMPLATE 6 the count of traces is no longer
    #                    fixed: a route decides how many fights a run takes, so
    #                    a per-COMBAT rate derived from these must be rescaled
    #                    by the observed fight count, never by a template
    #                    constant (see fanfare_telemetry.per_run).
    burst_traces: list = field(default_factory=list)     # C5: (act_index,
    #                    {source: (energy, events)}) per fight.
    kurage_traces: list = field(default_factory=list)    # P2: (act_index,
    #                    KurageTrace) per fight, in order. Empty traces
    #                    (pulses == 0) for every character that never fields
    #                    a Bake-Kurage, which is all of them but Kokomi.
    relics_by_act: list = field(default_factory=list)    # C2 (addendum): how
    #                    many GRANTED relics were held as each act's boss
    #                    resolved, in act order. `relics` above is overwritten
    #                    wholesale at every exit and so only ever describes the
    #                    END of the run; power growth is a per-act question.
    #                    Empty on grant_relics=False runs and on runs that
    #                    never finished an act.
    overlap_traces: list = field(default_factory=list)   # C4 (addendum):
    #                    (act_index, OverlapTrace) per fight -- plays of the
    #                    watched carry cards. `deck_ids` above already says
    #                    what was DRAFTED; this is the only record of what was
    #                    cast, and the drafted-vs-cast gap is half of what C4
    #                    is for. Empty dict for every character whose pool
    #                    holds none of the watched ids.
    aura_traces: list = field(default_factory=list)      # Curtain Call R85:
    #                    (act_index, AuraTrace) per fight -- hydro-application
    #                    uptime, the Track B retype tripwire (sprint log §4).
    encore_traces: list = field(default_factory=list)    # Salon UI Track 3:
    #                    (act_index, EncoreTrace) per fight -- D8's saturation
    #                    prerequisite. Act-tagged like the five above because
    #                    "the bar fills faster than the stage drains it" is a
    #                    claim about late acts, where the stage is largest.
    #                    Empty for every character without Encore.
    conditional_traces: list = field(default_factory=list)  # Salon UI Track 4:
    #                    (act_index, ConditionalTrace) per fight -- rider
    #                    fire-rates, D4's near-dead-condition question.


def node_template() -> list[str]:
    """DEAD as of RUNTEMPLATE_VERSION 6 (§11) -- kept only so archived tools
    can still name the v5 spine they were measured on. The run model no longer
    reads it: each act generates a map (tier05/maps.py) and a route policy
    walks it, so node kinds vary per run."""
    return list(C.RUN_NODE_TEMPLATE)


@dataclass
class _RunCtx:
    """One run's state in one object (EB-41 split of the 518-line run_one).

    Every local the single-function version carried lives here, including the
    per-ACT fields its two closures used to capture. The node phases are
    methods because each of them reads AND writes most of the run -- HP, gold,
    deck, relics, potions and the RunResult move together -- so passing them
    as parameters would rename the coupling rather than remove it.

    Module-level names (`run_fight`, `_potion_slots`, `build_act_map`,
    `build_node_encounter`) are deliberately still called UNQUALIFIED from
    these methods: the suite monkeypatches them on the module, and that seam
    has to keep working.
    """
    character: str
    archetype: str
    policy: DraftPolicy
    rng: random.Random
    pilot: object
    banner: frozenset
    route_policy: Callable
    res: RunResult
    deck_ids: list[str]
    hp: int
    max_hp: int
    gold: int
    n: int
    seed_ids: set
    grant_relics: bool = False
    grant_potions: bool = False
    always_choose3: bool = False
    pity_k: Optional[int] = None
    held: "Optional[relic_pool.HeldRelics]" = None
    bag: "Optional[potion_pool.PotionBag]" = None
    removal_uses: int = 0
    # Which shop this is, counted across the whole run (0-based). Stamped onto
    # every shop record so the run-level OFFER log and the run-level PURCHASE
    # log can be joined back together -- see shop.ShopOutcome. Bookkeeping
    # only: nothing branches on it and it draws no rng.
    shop_visits: int = 0
    screens_since_companion: int = 0
    just_rested: bool = False
    fights: int = 0
    seen_events: set = field(default_factory=set)
    # Per-ACT, all reset by begin_act: the map being walked, its encounter
    # draw, the run's Unknown pity table and the ACT-LOCAL route counters.
    act_i: int = 0
    act_map: object = None
    act_draw: object = None
    act_walk: dict = field(default_factory=dict)
    unknown_weights: object = None
    elites_taken: int = 0
    rests_taken: int = 0

    # -- shared helpers -------------------------------------------------

    def plan(self) -> str:
        """The plan label the ADAPTIVE sites act on. Policies flagged
        emergent_plan buy, smith and answer events toward the deck's own
        dominant shape, never the assigned label -- the A/B contract is that
        adaptive ignores the label everywhere, so every one of those sites
        asks this and none of them reads `archetype` directly."""
        if getattr(self.policy, "emergent_plan", False):
            return draft.dominant_archetype(
                [loader.peek_card(cid) for cid in self.deck_ids])
        return self.archetype

    def route_state(self) -> route.RouteState:
        return route.RouteState(
            hp=self.hp, max_hp=self.max_hp, gold=self.gold,
            deck_size=len(self.deck_ids),
            floor=len(self.res.node_kinds) % C.MAP_FLOORS, act=self.act_i,
            elites_taken=self.elites_taken, rests_taken=self.rests_taken)

    def pick(self, options):
        st = self.route_state()
        picked = self.route_policy(self.rng, self.act_map, options, st)
        self.act_walk["decisions"].append(
            {"floor": picked.floor, "options": list(options),
             "picked": picked, "state": st})
        return picked

    def mark_hindsight(self):
        """EB-16w: the hindsight state, refreshed after every resolved node
        and at both death exits -- never after the act loop, where an
        all-acts-empty run would have no act to snapshot at all."""
        self.res.route_hindsight = self.act_walk["hindsight"] = \
            self.route_state()

    def exit_dead(self, i: int) -> RunResult:
        """The shared death exit (fight loss, stall-out, or a killing event).
        The FULL held set is written back here -- without it an event death
        reported ONLY its event-granted relics (audit 2026-07-26 §1.5),
        mixing two populations in every relic-frequency read."""
        self.res.death_node = i
        self.res.deck_ids = self.deck_ids
        if self.held is not None:
            self.res.relics = [r for r in self.held.ids
                               if r not in self.seed_ids]
        if self.bag is not None:
            self.res.potions_end = list(self.bag.potions)
        self.mark_hindsight()
        return self.res

    def finish(self) -> RunResult:
        self.res.won = True
        self.res.deck_ids = self.deck_ids
        if self.held is not None:
            # W2: relics GRANTED this run (held minus any seed), in acquisition
            # order -- includes commons pulled by a grant_random_common boon.
            self.res.relics = [r for r in self.held.ids
                               if r not in self.seed_ids]
        if self.bag is not None:
            self.res.potions_end = list(self.bag.potions)
        return self.res

    # -- act setup ------------------------------------------------------

    def begin_act(self, act_i: int) -> bool:
        """Open act `act_i`; False for a scripted empty act (tests), which
        has nothing to walk."""
        self.act_i = act_i
        self.act_map = build_act_map(self.rng, act_i)
        if not self.act_map.floors:
            return False
        # Per-ACT encounter draw (§4/§10): easy/hard identity, the elite draw
        # and the boss-pool draw are fixed at each act's start from the run
        # rng, so the roster replays under the same seed.
        self.act_draw = acts.ActDraw(self.rng, act_i)
        self.unknown_weights = maps.fresh_unknown_weights()
        self.elites_taken = self.rests_taken = 0
        # EB-16w: the live walk RECORDS its decisions, in `walk_decisions`'
        # shape, so `run_metrics.route_regret` can price the roads not taken on
        # a real run. Recording only -- no rng is drawn and no decision changes,
        # so every existing seeded run is byte-identical.
        # `hindsight` is THIS ACT'S terminal state, refreshed after every
        # resolved node so the last write is the end-of-act snapshot (and a
        # death exit's write is the act's real end). It exists because
        # `RouteState.elites_taken` / `rests_taken` are ACT-LOCAL -- they reset
        # just above -- while `res.route_hindsight` is the FINAL act's state.
        # Repricing act 0 against act 2's snapshot fed act-2 elite counts into
        # `hunter`'s elite gate, so an earlier act's regret moved with what a
        # later act did: hindsight the run did not have at that decision.
        self.act_walk = {"act": act_i, "map": self.act_map, "decisions": [],
                         "hindsight": None}
        self.res.route_decisions.append(self.act_walk)
        return True

    # -- node phases ----------------------------------------------------

    def resolve_treasure(self):
        """T: the gold lump, plus a Common-pool relic on grant_relics runs."""
        self.gold += C.TREASURE_GOLD
        if self.grant_relics and self.held is not None:
            # W2: the 'ancient' step grants one Common-pool relic IN
            # ADDITION to the gold lump.
            rid = relic_pool.roll_relic_reward(self.rng, self.held,
                                               self.character)
            if rid is not None:
                self.hp, self.max_hp, self.gold = self.held.add(
                    rid, self.character, self.hp, self.max_hp, self.gold,
                    self.deck_ids, self.rng)
        else:
            shop.grant_treasure_relic(self.character, self.deck_ids)  # no-op stub
        self.res.gold = self.gold
        self.res.hp_by_node.append(self.hp)   # non-fight: HP carries, index holds

    def resolve_shop(self):
        """$ (§5): buy from the character's OWN pool, then the relic shelf
        (W2) and the potion shelf (potion pass)."""
        visit = self.shop_visits
        self.shop_visits += 1
        outcome = shop.visit_shop(self.rng, self.character, self.deck_ids,
                                  self.gold, self.plan(), self.policy,
                                  self.removal_uses, visit=visit)
        self.deck_ids = outcome.deck_ids
        self.gold = outcome.gold
        self.removal_uses = outcome.removal_uses
        self.res.shop.extend(outcome.purchases)
        self.res.shop_companion_offers.extend(outcome.companion_offers)
        self.res.removal_uses = self.removal_uses
        self.res.gold = self.gold
        if self.held is not None:
            # Book of Five Rings counts cards bought here; Meal Ticket heals.
            added = sum(1 for p in outcome.purchases
                        if p.get("buy") == "card")
            self.hp = self.held.note_cards_added(added, self.hp, self.max_hp)
            heal = self.held.shop_heal()
            if heal:
                self.hp = min(self.max_hp, self.hp + heal)
        if self.grant_relics and self.held is not None:
            # W2: stock 1-2 Common-pool relics for sale; auto-take-all
            # (relics are near-strictly-good) -- buy each iff gold allows.
            # A distinct shelf is rolled so no relic is offered twice.
            exclude = set(self.held.ids)
            shelf: list[str] = []
            for _ in range(self.rng.randint(1, 2)):
                stock = relic_pool.unowned_common(exclude, self.character)
                if not stock:
                    break
                rid = self.rng.choice(stock)
                shelf.append(rid)
                exclude.add(rid)
            for rid in shelf:
                if self.gold >= C.SHOP_RELIC_PRICE:
                    self.gold -= C.SHOP_RELIC_PRICE
                    self.hp, self.max_hp, self.gold = self.held.add(
                        rid, self.character, self.hp, self.max_hp, self.gold,
                        self.deck_ids, self.rng)
                    outcome.purchases.append(
                        {"buy": "relic", "id": rid,
                         "price": C.SHOP_RELIC_PRICE, "visit": visit})
            self.res.shop.extend(p for p in outcome.purchases
                                 if p.get("buy") == "relic")
            self.res.gold = self.gold
        if self.grant_potions and self.bag is not None:
            # Potion pass: stock 1-2 potions; auto-buy each iff a slot is
            # free AND gold allows. The shelf is rolled first (deterministic
            # off the run rng); an unaffordable / no-slot potion is simply
            # not bought (no swap prompt in this model).
            self.bag.slots = _potion_slots(self.held)
            for _ in range(self.rng.randint(1, 2)):
                pid = potion_pool.roll_potion(self.rng)
                if not self.bag.full() and self.gold >= C.POTION_PRICE:
                    self.gold -= C.POTION_PRICE
                    self.bag.add(pid)
                    self.res.shop.append({"buy": "potion", "id": pid,
                                          "price": C.POTION_PRICE,
                                          "visit": visit})
            self.res.gold = self.gold
        self.res.hp_by_node.append(self.hp)

    def resolve_rest(self, i: int, room):
        """R: heal / thin / smith (M7), with the DRAFTER_VERSION 5 lookahead
        now read off the ROUTE rather than a template -- what actually comes
        next is whichever room this rest leads to, and under a map that can
        be anything. A rest that leads only into E/B is the "top up before
        the big fight" case; a rest with a safe exit is not."""
        nxt = self.act_map.successors(room)
        action, target = rest_action(
            self.deck_ids, self.hp, self.max_hp, self.plan(),
            next_fight=bool(nxt) and all(
                r.kind in ("E", "B") for r in nxt))
        if action == "heal":
            self.hp = min(self.max_hp,
                          self.hp + round(C.REST_HEAL_FRACTION * self.max_hp))
        elif action == "remove":
            self.deck_ids.remove(target)
        else:                               # M7: rest-site smithing
            self.deck_ids[self.deck_ids.index(target)] = target + upgrades.SUFFIX
        if self.held is not None:
            # Regal Pillow: extra heal at the campfire. Venerable Tea Set's
            # post_rest_energy is injected into the NEXT fight (just_rested).
            heal = self.held.post_rest_heal()
            if heal:
                self.hp = min(self.max_hp, self.hp + heal)
        self.just_rested = True
        self.res.rests.append((i, action, target))
        self.res.hp_by_node.append(self.hp)

    def resolve_event(self, i: int) -> bool:
        """An Unknown that resolved to an Event (§11). The resolver is pure
        over deck/HP/gold/relics/potions, so it is handed a snapshot and its
        results are copied back -- no run local is reachable from event
        content. True when the event killed the run (a real rule)."""
        est = events.EventState(
            character=self.character, archetype=self.plan(), hp=self.hp,
            max_hp=self.max_hp, gold=self.gold, deck_ids=self.deck_ids,
            potions=list(self.bag.potions) if self.bag else [],
            potion_slots=self.bag.slots if self.bag else 0)
        events.visit(self.rng, self.act_i, est, self.seen_events,
                     held=self.held, bag=self.bag, policy=self.policy)
        self.hp, self.max_hp, self.gold = est.hp, est.max_hp, est.gold
        self.deck_ids = est.deck_ids
        self.res.events.extend(est.log)
        if self.grant_relics:
            self.res.relics.extend(est.relics_granted)
        if self.hp <= 0:
            self.res.hp_by_node.append(0)
            self.exit_dead(i)
            return True
        self.res.gold = self.gold
        self.res.hp_by_node.append(self.hp)
        return False

    def resolve_fight(self, i: int, kind: str) -> bool:
        """N / E / B. True when the run is over (death or stall-out)."""
        enemies = build_node_encounter(kind, self.rng, self.act_draw)
        # Context-dependent combat effects (spec): base held-relic combat
        # effects + post_rest_energy (if we just rested) + elite_combat_start
        # (on E nodes). None when no relics are held -> identical to before.
        relic_fx = None
        if self.held is not None:
            relic_fx = self.held.combat_effects_for(kind, self.just_rested)
            self.just_rested = False
        if self.grant_potions and self.bag is not None:
            # Potion pass: build the fight with the held bag + node_kind context
            # so the combat use-policy can drink (offensive drinks gated to
            # elite/boss by node_kind). A COPY of bag.potions goes in; combat
            # mutates the player's own list, which we sync back after the fight.
            self.bag.slots = _potion_slots(self.held)
            potions_before = list(self.bag.potions)
            player = loader.build_player_from_ids(
                self.character, self.deck_ids, relic_effects=relic_fx,
                potions=list(self.bag.potions), potion_slots=self.bag.slots,
                node_kind=_NODE_KIND_CTX.get(kind, ""))
        else:
            potions_before = None
            player = loader.build_player_from_ids(
                self.character, self.deck_ids, relic_effects=relic_fx)
        player.hp = self.hp
        player.max_hp = self.max_hp
        hp_start = self.hp
        state = run_fight(player, enemies, self.pilot,
                          seed=self.rng.randrange(2 ** 31))
        self.res.fight_stats.append(t0_metrics.extract(state, hp_start))
        self._record_traces(state)
        self.fights += 1
        self.hp = state.player.hp
        # Combat-scoped effects such as Feed can raise max HP permanently.
        # Keep that mutation on the existing run-local state so the next
        # fight is not rebuilt with the old ceiling (a fuller RunState object
        # is a separate architecture decision, not required for correctness).
        self.max_hp = state.player.max_hp
        fight_won = state.player.alive and not state.living_enemies
        if self.grant_potions and self.bag is not None:
            # Sync consumed potions back: combat removed each drunk/spent potion
            # (incl. an auto-consumed Fairy) from player.potions, so the survivor
            # list IS the bag, and the difference is what was used this fight.
            self.res.potions_used.extend(
                _consumed(potions_before, state.player.potions))
            self.bag.potions = list(state.player.potions)
        if fight_won:
            self._pay_fight_win(kind, player)
        self.res.hp_by_node.append(max(0, self.hp))
        if not fight_won:                   # death OR stall-out = run over
            self.exit_dead(i)
            return True
        final_act = self.act_i == self.n - 1
        if kind == "B":
            self.res.acts_completed += 1
            # C2 (Neap Tide addendum): relic count AT the act boundary,
            # recorded here because res.relics is overwritten wholesale
            # at each exit and therefore only ever describes run END.
            # An act that was never finished contributes no entry, which
            # is the honest shape: there is no boundary to measure.
            self.res.relics_by_act.append(
                0 if self.held is None
                else len([r for r in self.held.ids
                          if r not in self.seed_ids]))
        if kind != "B" or not final_act:
            self._reward_screens(i, kind, state)
        if kind == "B" and not final_act:
            self._act_boundary()
        return False

    def _record_traces(self, state):
        """The per-fight telemetry, act-tagged. ALL of it is taken here
        because `state.log` does not survive onto the RunResult -- anything
        not reduced at this point is unrecoverable -- and act-tagged because
        every question these answer ("by act 3...") is a per-act one that no
        fight-level or run-level average can reach. Each trace is empty for
        rosters the mechanism does not exist on, so it costs them nothing."""
        act_i = self.act_i
        log = state.log
        self.res.fanfare_traces.append(                # pass 4 Q1a
            (act_i, fanfare_telemetry.trace(log)))
        self.res.kurage_traces.append(                 # P2 (playtest sprint)
            (act_i, kurage_telemetry.trace(log)))
        self.res.burst_traces.append(                  # C5 (Neap Tide v2.1)
            (act_i, burst_telemetry.trace(log)))
        self.res.overlap_traces.append(                # C4 (Neap Tide addendum)
            (act_i, overlap_telemetry.trace(log)))
        self.res.aura_traces.append(                   # Curtain Call R85 Track D
            (act_i, aura_telemetry.trace(log)))
        self.res.encore_traces.append(                 # Salon UI Track 3
            (act_i, encore_telemetry.trace(log)))
        self.res.conditional_traces.append(            # Salon UI Track 4
            (act_i, conditional_telemetry.trace(log)))

    def _pay_fight_win(self, kind: str, player):
        """What a won fight pays: the run-layer heal, gold income, relic
        payouts and the potion drop."""
        # Burning Blood in the RUN LAYER (run-model rework §2): heal after
        # each won fight for relic-bearing characters. combat.py stays
        # emit-only; the heal that carries HP across fights lives ONLY
        # here, capped at max_hp.
        if "heal_after_won_fight" in player.relic_hooks:
            self.hp = min(self.max_hp, self.hp + C.BURNING_BLOOD_HEAL)
        self.gold += C.GOLD_INCOME.get(kind, 0)     # §5 per-fight income
        # Run-layer relic payouts on a won fight: gold_per_fight (Amethyst/
        # Aubergine) and fishing_rod's every-3rd-N-win upgrade.
        if self.held is not None:
            self.gold, self.hp = self.held.post_fight(
                kind, self.gold, self.hp, self.max_hp, self.deck_ids, self.rng)
        # W2: ELITE and BOSS wins grant a relic (Common pool -- boss-tier
        # relics are out of scope this pass). Normals give cards, not
        # relics, so N wins grant nothing here.
        if self.grant_relics and self.held is not None and kind in ("E", "B"):
            rid = relic_pool.roll_relic_reward(self.rng, self.held,
                                               self.character)
            if rid is not None:
                self.hp, self.max_hp, self.gold = self.held.add(
                    rid, self.character, self.hp, self.max_hp, self.gold,
                    self.deck_ids, self.rng)
        # Potion pass: a POTION_DROP_CHANCE drop after a won NORMAL/ELITE
        # fight (bosses end the run, so no boss drop). Slot-permitting: a
        # full bag discards the drop (logged in bag.discarded).
        if self.grant_potions and self.bag is not None and kind in ("N", "E"):
            if self.rng.random() < C.POTION_DROP_CHANCE:
                self.bag.slots = _potion_slots(self.held)
                self.bag.add(potion_pool.roll_potion(self.rng))
        self.res.gold = self.gold

    def _reward_screens(self, i: int, kind: str, state):
        """The reward screen. A FINAL boss ends the run with no reward; a
        non-final boss shows the act-transition screen (§10.1): the CARD
        offers are forced Rare -- the ratified "choice-of-3 Rares" boss drop
        -- and the companion slot is forced Rare too. (Shipped Pass 1 forced
        only the companion slot; a no-companion character got ordinary
        commons at the boundary -- the Ironclad-0.6% diagnosis, 2026-07-23.)"""
        n_comp = 1
        if self.always_choose3:
            n_comp = 3                  # choose3: every slot is
            #             a pick of three (spec §3). Applies to
            #             the act-boundary screen too -- it is a
            #             companion slot like any other, forced
            #             to Rare rather than exempted.
        elif (self.pity_k is not None
                and self.screens_since_companion >= self.pity_k):
            n_comp = 3                  # pity fires: choose-3 slot
        # THE FIGHT'S OWN SCREEN, then any screen the fight EARNED.
        # The Hunt's extra reward is granted here and only here:
        # combat recorded that it happened (state.extra_card_screens)
        # and the run layer is what owns rolling and drafting, the
        # same division the Burning Blood heal keeps above. An extra
        # screen is CARD-ONLY -- no companion slot, no pity credit,
        # and never the boss's forced-Rare tier, because it is an
        # ordinary CardReward the room hands over after the fight.
        # (Lost fights never reach here at all, so a Hunt that fires
        # in a fight the player then loses pays nothing, exactly as
        # in the base game -- there is no rewards screen to pay on.)
        screens = [(n_comp, "rare" if kind == "B" else None)]
        screens += [(0, None)] * state.extra_card_screens
        for n_comp_i, forced in screens:
            offers = rewards.roll_rewards(
                self.rng, self.character, companion_offers=n_comp_i,
                banner=self.banner, companion_rarity=forced,
                card_rarity=forced)
            # Read-only: the drafter, the relevance probes and the core
            # check below only SCORE the deck. Copying it three times per
            # screen was the run layer's single biggest cost.
            deck_cards = [loader.peek_card(cid) for cid in self.deck_ids]
            # Relevance is judged on the deck as it stood WHEN THE SCREEN WAS
            # SHOWN, before the pick lands -- judging after would let the pick
            # itself change the answer.
            advanced = draft.offer_advances_plan(offers, deck_cards,
                                                 self.archetype)
            # Whether there was still a plan to advance. Core progress caps at
            # 1.0, so once the core is online NOTHING can advance it and
            # `advanced` is structurally False for the rest of the run. Without
            # this flag, relevance charges those screens to the pool as misses
            # -- and half of demolition's screens fall after its core completes.
            plan_live = not draft.core_complete(deck_cards, self.archetype)
            engaging = draft.offer_worth_engaging(offers, deck_cards,
                                                  self.archetype)
            pick = self.policy(self.rng, deck_cards, offers, self.archetype)
            self.res.decisions.append({
                "node": i, "offers": offers,
                "picked": pick.id if pick else None,
                "advanced_plan": advanced,
                "plan_live": plan_live,
                "engaging": engaging})
            if pick is not None:
                self.deck_ids.append(pick.id)
                if self.held is not None:      # Book of Five Rings tally
                    self.hp = self.held.note_cards_added(1, self.hp,
                                                         self.max_hp)
            if n_comp_i == 0:
                # A card-only screen cannot produce a companion, so
                # counting it toward the pity clock would let The
                # Hunt accelerate the companion pity timer -- an
                # interaction nobody designed and nothing prints.
                pass
            elif pick is not None and pick.is_companion:
                self.screens_since_companion = 0
            else:
                self.screens_since_companion += 1
            if (self.res.time_to_online is None
                    and draft.core_complete(
                        [loader.peek_card(cid) for cid in self.deck_ids],
                        self.archetype)):
                self.res.time_to_online = self.fights

    def _act_boundary(self):
        """Act boundary (§10.1): the Ancient heals 100% of missing HP, and on
        grant_relics runs offers a 1-of-3 Ancient-relic pick. Deck, gold,
        relics and potions persist in their run locals; only HP resets."""
        self.hp = self.max_hp
        if self.grant_relics and self.held is not None:
            offer = relic_pool.ancient_offer(self.rng, self.held,
                                             self.character)
            pick = relic_pool.ancient_pick(offer, self.character)
            if pick is not None:
                self.hp, self.max_hp, self.gold = self.held.add(
                    pick, self.character, self.hp, self.max_hp, self.gold,
                    self.deck_ids, self.rng)


def _setup_run(character: str, archetype: str, pilot_id: str,
               policy: DraftPolicy, seed: int, slot_mode: str,
               relics: list[str] | None, grant_relics: bool,
               grant_potions: bool, n_acts: int | None,
               route_name: str,
               force_cards: list[str] | None = None) -> _RunCtx:
    """Run start: the slot mode, the three rng streams, the starting deck and
    the seeded/Neow relics and the potion bag. Everything up to the first
    node. Argument meanings are documented on run_one, the public entry."""
    pity_k = None
    always_choose3 = slot_mode == "choose3"
    if slot_mode.startswith("pity(") and slot_mode.endswith(")"):
        pity_k = int(slot_mode[5:-1])
    elif slot_mode not in ("standard", "choose3"):
        raise ValueError(f"unknown slot mode {slot_mode!r}")
    rng = random.Random(seed)
    # v1.8 Featured Banner: rolled once per run and fixed for its duration.
    # DEDICATED rng stream, the same trick draft_regret uses, for a specific
    # reason: drawing the banner from `rng` would advance the main stream and
    # silently renumber every existing measurement, including the frozen v0.1
    # snapshot. Seed-determined either way, which is all the spec asks for.
    # `nations` is passed EXPLICITLY rather than left to the default. This call
    # site is the entire reason the default was wrong for as long as it was:
    # it took the argument-free form, so the banner covered Mondstadt alone and
    # every other nation's 5-stars were filtered out of every offer in the run.
    # Naming the set here means the audit is visible where the run is built.
    banner = rewards.roll_banner(random.Random(seed + 2 * 10 ** 9),
                                 nations=rewards.designed_nations())
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    # Dedicated stream: randomized starters are seed-replayable but do not
    # renumber encounters, reward rolls, shops, or any calibrated run result.
    starter_rng = random.Random(seed + 3 * 10 ** 9)
    deck_ids = loader.starting_deck(character, starter_rng)
    max_hp = loader._character_index()[character]["hp"]
    hp = max_hp
    gold = C.GOLD_START
    # Held relics (the run-layer half). Constructed ONLY when a run actually
    # holds relics, so relics=None keeps every relic branch dead. Pickup relics
    # (max-HP / gold / deck upgrades) are applied ONCE, here at run start.
    held = None
    seed_ids = set(relics or [])
    if relics:
        held = relic_pool.HeldRelics.hold(relics, character)
        hp, max_hp, gold = held.apply_pickups(hp, max_hp, gold, deck_ids, rng)
    if grant_relics:
        # W2 granting cadence. Build an empty holder if the run wasn't seeded,
        # so relics accrue onto it. Honour BOTH when seeded: seed first (above),
        # then the Neow pick. All accrual is gated on grant_relics, so a seeded
        # run with grant_relics=False never grants -- the W1 world is intact.
        if held is None:
            held = relic_pool.HeldRelics.empty(character)
        offer = relic_pool.neow_offer(rng)                  # 1-of-3 (positive)
        pick = relic_pool.neow_pick(offer, character)
        if pick is not None:
            hp, max_hp, gold = held.add(pick, character, hp, max_hp, gold,
                                        deck_ids, rng)
    # Held-potion bag (potion pass). Constructed ONLY on grant_potions runs, so
    # a grant_potions=False run never holds potions and every combat is built
    # exactly as before. Slot count is recomputed at each use site from `held`
    # so a Potion Belt granted mid-run raises the cap immediately.
    bag = None
    if grant_potions:
        bag = potion_pool.PotionBag(potions=[], slots=_potion_slots(held))
    total_acts = acts.n_acts()
    n = total_acts if n_acts is None else n_acts
    if not 1 <= n <= total_acts:
        raise ValueError(f"n_acts={n} out of range: {total_acts} act(s) "
                         f"registered in RUN_ACTS")
    res = RunResult(seed=seed, won=False, death_node=None, hp_by_node=[],
                    deck_ids=deck_ids, node_kinds=[], banner=banner,
                    n_acts=n, route=route_name)
    # EB-17p deck injection, LAST in run start and deliberately so. Two
    # run-start relic effects consume the MAIN rng stream in a way that
    # depends on how big the deck is -- `_pickup_upgrade` shuffles the
    # upgradable deck indices (relics.py:433-445) and `grant_random_common`
    # rolls off the same stream (:424-430). Injecting before them would
    # desynchronise the shared stream at floor zero and destroy the seed
    # pairing before the first node is even entered. Injecting here leaves
    # run start byte-identical between a forced arm and its control: same
    # map, same seeded/Neow relics, same gold, one extra card.
    #
    # Appended to `deck_ids`, which IS the list object `res.deck_ids` holds,
    # so the injection is visible to every downstream deck read without a
    # second write.
    for cid in force_cards or ():
        # Fail loudly HERE, on a typo, rather than as a KeyError deep inside
        # a worker process halfway through a batch -- the contract Cell's
        # __post_init__ gives a plan id. peek_card is the read-only door and
        # consumes no randomness, so this validation cannot move a run.
        loader.peek_card(cid)
        deck_ids.append(cid)
    return _RunCtx(character=character, archetype=archetype, policy=policy,
                   rng=rng, pilot=pilot, banner=banner,
                   route_policy=route.POLICIES[route_name], res=res,
                   deck_ids=deck_ids, hp=hp, max_hp=max_hp, gold=gold, n=n,
                   seed_ids=seed_ids, grant_relics=grant_relics,
                   grant_potions=grant_potions,
                   always_choose3=always_choose3, pity_k=pity_k,
                   held=held, bag=bag)


def run_one(character: str, archetype: str, pilot_id: str,
            policy: DraftPolicy, seed: int,
            slot_mode: str = "standard",
            relics: list[str] | None = None,
            grant_relics: bool = False,
            grant_potions: bool = False,
            n_acts: int | None = None,
            route_name: str = "hunter",
            force_cards: list[str] | None = None) -> RunResult:
    """slot_mode: the draft-sim spec's three modes (§3, "build all three
    now") -- 'standard' (1 companion offer), 'choose3' (every companion slot
    is a pick of three), or 'pity(k)' (k screens without taking a companion
    make the NEXT slot a choose-3). Mode set per-config; default standard.
    `choose3` is the standalone mode EB-27 found never built: the mechanism
    existed only as pity's payload, so the fishable arm of the dream-team
    metric (spec §5, "deliberately fishable under choose3/pity") had no
    choose3 half to read. It is INERT until a caller asks for it -- nothing
    in the live instruments passes it, and `standard` is byte-identical.

    n_acts (§10.1): how many acts the run spans -- None (default) spans every
    act registered in constants.RUN_ACTS; an explicit count must not exceed
    the registry (`--acts 1` is the supported single-act instrument).

    relics: relic ids the run STARTS holding (the W1 seed seam). None -> no
    relics seeded.

    grant_relics (W2): when True, the run ACCRUES relics through the StS Act-1
    cadence -- a Neow run-start pick, treasure/elite/boss grants, and shop
    stock. Default False. When grant_relics=False AND relics=None the whole
    relic path is dead: build_player_from_ids is called with relic_effects=None
    exactly as before, so it is byte-identical to the pre-relic model. Seeded
    (relics=[...]) runs with grant_relics=False keep the W1 behaviour unchanged:
    the granting sites are ALL gated on grant_relics, never on `held`.

    grant_potions (potion pass): when True, the run holds a PotionBag (3 slots,
    +2 if Potion Belt is held), takes a POTION_DROP_CHANCE drop after each won
    normal/elite fight, buys 1-2 shop potions when a slot and gold allow, and
    builds each fight with the held bag + node_kind context (so the combat
    use-policy can drink). Default False. When grant_potions=False the bag is
    never constructed and potions are never passed to build_player_from_ids, so
    the potions=None path is byte-identical to the pre-potion model.

    force_cards (EB-17p): card ids appended to the deck at the END of run
    start, after every run-start relic effect has drawn from the main stream.
    Default None, which is the world we have -- a None batch is
    element-for-element identical to the pre-seam batch, pinned by
    `tier05/tests/test_eb17p_force_cards.py`. This is a DECK change, not a
    drafter change: the drafter scores a different deck by the same function,
    so a forced arm and its control run at the same RT/D/P/C stamp.

    ASSIGNMENT ONLY, never enforcement. The run layer may still upgrade a
    forced copy (a smith node rewrites the id in place) or remove it at a
    rest node. Reads keyed on a forced id must pool `X` with `X+`, and the
    estimand any experiment builds on this seam is intent-to-treat.

    EB-41: the walk itself is this function; run start, the per-act setup and
    each node kind are phases on `_RunCtx` above."""
    ctx = _setup_run(character, archetype, pilot_id, policy, seed, slot_mode,
                     relics, grant_relics, grant_potions, n_acts, route_name,
                     force_cards)
    res = ctx.res

    # RUNTEMPLATE_VERSION 6 (§11): the fixed 11-node spine is gone. Each act
    # generates a real 16-floor map and a route policy walks it, so node KINDS
    # now vary per run. Every path still visits exactly one room per floor, so
    # len(node_kinds) stays MAP_FLOORS * n_acts and the index IS the floor
    # index -- which is what keeps the funnel and the death heatmap meaningful
    # (they are per-floor now, not per-authored-node).
    for act_i in range(ctx.n):
        if not ctx.begin_act(act_i):    # scripted empty act (tests)
            continue
        room = ctx.pick(ctx.act_map.rooms_on(0))
        while True:
            i = len(res.node_kinds)
            kind = room.kind
            if kind == maps.UNKNOWN:
                # Resolved AT ENTRY, through the run's pity table (§1).
                kind = maps.resolve_unknown(ctx.rng, ctx.unknown_weights)
            res.node_kinds.append(kind)
            ctx.elites_taken += kind == "E"
            ctx.rests_taken += kind == "R"
            if kind == "T":                     # treasure: gold lump + relic
                ctx.resolve_treasure()
            elif kind == "$":                   # shop (§5): buy from OWN pool
                ctx.resolve_shop()
            elif kind == "R":
                ctx.resolve_rest(i, room)
            elif kind == "event":
                if ctx.resolve_event(i):
                    return res
            else:                               # N / E / B: a fight
                if ctx.resolve_fight(i, kind):
                    return res

            # Route to the next room. The decision is made HERE, after the
            # node has resolved, so it sees post-fight HP -- which is the
            # whole mechanism behind "a hurt run ducks the next elite".
            ctx.mark_hindsight()
            succ = ctx.act_map.successors(room)
            if not succ:
                break
            room = ctx.pick(succ)

    return ctx.finish()


def _run_range(character: str, archetype: str, pilot_id: str,
               policy: DraftPolicy, seed: int, lo: int, hi: int,
               slot_mode: str, relics: list[str] | None,
               grant_relics: bool, grant_potions: bool,
               n_acts: int | None, route_name: str,
               force_cards: list[str] | None = None) -> list[RunResult]:
    """Runs [lo, hi) of the batch. Each is a pure function of `seed + i`."""
    out = []
    for i in range(lo, hi):
        r = run_one(character, archetype, pilot_id, policy, seed + i,
                    slot_mode=slot_mode, relics=relics,
                    grant_relics=grant_relics, grant_potions=grant_potions,
                    n_acts=n_acts, route_name=route_name,
                    force_cards=force_cards)
        # draft_regret: sampled re-score in the final-deck context, using
        # a DEDICATED rng stream so sampling can't perturb run decisions.
        r.regret_samples = draft.draft_regret(
            random.Random(seed + i + 10 ** 9), r.decisions,
            [loader.peek_card(cid) for cid in r.deck_ids], archetype)
        # route_regret (EB-16w): the same construction one layer out -- sampled
        # re-scoring of recorded decisions in hindsight, on its own +5e9 stream
        # (the offset registry lives in understudy/rng.py). Per ACT, because a
        # path value only means anything against its own map -- AND, since
        # 2026-08-08, against its OWN act's terminal state.
        # NOT one state for all of them. The drafter can re-score every screen
        # against one final deck because a deck accumulates across the whole
        # run; a RouteState does not. `elites_taken` / `rests_taken` reset at
        # each act boundary, and `hunter`'s elite gate reads `elites_taken`
        # twice -- so pricing act 0 against the FINAL act's snapshot let a
        # later act's elites move an earlier act's regret. That is hindsight
        # the run never had at that decision: a leak, not a re-pricing.
        # `res.route_hindsight` still holds the final act's state, unchanged,
        # for readers that want the run's end.
        # The import is deferred on purpose: run_metrics imports RunResult from
        # this module, so a module-level import would close the cycle.
        from tier05 import run_metrics
        # An act that resolved no node has no terminal state to price in and
        # is skipped -- so every summary carries its `act`, and a skip can
        # never misalign a positional reader.
        r.route_regret = [
            {**run_metrics.route_regret(
                random.Random(seed + i + 5 * 10 ** 9), w["map"],
                w["decisions"], w["hindsight"], route_name),
             "act": w["act"]}
            for w in r.route_decisions if w["hindsight"] is not None]
        out.append(r)
    return out


def _run_chunk(args: tuple) -> list[RunResult]:
    """Process-pool entry point. Module-level (picklable), and it takes the
    policy by NAME because a policy callable cannot cross a process boundary."""
    name, rest = args[0], args[1:]
    return _run_range(rest[0], rest[1], rest[2], draft.POLICIES[name],
                      *rest[3:])


def _policy_name(policy: DraftPolicy) -> Optional[str]:
    for name, fn in draft.POLICIES.items():
        if fn is policy:
            return name
    return None


def run_many(character: str, archetype: str, pilot_id: str,
             policy: DraftPolicy, runs: int, seed: int,
             slot_mode: str = "standard",
             relics: list[str] | None = None,
             grant_relics: bool = False,
             grant_potions: bool = False,
             n_acts: int | None = None,
             jobs: int = 1,
             route_name: str = "hunter",
             force_cards: list[str] | None = None) -> list[RunResult]:
    """`jobs` > 1 spreads the batch over that many worker PROCESSES;
    `jobs=0` means one per CPU.

    This is a wall-clock lever ONLY, never a fidelity tradeoff: run i is a
    pure function of `seed + i` (spec §2 -- one Random per run, no global
    state), each worker gets a contiguous block, and the blocks concatenate
    back in index order. An N-job result list is element-for-element
    identical to the serial one, which `test_runner.py` pins.

    Serial fallback when there is nothing to parallelize, and when `policy`
    is not one of the named `draft.POLICIES` -- an experiment script may pass
    its own closure, which cannot be pickled; running that in-process is
    better than refusing to run it.
    """
    common = (character, archetype, pilot_id, seed)
    tail = (slot_mode, relics, grant_relics, grant_potions, n_acts,
            route_name, force_cards)
    workers = min((os.cpu_count() or 1) if jobs == 0 else jobs, runs)
    name = _policy_name(policy)
    if workers <= 1 or name is None:
        if name is None and workers > 1:
            warnings.warn(
                "run_many(jobs>1) needs one of draft.POLICIES to send across "
                "processes; running serially.", stacklevel=2)
        return _run_range(*common[:3], policy, seed, 0, runs, *tail)

    edges = [runs * k // workers for k in range(workers + 1)]
    chunks = [(name, *common, lo, hi, *tail)
              for lo, hi in zip(edges, edges[1:]) if lo < hi]
    with ProcessPoolExecutor(max_workers=len(chunks)) as pool:
        return [r for block in pool.map(_run_chunk, chunks) for r in block]
