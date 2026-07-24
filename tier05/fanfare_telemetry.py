"""Fanfare trajectory telemetry (sheet pass 4, Q1a).

Reads the combat event log; changes nothing. The metric definitions are
REGISTERED in docs/furina-sheet-pass-4-plan.md and are fixed for the whole
pass so no later cell can redefine them mid-sweep:

- time-at-cap   fraction of PLAYER TURNS whose start-of-turn snapshot has
                fanfare == cap. The snapshot (`fanfare_turn`) is emitted
                after turn-start triggers, upkeep and draw -- the state the
                pilot decides in.
- overflow      sum(wasted) / sum(requested) over every gain_fanfare call,
                where wasted = requested - applied. Before pass 4 the clamp
                was silent, which is the mechanical reason no earlier
                FANFARE_CAP_FRACTION sweep could see saturation: those cells
                read win rate only, and the pool being pinned at its ceiling
                is invisible in win rate.
- spends        count and total of fanfare_spent.
- peak / mean   over the per-turn snapshots.

R14: diagnostics feeding a ruling. No acceptance targets live here.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FanfareTrace:
    """One combat's trajectory."""

    turns: int = 0
    turns_at_cap: int = 0
    requested: int = 0
    wasted: int = 0
    spend_events: int = 0
    spent: int = 0
    peak: int = 0
    cap: int = 0
    held: list[int] = field(default_factory=list)

    @property
    def time_at_cap(self) -> float:
        return self.turns_at_cap / self.turns if self.turns else 0.0

    @property
    def overflow(self) -> float:
        return self.wasted / self.requested if self.requested else 0.0

    @property
    def mean_held(self) -> float:
        return sum(self.held) / len(self.held) if self.held else 0.0

    @property
    def held_fraction(self) -> float:
        """Mean held as a fraction of the cap -- comparable across cap
        sweeps, where the raw mean is not."""
        return self.mean_held / self.cap if self.cap else 0.0


def trace(log: list[dict]) -> FanfareTrace:
    out = FanfareTrace()
    for ev in log:
        kind = ev["event"]
        if kind == "fanfare_turn":
            out.turns += 1
            out.turns_at_cap += 1 if ev["at_cap"] else 0
            out.held.append(ev["total"])
            out.peak = max(out.peak, ev["total"])
            out.cap = ev["cap"]
        elif kind == "gain_fanfare":
            # Pre-pass-4 logs carry no requested/wasted keys; treat those as
            # "unmeasured" rather than "zero waste", which would read as a
            # healthy world.
            if "requested" not in ev:
                continue
            out.requested += ev["requested"]
            out.wasted += ev["wasted"]
            out.peak = max(out.peak, ev["total"])
        elif kind == "fanfare_spent":
            out.spend_events += 1
            out.spent += ev["amount"]
    return out


def aggregate(traces: list[FanfareTrace]) -> dict:
    """Pooled across combats. Pooling the RATIOS' numerators and
    denominators (not averaging per-combat ratios) keeps a 2-turn combat
    from weighing as much as a 20-turn one."""
    live = [t for t in traces if t.turns]
    if not live:
        return {}
    turns = sum(t.turns for t in live)
    requested = sum(t.requested for t in live)
    return {
        "combats": len(live),
        "turns": turns,
        "time_at_cap": sum(t.turns_at_cap for t in live) / turns,
        "overflow": (sum(t.wasted for t in live) / requested
                     if requested else 0.0),
        "requested": requested,
        "wasted": sum(t.wasted for t in live),
        "spend_events_per_combat": sum(t.spend_events for t in live) / len(live),
        "spent_per_combat": sum(t.spent for t in live) / len(live),
        "mean_held_fraction": sum(t.held_fraction for t in live) / len(live),
        "peak_fraction": sum(t.peak / t.cap for t in live if t.cap) / len(live),
    }


def format_row(label: str, agg: dict) -> str:
    if not agg:
        return f"  {label:<20} (no fanfare turns)"
    return (f"  {label:<20} at-cap {agg['time_at_cap']:6.1%}   "
            f"overflow {agg['overflow']:6.1%}   "
            f"held {agg['mean_held_fraction']:5.1%} of cap   "
            f"peak {agg['peak_fraction']:5.1%}   "
            f"spends {agg['spend_events_per_combat']:4.1f}/combat "
            f"({agg['spent_per_combat']:5.1f} Fanfare)   "
            f"n={agg['combats']} combats / {agg['turns']} turns")
