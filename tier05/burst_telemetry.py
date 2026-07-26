"""C5 (Neap Tide v2.1): where Burst energy actually comes from.

R14: diagnostic. No acceptance target lives here and nothing reads these
numbers to make a decision.

WHY THIS EXISTS. Burst income arrived at ten scattered `p.burst_energy +=`
sites across five engine modules, none of which recorded a source. The meter
was observable and its CAUSES were not, so "how does her Burst actually fill?"
could only be answered by reading the engine and reasoning -- which is how the
playtest sprint came to believe her meter filled from exhausts alone when the
universal skill-tag line was paying roughly half of it.

P8 is a claim about exactly this shape: mustered-companion exhausts should be
top-two income in commander decks. A prediction whose evidence has to be
derived by hand is not gradeable, so `resources.gain_burst` now stamps a
source and this reduces the stream.

METRIC DEFINITIONS, fixed here so no later run can redefine them mid-sweep:

- share       fraction of total burst ENERGY from a source, not fraction of
              events. A source that fires often for 1 and a source that fires
              rarely for 5 are different answers to "what fills the meter",
              and the event count flatters the first.
- events      how often it fired, reported alongside share precisely so the
              two can disagree visibly.
- per_run     mean energy from that source per run, which is the only column
              that survives a change in run length. Share is a composition and
              moves when ANY source moves; per_run does not.

Sources are whatever the engine stamped. Deliberately not an allowlist: a new
income site appears in this report as a new row rather than being silently
bucketed into "other", which is the failure mode a fixed schema would have.
"""

from __future__ import annotations

from collections import defaultdict


def trace(log: list[dict]) -> dict[str, tuple[int, int]]:
    """One combat's burst income: source -> (energy, events).

    Same shape as fanfare_telemetry.trace / kurage_telemetry.trace and taken
    at the same moment, because a fight's log does not survive onto the
    RunResult -- only the reduced trace does.
    """
    out: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for ev in log:
        if ev.get("event") != "burst_income":
            continue
        row = out[ev.get("source", "unknown")]
        row[0] += int(ev.get("amount", 0))
        row[1] += 1
    return {source: (energy, events)
            for source, (energy, events) in out.items()}


def tally(results: list) -> dict:
    """Fold every run's burst traces into per-source totals."""
    energy: dict[str, int] = defaultdict(int)
    events: dict[str, int] = defaultdict(int)
    runs = len(results) or 1
    for result in results:
        for _act, per_source in getattr(result, "burst_traces", []):
            for source, (amount, count) in per_source.items():
                energy[source] += amount
                events[source] += count
    total = sum(energy.values())
    if not total:
        return {}
    return {
        "total": total,
        "runs": runs,
        "by_source": {
            source: {
                "energy": amount,
                "share": amount / total,
                "events": events[source],
                "per_run": amount / runs,
            }
            for source, amount in sorted(
                energy.items(), key=lambda kv: -kv[1])
        },
    }


def format_block(tallied: dict) -> str:
    """Report-only rendering. Empty string when nothing generated Burst, so
    characters without a meter print nothing rather than a row of zeroes."""
    if not tallied:
        return ""
    lines = ["  Burst income by source (C5, report-only; no threshold -- R14)"]
    for source, row in tallied["by_source"].items():
        lines.append(
            f"    {source:<20} {row['share']:6.1%}"
            f"   {row['per_run']:7.1f}/run"
            f"   {row['events']:6d} events")
    lines.append(f"    {'TOTAL':<20} {'':6}   "
                 f"{tallied['total'] / tallied['runs']:7.1f}/run")
    return "\n".join(lines)
