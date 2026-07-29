"""C2: the elite blitz columns (Neap Tide addendum, 2026-07-26).

Reads finished RunResults; changes nothing and gates nothing. R14: this is a
diagnostic, and no acceptance target lives here.

WHY THIS EXISTS. Every headline number the sprint moved is an ELITE number in
disguise. Act-1 clear is mostly "did the two elites go well"; the hunter route
is elite-SEEKING by default, so a Kokomi run meets them on purpose; and the one
thing R73 edited -- the pulse tail -- is a large-single-target term, which is
the shape elites are and normals are not. When act-1 clear moved 16 points
across the F batch, nothing in the report could say whether that was elites
becoming unwinnable, elites costing more HP and killing the run two floors
later, or fewer elites being attempted at all. Those want three different fixes.

METRIC DEFINITIONS, fixed here so no later run can redefine them mid-sweep:

- attempted        elite nodes ENTERED, per act. The route decides this, so it
                   is a behaviour column as much as an outcome one: a hurt run
                   ducking elites shows up here and nowhere else.
- cleared          elite fights won. `attempted - cleared` is at most 1 per run
                   (a lost fight ends the run), so a low clear rate and a low
                   attempt rate are very different diseases with similar
                   act-clear symptoms.
- hp cost          hp_start - hp_end for won elite fights, from FightStats
                   rather than from hp_by_node deltas. Those two disagree at an
                   act boundary, where the Ancient heals to full AFTER the boss
                   node is recorded; FightStats brackets the fight itself and
                   has no such seam. LOST fights are excluded from the mean --
                   a death costs all remaining HP and would drag the mean
                   toward "elites cost about your whole bar", which is true and
                   useless.
- relics at boundary
                   granted relics held as each act's boss resolved. This is the
                   power-growth control: an act-2 collapse means something
                   different if the run arrived with 2 relics than with 6.
- p95 pulse vs pool
                   the act's elite p95 pulse against that act's elite HP POOL
                   -- both the encounter totals and the largest single body.
                   The pulse is single-target, so `p95 / largest body` is the
                   fraction of a real health bar one turn-end tick removes. It
                   is the number the §2.2 reader hierarchy is actually about,
                   and C1 is the record of what happens when a tail is printed
                   with nothing to be large relative to.

WHAT THIS DOES NOT MEASURE, said plainly. Elite HP pools are the DESIGNED bands
from the act pools, not the rolled HP of the encounters this cohort actually
met -- rolled HP is not carried on RunResult. Within a band the spread is a few
points, so the ratio is a good estimate and a bad exact figure. Do not read the
third decimal.
"""

from __future__ import annotations

from tier0 import constants as C
from tier05 import acts, kurage_telemetry, stats

FIGHT_KINDS = ("N", "E", "B")


# It used to say "nearest-rank, matching kurage_telemetry._percentile and
# run_metrics._percentile" -- and run_metrics interpolated, so the sentence was
# false and this reader was the second convention it warned about. Fixed by the
# sim-hygiene sprint (2026-07-29): ONE percentile, linear, in tier05.stats.
# p95_pulse therefore MOVED (reported telemetry, never a ratified band).
_percentile = stats.percentile


def _band_mid(hp) -> float:
    """An `hp` field is either a literal or a [lo, hi] band."""
    if isinstance(hp, (list, tuple)):
        return sum(hp) / len(hp)
    return float(hp)


def elite_hp_pool(act: int) -> dict:
    """The act's designed elite encounters: total HP and largest single body.

    Both, because they answer different questions. Total is what the fight
    costs in aggregate; largest body is what a SINGLE-TARGET term like the
    Kurage pulse is measured against, and a 4-body swarm with the same total
    is a completely different check.
    """
    totals, bodies = [], []
    for enc in acts.pools(act).get("elite", []):
        total = 0.0
        for body in enc.get("enemies", []):
            mid = _band_mid(body["hp"])
            total += mid * int(body.get("count", 1))
            bodies.append(mid)
        totals.append(total)
    if not totals:
        return {}
    return {
        "encounters": len(totals),
        "mean_total": sum(totals) / len(totals),
        "max_total": max(totals),
        "largest_body": max(bodies),
        "smallest_body": min(bodies),
    }


