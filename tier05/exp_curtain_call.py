"""Curtain Call sweep (R85) — the §6 telemetry riders, per Furina arm.

The roster table itself comes from the UNCHANGED `exp_roster_anchors`
invocation (cells 0–3 quote only that); this script adds the riders the
pre-registration names, from the same canonical cell parameters:

- hydro-application uptime per combat (aura_telemetry; registered
  definition in the sprint log §4) — the Track B retype tripwire
  (prediction 7: within ±10% relative of cell 0).
- fanfare payoffs drafted per deck (`draft._reads_fanfare`, the ghost
  check's metric, the null result's own denominator).
- per-card take-when-offered for the sweep's touched cards, from the
  fanfare arm's decks (held-in-deck rate, the ghost check's presence
  metric — offer-level accounting lives in the drafter sweeps, not here).

R14: diagnostics feeding a ruling. No acceptance targets in this file; the
registered bars live in the sprint log §5.

Usage: python -m tier05.exp_curtain_call [--runs N] [--seed N]
"""

from __future__ import annotations

import statistics
import sys

from tier0.content import loader
from tier05 import aura_telemetry, cells, draft

BASE = cells.CANONICAL.but(name="curtain-call-riders")
ARMS = ("salon", "spotlight", "fanfare")

# The sweep's touched cards (sprint §7 + the authored red-pen), for the
# take-when-offered table. Ids, not names -- renames are display-only.
WATCHED = (
    "dramatic_entrance", "standing_room_only", "crescendo", "showstopper",
    "flood_of_emotion", "high_tide", "thunderous_ovation", "warmup_act",
    "rapturous_applause", "lasting_impression", "crowd_work",
    "fortissimo_guard", "pit_orchestra", "courtroom_drama", "quick_change",
    "poised_riposte", "matinee_performance", "usher_the_waves",
    "torrential_turn", "audience_participation",
)


def main(argv: list[str] | None = None) -> int:
    base, _ = cells.parse_overrides(
        list(sys.argv[1:] if argv is None else argv), BASE)
    cells.print_header(base, "CURTAIN CALL RIDERS",
                       f"furina, {len(ARMS)} assigned arms")
    print(f"\n  {'arm':>10} {'win':>7} {'act-1':>7} {'uptime':>7} "
          f"{'apps/fight':>11} {'payoffs':>8} {'deck':>6}")

    fanfare_decks = None
    for archetype in ARMS:
        a = base.but(character="furina", archetype=archetype).arm()
        results = a["results"]
        traces = [tr for r in results for _, tr in r.aura_traces]
        agg = aura_telemetry.aggregate(traces)
        decks = [[loader.peek_card(cid) for cid in r.deck_ids]
                 for r in results]
        payoffs = statistics.mean(
            sum(1 for c in d if draft._reads_fanfare(c)) for d in decks)
        if archetype == "fanfare":
            fanfare_decks = decks
        print(f"  {archetype:>10} {a['win']:>6.1%} {a['act1']:>6.1%} "
              f"{agg['uptime']:>6.1%} {agg['applications_per_fight']:>11.2f} "
              f"{payoffs:>8.2f} {a['decksize']:>6.1f}")

    print("\n  fanfare-arm presence of the sweep's touched cards:")
    for cid in WATCHED:
        held = sum(any(c.id.rstrip("+") == cid for c in d)
                   for d in fanfare_decks)
        print(f"    {cid:>24}  in {held / len(fanfare_decks):>5.1%} of decks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
