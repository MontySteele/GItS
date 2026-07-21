"""Realistic-ish Act 1 roster (run-model rework §4, RATIFIED 2026-07-21).

This is the tier0.5-ONLY realistic gauntlet that replaces the old
battery-derived node encounters in `model.build_node_encounter`. The
statlines live in `content/act1_pool.yaml`; this module loads them, rolls
spawn-time HP within each enemy's band, and owns the per-run draw:

  - EASY pool  -> the first three N nodes (fights 1-3)   §4.1
  - HARD pool  -> later N nodes (fight 4+)               §4.2
  - ELITE pool -> 3 enemies, DRAW 2 distinct per run     §4.3
  - BOSS       -> Vantom                                 §4.4

Draw rule (StS-real, §3.2): first 3 monster fights from easy, fights 4+
from hard, no encounter repeats within an act. `ActDraw` is created once
per run and threaded through `build_node_encounter`; ALL of its randomness
flows through the run's single `random.Random` -- same determinism contract
as tier0 (never `random.*` module globals).

LAYER BOUNDARY: the tier0 battery (tier0/content/encounters/) is frozen and
untouched. NO progression-gap compensator is applied here -- the roster uses
real StS2 numbers directly (§4); the old battery-calibrated compensator was
tuned against synthetic lites and does not carry over.
"""

from __future__ import annotations

import copy
import random
from functools import lru_cache
from pathlib import Path

import yaml

from tier0.engine.state import Enemy

_POOL_PATH = Path(__file__).parent / "content" / "act1_pool.yaml"

# StS-real draw rule (§3.2): the first three monster fights draw the easy
# pool; the elite NODES draw two DISTINCT enemies from the elite pool.
EASY_FIGHTS = 3
ELITES_PER_ACT = 2


@lru_cache(maxsize=1)
def _raw() -> dict:
    return yaml.safe_load(_POOL_PATH.read_text())


def pools() -> dict[str, list[dict]]:
    """The three draftable fight pools, keyed easy/hard/elite."""
    r = _raw()
    return {"easy": r["easy"], "hard": r["hard"], "elite": r["elite"]}


def boss_encounter() -> dict:
    """The act boss (Vantom). A single encounter, not a pool."""
    return _raw()["boss"][0]


def _roll_hp(hp, rng: random.Random) -> int:
    """HP is a spawn-time RANGE: [lo, hi] rolls uniformly per spawn; a bare
    int is a fixed statline. Rolled through the run rng, never Math.random."""
    if isinstance(hp, (list, tuple)):
        return rng.randint(hp[0], hp[1])
    return hp


def spawn(encounter: dict, rng: random.Random) -> list[Enemy]:
    """Materialize an encounter spec into live Enemies, rolling each body's
    HP within its band. `count` clones a body; `stagger` starts each clone
    a beat further into its rotation (the AoE elite's 4 bodies on offset
    standard cycles). Intents are deep-copied so the cached spec never
    mutates across spawns."""
    out: list[Enemy] = []
    for espec in encounter["enemies"]:
        count = espec.get("count", 1)
        stagger = espec.get("stagger", False)
        n_intents = len(espec["intents"])
        for i in range(count):
            hp = _roll_hp(espec["hp"], rng)
            idx = (i % n_intents) if stagger else espec.get("intent_index", 0)
            out.append(Enemy(
                hp=hp, max_hp=hp, name=espec["name"],
                intents=copy.deepcopy(espec["intents"]),
                is_boss=espec.get("is_boss", False),
                sleep_turns=espec.get("sleep_turns", 0),
                intent_index=idx))
    return out


class ActDraw:
    """Per-run encounter draw. Built once at run start (consuming the run
    rng) so easy/hard identity and the 2-of-3 elite draw are fixed for the
    run and replay identically under the same seed.

    No encounter repeats within an act: the easy pool (3 entries) is
    shuffled and consumed in order for the 3 easy fights; the elite pool
    (3 entries) is shuffled and the first two taken for the 2 elite nodes;
    the single hard N draws from the hard pool."""

    def __init__(self, rng: random.Random):
        p = pools()
        self._easy = list(p["easy"])
        rng.shuffle(self._easy)
        self._hard = list(p["hard"])
        elite = list(p["elite"])
        rng.shuffle(elite)
        self._elites = elite[:ELITES_PER_ACT]
        self._boss = boss_encounter()
        self._n_seen = 0
        self._e_seen = 0

    def encounter_for(self, kind: str, rng: random.Random) -> dict:
        if kind == "N":
            i = self._n_seen
            self._n_seen += 1
            if i < EASY_FIGHTS:               # first three N -> easy pool
                return self._easy[i]
            return rng.choice(self._hard)     # fight 4+ -> hard pool
        if kind == "E":
            spec = self._elites[self._e_seen]   # 2 distinct per run
            self._e_seen += 1
            return spec
        if kind == "B":
            return self._boss
        raise ValueError(f"non-fight node {kind!r} has no encounter")
