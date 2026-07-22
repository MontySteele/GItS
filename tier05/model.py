"""The run model (spec §2; run-model rework §3-§5): fixed node template
(RUNTEMPLATE_VERSION 3: "NNNRETN$ERB" -- 11 nodes, 7 fights, 2 rests, plus
a treasure T and a shop $), HP persistence, rest nodes with smithing (M7),
battery-derived fights (the realistic roster lands in a later phase).

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
from tier05 import act1, draft, rewards, shop
from tier05 import relics as relic_pool

# policy(rng, deck_cards, offers, archetype) -> Card | None
DraftPolicy = Callable[[random.Random, list[Card], list[Card], str],
                       Optional[Card]]


def build_node_encounter(node_kind: str, rng: random.Random,
                         draw: act1.ActDraw) -> list[Enemy]:
    """Realistic Act-1 roster (run-model rework §4). `draw` is the per-run
    ActDraw: it resolves node kind -> encounter (easy pool for the first
    three N nodes, hard pool for later N, the run's two drawn elites for E,
    Vantom for B), then `act1.spawn` rolls each body's HP within its band
    via the run rng.

    NO progression-gap compensator: this roster uses REAL StS2 numbers (§4),
    so the old battery-calibrated PROGRESSION_GAP_COMPENSATOR does not apply.
    The tier0 battery stays frozen and is no longer read at the run layer."""
    encounter = draw.encounter_for(node_kind, rng)
    return act1.spawn(encounter, rng)


def rest_action(deck_ids: list[str], hp: int, max_hp: int,
                archetype: str = "generic") -> tuple[str, Optional[str]]:
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
    fired at all."""
    if hp < C.REST_SMITH_DANGER * max_hp:
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


def node_template() -> list[str]:
    # RUNTEMPLATE_VERSION 3: "NNNRETN$ERB" -- the burst-check NODE is gone
    # (no BC swap). Node kinds: N/E/B fights, R rest, T treasure, $ shop.
    return list(C.RUN_NODE_TEMPLATE)


def run_one(character: str, archetype: str, pilot_id: str,
            policy: DraftPolicy, seed: int,
            slot_mode: str = "standard",
            relics: list[str] | None = None) -> RunResult:
    """slot_mode: 'standard' (1 companion offer) or 'pity(k)' — k screens
    without taking a companion make the next slot a choose-3.

    relics: relic ids the run STARTS holding (the W2 seam -- Neow + loot will
    populate it; for now the test/seed entry point). None -> no relics held,
    and the whole relic path is dead: build_player_from_ids is called with
    relic_effects=None exactly as before, so a relics=None run is byte-identical
    to the pre-relic model."""
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
    deck_ids = loader.starting_deck(character)
    max_hp = loader._character_index()[character]["hp"]
    hp = max_hp
    gold = C.GOLD_START
    removal_uses = 0
    # Held relics (the run-layer half). Constructed ONLY when a run actually
    # holds relics, so relics=None keeps every relic branch dead. Pickup relics
    # (max-HP / gold / deck upgrades) are applied ONCE, here at run start.
    held = None
    if relics:
        held = relic_pool.HeldRelics.hold(relics, character)
        hp, max_hp, gold = held.apply_pickups(hp, max_hp, gold, deck_ids, rng)
    just_rested = False
    nodes = node_template()
    # Per-run encounter draw (run-model rework §4): easy/hard identity and
    # the 2-of-3 elite draw are fixed here from the run rng, so the roster
    # replays identically under the same seed.
    act_draw = act1.ActDraw(rng)
    res = RunResult(seed=seed, won=False, death_node=None, hp_by_node=[],
                    deck_ids=deck_ids, node_kinds=nodes, banner=banner)
    fights = 0
    for i, kind in enumerate(nodes):
        if kind == "T":                     # treasure: gold lump + relic stub
            gold += C.TREASURE_GOLD
            shop.grant_treasure_relic(character, deck_ids)   # no-op (§1 stub)
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
            action, target = rest_action(deck_ids, hp, max_hp, rest_plan)
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
        fight_won = state.player.alive and not state.living_enemies
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
            res.gold = gold
        res.hp_by_node.append(max(0, hp))
        if not fight_won:                   # death OR stall-out = run over
            res.death_node = i
            res.deck_ids = deck_ids
            return res
        if kind != "B":                     # boss ends the run — no reward
            n_comp = 1
            if pity_k is not None and screens_since_companion >= pity_k:
                n_comp = 3                  # pity fires: choose-3 slot
            offers = rewards.roll_rewards(rng, character,
                                          companion_offers=n_comp,
                                          banner=banner)
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
    res.won = True
    res.deck_ids = deck_ids
    return res


def run_many(character: str, archetype: str, pilot_id: str,
             policy: DraftPolicy, runs: int, seed: int,
             slot_mode: str = "standard",
             relics: list[str] | None = None) -> list[RunResult]:
    out = []
    for i in range(runs):
        r = run_one(character, archetype, pilot_id, policy, seed + i,
                    slot_mode=slot_mode, relics=relics)
        # draft_regret: sampled re-score in the final-deck context, using
        # a DEDICATED rng stream so sampling can't perturb run decisions.
        r.regret_samples = draft.draft_regret(
            random.Random(seed + i + 10 ** 9), r.decisions,
            [loader.get_card(cid) for cid in r.deck_ids], archetype)
        out.append(r)
    return out
