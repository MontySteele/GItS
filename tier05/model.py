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

import random
from dataclasses import dataclass, field
from typing import Callable, Optional

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine.combat import run_fight
from tier0.engine.state import Card, Enemy
from tier0.harness import metrics as t0_metrics
from tier0.pilot.policy import make_pilot
from tier05 import acts, draft, potions as potion_pool, rewards, shop
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
    deck = [loader.get_card(cid) for cid in deck_ids]
    upgradable = [c for c in deck if upgrades.has_upgrade(c.id)]
    on_plan = [c for c in upgradable if archetype in c.archetypes]
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
    removal_uses: int = 0               # §5: running removal count (rising price)
    relics: list[str] = field(default_factory=list)  # W2: relics GRANTED this
    #                    run (Neow + treasure + elite + boss + shop), in order;
    #                    excludes any relics= SEED. Empty when grant_relics=False.
    potions_used: list[str] = field(default_factory=list)   # potion pass: ids
    #                    consumed in combat across the run, in order. Empty when
    #                    grant_potions=False (no potions ever held).
    potions_end: list[str] = field(default_factory=list)    # potions still held
    #                    at run end (or at death). Empty when grant_potions=False.
    n_acts: int = 1                     # §10.1: acts this run spans; node_kinds
    #                    is the per-act template repeated n_acts times, so act
    #                    boundaries sit at multiples of len(node_template()).
    acts_completed: int = 0             # §10.1: boss wins (final boss included)


def node_template() -> list[str]:
    # RUNTEMPLATE_VERSION 5: the PER-ACT template ("NNNRETN$ERB"); a run is
    # this repeated once per act (§10.1). Node kinds: N/E/B fights, R rest,
    # T treasure, $ shop.
    return list(C.RUN_NODE_TEMPLATE)


