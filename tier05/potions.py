"""Run-layer potion pool + held-bag (potion pass).

The COMBAT half of every potion lives in tier0/engine/potions.py, applied off
``Player.potions``. This module owns the RUN half: it loads the pool
(tier05/content/potions.yaml), rolls rarity-weighted drops/shop stock through
the run's single ``random.Random``, and models the held bag (potions + slot
count, overflow discarded and logged).

LAYER BOUNDARY: combat.py and the frozen tier0 battery are untouched. Potions
are granted only on grant_potions=True runs; a run that never grants potions
never touches this module, so the pre-potion model is byte-identical.

Determinism: every roll flows through the run rng passed in -- never a module
global, never random.*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

import random

import yaml

_POOL_PATH = Path(__file__).parent / "content" / "potions.yaml"

# Fixed tier order: iterated deterministically for the weighted roll.
_TIER_ORDER = ("common", "uncommon", "rare")

# The engine is the single source of truth for which ids it can apply; the run
# layer must never roll a potion the engine cannot honour. Imported rather than
# duplicated, same discipline tier05/relics.py uses for the relic vocabulary.
from tier0.engine.potions import KNOWN as _ENGINE_KNOWN


# ---------------------------------------------------------------------------
# Pool loading.
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _pool() -> dict:
    raw = yaml.safe_load(_POOL_PATH.read_text()) or {}
    # Guard the layer contract: every yaml potion id must be one the engine can
    # apply. A typo or an id the engine lacks is a loud error, never a silently
    # unrollable dead id.
    for tier in _TIER_ORDER:
        for pid in (raw.get(tier) or {}):
            if pid not in _ENGINE_KNOWN:
                raise ValueError(
                    f"potion {pid!r} in tier {tier!r} is unknown to the engine "
                    f"(tier0/engine/potions.py KNOWN) -- pool/engine mismatch.")
    return raw


def tiers() -> dict[str, list[str]]:
    """tier name -> sorted list of potion ids in that tier."""
    pool = _pool()
    return {t: sorted((pool.get(t) or {}).keys()) for t in _TIER_ORDER}


def pool() -> dict[str, dict]:
    """Flat id -> {name, tier} for every potion in the pool."""
    out: dict[str, dict] = {}
    raw = _pool()
    for t in _TIER_ORDER:
        for pid, spec in (raw.get(t) or {}).items():
            out[pid] = {"name": (spec or {}).get("name", pid), "tier": t}
    return out


def name_of(pid: str) -> str:
    return pool().get(pid, {}).get("name", pid)


def _weights() -> dict[str, float]:
    return dict((_pool().get("weights") or {}))


# ---------------------------------------------------------------------------
# Rarity-weighted roll (all randomness through the run rng).
# ---------------------------------------------------------------------------

def roll_potion(rng: random.Random) -> str:
    """Roll ONE potion id: pick a tier by its weight, then a potion uniformly
    within that tier. Common-frequent, rare-scarce -- and rare holds only
    fairy_in_a_bottle, so its low weight is what makes the revive scarce.

    Deterministic: consumes one rng.random() (tier) + one rng.choice (id) off
    the run's single Random. Tiers/ids are iterated in a fixed sorted order so
    the same seed always rolls the same potion."""
    tiers_map = tiers()
    weights = _weights()
    # Only tiers that actually hold potions participate.
    live = [(t, weights.get(t, 0.0)) for t in _TIER_ORDER if tiers_map.get(t)]
    total = sum(w for _, w in live)
    if total <= 0:
        # No weights configured: fall back to a flat pick over every id.
        allids = sorted(pid for t in _TIER_ORDER for pid in tiers_map.get(t, []))
        return rng.choice(allids)
    r = rng.random() * total
    acc = 0.0
    chosen = live[-1][0]
    for t, w in live:
        acc += w
        if r < acc:
            chosen = t
            break
    return rng.choice(tiers_map[chosen])


# ---------------------------------------------------------------------------
# Held bag: the potions a run holds + its slot count. Overflow is discarded and
# logged (StS has no "swap" prompt in this model -- a full bag drops the drop).
# ---------------------------------------------------------------------------

@dataclass
class PotionBag:
    potions: list[str] = field(default_factory=list)
    slots: int = 0
    discarded: list[str] = field(default_factory=list)   # overflow log

    def free(self) -> int:
        return max(0, self.slots - len(self.potions))

    def full(self) -> bool:
        return len(self.potions) >= self.slots

    def add(self, pid: str) -> bool:
        """Add ``pid`` if a slot is free. On overflow the drop is DISCARDED
        (recorded in ``discarded``) and False is returned -- never silently
        dropped, never over-filled past ``slots``."""
        if self.full():
            self.discarded.append(pid)
            return False
        self.potions.append(pid)
        return True
