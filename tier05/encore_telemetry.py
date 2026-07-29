"""Encore saturation telemetry (salon UI sprint Track 3, D8 prerequisite).

Reads the combat event log; changes nothing. Same shape as
`fanfare_telemetry`, and for the same reason: the playtest read is that
Encore refills faster than the stage drains it and trends toward a passively
full free-block bar, and win rate cannot see that. A meter that is always
full and a meter that is exactly adequate produce the same fights.

The metric definitions are REGISTERED here and fixed for the pass, so no
later cell can redefine them mid-sweep:

- dry rate      fraction of STAGE-ACTIVE upkeeps that arrive with less
                than one member's tick cost. This is the "the stage
                starves" reading.
- full rate     fraction of stage-active upkeeps that arrive holding
                enough for EVERY member to tick (encore >= members x
                cost). The "the stage never starves" reading, and the one
                D8 is actually about.
- surplus       encore held at upkeep MINUS what the whole stage needs,
                pooled. Positive mean = the bar is running ahead of the
                stage; this is the saturation number.
- all-ticked    fraction of upkeeps where every member actually paid.
                Distinct from full rate: full rate is measured before any
                member spends, all-ticked after, so a stage that arrives
                one short shows as not-full AND not-all-ticked, while a
                stage that arrives exactly adequate shows as both.
- runway rate   fraction of stage-active upkeeps arriving with at least
                RUNWAY_SATURATED_TURNS turns of the whole stage's bill in
                hand (encore >= turns x members x cost). Added by the
                pilot-gap sprint (2026-07-28) as the direct sim analogue of
                what a playtester SEES: nobody reads a meter as "full", they
                read the runway bar as "I am not going to run out". Full
                rate answers "can the stage tick THIS turn", which is a much
                weaker claim and is why the two can disagree.
- end level     Encore still held when the combat ends -- the most direct
                statement of "generated and never needed".
- gained/drained totals over the combat, and the ratio. A ratio above 1
                means the combat generated Encore it did not use.

                DRAINED IS NOT `encore_spent`. Absorption is a second sink:
                `absorb_into_encore` eats incoming damage off the meter and
                emits `encore_absorb`, never `encore_spent`. Reading the
                ratio against spends alone reports every point the buffer
                ATE as a point it wasted -- the exact inversion of what the
                buffer is for -- and the first run of this instrument did
                exactly that, showing a gained/spent of 3.07 against a mean
                end level of 4.0 that could not be reconciled with it. The
                unaccounted points were the ones that did their job.

INCOMPLETE UPKEEPS: `salon_tick` is emitted per member inside a loop that
breaks when the fight ends mid-upkeep. An upkeep whose tick count is short
of its member count is therefore NOT evidence of a dry stage -- the fight
simply ended. Those upkeeps are excluded from the all-ticked rate and
counted separately, because silently treating them as "not all ticked"
would report the lethal-blow turn as an Encore failure.

MEASURE ONLY (sprint brief Track 3): no acceptance targets live here, and
the lever pick between "more sinks" and "faster drain + power bump" is
[USER] red-pen and out of scope.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# How many turns of the WHOLE stage's bill counts as a saturated runway.
# Registered here with the metric definitions, not passed in per call, so no
# cell can quietly re-cut the threshold and quote the result as the same
# column. 5 is the sprint brief's number.
RUNWAY_SATURATED_TURNS = 5


@dataclass
class EncoreTrace:
    """One combat's Encore trajectory."""

    upkeeps: int = 0
    upkeeps_dry: int = 0
    upkeeps_full: int = 0
    upkeeps_saturated: int = 0
    upkeeps_all_ticked: int = 0
    upkeeps_complete: int = 0
    upkeeps_truncated: int = 0
    surplus: list[int] = field(default_factory=list)
    held: list[int] = field(default_factory=list)
    members: list[int] = field(default_factory=list)
    ticks: int = 0
    ticks_paid: int = 0
    gained: int = 0
    spent: int = 0
    overdrawn: int = 0
    absorbed: int = 0
    end_encore: int | None = None
    end_members: int | None = None

    @property
    def dry_rate(self) -> float:
        return self.upkeeps_dry / self.upkeeps if self.upkeeps else 0.0

    @property
    def full_rate(self) -> float:
        return self.upkeeps_full / self.upkeeps if self.upkeeps else 0.0

    @property
    def runway_rate(self) -> float:
        return (self.upkeeps_saturated / self.upkeeps
                if self.upkeeps else 0.0)

    @property
    def all_ticked_rate(self) -> float:
        """Denominator is COMPLETE upkeeps only -- see the module note on
        fights that end mid-upkeep."""
        return (self.upkeeps_all_ticked / self.upkeeps_complete
                if self.upkeeps_complete else 0.0)

    @property
    def mean_surplus(self) -> float:
        return sum(self.surplus) / len(self.surplus) if self.surplus else 0.0

    @property
    def mean_held(self) -> float:
        return sum(self.held) / len(self.held) if self.held else 0.0

    @property
    def paid_rate(self) -> float:
        return self.ticks_paid / self.ticks if self.ticks else 0.0


