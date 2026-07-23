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

# A6 instrument version (R18, pass 2) -- same archive discipline as
# CONSTANTS_VERSION: v1 = 0.7*AoE + 0.3*debuff (Klee M-reports and the
# Furina pass-1 report are its archive; Furina measured 3.6 under it).
# v2 adds APPLICATION UPTIME (fraction of enemy intents taken under an
# elemental aura) at 0.5*AoE + 0.3*debuff + 0.2*uptime-factor. Numbers
# are discontinuous BY DESIGN; never compare v1/v2 A6 unlabeled.
A6_INSTRUMENT_VERSION = 2

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

    # A2: DPT t8-10 / DPT t2-4, fights that reached turn 10 (TANK BOSS
    # mostly). Early window is 2-4, not 1-3 (ruling 3.1): bombs placed
    # turn 1 pay on turn 2, and the 1-3 window read that lag as scaling.
    ratios = []
    for s in pooled:
        if s.turns >= 10:
            lo = _avg(s.damage_by_turn.get(t, 0) for t in (2, 3, 4))
            hi = _avg(s.damage_by_turn.get(t, 0) for t in (8, 9, 10))
            if lo > 0:
                ratios.append(hi / lo)
    a2 = _avg(ratios) or 1.0

    # A3: enemy damage absorbed by block, per energy (ATTRITION pool if
    # present, else all fights). "Damage prevented by kills" deferred.
    a3_pool = stats_by_enc.get("attrition", pooled) or pooled
    a3 = (sum(s.damage_blocked for s in a3_pool)
          / max(1, sum(s.energy_spent for s in a3_pool)))

    # A4: healing/recovery per fight (ruling 1). Chip-avoidance belongs to
    # A3, speed to A1 — every HP-delta variant let kill-speed masquerade
    # as durability. Includes post-fight relic healing (Burning Blood).
    # Encore absorption credits HERE, never A3 (Furina kickoff §2 harness
    # note, binding): the buffer is her healing metric's chip-reduction
    # form, and folding it into block would grow a phantom elite axis.
    a4 = _avg(s.healing + s.encore_absorbed for s in pooled)

    # A5: (extra draws + extra energy) per turn, anchored on base economy
    # so the starter baseline (0 extra) still normalizes.
    a5 = _BASE_ECONOMY + (sum(s.cards_drawn_extra + s.energy_generated_extra
                              for s in pooled)
                          / max(1, sum(s.turns for s in pooled)))

    # A6 components (ruling 2): both baseline-anchored in normalize().
    # Self-relative AoE penalized characters who are also fast single-
    # target; absolute swarm DPT vs baseline measures AoE directly.
    swarm = stats_by_enc.get("swarm", pooled)
    a6_aoe = _avg(s.total_damage_dealt / max(1, s.turns) for s in swarm)
    a6_debuff = _avg(s.debuff_stacks_applied for s in pooled)
    # A6 v2 (R18): application uptime, pooled across the battery. The
    # baseline applies nothing (uptime 0), so this term is anchored
    # additively in normalize(), never as a ratio.
    a6_app = (sum(s.aura_intents for s in pooled)
              / max(1, sum(s.total_intents for s in pooled)))

    # A7: setup tax — avg first turn where the 3-turn-window DPT reaches
    # 70% of the config's OWN peak window (self-referential: "when does
    # YOUR plan come online", independent of absolute power). The old
    # 1.5x-baseline threshold saturated for any competent deck.
    a7 = _avg(_turns_to_own_peak(s) for s in pooled)

    return {"A1_frontload": a1, "A2_scaling": a2, "A3_block": a3,
            "A4_sustain": a4, "A5_velocity": a5,
            "A6_utility": a6_aoe,          # headline raw = swarm DPT
            "A6_aoe": a6_aoe, "A6_debuff": a6_debuff, "A6_app": a6_app,
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


A4_FLOOR = 0.5     # zero-healing configs score the floor, not zero


def normalize(raw: dict[str, float], baseline: dict[str, float]) -> dict[str, float]:
    """Score each axis so baseline = 3.0. Higher = better on every axis."""
    eps = 1e-9
    scores = {}
    for ax in AXES:
        r, b = raw[ax], baseline[ax]
        if ax == "A4_sustain":
            score = max(A4_FLOOR, 3.0 * r / max(eps, b))
        elif ax == "A6_utility":
            # v2 composite (R18): AoE and debuff ratio-anchored as
            # before; application uptime anchored ADDITIVELY (the
            # baseline's uptime is 0 -- a ratio would divide by it).
            # At baseline every term is 1 -> exactly 3.0: anchor held.
            aoe = raw["A6_aoe"] / max(eps, baseline["A6_aoe"])
            deb = raw["A6_debuff"] / max(eps, baseline["A6_debuff"])
            app = 1.0 + raw["A6_app"] - baseline["A6_app"]
            score = 3.0 * (0.5 * aoe + 0.3 * deb + 0.2 * app)
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