def _fight_contexts(result) -> list[tuple[int, str]]:
    """(act_index, node_kind) per FIGHT, aligned with `fight_stats`.

    Only N/E/B nodes run a fight (see model.run_one), so filtering node_kinds
    to those reproduces the fight order exactly. Act index comes from the floor
    index: every path visits one room per floor, so act boundaries sit at
    multiples of MAP_FLOORS -- the same rule RunResult.node_kinds documents.
    """
    out = []
    for floor, kind in enumerate(result.node_kinds):
        if kind in FIGHT_KINDS:
            out.append((floor // C.MAP_FLOORS, kind))
    return out


def aggregate(results: list) -> dict:
    """RunResults -> per-act elite columns."""
    if not results:
        return {}

    attempted: dict[int, int] = {}
    cleared: dict[int, int] = {}
    hp_costs: dict[int, list[int]] = {}
    relics: dict[int, list[int]] = {}
    pulses: dict[int, list[int]] = {}

    for r in results:
        contexts = _fight_contexts(r)
        stats = list(r.fight_stats)
        # A run that died mid-fight still recorded that fight, so the two lists
        # are the same length. Truncate defensively rather than assume: an
        # off-by-one here would silently mis-attribute an elite to the wrong
        # act, which is exactly the kind of quiet wrongness R14 telemetry is
        # supposed to avoid being.
        for (act, kind), fs in zip(contexts, stats):
            if kind != "E":
                continue
            attempted[act] = attempted.get(act, 0) + 1
            if fs.won:
                cleared[act] = cleared.get(act, 0) + 1
                hp_costs.setdefault(act, []).append(fs.hp_start - fs.hp_end)
        for act, count in enumerate(r.relics_by_act):
            relics.setdefault(act, []).append(count)
        for act, trace in r.kurage_traces:
            pulses.setdefault(act, []).extend(trace.amounts)

    per_act = {}
    for act in sorted(set(attempted) | set(relics) | set(pulses)):
        costs = hp_costs.get(act, [])
        held = relics.get(act, [])
        p95 = _percentile(pulses.get(act, []), 0.95)
        pool = elite_hp_pool(act)
        per_act[act] = {
            "attempted": attempted.get(act, 0),
            "cleared": cleared.get(act, 0),
            "clear_rate": (cleared.get(act, 0) / attempted[act]
                           if attempted.get(act) else 0.0),
            "attempts_per_run": attempted.get(act, 0) / len(results),
            "mean_hp_cost": (sum(costs) / len(costs)) if costs else 0.0,
            "max_hp_cost": max(costs) if costs else 0,
            "mean_relics": (sum(held) / len(held)) if held else 0.0,
            "boundary_runs": len(held),
            "p95_pulse": p95,
            "pool": pool,
            # The §2.2 question, as a number: what fraction of the act's
            # largest elite body does one turn-end pulse remove at the tail?
            "p95_over_largest_body": (p95 / pool["largest_body"]
                                      if pool.get("largest_body") else 0.0),
        }
    return per_act


def format_block(per_act: dict) -> str:
    """Report-only rendering. '' when no elite was ever attempted, so a cohort
    that never met one prints nothing rather than a row of zeroes."""
    if not per_act or not any(a["attempted"] for a in per_act.values()):
        return ""
    lines = ["  C2 elite blitz (report-only, R14)",
             f"    {'act':>4} {'attempts/run':>13} {'clear%':>7} "
             f"{'hp cost':>8} {'worst':>6} {'relics@boss':>12} "
             f"{'p95 pulse':>10} {'biggest body':>13} {'p95/body':>9}"]
    for act, a in sorted(per_act.items()):
        pool = a["pool"]
        lines.append(
            f"    {act + 1:>4} {a['attempts_per_run']:13.2f} "
            f"{a['clear_rate'] * 100:7.1f} {a['mean_hp_cost']:8.1f} "
            f"{a['max_hp_cost']:6d} "
            f"{a['mean_relics']:6.2f} (n={a['boundary_runs']:<3}) "
            f"{a['p95_pulse']:10.0f} {pool.get('largest_body', 0):13.0f} "
            f"{a['p95_over_largest_body']:9.2f}")
    lines.append("    (hp cost is WON elites only; pools are designed bands, "
                 "not rolled HP)")
    return "\n".join(lines)


def pulse_tail(results: list) -> dict:
    """Convenience: the kurage tail by act, so a caller wanting both blocks
    does not re-walk the traces. Same aggregation kurage_telemetry does."""
    return kurage_telemetry.by_act(
        [pair for r in results for pair in r.kurage_traces])
