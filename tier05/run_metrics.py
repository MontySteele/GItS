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


def print_run_report(character: str, archetype: str, s: dict,
                     node_kinds: list[str]) -> None:
    print(f"\n=== Tier 0.5 runs: {character}/{archetype} "
          f"({s['runs']} runs) ===")
    print(f"  run winrate      {s['winrate']:.1%}")
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