def run_one(character: str, archetype: str, pilot_id: str,
            policy: DraftPolicy, seed: int,
            slot_mode: str = "standard",
            relics: list[str] | None = None,
            grant_relics: bool = False,
            grant_potions: bool = False,
            n_acts: int | None = None) -> RunResult:
    """slot_mode: 'standard' (1 companion offer) or 'pity(k)' — k screens
    without taking a companion make the next slot a choose-3.

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
    the potions=None path is byte-identical to the pre-potion model."""
    pity_k = None
    if slot_mode.startswith("pity(") and slot_mode.endswith(")"):
        pity_k = int(slot_mode[5:-1])
    elif slot_mode != "standard":
        raise ValueError(f"unknown slot mode {slot_mode!r}")
    screens_since_companion = 0
    rng = random.Random(seed)
    # v1.8 Featured Banner: rolled once per run and fixed for its duration.
    # DEDICATED rng stream, the same trick draft_regret uses, for a specific
    # reason: drawing the banner from `rng` would advance the main stream and
    # silently renumber every existing measurement, including the frozen v0.1
    # snapshot. Seed-determined either way, which is all the spec asks for.
    banner = rewards.roll_banner(random.Random(seed + 2 * 10 ** 9))
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    # Dedicated stream: randomized starters are seed-replayable but do not
    # renumber encounters, reward rolls, shops, or any calibrated run result.
    starter_rng = random.Random(seed + 3 * 10 ** 9)
    deck_ids = loader.starting_deck(character, starter_rng)
    max_hp = loader._character_index()[character]["hp"]
    hp = max_hp
    gold = C.GOLD_START
    removal_uses = 0
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
    just_rested = False
    template = node_template()
    total_acts = acts.n_acts()
    n = total_acts if n_acts is None else n_acts
    if not 1 <= n <= total_acts:
        raise ValueError(f"n_acts={n} out of range: {total_acts} act(s) "
                         f"registered in RUN_ACTS")
    nodes = template * n
    res = RunResult(seed=seed, won=False, death_node=None, hp_by_node=[],
                    deck_ids=deck_ids, node_kinds=nodes, banner=banner,
                    n_acts=n)
    fights = 0
    act_draw = None
    act_i = -1
    for i, kind in enumerate(nodes):
        if i % len(template) == 0:
            # Per-ACT encounter draw (§4/§10): easy/hard identity, the 2-of-3
            # elite draw and the boss-pool draw are fixed at each act's start
            # from the run rng, so the roster replays under the same seed.
            act_i += 1
            act_draw = acts.ActDraw(rng, act_i)
        if kind == "T":                     # treasure: gold lump + relic
            gold += C.TREASURE_GOLD
            if grant_relics and held is not None:
                # W2: the 'ancient' step grants one Common-pool relic IN
                # ADDITION to the gold lump.
                rid = relic_pool.roll_relic_reward(rng, held, character)
                if rid is not None:
                    hp, max_hp, gold = held.add(rid, character, hp, max_hp,
                                                gold, deck_ids, rng)
            else:
                shop.grant_treasure_relic(character, deck_ids)   # no-op stub
            res.gold = gold
            res.hp_by_node.append(hp)       # non-fight: HP carries, index holds
            continue
        if kind == "$":                     # shop (§5): buy from OWN pool
            # Adaptive policies buy toward the deck's emergent shape, never
            # the assigned label -- same contract as rest-site smithing.
            shop_plan = archetype
            if getattr(policy, "emergent_plan", False):
                shop_plan = draft.dominant_archetype(
                    [loader.get_card(cid) for cid in deck_ids])
            outcome = shop.visit_shop(rng, character, deck_ids, gold,
                                      shop_plan, policy, removal_uses)
            deck_ids = outcome.deck_ids
            gold = outcome.gold
            removal_uses = outcome.removal_uses
            res.shop.extend(outcome.purchases)
            res.removal_uses = removal_uses
            res.gold = gold
            if held is not None:
                # Book of Five Rings counts cards bought here; Meal Ticket heals.
                added = sum(1 for p in outcome.purchases
                            if p.get("buy") == "card")
                hp = held.note_cards_added(added, hp, max_hp)
                heal = held.shop_heal()
                if heal:
                    hp = min(max_hp, hp + heal)
            if grant_relics and held is not None:
                # W2: stock 1-2 Common-pool relics for sale; auto-take-all
                # (relics are near-strictly-good) -- buy each iff gold allows.
                # A distinct shelf is rolled so no relic is offered twice.
                exclude = set(held.ids)
                shelf: list[str] = []
                for _ in range(rng.randint(1, 2)):
                    stock = relic_pool.unowned_common(exclude, character)
                    if not stock:
                        break
                    rid = rng.choice(stock)
                    shelf.append(rid)
                    exclude.add(rid)
                for rid in shelf:
                    if gold >= C.SHOP_RELIC_PRICE:
                        gold -= C.SHOP_RELIC_PRICE
                        hp, max_hp, gold = held.add(rid, character, hp, max_hp,
                                                    gold, deck_ids, rng)
                        outcome.purchases.append(
                            {"buy": "relic", "id": rid,
                             "price": C.SHOP_RELIC_PRICE})
                res.shop.extend(p for p in outcome.purchases
                                if p.get("buy") == "relic")
                res.gold = gold
            if grant_potions and bag is not None:
                # Potion pass: stock 1-2 potions; auto-buy each iff a slot is
                # free AND gold allows. The shelf is rolled first (deterministic
                # off the run rng); an unaffordable / no-slot potion is simply
                # not bought (no swap prompt in this model).
                bag.slots = _potion_slots(held)
                for _ in range(rng.randint(1, 2)):
                    pid = potion_pool.roll_potion(rng)
                    if not bag.full() and gold >= C.POTION_PRICE:
                        gold -= C.POTION_PRICE
                        bag.add(pid)
                        res.shop.append({"buy": "potion", "id": pid,
                                         "price": C.POTION_PRICE})
                res.gold = gold
            res.hp_by_node.append(hp)
            continue
        if kind == "R":
            # Policies flagged emergent_plan (adaptive) smith toward the
            # deck's own dominant shape, never the assigned label -- the
            # A/B contract is that adaptive ignores the label everywhere.
            rest_plan = archetype
            if getattr(policy, "emergent_plan", False):
                rest_plan = draft.dominant_archetype(
                    [loader.get_card(cid) for cid in deck_ids])
            action, target = rest_action(
                deck_ids, hp, max_hp, rest_plan,
                next_fight=(i + 1 < len(nodes)
                            and nodes[i + 1] in ("E", "B")))
            if action == "heal":
                hp = min(max_hp, hp + round(C.REST_HEAL_FRACTION * max_hp))
            elif action == "remove":
                deck_ids.remove(target)
            else:                               # M7: rest-site smithing
                deck_ids[deck_ids.index(target)] = target + upgrades.SUFFIX
            if held is not None:
                # Regal Pillow: extra heal at the campfire. Venerable Tea Set's
                # post_rest_energy is injected into the NEXT fight (just_rested).
                heal = held.post_rest_heal()
                if heal:
                    hp = min(max_hp, hp + heal)
            just_rested = True
            res.rests.append((i, action, target))
            res.hp_by_node.append(hp)
            continue
        enemies = build_node_encounter(kind, rng, act_draw)
        # Context-dependent combat effects (spec): base held-relic combat
        # effects + post_rest_energy (if we just rested) + elite_combat_start
        # (on E nodes). None when no relics are held -> identical to before.
        relic_fx = None
        if held is not None:
            relic_fx = held.combat_effects_for(kind, just_rested)
            just_rested = False
        if grant_potions and bag is not None:
            # Potion pass: build the fight with the held bag + node_kind context
            # so the combat use-policy can drink (offensive drinks gated to
            # elite/boss by node_kind). A COPY of bag.potions goes in; combat
            # mutates the player's own list, which we sync back after the fight.
            bag.slots = _potion_slots(held)
            potions_before = list(bag.potions)
            player = loader.build_player_from_ids(
                character, deck_ids, relic_effects=relic_fx,
                potions=list(bag.potions), potion_slots=bag.slots,
                node_kind=_NODE_KIND_CTX.get(kind, ""))
        else:
            potions_before = None
            player = loader.build_player_from_ids(character, deck_ids,
                                                  relic_effects=relic_fx)
        player.hp = hp
        player.max_hp = max_hp
        hp_start = hp
        state = run_fight(player, enemies, pilot,
                          seed=rng.randrange(2 ** 31))
        res.fight_stats.append(t0_metrics.extract(state, hp_start))
        fights += 1
        hp = state.player.hp
        # Combat-scoped effects such as Feed can raise max HP permanently.
        # Keep that mutation on the existing run-local state so the next
        # fight is not rebuilt with the old ceiling (a fuller RunState object
        # is a separate architecture decision, not required for correctness).
        max_hp = state.player.max_hp
        fight_won = state.player.alive and not state.living_enemies
        if grant_potions and bag is not None:
            # Sync consumed potions back: combat removed each drunk/spent potion
            # (incl. an auto-consumed Fairy) from player.potions, so the survivor
            # list IS the bag, and the difference is what was used this fight.
            res.potions_used.extend(
                _consumed(potions_before, state.player.potions))
            bag.potions = list(state.player.potions)
        if fight_won:
            # Burning Blood in the RUN LAYER (run-model rework §2): heal after
            # each won fight for relic-bearing characters. combat.py stays
            # emit-only; the heal that carries HP across fights lives ONLY
            # here, capped at max_hp.
            if "heal_after_won_fight" in player.relic_hooks:
                hp = min(max_hp, hp + C.BURNING_BLOOD_HEAL)
            gold += C.GOLD_INCOME.get(kind, 0)     # §5 per-fight income
            # Run-layer relic payouts on a won fight: gold_per_fight (Amethyst/
            # Aubergine) and fishing_rod's every-3rd-N-win upgrade.
            if held is not None:
                gold, hp = held.post_fight(kind, gold, hp, max_hp,
                                           deck_ids, rng)
            # W2: ELITE and BOSS wins grant a relic (Common pool -- boss-tier
            # relics are out of scope this pass). Normals give cards, not
            # relics, so N wins grant nothing here.
            if grant_relics and held is not None and kind in ("E", "B"):
                rid = relic_pool.roll_relic_reward(rng, held, character)
                if rid is not None:
                    hp, max_hp, gold = held.add(rid, character, hp, max_hp,
                                                gold, deck_ids, rng)
            # Potion pass: a POTION_DROP_CHANCE drop after a won NORMAL/ELITE
            # fight (bosses end the run, so no boss drop). Slot-permitting: a
            # full bag discards the drop (logged in bag.discarded).
            if grant_potions and bag is not None and kind in ("N", "E"):
                if rng.random() < C.POTION_DROP_CHANCE:
                    bag.slots = _potion_slots(held)
                    bag.add(potion_pool.roll_potion(rng))
            res.gold = gold
        res.hp_by_node.append(max(0, hp))
        if not fight_won:                   # death OR stall-out = run over
            res.death_node = i
            res.deck_ids = deck_ids
            if held is not None:
                res.relics = [r for r in held.ids if r not in seed_ids]
            if bag is not None:
                res.potions_end = list(bag.potions)
            return res
        final_act = act_i == n - 1
        if kind == "B":
            res.acts_completed += 1
        if kind != "B" or not final_act:
            # Reward screen. A FINAL boss ends the run with no reward; a
            # non-final boss shows the act-transition screen (§10.1): the
            # CARD offers are forced Rare -- the ratified "choice-of-3
            # Rares" boss drop -- and the companion slot is forced Rare
            # too. (Shipped Pass 1 forced only the companion slot; a
            # no-companion character got ordinary commons at the boundary
            # -- the Ironclad-0.6% diagnosis, 2026-07-23.)
            n_comp = 1
            if pity_k is not None and screens_since_companion >= pity_k:
                n_comp = 3                  # pity fires: choose-3 slot
            offers = rewards.roll_rewards(
                rng, character, companion_offers=n_comp, banner=banner,
                companion_rarity="rare" if kind == "B" else None,
                card_rarity="rare" if kind == "B" else None)
            deck_cards = [loader.get_card(cid) for cid in deck_ids]
            # Relevance is judged on the deck as it stood WHEN THE SCREEN WAS
            # SHOWN, before the pick lands -- judging after would let the pick
            # itself change the answer.
            advanced = draft.offer_advances_plan(offers, deck_cards, archetype)
            # Whether there was still a plan to advance. Core progress caps at
            # 1.0, so once the core is online NOTHING can advance it and
            # `advanced` is structurally False for the rest of the run. Without
            # this flag, relevance charges those screens to the pool as misses
            # -- and half of demolition's screens fall after its core completes.
            plan_live = not draft.core_complete(deck_cards, archetype)
            engaging = draft.offer_worth_engaging(offers, deck_cards,
                                                  archetype)
            pick = policy(rng, deck_cards, offers, archetype)
            res.decisions.append({
                "node": i, "offers": offers,
                "picked": pick.id if pick else None,
                "advanced_plan": advanced,
                "plan_live": plan_live,
                "engaging": engaging})
            if pick is not None:
                deck_ids.append(pick.id)
                if held is not None:               # Book of Five Rings tally
                    hp = held.note_cards_added(1, hp, max_hp)
            if pick is not None and pick.is_companion:
                screens_since_companion = 0
            else:
                screens_since_companion += 1
            if (res.time_to_online is None
                    and draft.core_complete(
                        [loader.get_card(cid) for cid in deck_ids],
                        archetype)):
                res.time_to_online = fights
        if kind == "B" and not final_act:
            # Act boundary (§10.1): the Ancient heals 100% of missing HP,
            # and on grant_relics runs offers a 1-of-3 Ancient-relic pick.
            # Deck, gold, relics and potions persist in their run locals;
            # only HP resets.
            hp = max_hp
            if grant_relics and held is not None:
                offer = relic_pool.ancient_offer(rng, held, character)
                pick = relic_pool.ancient_pick(offer, character)
                if pick is not None:
                    hp, max_hp, gold = held.add(pick, character, hp, max_hp,
                                                gold, deck_ids, rng)
    res.won = True
    res.deck_ids = deck_ids
    if held is not None:
        # W2: relics GRANTED this run (held minus any seed), in acquisition
        # order -- includes commons pulled by a grant_random_common boon.
        res.relics = [r for r in held.ids if r not in seed_ids]
    if bag is not None:
        res.potions_end = list(bag.potions)
    return res


def run_many(character: str, archetype: str, pilot_id: str,
             policy: DraftPolicy, runs: int, seed: int,
             slot_mode: str = "standard",
             relics: list[str] | None = None,
             grant_relics: bool = False,
             grant_potions: bool = False,
             n_acts: int | None = None) -> list[RunResult]:
    out = []
    for i in range(runs):
        r = run_one(character, archetype, pilot_id, policy, seed + i,
                    slot_mode=slot_mode, relics=relics,
                    grant_relics=grant_relics, grant_potions=grant_potions,
                    n_acts=n_acts)
        # draft_regret: sampled re-score in the final-deck context, using
        # a DEDICATED rng stream so sampling can't perturb run decisions.
        r.regret_samples = draft.draft_regret(
            random.Random(seed + i + 10 ** 9), r.decisions,
            [loader.get_card(cid) for cid in r.deck_ids], archetype)
        out.append(r)
    return out
