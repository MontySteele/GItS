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
    turns_at_floor: int = 0
    requested: int = 0
    wasted: int = 0
    spend_events: int = 0
    spent: int = 0
    peak: int = 0
    cap: int = 0
    held: list[int] = field(default_factory=list)
    # "The Tide Turns": read-time samples. THE governing metric for this
    # sprint -- pass 4 measured turn-start and read-time saturation and they
    # disagreed by 25 points, because the pool refills mid-turn and spills.
    reads: int = 0
    reads_at_cap: int = 0
    reads_at_floor: int = 0
    # A read that found NOTHING. Distinct from at-floor and it must stay
    # distinct: `at_floor` is true whenever total == floor, and before any
    # grant the floor is 0 -- so an empty meter and a meter resting on a
    # built baseline are the same event to that flag, while being opposite
    # diagnoses ("the stat is dead" vs "the stat is pinned"). Conflating
    # them would let a dead act-1 meter read as successful floor-building.
    reads_empty: int = 0
    read_values: list[int] = field(default_factory=list)
    floor_grants: int = 0
    floor_granted: int = 0
    decayed: int = 0

    @property
    def time_at_cap(self) -> float:
        return self.turns_at_cap / self.turns if self.turns else 0.0

    @property
    def time_at_floor(self) -> float:
        return self.turns_at_floor / self.turns if self.turns else 0.0

    @property
    def read_at_cap(self) -> float:
        """Gate (2)'s primary: of the times a card actually READ the meter,
        how often was it pinned at the ceiling?"""
        return self.reads_at_cap / self.reads if self.reads else 0.0

    @property
    def read_at_floor(self) -> float:
        """Gate (2)'s other half, NET of empty reads. A grant raises cap
        alongside floor, so a floor-pinned meter never reads at-cap --
        without this the tripwire is silent through exactly the risk it was
        written to catch. Empty reads are excluded because a floor of 0 is
        not a floor the player built."""
        pinned = self.reads_at_floor - self.reads_empty
        return pinned / self.reads if self.reads else 0.0

    @property
    def read_empty(self) -> float:
        """Reads that found an empty meter -- the archetype's other failure
        mode, and the one act 1 actually has."""
        return self.reads_empty / self.reads if self.reads else 0.0

    @property
    def mean_at_read(self) -> float:
        return (sum(self.read_values) / len(self.read_values)
                if self.read_values else 0.0)

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
            # Pre-Tide-Turns logs carry no at_floor key; absent means the
            # world had no floors at all, which reads as never-at-floor only
            # because the floor was 0 and the meter was above it.
            out.turns_at_floor += 1 if ev.get("at_floor") else 0
            out.held.append(ev["total"])
            out.peak = max(out.peak, ev["total"])
            out.cap = ev["cap"]
        elif kind == "fanfare_read":
            out.reads += 1
            out.reads_at_cap += 1 if ev["at_cap"] else 0
            out.reads_at_floor += 1 if ev["at_floor"] else 0
            out.reads_empty += 1 if ev["total"] == 0 else 0
            out.read_values.append(ev["total"])
        elif kind == "fanfare_floor_granted":
            out.floor_grants += 1
            out.floor_granted += ev["amount"]
        elif kind == "fanfare_decay":
            out.decayed += ev["amount"]
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
    reads = sum(t.reads for t in live)
    read_vals = [v for t in live for v in t.read_values]
    return {
        "combats": len(live),
        "turns": turns,
        "reads": reads,
        # Gate (2), both pins. 0/0 reports as 0.0 with reads == 0 alongside,
        # so "no card in this deck ever read the meter" stays distinguishable
        # from "every read was healthy".
        "read_at_cap": (sum(t.reads_at_cap for t in live) / reads
                        if reads else 0.0),
        "read_at_floor": ((sum(t.reads_at_floor for t in live)
                           - sum(t.reads_empty for t in live)) / reads
                          if reads else 0.0),
        "read_empty": (sum(t.reads_empty for t in live) / reads
                       if reads else 0.0),
        "mean_at_read": (sum(read_vals) / len(read_vals)
                         if read_vals else 0.0),
        "floor_grants_per_run": sum(t.floor_grants for t in live) / len(live),
        "floor_granted_per_run": sum(t.floor_granted for t in live) / len(live),
        "decayed_per_combat": sum(t.decayed for t in live) / len(live),
        "time_at_cap": sum(t.turns_at_cap for t in live) / turns,
        "time_at_floor": sum(t.turns_at_floor for t in live) / turns,
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
    """Read-time first: it is the metric this sprint's gates are written
    against. Turn-start at-cap is kept as the secondary because pass 4's
    archive is expressed in it."""
    if not agg:
        return f"  {label:<20} (no fanfare turns)"
    return (f"  {label:<20} READ at-cap {agg['read_at_cap']:6.1%} "
            f"pinned {agg['read_at_floor']:6.1%} "
            f"empty {agg['read_empty']:6.1%} "
            f"mean {agg['mean_at_read']:5.1f} (n={agg['reads']})   "
            f"| turn at-cap {agg['time_at_cap']:6.1%}   "
            f"overflow {agg['overflow']:6.1%}   "
            f"floors {agg['floor_granted_per_run']:5.1f}/run "
            f"({agg['floor_grants_per_run']:.1f} grants)   "
            f"decay {agg['decayed_per_combat']:5.1f}/combat   "
            f"n={agg['combats']} combats / {agg['turns']} turns")
