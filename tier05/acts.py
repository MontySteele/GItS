"""Realistic-ish act rosters (run-model rework §4 + §10).

Generalizes the former ``tier05/act1.py`` (RATIFIED 2026-07-21) to the
multi-act world (§10, RATIFIED 2026-07-23): every act is the same machine --
an easy/hard/elite/boss pool file -- and this module loads a pool per act,
rolls spawn-time HP within each enemy's band, and owns the per-run draw:

  - EASY pool  -> the first `easy_fights` N nodes (Act 1: 3, Acts 2-3: 2,
                  the real StS2 rule)                          §4.1 / §10.1
  - HARD pool  -> later N nodes                                §4.2
  - ELITE pool -> 3 enemies, DRAW 2 distinct per act           §4.3
  - BOSS pool  -> >= 2 bosses, DRAW 1 per act (§10.0 ruling:
                  boss pools everywhere, including Act 1)      §10.5

The act registry is ``constants.RUN_ACTS``: one spec per act (pool file +
easy_fights). Acts 2-3 land in Passes 2-3 by appending specs there; the run
model spans ALL registered acts by default.

Draw rule (StS-real, §3.2): the first `easy_fights` monster fights come from
the easy pool, later fights from hard, no encounter repeats within an act.
`ActDraw` is created once per ACT and threaded through
`model.build_node_encounter`; ALL of its randomness flows through the run's
single `random.Random` -- same determinism contract as tier0 (never
`random.*` module globals).

LAYER BOUNDARY: the tier0 battery (tier0/content/encounters/) is frozen and
untouched. NO progression-gap compensator is applied here -- rosters use
real StS2 numbers directly (§4); the old battery-calibrated compensator was
tuned against synthetic lites and does not carry over.
"""

from __future__ import annotations

import copy
import random
from functools import lru_cache
from pathlib import Path

import yaml

from tier0 import constants as C
from tier0.engine.state import Enemy

_CONTENT_DIR = Path(__file__).parent / "content"

# DEAD as of §11: the old "two distinct elites per act" rule existed because
# the authored template had exactly two elite NODES. Under a real map the
# count is a routing outcome, so elites are drawn per node instead (ActDraw).
# Kept as a name so archived tools referencing it still import.
ELITES_PER_ACT = 2


# --- content-boundary allowlists (audit sec.5) -----------------------------
# The act pools are the largest content in the repo and read every key through
# `.get()`, so a typo'd key does not fail -- it silently does nothing. The
# audit's example is exact: `is_bos: true` makes a non-boss boss with no signal
# anywhere, and the encounter then fills a boss slot with an ordinary statline.
# Same guard shape as tier05/potions.py, which validates loudly because it is
# small enough that somebody bothered.
POOL_TIERS = frozenset({"easy", "hard", "elite", "boss"})

ENCOUNTER_KEYS = frozenset({"id", "name", "enemies"})

ENEMY_KEYS = frozenset({
    "name", "hp", "intents", "count",
    "is_boss",         # boss accounting (and the audit's typo example)
    # NOT "is_minion": the sim's MinionPower mirror (NC-7 alpha, Q13/R117)
    # is set by the SUMMON spawn path (tier0/engine/combat.py), which is the
    # only mechanical source -- no authored pool enemy carries the fact
    # (Kaiser Crab's claws are slotted monsters, verified by reflection), and
    # test_content_boundaries forbids allowlisting a key no pool uses. Add it
    # here (and in `spawn` below) the day a pool authors one.
    "phases",          # multi-phase bosses
    "on_ally_death",   # reaction to a sibling dying
    "skittish", "slow", "stagger", "sleep_turns",
})

INTENT_KEYS = frozenset({
    "kind", "amount", "times", "count",
    "power", "status", "pile",     # buff / debuff / status payloads
    "ramp", "ramp_after",          # escalating intents
    "wave",                        # summon waves
})


def _validate_pool(pool_file: str, raw: dict) -> dict:
    def check(where: str, mapping: dict, allowed: frozenset) -> None:
        unknown = set(mapping) - allowed
        if unknown:
            raise ValueError(
                f"{pool_file}: {where}: unknown key(s) {sorted(unknown)}. "
                "A key nothing reads is a silent no-op -- add it to the "
                "allowlist in tier05/acts.py AND to the reader, or fix the "
                "spelling.")

    unknown_tiers = set(raw or {}) - POOL_TIERS
    if unknown_tiers:
        raise ValueError(
            f"{pool_file}: unknown pool tier(s) {sorted(unknown_tiers)}")
    for tier, encounters in (raw or {}).items():
        for enc in encounters or []:
            eid = enc.get("id", "?")
            check(f"{tier}/{eid}", enc, ENCOUNTER_KEYS)
            for enemy in enc.get("enemies") or []:
                name = enemy.get("name", "?")
                check(f"{tier}/{eid}/{name}", enemy, ENEMY_KEYS)
                for intent in enemy.get("intents") or []:
                    check(f"{tier}/{eid}/{name}/intent", intent, INTENT_KEYS)
    return raw


