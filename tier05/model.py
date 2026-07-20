"""The run model (spec §2): 14-slot fixed template, HP persistence,
rest nodes, battery-derived normals. No pathing, no gold, no upgrades
(logged gap — DECISIONS.md).

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
from tier0.content import loader
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


def build_node_encounter(node_kind: str, rng: random.Random) -> list[Enemy]:
    """Battery-derived encounters only — same frozen statlines, no new
    tuning (spec §2). Lites are mechanical derivations, not designs."""
    if node_kind == "E":
        return loader.build_encounter("punisher")
    if node_kind == "B":
        return loader.build_encounter("tank_boss")
    if node_kind == "BC":
        return loader.build_encounter("burst_check")
    pool = list(C.NORMAL_POOL_WEIGHTS)
    weights = [C.NORMAL_POOL_WEIGHTS[p] for p in pool]
    pick = rng.choices(pool, weights=weights, k=1)[0]
    if pick == "swarm":
        return loader.build_encounter("swarm")
    if pick == "attrition_lite":
        spec = loader._encounter_index()["attrition"]["enemies"][0]
        lite = copy.deepcopy(spec)
        lite["hp"] = C.ATTRITION_LITE_HP
        return [Enemy(hp=lite["hp"], max_hp=lite["hp"], name="grinder_lite",
                      intents=copy.deepcopy(lite["intents"]))]
    if pick == "punisher_lite":
        spec = loader._encounter_index()["punisher"]["enemies"][0]
        lite = _scale_enemy_spec(spec, C.PUNISHER_LITE_SCALE)
        return [Enemy(hp=lite["hp"], max_hp=lite["hp"], name="punisher_lite",
                      intents=lite["intents"])]
    raise ValueError(f"unknown normal pool entry {pick!r}")


def rest_action(deck_ids: list[str], hp: int, max_hp: int) -> tuple[str, Optional[str]]:
    """Rest policy (spec §2): heal 30% max HP OR remove 1 card. Heal when
    hurt below the threshold; otherwise thin a basic. Removal preference:
    basic attacks first — basic block only if the defense quota survives."""
    if hp < C.REST_HEAL_THRESHOLD * max_hp:
        return "heal", None
    deck = [loader.get_card(cid) for cid in deck_ids]
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


def node_template() -> list[str]:
    nodes = list(C.RUN_NODE_TEMPLATE)
    nodes[C.BURST_CHECK_NODE] = "BC"    # the swapped-in burst check
    return nodes


def run_one(character: str, archetype: str, pilot_id: str,
            policy: DraftPolicy, seed: int) -> RunResult:
    rng = random.Random(seed)
    pilot = make_pilot(loader.pilot_weights(pilot_id))
    deck_ids = loader.starting_deck(character)
    max_hp = loader._character_index()[character]["hp"]
    hp = max_hp
    nodes = node_template()
    res = RunResult(seed=seed, won=False, death_node=None, hp_by_node=[],
                    deck_ids=deck_ids, node_kinds=nodes)
    fights = 0
    for i, kind in enumerate(nodes):
        if kind == "R":
            action, removed = rest_action(deck_ids, hp, max_hp)
            if action == "heal":
                hp = min(max_hp, hp + round(C.REST_HEAL_FRACTION * max_hp))
            else:
                deck_ids.remove(removed)
            res.rests.append((i, action, removed))
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
            offers = rewards.roll_rewards(rng, character)
            deck_cards = [loader.get_card(cid) for cid in deck_ids]
            pick = policy(rng, deck_cards, offers, archetype)
            res.decisions.append({
                "node": i, "offers": offers,
                "picked": pick.id if pick else None})
            if pick is not None:
                deck_ids.append(pick.id)
            if (res.time_to_online is None
                    and draft.core_complete(
                        [loader.get_card(cid) for cid in deck_ids],
                        archetype)):
                res.time_to_online = fights
    res.won = True
    res.deck_ids = deck_ids
    return res


def run_many(character: str, archetype: str, pilot_id: str,
             policy: DraftPolicy, runs: int, seed: int) -> list[RunResult]:
    out = []
    for i in range(runs):
        r = run_one(character, archetype, pilot_id, policy, seed + i)
        # draft_regret: sampled re-score in the final-deck context, using
        # a DEDICATED rng stream so sampling can't perturb run decisions.
        r.regret_samples = draft.draft_regret(
            random.Random(seed + i + 10 ** 9), r.decisions,
            [loader.get_card(cid) for cid in r.deck_ids], archetype)
        out.append(r)
    return out
