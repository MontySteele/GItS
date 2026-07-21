"""Run-level metrics (spec §5, M5 slice): fragility is the point —
winrate, death-node heatmap, HP trajectory percentile bands. The A4 saga
proved fight-level metrics can't express "62 HP, reluctant defense";
these can.
"""

from __future__ import annotations

from collections import Counter

from tier05.model import RunResult


def _percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    idx = q * (len(s) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (idx - lo)


def summarize_runs(results: list[RunResult]) -> dict:
    n = len(results)
    if n == 0:
        return {}
    deaths = Counter(r.death_node for r in results if r.death_node is not None)
    n_nodes = len(results[0].node_kinds)
    # HP trajectory bands: per node position, over runs that REACHED it.
    bands = []
    for pos in range(n_nodes):
        alive_here = [r.hp_by_node[pos] for r in results
                      if len(r.hp_by_node) > pos]
        if not alive_here:
            bands.append(None)
            continue
        bands.append({"p25": _percentile(alive_here, 0.25),
                      "p50": _percentile(alive_here, 0.50),
                      "p75": _percentile(alive_here, 0.75),
                      "reached": len(alive_here)})
    picks = sum(1 for r in results for d in r.decisions if d["picked"])
    screens = sum(len(r.decisions) for r in results)
    online = [r.time_to_online for r in results if r.time_to_online]
    return {
        "runs": n,
        "winrate": sum(r.won for r in results) / n,
        "death_heatmap": dict(sorted(deaths.items())),
        "hp_bands": bands,
        "avg_final_deck": sum(len(r.deck_ids) for r in results) / n,
        "pick_rate": picks / max(1, screens),
        "regretted_decisions": sum(r.regret_samples for r in results),
        "median_time_to_online": (sorted(online)[len(online) // 2]
                                  if online else None),
        "online_rate": len(online) / n,
    }


NEAR_DEATH_FRACTION = 0.15      # "one bad turn from dead"


def survival_profile(results: list[RunResult], max_hp: int) -> dict:
    """Fragility as SCALARS, normalized by max HP.

    Pass-4 sim-fidelity finding (2026-07-21): `hp_bands` already carried
    this signal and was already printed, but the design conversation
    travelled on the run-winrate scalar alone, which compresses "she
    spends the whole act one bad turn from dead" into a single percent.
    Absolute HP is also uninterpretable across characters with different
    max HP (Klee 62 vs REF_IRONCLAD 80) -- so everything here is a
    FRACTION of max, which is what makes an anchor comparison possible.

    Not banded, deliberately: bands are user-ratified (house rule). This
    reports; a ruling decides what is acceptable.
    """
    if not results:
        return {}
    kinds = results[0].node_kinds
    fight_pos = [i for i, k in enumerate(kinds) if k != "R"]
    pct = []
    for pos in fight_pos:
        vals = [r.hp_by_node[pos] for r in results if len(r.hp_by_node) > pos]
        pct.append(_percentile(vals, 0.50) / max_hp if vals else 0.0)
    floor = NEAR_DEATH_FRACTION * max_hp
    ever_near = sum(1 for r in results
                    if any(0 < h <= floor for h in r.hp_by_node))
    return {
        "median_hp_pct_by_fight": pct,
        # Mean of the median HP fraction across the act: one number for
        # "how much health does this character actually run on".
        "act_median_hp_pct": sum(pct) / len(pct) if pct else 0.0,
        # Share of the act the median run spends under 30% HP.
        "act_share_below_30pct": (sum(1 for p in pct if p < 0.30)
                                  / len(pct) if pct else 0.0),
        # Share of runs that ever touch the near-death floor while alive.
        "near_death_rate": ever_near / len(results),
        "max_hp": max_hp,
    }


def banner_variance(results: list[RunResult]) -> dict:
    """v1.8 addendum: the bad-roll-bricking detector.

    Groups runs by the banner they rolled and reports the spread of winrate
    across those groups. If some featured lineups are meaningfully worse than
    others, this is where it shows up -- and a large spread is the evidence
    that would flip `standard: true` companions to off-banner floor status.

    Degenerate while a nation has no more 5-stars than banner slots: every run
    rolls the same lineup, so there is exactly one group and the spread is 0.
    Reported as `degenerate` rather than silently looking like a clean result,
    because "no variance" and "no variation possible" are different claims.
    """
    if not results:
        return {}
    groups: dict[frozenset[str], list[RunResult]] = {}
    for r in results:
        groups.setdefault(r.banner, []).append(r)
    rates = {b: sum(x.won for x in rs) / len(rs) for b, rs in groups.items()}
    values = list(rates.values())
    return {
        "distinct_banners": len(groups),
        "degenerate": len(groups) <= 1,
        "winrate_by_banner": {tuple(sorted(b)): v for b, v in rates.items()},
        "spread": (max(values) - min(values)) if len(values) > 1 else 0.0,
        "runs_per_banner": {tuple(sorted(b)): len(rs)
                            for b, rs in groups.items()},
    }


def conditional_assembly(results: list[RunResult], card_ids: list[str]) -> dict:
    """v1.8 addendum: dream-team assembly becomes P(assembly | featured).

    Unconditional assembly stops being the meaningful number once a banner
    gates availability -- a run that never had the card featured was never in
    the running, and averaging it in measures the banner rather than the
    draft. Denominator is runs where every required 5-star was featured;
    4-stars are never gated, so they impose no condition.
    """
    if not results:
        return {}
    required = set(card_ids)
    eligible = [r for r in results
                if required.issubset(r.banner | _ungated(required, r))]
    assembled = [r for r in eligible if required.issubset(set(r.deck_ids))]
    return {
        "eligible_runs": len(eligible),
        "eligible_rate": len(eligible) / len(results),
        "assembled": len(assembled),
        "conditional_rate": (len(assembled) / len(eligible)
                             if eligible else None),
        "unconditional_rate": sum(
            1 for r in results if required.issubset(set(r.deck_ids))
        ) / len(results),
    }


def _ungated(required: set[str], r: RunResult) -> set[str]:
    """Required ids that the banner does not gate (anything not a 5-star)."""
    from tier0.content import loader
    return {cid for cid in required
            if loader.get_card(cid).star != 5}


def print_run_report(character: str, archetype: str, s: dict,
                     node_kinds: list[str], survival: dict | None = None) -> None:
    print(f"\n=== Tier 0.5 runs: {character}/{archetype} "
          f"({s['runs']} runs) ===")
    print(f"  run winrate      {s['winrate']:.1%}")
    if survival:
        print(f"  survival         act median HP "
              f"{survival['act_median_hp_pct']:.0%} of max "
              f"({survival['max_hp']} HP)   "
              f"{survival['act_share_below_30pct']:.0%} of the act under 30%"
              f"   near-death {survival['near_death_rate']:.0%} of runs")
        print("                   median HP% by fight: "
              + " ".join(f"{p:.0%}" for p in
                         survival["median_hp_pct_by_fight"]))
    print(f"  final deck size  {s['avg_final_deck']:.1f}   "
          f"pick rate {s['pick_rate']:.0%}   "
          f"regrets {s['regretted_decisions']}")
    onl = s["median_time_to_online"]
    print(f"  time-to-online   median {onl} fights, "
          f"online in {s['online_rate']:.0%} of runs")
    print("  node  kind  reached   p25/p50/p75 HP   deaths")
    for i, kind in enumerate(node_kinds):
        b = s["hp_bands"][i]
        d = s["death_heatmap"].get(i, 0)
        bar = "█" * round(40 * d / max(1, s["runs"]))
        if b is None:
            print(f"  {i:>4}  {kind:<4}  (never reached)")
            continue
        print(f"  {i:>4}  {kind:<4}  {b['reached']:>7}   "
              f"{b['p25']:>4.0f}/{b['p50']:>4.0f}/{b['p75']:>4.0f}       "
              f"{d:>4} {bar}")
