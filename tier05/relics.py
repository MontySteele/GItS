"""Run-layer relic application (relic-content pass).

The COMBAT half of every relic lives in tier0/engine/relics.py, read off
``Player.relic_effects``. This module owns the RUN half: it loads the pool
(tier05/content/relics.yaml), splits a held set into combat-scoped effects
(handed verbatim to loader.build_player_from_ids) and run-scoped effects
(max-HP/gold/heal/deck ops applied here and in tier05/model.py), and computes
the CONTEXT-DEPENDENT combat injections (post-rest energy, elite draw/energy)
that combat.py -- which is context-free by design -- cannot compute itself.

LAYER BOUNDARY: combat.py and the frozen tier0 battery are untouched. A run
that holds no relics never constructs a HeldRelics with effects, so
build_player_from_ids is called with relic_effects=None exactly as before.

Determinism: the only randomness here (fishing_rod's card pick) flows through
the run's single random.Random, passed in -- never a module global.

House rule: a run hook this module does not recognise raises a loud
``warnings.warn`` rather than being silently dropped.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

import random

import yaml

from tier0.content import loader, upgrades
from tier0.engine import relics as engine_relics

_POOL_PATH = Path(__file__).parent / "content" / "relics.yaml"

# Combat-scoped hooks: the engine is the single source of truth for what it
# consumes, so we import its set rather than duplicating the vocabulary.
COMBAT_HOOKS = frozenset(engine_relics.COMBAT_HOOKS)

# Run-scoped hooks handled in this module + model.py. Engine RUN_HOOKS plus
# pickup_upgrade (a pure deck op that never rides in relic_effects).
RUN_HOOKS = frozenset(engine_relics.RUN_HOOKS) | {"pickup_upgrade"}


# ---------------------------------------------------------------------------
# Pool loading.
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _pool() -> dict:
    raw = yaml.safe_load(_POOL_PATH.read_text()) or {}
    # SKIP relics: warn once, loudly, naming the missing mechanic. They are
    # NEVER handed back as playable relics (get_relic refuses them).
    for rid, spec in (raw.get("skip") or {}).items():
        warnings.warn(
            f"relic {rid!r} SKIPPED: {spec.get('missing', 'unknown mechanic')} "
            f"-- not implemented, not faked (house rule).",
            stacklevel=2)
    return raw


def common_pool() -> dict[str, dict]:
    """id -> relic spec for the shared common pool."""
    return dict(_pool().get("common") or {})


def neow_pool() -> dict[str, dict]:
    """id -> relic spec for the 3 Neow persistent relics."""
    return dict(_pool().get("neow") or {})


def skipped_ids() -> frozenset[str]:
    return frozenset((_pool().get("skip") or {}).keys())


def get_relic(rid: str) -> dict:
    """Fetch a relic spec by id from common or neow. A SKIP relic or an unknown
    id is a hard error -- never a hollow relic."""
    pool = _pool()
    for group in ("common", "neow"):
        if rid in (pool.get(group) or {}):
            return (pool[group])[rid]
    if rid in (pool.get("skip") or {}):
        raise KeyError(f"relic {rid!r} is a SKIP relic (missing mechanic) and "
                       f"cannot be held -- see loader warning.")
    raise KeyError(f"unknown relic id {rid!r}")


# ---------------------------------------------------------------------------
# Effect split.
# ---------------------------------------------------------------------------

def _relic_effects(rid: str, character: str) -> list[dict]:
    """A relic's effects, owner-gated. A non-owner holding an owner-locked relic
    (Red Skull on a non-Ironclad) contributes nothing, loudly."""
    spec = get_relic(rid)
    owner = spec.get("owner")
    if owner and character not in owner:
        warnings.warn(
            f"relic {rid!r} is owner-locked to {owner}; {character!r} holds it "
            f"but gains nothing from it.", stacklevel=2)
        return []
    return list(spec.get("effects") or [])


def split_effects(held_ids: list[str], character: str
                  ) -> tuple[list[dict], list[dict]]:
    """(combat_effects, run_effects) for a held set. Combat effects are the
    dicts handed to build_player_from_ids; run effects are applied here.

    An effect whose hook is in NEITHER vocabulary is a loud warning (house
    rule) and is dropped from both lists."""
    combat: list[dict] = []
    run: list[dict] = []
    for rid in held_ids:
        for fx in _relic_effects(rid, character):
            hook = fx.get("hook")
            if hook in COMBAT_HOOKS:
                combat.append(fx)
            elif hook in RUN_HOOKS:
                run.append(fx)
            else:
                warnings.warn(
                    f"relic {rid!r}: hook {hook!r} is in no vocabulary -- "
                    f"dropped (never approximated).", stacklevel=2)
    return combat, run


# ---------------------------------------------------------------------------
# Held-relic run state: counters + the run-layer application helpers model
# threads through a run. Constructed ONLY when a run actually holds relics, so
# a relics=None run never touches any of this.
# ---------------------------------------------------------------------------

@dataclass
class HeldRelics:
    ids: list[str]
    character: str
    combat_effects: list[dict] = field(default_factory=list)
    run_effects: list[dict] = field(default_factory=list)
    # run counters (spec: cards_added_total, normal_fights_won)
    cards_added_total: int = 0
    normal_fights_won: int = 0
    _book_chunks_healed: int = 0

    @classmethod
    def hold(cls, ids: list[str], character: str) -> "HeldRelics":
        combat, run = split_effects(ids, character)
        return cls(ids=list(ids), character=character,
                   combat_effects=combat, run_effects=run)

    # --- run-hook lookups -------------------------------------------------

    def _run(self, hook: str) -> list[dict]:
        return [fx for fx in self.run_effects if fx.get("hook") == hook]

    def has_run_effects(self) -> bool:
        return bool(self.run_effects)

    # --- combat effect assembly (context-dependent, spec) -----------------

    def combat_effects_for(self, node_kind: str,
                           just_rested: bool) -> list[dict]:
        """Effective per-fight relic_effects: the base held combat effects plus
        the context injections combat.py cannot compute -- post_rest_energy (if
        the previous node was a rest) and elite_combat_start (on E nodes)."""
        effects = list(self.combat_effects)
        if just_rested:
            for fx in self._run("post_rest_energy"):
                effects.append({"hook": "combat_start_energy",
                                "amount": int(fx["amount"])})
        if node_kind == "E":
            for fx in self._run("elite_combat_start"):
                if int(fx.get("draw", 0)):
                    effects.append({"hook": "combat_start_draw",
                                    "amount": int(fx["draw"])})
                if int(fx.get("energy", 0)):
                    effects.append({"hook": "combat_start_energy",
                                    "amount": int(fx["energy"])})
        return effects

    # --- pickup (once, at run start for seeded relics) --------------------

    def apply_pickups(self, hp: int, max_hp: int, gold: int,
                      deck_ids: list[str], rng: random.Random
                      ) -> tuple[int, int, int]:
        """on_pickup_maxhp / gold_on_pickup / pickup_upgrade. Mutates deck_ids
        in place (upgrades); returns updated (hp, max_hp, gold)."""
        for fx in self.run_effects:
            hook = fx.get("hook")
            if hook == "on_pickup_maxhp":
                amt = int(fx["amount"])
                max_hp += amt
                hp += amt
            elif hook == "gold_on_pickup":
                gold += int(fx["amount"])
            elif hook == "pickup_upgrade":
                self._pickup_upgrade(deck_ids, fx.get("kind"),
                                     int(fx.get("count", 0)), rng)
        return hp, max_hp, gold

    def _pickup_upgrade(self, deck_ids: list[str], kind: Optional[str],
                        count: int, rng: random.Random) -> None:
        """Upgrade up to `count` random deck cards of card-type `kind`
        (skill/attack) that have an upgrade path. In-place id rewrite."""
        cands = []
        for idx, cid in enumerate(deck_ids):
            if not upgrades.has_upgrade(cid):
                continue
            card = loader.get_card(cid)
            if kind is None or card.type == kind:
                cands.append(idx)
        rng.shuffle(cands)
        for idx in cands[:count]:
            deck_ids[idx] = deck_ids[idx] + upgrades.SUFFIX

    # --- card-add tracking (Book of Five Rings) ---------------------------

    def note_cards_added(self, n: int, hp: int, max_hp: int) -> int:
        """Record `n` cards added to the deck; return hp after any Book of Five
        Rings heal(s) that the new cumulative total unlocked."""
        if n <= 0:
            return hp
        self.cards_added_total += n
        for fx in self._run("book_of_five_rings"):
            per = int(fx.get("per", 5))
            heal = int(fx.get("heal", 0))
            if per <= 0:
                continue
            chunks = self.cards_added_total // per
            new = chunks - self._book_chunks_healed
            if new > 0:
                self._book_chunks_healed = chunks
                hp = min(max_hp, hp + heal * new)
        return hp

    # --- post-fight (won) -------------------------------------------------

    def post_fight(self, node_kind: str, gold: int, hp: int, max_hp: int,
                   deck_ids: list[str], rng: random.Random,
                   disable_heal: bool = False) -> tuple[int, int]:
        """After a WON fight: gold_per_fight, and (on N wins) fishing_rod's
        every-3rd-win upgrade. Returns (gold, hp). `disable_heal` gates any
        heal-shaped payout (none in this pool, but kept correct/cheap)."""
        for fx in self._run("gold_per_fight"):
            gold += int(fx["amount"])
        if node_kind == "N":
            self.normal_fights_won += 1
            for fx in self._run("fishing_rod"):
                per = int(fx.get("per", 3))
                if per > 0 and self.normal_fights_won % per == 0:
                    self._fishing_upgrade(deck_ids, rng)
        return gold, hp

    def _fishing_upgrade(self, deck_ids: list[str],
                         rng: random.Random) -> None:
        cands = [i for i, cid in enumerate(deck_ids)
                 if upgrades.has_upgrade(cid)]
        if not cands:
            return
        idx = rng.choice(cands)
        deck_ids[idx] = deck_ids[idx] + upgrades.SUFFIX

    # --- rest / shop heal lookups -----------------------------------------

    def post_rest_heal(self) -> int:
        return sum(int(fx["amount"]) for fx in self._run("post_rest_heal"))

    def shop_heal(self) -> int:
        return sum(int(fx["amount"]) for fx in self._run("shop_heal"))