@lru_cache(maxsize=None)
def _load(pool_file: str) -> dict:
    """Pool YAML by FILENAME (not act index), so a monkeypatched RUN_ACTS in
    tests can never serve a stale cache entry for a different file."""
    return _validate_pool(
        pool_file, yaml.safe_load((_CONTENT_DIR / pool_file).read_text(encoding="utf-8")))


def n_acts() -> int:
    """How many acts are registered (the default run spans them all)."""
    return len(C.RUN_ACTS)


def _raw(act: int) -> dict:
    try:
        spec = C.RUN_ACTS[act]
    except IndexError:
        raise ValueError(
            f"act {act} is not registered -- RUN_ACTS defines "
            f"{len(C.RUN_ACTS)} act(s)") from None
    return _load(spec["pool"])


def easy_fights(act: int) -> int:
    """How many N fights this act draws from its easy pool (Act 1: 3,
    Acts 2-3: 2 -- the real StS2 rule, §10.1)."""
    return int(C.RUN_ACTS[act]["easy_fights"])


def pools(act: int = 0) -> dict[str, list[dict]]:
    """The three draftable fight pools for an act, keyed easy/hard/elite."""
    r = _raw(act)
    return {"easy": r["easy"], "hard": r["hard"], "elite": r["elite"]}


def boss_pool(act: int = 0) -> list[dict]:
    """The act's boss POOL (§10.0 ruling: >= 2 per act; ActDraw draws 1)."""
    return list(_raw(act)["boss"])


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
            phases = copy.deepcopy(espec.get("phases") or [])
            out.append(Enemy(
                hp=hp, max_hp=hp, name=espec["name"],
                intents=copy.deepcopy(espec["intents"]),
                is_boss=espec.get("is_boss", False),
                sleep_turns=espec.get("sleep_turns", 0),
                intent_index=idx,
                # §10.9 promotions: per-card-played counterplay powers.
                slow=espec.get("slow", 0),
                skittish=espec.get("skittish", 0),
                # §10.2 boss ops. A phased enemy is fatal-exempt until its
                # LAST phase (combat._settle_phases flips it back) so Feed
                # can never farm a phase-down for permanent max HP.
                ally_death_buff=copy.deepcopy(espec.get("on_ally_death")),
                phases=phases,
                counts_for_fatal=not phases))
    return out


class ActDraw:
    """Per-act encounter draw. Built once at each act's start (consuming the
    run rng) so easy/hard identity, the 2-of-3 elite draw and the boss draw
    are fixed for the act and replay identically under the same seed.

    The easy pool is shuffled and consumed in order for the act's
    `easy_fights` easy fights; later N draw from the hard pool. ELITES draw
    per node from the act's shuffled pool, never the same one twice in a row
    (§11: the run fights however many the route finds, so a pre-drawn pair
    would cap it at two -- which is exactly the authored constant the map
    layer exists to remove). The boss is ONE draw from the act's boss pool
    (§10.5 -- a 1-entry pool still consumes the draw, so growing a pool never
    silently renumbers the other streams)."""

    def __init__(self, rng: random.Random, act: int = 0):
        p = pools(act)
        self.act = act
        self._easy_fights = easy_fights(act)
        self._easy = list(p["easy"])
        rng.shuffle(self._easy)
        self._hard = list(p["hard"])
        self._elite_pool = list(p["elite"])
        rng.shuffle(self._elite_pool)
        self._last_elite = None
        bosses = boss_pool(act)
        self._boss = bosses[rng.randrange(len(bosses))]
        self._n_seen = 0
        self._e_seen = 0

    def encounter_for(self, kind: str, rng: random.Random) -> dict:
        if kind == "N":
            i = self._n_seen
            self._n_seen += 1
            if i < min(self._easy_fights, len(self._easy)):
                return self._easy[i]          # first easy_fights N -> easy
            return rng.choice(self._hard)     # later N -> hard pool
        if kind == "E":
            # §11: how many elites a run fights is a ROUTING outcome (0-5),
            # not a fixed 2, so the draw can no longer pre-pick a pair. The
            # real rule: the same elite may appear more than once in an act
            # but never twice in a row (Map Locations).
            choices = [e for e in self._elite_pool
                       if e["id"] != self._last_elite] or self._elite_pool
            spec = choices[rng.randrange(len(choices))]
            self._last_elite = spec["id"]
            self._e_seen += 1
            return spec
        if kind == "B":
            return self._boss
        raise ValueError(f"non-fight node {kind!r} has no encounter")
