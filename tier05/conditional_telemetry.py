"""Conditional rider fire-rate telemetry (salon UI sprint Track 4, D4).

Reads the combat event log; changes nothing.

The immediate question is `graceful_retreat` (Slip Backstage), whose
`hp_lost_this_turn` rider is suspected near-dead: it is a BLOCK card, and
block resolves before the enemy swings, so the condition it reads describes
damage that has usually not happened yet on the turn the card is played.

The instrument is generic on purpose. "How often does this rider actually
fire" is a question every conditional on the sheet can be asked, and a
graceful_retreat counter would have to be rewritten for the next suspect.
`_op_conditional` emits one row per evaluation carrying the card id and the
predicate name, so a rate can be read per card, per predicate, or both.

WHAT THE DENOMINATOR IS: evaluations, not plays. They differ -- a card that
repeats itself evaluates its conditional twice in one play -- and
evaluations is the right unit for "how often does the rider pay", which is
the question. Plays are recoverable from the `play` events if a later pass
wants the other unit.

MEASURE ONLY (sprint brief Track 4): any re-authoring of the condition is
red-pen and out of scope.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConditionalTrace:
    """One combat's conditional evaluations, keyed (card, predicate)."""

    evaluated: dict[tuple[str, str], int] = field(default_factory=dict)
    fired: dict[tuple[str, str], int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.evaluated.values())


def trace(log: list[dict]) -> ConditionalTrace:
    out = ConditionalTrace()
    for ev in log:
        if ev["event"] != "conditional":
            continue
        key = (ev["card"], ev["predicate"])
        out.evaluated[key] = out.evaluated.get(key, 0) + 1
        if ev["fired"]:
            out.fired[key] = out.fired.get(key, 0) + 1
    return out


def aggregate(traces: list[ConditionalTrace]) -> dict:
    """Pooled counts per (card, predicate), plus the rate. Pooled, not
    averaged: a combat that played the card once must not weigh as much as
    one that played it six times."""
    evaluated: dict[tuple[str, str], int] = {}
    fired: dict[tuple[str, str], int] = {}
    for t in traces:
        for key, n in t.evaluated.items():
            evaluated[key] = evaluated.get(key, 0) + n
        for key, n in t.fired.items():
            fired[key] = fired.get(key, 0) + n
    return {
        key: {
            "evaluated": n,
            "fired": fired.get(key, 0),
            "rate": fired.get(key, 0) / n if n else 0.0,
        }
        for key, n in evaluated.items()
    }


def format_rows(agg: dict, only_card: str | None = None) -> list[str]:
    """Sorted by fire rate ASCENDING -- the dead riders are the finding, so
    they belong at the top of the table rather than buried under the ones
    that work."""
    rows = [(k, v) for k, v in agg.items()
            if only_card is None or k[0] == only_card]
    rows.sort(key=lambda kv: (kv[1]["rate"], -kv[1]["evaluated"]))
    return [f"  {card:<24} {pred:<28} {v['rate']:6.1%} "
            f"({v['fired']}/{v['evaluated']})"
            for (card, pred), v in rows]
