"""Kurage pulse telemetry (playtest sprint, Track P item P2).

Reads the combat event log; changes nothing and gates nothing. R14: this is a
diagnostic, and no acceptance target lives here.

WHY THIS EXISTS. `KURAGE_PULSE_PER_CHARGE` is a MULTIPLIER on a bank that is
uncapped and never spent, so the pulse term has no natural ceiling -- it is the
only number in Kokomi's kit that can only grow. [USER] ratified it over the
assistant's objection (Necrobinder precedent, R56) with one standing caveat:
Osty's HP can drop, Charge cannot, so *watch act 3*.

"Watch act 3" is a instruction to a person, and people forget. This turns it
into a column. The metric is deliberately keyed on the pulse SIZE rather than
on win rate, because the runaway failure mode is invisible in win rate: a kit
that one-shots act-3 elites still reports a win, and reports it as success.

METRIC DEFINITIONS, fixed here so no later run can redefine them mid-sweep:

- p95 pulse      the 95th percentile of per-pulse damage, by act. The tail is
                 the question. A mean is dominated by the many small pulses
                 thrown early in every fight and would stay flat through
                 exactly the blow-up this is watching for.
- max pulse      the single largest pulse observed. Reported alongside p95 so
                 a lone freak sample cannot be mistaken for a moved tail.
- mean charge    the bank at pulse time. Separates the two ways the tail can
                 rise: more Charge (a drafting/sourcing change) or a bigger
                 multiplier (a constants change).

Pulses that land on an empty board are INCLUDED. They are samples of the curve,
and dropping them would bias the tail down precisely when fights end quickly --
i.e. when the kit is strongest. See the emit site in tier0/engine/effects.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field


def _percentile(values: list[int], q: float) -> float:
    """Nearest-rank on sorted samples. Matches run_metrics._percentile rather
    than inventing a second convention: two percentile definitions in one
    report is how a moved tail gets argued about instead of acted on."""
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(int(q * len(ordered)), len(ordered) - 1)
    return float(ordered[idx])


@dataclass
class KurageTrace:
    """One combat's pulses."""

    amounts: list[int] = field(default_factory=list)
    charges: list[int] = field(default_factory=list)
    landed: int = 0

    @property
    def pulses(self) -> int:
        return len(self.amounts)


def trace(log: list[dict]) -> KurageTrace:
    out = KurageTrace()
    for ev in log:
        if ev["event"] != "kurage_pulse":
            continue
        out.amounts.append(ev["amount"])
        out.charges.append(ev["charge"])
        out.landed += 1 if ev.get("landed") else 0
    return out


def aggregate(traces: list[KurageTrace]) -> dict:
    """Pooled over PULSES, not over combats.

    A per-combat average of per-combat p95s is not a p95 of anything, and the
    tail is the whole point -- so the samples are pooled and the percentile is
    taken once, over the pool.
    """
    amounts = [a for t in traces for a in t.amounts]
    charges = [c for t in traces for c in t.charges]
    if not amounts:
        return {}
    return {
        "pulses": len(amounts),
        "combats": sum(1 for t in traces if t.pulses),
        "p50": _percentile(amounts, 0.50),
        "p95": _percentile(amounts, 0.95),
        "max": max(amounts),
        "mean_charge": sum(charges) / len(charges),
        "max_charge": max(charges),
        "landed": sum(t.landed for t in traces) / len(amounts),
    }


def by_act(traces: list[tuple[int, KurageTrace]]) -> dict[int, dict]:
    """(act_index, trace) pairs -> per-act aggregates.

    Act 3 is the cell that matters; the earlier acts are there so the SHAPE is
    visible. A tail that triples from act 1 to act 3 is a different finding
    from one that is already large in act 1, and only the trend distinguishes
    "scaling as designed" from "scaling away from the game".
    """
    buckets: dict[int, list[KurageTrace]] = {}
    for act_i, t in traces:
        buckets.setdefault(act_i, []).append(t)
    return {act: aggregate(ts) for act, ts in sorted(buckets.items())
            if aggregate(ts)}


def format_block(per_act: dict[int, dict]) -> str:
    """Report-only rendering. Returns '' when the run had no pulses at all, so
    every non-Kokomi character prints nothing rather than a row of zeroes."""
    if not per_act:
        return ""
    lines = ["  Kurage pulse (P2 runaway telemetry, report-only)"]
    for act, a in per_act.items():
        lines.append(
            f"    act {act + 1}    p50 {a['p50']:6.0f}   p95 {a['p95']:6.0f}"
            f"   max {a['max']:6.0f}   charge mean {a['mean_charge']:5.1f}"
            f" max {a['max_charge']:4.0f}   n={a['pulses']}")
    return "\n".join(lines)
