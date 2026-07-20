"""The run model (spec §2): fixed node template (RUNTEMPLATE_VERSION 2:
11 fights, 3 rests with the pre-boss campfire guaranteed — ruling R7),
HP persistence, rest nodes with smithing (M7), battery-derived normals.
No pathing, no gold.

All randomness for a run flows through ONE random.Random seeded by the
harness (fight seeds, reward rolls, regret sampling) — determinism at
run granularity, same contract as Tier 0.
"""

from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Callable, Optional

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine.combat import run_fight
from tier0.engine.state import Card, Enemy
from tier0.harness import metrics as t0_metrics
from tier0.pilot.policy import make_pilot
from tier05 import draft, rewards

# policy(rng, deck_cards, offers, archetype) -> Card | None
DraftPolicy = Callable[[random.Random, list[Card], list[Card], str],
                       Optional[Card]]


def _scale_enemy_spec(spec: dict, scale: float) -> dict:
    out = copy.deepcopy(spec)
    out["hp"] = max(1, round(out["hp"] * scale))
    for intent in out["intents"]:
        for key in ("amount", "ramp"):
            if key in intent and intent["kind"] in ("attack",):
                intent[key] = max(1, round(intent[key] * scale))
    return out


def _apply_compensator(enemies: list[Enemy], tier: str) -> list[Enemy]:
    """Triage ruling 3b: the progression-gap compensator scales enemy hp
    and attack damage per node tier — one number standing in for the
    missing upgrades+relics growth, not a model of them. Tier 0 battery
    statlines themselves stay frozen; this is run-context only."""
    f = C.PROGRESSION_GAP_COMPENSATOR[tier]
    if f == 1.0:
        return enemies
    for e in enemies:
        e.hp = max(1, round(e.hp * f))
        e.max_hp = e.hp
        for intent in e.intents:
            if intent["kind"] == "attack":
                intent["amount"] = max(1, round(intent["amount"] * f))
                if "ramp" in intent:
                    intent["ramp"] = max(1, round(intent["ramp"] * f))
    return enemies


def build_node_encounter(node_kind: str, rng: random.Random) -> list[Enemy]:
    """Battery-derived encounters only — same frozen statlines, no new
    tuning (spec §2). Lites are mechanical derivations, not designs."""
    if node_kind == "E":
        return _apply_compensator(loader.build_encounter("punisher"), "elite")
    if node_kind == "B":
        return _apply_compensator(loader.build_encounter("tank_boss"), "boss")
    if node_kind == "BC":
        return _apply_compensator(loader.build_encounter("burst_check"),
                                  "normal")
    pool = list(C.NORMAL_POOL_WEIGHTS)
    weights = [C.NORMAL_POOL_WEIGHTS[p] for p in pool]
    pick = rng.choices(pool, weights=weights, k=1)[0]
    if pick == "swarm":
        out = loader.build_encounter("swarm")
    elif pick == "attrition_lite":
        spec = loader._encounter_index()["attrition"]["enemies"][0]
        lite = copy.deepcopy(spec)
        lite["hp"] = C.ATTRITION_LITE_HP
        out = [Enemy(hp=lite["hp"], max_hp=lite["hp"], name="grinder_lite",
                     intents=copy.deepcopy(lite["intents"]))]
    elif pick == "punisher_lite":
        spec = loader._encounter_index()["punisher"]["enemies"][0]
        lite = _scale_enemy_spec(spec, C.PUNISHER_LITE_SCALE)
        out = [Enemy(hp=lite["hp"], max_hp=lite["hp"], name="punisher_lite",
                     intents=lite["intents"])]
    else:
        raise ValueError(f"unknown normal pool entry {pick!r}")
    if C.NORMAL_ATTRITION_SCALE != 1.0:
        # R7 sweep knob: attack amounts only, plain normals only -- HP is
        # untouched so fight length (and thus draft economy) stays put.
        for e in out:
            for intent in e.intents:
                if intent["kind"] == "attack":
                    intent["amount"] = max(1, round(
                        intent["amount"] * C.NORMAL_ATTRITION_SCALE))
    return _apply_compensator(out, "normal")


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


def node_template() -> list[str]:
    nodes = list(C.RUN_NODE_TEMPLATE)
    nodes[C.BURST_CHECK_NODE] = "BC"    # the swapped-in burst check
    return nodes


def run_one(character: str, archetype: str, pilot_id: str,
            policy: DraftPolicy, seed: int,
            slot_mode: str = "standard") -> RunResult:
    """slot_mode: 'standard' (1 companion offer) or 'pity(k)' — k screens
    without taking a companion make the next slot a choose-3."""
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
    nodes = node_template()
    res = RunResult(seed=seed, won=False, death_node=None, hp_by_node=[],
                    deck_ids=deck_ids, node_kinds=nodes, banner=banner)
    fights = 0
    for i, kind in enumerate(nodes):
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
            res.rests.append((i, action, target))
            res.hp_by_node.append(hp)
            continue
        enemies = build_node_encounter(kind, rng)
        player = loader.build_player_from_ids(character, deck_ids)
        player.hp = hp
        player.max_hp = max_hp
        hp_start = hp
        state = run_fight(player, enemies, pilot,
                          seed=rng.randrange(2 ** 31))
        res.fight_stats.append(t0_metrics.extract(state, hp_start))
        fights += 1
        hp = state.player.hp
        res.hp_by_node.append(max(0, hp))
        fight_won = state.player.alive and not state.living_enemies
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
             slot_mode: str = "standard") -> list[RunResult]:
    out = []
    for i in range(runs):
        r = run_one(character, archetype, pilot_id, policy, seed + i,
                    slot_mode=slot_mode)
        # draft_regret: sampled re-score in the final-deck context, using
        # a DEDICATED rng stream so sampling can't perturb run decisions.
        r.regret_samples = draft.draft_regret(
            random.Random(seed + i + 10 ** 9), r.decisions,
            [loader.get_card(cid) for cid in r.deck_ids], archetype)
        out.append(r)
    return out
