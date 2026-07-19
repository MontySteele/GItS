"""Seven-axis scorecard (spec §2), normalized so REF_IRONCLAD starter = 3.0.

Raw axis values are computed from pooled battery stats; scores are
baseline-relative ratios (inverted where lower-is-better), capped at 10.
Where a raw baseline can be ~0 (A5 velocity: starter has no extra draw),
the raw value includes the base turn economy so ratios stay finite —
noted per-axis below.
"""

from __future__ import annotations

import math

from tier0 import constants as C
from tier0.harness.metrics import FightStats

AXES = ["A1_frontload", "A2_scaling", "A3_block", "A4_sustain",
        "A5_velocity", "A6_utility", "A7_setup_tax"]

SCORE_CAP = 10.0
_BASE_ECONOMY = C.CARDS_DRAWN_PER_TURN + C.BASE_ENERGY_PER_TURN  # A5 anchor


def _pool(stats_by_enc: dict[str, list[FightStats]]) -> list[FightStats]:
    return [s for stats in stats_by_enc.values() for s in stats]


def _avg(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def raw_axes(stats_by_enc: dict[str, list[FightStats]]) -> dict[str, float]:
    pooled = _pool(stats_by_enc)

    # A1: damage dealt turns 1-3 per energy spent turns 1-3.
    e13 = sum(sum(s.energy_by_turn.get(t, 0) for t in (1, 2, 3)) for s in pooled)
    d13 = sum(sum(s.damage_by_turn.get(t, 0) for t in (1, 2, 3)) for s in pooled)
    a1 = d13 / max(1, e13)

    # A2: DPT t8-10 / DPT t1-3, fights that reached turn 10 (TANK BOSS mostly).
    ratios = []
    for s in pooled:
        if s.turns >= 10:
            lo = _avg(s.damage_by_turn.get(t, 0) for t in (1, 2, 3))
            hi = _avg(s.damage_by_turn.get(t, 0) for t in (8, 9, 10))
            if lo > 0:
                ratios.append(hi / lo)
    a2 = _avg(ratios) or 1.0

    # A3: enemy damage absorbed by block, per energy (ATTRITION pool if
    # present, else all fights). "Damage prevented by kills" deferred.
    a3_pool = stats_by_enc.get("attrition", pooled) or pooled
    a3 = (sum(s.damage_blocked for s in a3_pool)
          / max(1, sum(s.energy_spent for s in a3_pool)))

    # A4: net HP delta per fight (negative = chip taken).
    a4 = _avg(s.hp_delta for s in pooled)

    # A5: (extra draws + extra energy) per turn, anchored on base economy
    # so the starter baseline (0 extra) still normalizes.
    a5 = _BASE_ECONOMY + (sum(s.cards_drawn_extra + s.energy_generated_extra
                              for s in pooled)
                          / max(1, sum(s.turns for s in pooled)))

    # A6: composite utility — AoE coverage (single-target TTK / swarm TTK;
    # AoE decks push it up) x (1 + debuff uptime).
    swarm_ttk = _avg(s.turns for s in stats_by_enc.get("swarm", [])) or 1.0
    single_ttk = _avg(s.turns for s in stats_by_enc.get("punisher", [])) or 1.0
    uptime = (sum(s.debuffed_intents for s in pooled)
              / max(1, sum(s.total_intents for s in pooled)))
    a6 = (single_ttk / swarm_ttk) * (1.0 + uptime)

    # A7: setup tax — avg first turn where the 3-turn-window DPT reaches
    # 70% of the config's OWN peak window (self-referential: "when does
    # YOUR plan come online", independent of absolute power). The old
    # 1.5x-baseline threshold saturated for any competent deck.
    a7 = _avg(_turns_to_own_peak(s) for s in pooled)

    return {"A1_frontload": a1, "A2_scaling": a2, "A3_block": a3,
            "A4_sustain": a4, "A5_velocity": a5, "A6_utility": a6,
            "A7_setup_tax": a7}


def _turns_to_own_peak(s: FightStats) -> int:
    windows = {t: _avg(s.damage_by_turn.get(x, 0)
                       for x in range(max(1, t - 2), t + 1))
               for t in range(1, s.turns + 1)}
    if not windows:
        return C.MAX_TURNS
    threshold = 0.7 * max(windows.values())
    for t in range(1, s.turns + 1):
        if windows[t] >= threshold and threshold > 0:
            return t
    return C.MAX_TURNS


def normalize(raw: dict[str, float], baseline: dict[str, float]) -> dict[str, float]:
    """Score each axis so baseline = 3.0. Higher = better on every axis."""
    eps = 1e-9
    scores = {}
    for ax in AXES:
        r, b = raw[ax], baseline[ax]
        if ax == "A4_sustain":
            # Lower HP loss is better; net healing caps out.
            loss_r, loss_b = max(eps, -r), max(eps, -b)
            score = 3.0 * loss_b / loss_r
        elif ax == "A7_setup_tax":
            score = 3.0 * b / max(eps, r)      # fewer setup turns = better
        else:
            score = 3.0 * r / max(eps, b)
        scores[ax] = min(SCORE_CAP, score)
    return scores


def curve_exponent(stats: list[FightStats]) -> float:
    """Log-log least-squares fit of mean DPT vs turn: ~1 linear-flat,
    >1 superlinear. Logged alongside A2 (spec §2)."""
    max_t = max((s.turns for s in stats), default=0)
    points = []
    for t in range(1, max_t + 1):
        vals = [s.damage_by_turn.get(t, 0) for s in stats if s.turns >= t]
        mean = _avg(vals)
        if mean > 0:
            points.append((math.log(t), math.log(mean)))
    if len(points) < 3:
        return 0.0
    n = len(points)
    sx = sum(x for x, _ in points)
    sy = sum(y for _, y in points)
    sxx = sum(x * x for x, _ in points)
    sxy = sum(x * y for x, y in points)
    denom = n * sxx - sx * sx
    return (n * sxy - sx * sy) / denom if denom else 0.0


def heuristic_flags(scores: dict[str, float]) -> list[str]:
    """Spec §2 balance heuristic: healthy = 4-5 on exactly two axes,
    <=2 on at least one."""
    flags = []
    strong = [a for a, v in scores.items() if v >= 4.0]
    weak = [a for a, v in scores.items() if v <= 2.0]
    if len(strong) == 0:
        flags.append("FLAT (no axis >= 4: boring)")
    elif len(strong) > 2:
        flags.append(f"TOO_STRONG ({len(strong)} axes >= 4: {strong})")
    if not weak:
        flags.append("NO_WEAKNESS (no axis <= 2: broken)")
    return flags
