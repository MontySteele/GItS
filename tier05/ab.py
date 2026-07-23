"""M6: divergence / relevance / achievability metrics and the A/B harness
(spec §4-§6).

The three alarms this module owns come from spec §5 as amended by the
morning triage rulings:
  divergence     adaptive-mode shape distribution over >=1000 runs; alarm if
                 any single shape > 55% or any archetype < 10%
  relevance      P(>=1 offer advances the run's LIVE plan); enforced floor
                 >=35% per archetype (the revised claim -- the original
                 60-70% was a faith-era number that conflated advancing the
                 plan with being worth engaging; the loose read is reported
                 alongside, expected 60-75, unenforced)
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
    """P(>=1 offer advances the run's plan), over screens where a plan is LIVE.

    Conditioning on `plan_live` is the whole correctness of this metric, not a
    refinement. Core progress caps at 1.0, so once the core is online no offer
    can advance it and `advanced_plan` is structurally False from then on --
    measured at exactly 0.0% after completion for all three archetypes. Those
    screens are not the pool failing to offer anything; they are the plan
    already being finished.

    It matters most where the claim is judged hardest: 50.1% of demolition's
    screens fall after its core completes, so counting them dragged its
    relevance from 45.8% to 23.3% for a reason that has nothing to do with the
    pool. Spark sees 10.3% and reaction 2.3%, so the unconditioned number also
    penalised the archetypes unequally -- the fastest-assembling one worst.

    `after_core_share` is reported because it is a finding in its own right: an
    archetype that finishes half a run early is one whose remaining rewards are
    all off-plan by construction.
    """
    screens = [d for r in results for d in r.decisions]
    if not screens:
        return {}
    live = [d for d in screens if d.get("plan_live", True)]
    advanced = sum(1 for d in live if d.get("advanced_plan"))
    rate = advanced / len(live) if live else 0.0
    engaging = sum(1 for d in screens if d.get("engaging"))
    return {
        "screens": len(screens),
        "live_screens": len(live),
        "after_core_share": 1 - len(live) / len(screens),
        "relevance": rate,
        "meets_floor": rate >= C.RELEVANCE_FLOOR,   # ruled acceptance
        # Loose secondary, over ALL screens: an on-plan card was on offer,
        # whether or not the plan still needed it. Unenforced by ruling.
        "engaging_rate": engaging / len(screens),
    }


def achievability(results: list[RunResult]) -> dict:
    """Assigned-mode time-to-online. Alarm above ACHIEVABILITY_ALARM_FIGHTS.

    The old caveat here -- reaction's number being dominated by 10%-ever-
    sees-the-Burst pool odds -- is RESOLVED by v1.9: the Burst is kit, it
    left both the pool and the core definition, and reaction's
    achievability now measures applier + amp assembly, which is what it
    always claimed to measure.
    """
    # `is not None`, NOT truthiness. time_to_online is a fight COUNT, and a
    # falsy test silently drops any run that came online on fight 0. The
    # observed floor is 1 today (fights is incremented before the check), so
    # this is not a live bug -- but it is one reordering away from being one,
    # and a metric that quietly discards its best runs fails safe-looking.
    online = [r.time_to_online for r in results if r.time_to_online is not None]
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
           runs: int, seed: int,
           grant_relics: bool = False,
           grant_potions: bool = False,
           n_acts: int | None = None) -> dict:
    """Assigned vs adaptive over identical seeds.

    Adaptive ignores `archetype` by construction, so it is passed through only
    to keep the two calls otherwise identical -- the comparison is meaningless
    if anything but the policy differs.
    """
    out = {}
    for name, policy in draft.POLICIES.items():
        results = model.run_many(character, archetype, pilot_id,
                                 policy, runs, seed,
                                 grant_relics=grant_relics,
                                 grant_potions=grant_potions,
                                 n_acts=n_acts)
        out[name] = {
            "results": results,
            "winrate": sum(r.won for r in results) / max(1, len(results)),
            "relevance": relevance(results),
            "achievability": achievability(results),
            # Divergence ONLY for adaptive. Under the assigned policy the
            # deck's shape is the target it was handed, so the distribution
            # would restate the input and read like a finding. Storing it for
            # both was a loaded gun in the dict: the printer ignored it, the
            # next caller would not have.
            "divergence": divergence(results) if name == "adaptive" else None,
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
            floor = "clears" if rel["meets_floor"] else "BELOW FLOOR"
            print(f"  relevance      {rel['relevance']:.1%} "
                  f"({floor}, floor {C.RELEVANCE_FLOOR:.0%})")
            print(f"  engaging       {rel['engaging_rate']:.1%} "
                  f"(loose secondary, expected 60-75, unenforced)")
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