def trace(log: list[dict]) -> EncoreTrace:
    out = EncoreTrace()
    pending: dict | None = None

    def close(upkeep: dict | None) -> None:
        """Score the upkeep now that its member ticks have all been seen."""
        if upkeep is None:
            return
        members = upkeep["members"]
        seen = upkeep["seen"]
        if seen < members:
            out.upkeeps_truncated += 1
            return
        out.upkeeps_complete += 1
        if upkeep["paid"] == members:
            out.upkeeps_all_ticked += 1

    for ev in log:
        kind = ev["event"]
        if kind == "salon_upkeep":
            close(pending)
            pending = {"members": ev["members"], "seen": 0, "paid": 0}
            out.upkeeps += 1
            out.held.append(ev["encore"])
            out.members.append(ev["members"])
            out.surplus.append(ev["encore"] - ev["cost"])
            # "Dry" is one member's cost, not the stage's: the first member
            # in the queue is the one that starves first, and cost/members
            # is exactly that per-member price.
            per_member = ev["cost"] // ev["members"] if ev["members"] else 0
            if ev["encore"] < per_member:
                out.upkeeps_dry += 1
            if ev["encore"] >= ev["cost"]:
                out.upkeeps_full += 1
            if ev["encore"] >= RUNWAY_SATURATED_TURNS * ev["cost"]:
                out.upkeeps_saturated += 1
        elif kind == "salon_tick":
            out.ticks += 1
            out.ticks_paid += 1 if ev["paid"] else 0
            if pending is not None:
                pending["seen"] += 1
                pending["paid"] += 1 if ev["paid"] else 0
        elif kind == "gain_encore":
            out.gained += ev["amount"]
        elif kind == "encore_spent":
            out.spent += ev["amount"]
        elif kind == "encore_overdraw":
            out.overdrawn += ev["amount"]
        elif kind == "encore_absorb":
            out.absorbed += ev["amount"]
        elif kind == "encore_end":
            out.end_encore = ev["encore"]
            out.end_members = ev["members"]
    close(pending)
    return out


def aggregate(traces: list[EncoreTrace]) -> dict:
    """Pooled across combats. Pooling the RATIOS' numerators and
    denominators (not averaging per-combat ratios) keeps a 2-turn combat
    from weighing as much as a 20-turn one -- the same rule the Fanfare
    aggregate follows."""
    live = [t for t in traces if t.upkeeps or t.end_encore is not None]
    if not live:
        return {}
    upkeeps = sum(t.upkeeps for t in live)
    complete = sum(t.upkeeps_complete for t in live)
    surplus = [v for t in live for v in t.surplus]
    held = [v for t in live for v in t.held]
    ends = [t.end_encore for t in live if t.end_encore is not None]
    gained = sum(t.gained for t in live)
    drained = sum(t.spent + t.absorbed for t in live)
    return {
        "combats": len(live),
        "upkeeps": upkeeps,
        "stage_combats": sum(1 for t in live if t.upkeeps),
        "dry_rate": (sum(t.upkeeps_dry for t in live) / upkeeps
                     if upkeeps else 0.0),
        "full_rate": (sum(t.upkeeps_full for t in live) / upkeeps
                      if upkeeps else 0.0),
        "runway_rate": (sum(t.upkeeps_saturated for t in live) / upkeeps
                        if upkeeps else 0.0),
        "all_ticked_rate": (sum(t.upkeeps_all_ticked for t in live) / complete
                            if complete else 0.0),
        "truncated_upkeeps": sum(t.upkeeps_truncated for t in live),
        "mean_surplus": sum(surplus) / len(surplus) if surplus else 0.0,
        "mean_held": sum(held) / len(held) if held else 0.0,
        "mean_members": (sum(t2 for t in live for t2 in t.members)
                         / len(surplus) if surplus else 0.0),
        "gained_per_combat": gained / len(live),
        "spent_per_combat": sum(t.spent for t in live) / len(live),
        # Above 1.0 means the combat generated Encore it never used. DRAINED
        # is every sink that takes points off the meter -- upkeep and
        # spend_encore cards (`encore_spent`) plus absorbed damage
        # (`encore_absorb`) -- see the module note on why spends alone is the
        # wrong denominator.
        #
        # None, NOT 0.0, when nothing was ever drained: a deck that generated
        # Encore and never used a point is the most saturated case there is,
        # and reporting it as the ratio's minimum would print the strongest
        # finding as the weakest number.
        "drained_per_combat": drained / len(live),
        "gain_drain_ratio": gained / drained if drained else None,
        "overdrawn_per_combat": sum(t.overdrawn for t in live) / len(live),
        "absorbed_per_combat": sum(t.absorbed for t in live) / len(live),
        "mean_end_encore": sum(ends) / len(ends) if ends else 0.0,
        "end_samples": len(ends),
    }


def format_row(label: str, agg: dict) -> str:
    if not agg:
        return f"  {label:<20} (no encore combats)"
    ratio = agg["gain_drain_ratio"]
    ratio_text = "NEVER USED" if ratio is None else f"{ratio:4.2f}"
    return (f"  {label:<20} dry {agg['dry_rate']:6.1%} "
            f"full {agg['full_rate']:6.1%} "
            f"runway{RUNWAY_SATURATED_TURNS}+ {agg['runway_rate']:6.1%} "
            f"all-ticked {agg['all_ticked_rate']:6.1%}   "
            f"surplus {agg['mean_surplus']:+6.1f} "
            f"held {agg['mean_held']:5.1f} "
            f"end {agg['mean_end_encore']:5.1f}   "
            f"gain/drain {ratio_text} "
            f"({agg['gained_per_combat']:.1f} vs "
            f"{agg['drained_per_combat']:.1f} = "
            f"{agg['spent_per_combat']:.1f} spent + "
            f"{agg['absorbed_per_combat']:.1f} absorbed, per combat)   "
            f"n={agg['combats']} combats / {agg['upkeeps']} upkeeps")
