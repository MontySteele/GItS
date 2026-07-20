"""M6: divergence / relevance / achievability metrics and the A/B harness
(spec §4-§6).

The three alarms this module owns come straight from spec §5:
  divergence     adaptive-mode shape distribution over >=1000 runs; alarm if
                 any single shape > 55% or any archetype < 10%
  relevance      P(>=1 offer advances the run's plan); claim 60-70%
  achievability  assigned-mode median time-to-online; alarm above 7 fights

The A/B is structural, not a stretch goal: assigned and adaptive run over the
SAME seeds so their differences are policy differences and not sampling noise.
"""

from __future__ import annotations

import random
from collections import Counter

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft, model
from tier05.model import RunResult


def _decks(results: list[RunResult]) -> list[list]:
    return [[loader.get_card(cid) for cid in r.deck_ids] for r in results]


def divergence(results: list[RunResult]) -> dict:
    """The goodstuff detector. Adaptive-mode shape distribution.

    Note the two alarms answer different questions and can fire together: a
    pool can be simultaneously dominated by one shape and starving another.
    'goodstuff' decks -- ones that never committed -- are reported in the
    distribution but excluded from the starvation check, because starvation is
    a claim about archetypes and goodstuff is the absence of one.
    """
    if not results:
        return {}
    shapes = Counter(draft.dominant_archetype(d) for d in _decks(results))
    n = len(results)
    dist = {s: c / n for s, c in shapes.items()}
    dominant = max(dist, key=lambda s: dist[s])
    starved = {a: dist.get(a, 0.0) for a in draft.ARCHETYPES
               if dist.get(a, 0.0) < C.DIVERGENCE_STARVATION_ALARM}
    return {
        "runs": n,
        "distribution": dict(sorted(dist.items(), key=lambda kv: -kv[1])),
        "dominant_shape": dominant,
        "dominant_share": dist[dominant],
        "dominance_alarm": dist[dominant] > C.DIVERGENCE_DOMINANCE_ALARM,
        "starved_archetypes": starved,
        "starvation_alarm": bool(starved),
        "goodstuff_share": dist.get("goodstuff", 0.0),
        "underpowered_sample": n < 1000,
    }


def relevance(results: list[RunResult]) -> dict:
    """P(>=1 offer advances the run's plan), over reward screens."""
    screens = [d for r in results for d in r.decisions]
    if not screens:
        return {}
    advanced = sum(1 for d in screens if d.get("advanced_plan"))
    rate = advanced / len(screens)
    return {
        "screens": len(screens),
        "relevance": rate,
        "in_claimed_band": 0.60 <= rate <= 0.70,   # spec §5 claim
    }


def achievability(results: list[RunResult]) -> dict:
    """Assigned-mode time-to-online. Alarm above ACHIEVABILITY_ALARM_FIGHTS.

    CAVEAT, carried from the triage report: for the reaction archetype this
    number is currently dominated by one design question -- sparks_n_splash is
    one of 15 rares at 5% odds, so ~10% of runs ever SEE the Burst its core
    requires. Until the Burst-acquisition ruling lands, a reaction alarm here
    is measuring pool odds, not achievability. Flagged rather than silently
    reported as a policy result.
    """
    online = [r.time_to_online for r in results if r.time_to_online]
    if not results:
        return {}
    med = sorted(online)[len(online) // 2] if online else None
    return {
        "online_rate": len(online) / len(results),
        "median_time_to_online": med,
        "alarm": med is not None and med > C.ACHIEVABILITY_ALARM_FIGHTS,
        "never_online_share": 1 - len(online) / len(results),
    }


def run_ab(character: str, archetype: str, pilot_id: str,
           runs: int, seed: int) -> dict:
    """Assigned vs adaptive over identical seeds.

    Adaptive ignores `archetype` by construction, so it is passed through only
    to keep the two calls otherwise identical -- the comparison is meaningless
    if anything but the policy differs.
    """
    out = {}
    for name, policy in draft.POLICIES.items():
        results = model.run_many(character, archetype, pilot_id,
                                 policy, runs, seed)
        out[name] = {
            "results": results,
            "winrate": sum(r.won for r in results) / max(1, len(results)),
            "relevance": relevance(results),
            "achievability": achievability(results),
            "divergence": divergence(results),
            "avg_deck": sum(len(r.deck_ids) for r in results)
                        / max(1, len(results)),
            "regretted": sum(r.regret_samples for r in results),
        }
    return out


def print_ab_report(character: str, archetype: str, ab: dict) -> None:
    print(f"\n=== M6 A/B: {character} / assigned-target={archetype} ===")
    for name in ("assigned", "adaptive"):
        d = ab[name]
        print(f"\n-- {name} --")
        print(f"  winrate        {d['winrate']:.1%}")
        print(f"  avg deck       {d['avg_deck']:.1f}")
        rel = d["relevance"]
        if rel:
            band = "in band" if rel["in_claimed_band"] else "OUT OF BAND"
            print(f"  relevance      {rel['relevance']:.1%} "
                  f"({band}, claim 60-70%)")
        ach = d["achievability"]
        if ach:
            print(f"  online rate    {ach['online_rate']:.1%}")
            print(f"  median TTO     {ach['median_time_to_online']}"
                  f"{'  ** ALARM **' if ach['alarm'] else ''}")
        print(f"  regretted      {d['regretted']}")
    div = ab["adaptive"]["divergence"]
    if div:
        print("\n-- divergence (adaptive = the goodstuff detector) --")
        for shape, share in div["distribution"].items():
            print(f"  {shape:<12} {share:.1%}")
        if div["underpowered_sample"]:
            print(f"  NOTE: {div['runs']} runs; spec asks for >=1000 before "
                  "reading these alarms.")
        if div["dominance_alarm"]:
            print(f"  ** DOMINANCE ALARM ** {div['dominant_shape']} at "
                  f"{div['dominant_share']:.1%} (> "
                  f"{C.DIVERGENCE_DOMINANCE_ALARM:.0%})")
        if div["starvation_alarm"]:
            print(f"  ** STARVATION ALARM ** {div['starved_archetypes']} "
                  f"(< {C.DIVERGENCE_STARVATION_ALARM:.0%})")
        if not (div["dominance_alarm"] or div["starvation_alarm"]):
            print("  no divergence alarms")
