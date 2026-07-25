"""Ghost check: does the Fanfare sprint's null survive RUNTEMPLATE_VERSION 6?

The map rework replaces the linear `node_template` spine with a generated
16-floor DAG plus route policies and an event layer, and it was built partly
to fix instrumentation errors. The Fanfare sprint closed on a null that was
measured under RUNTEMPLATE 5, so by house rule every number in
docs/furina-fanfare-sprint-log.md is now archive. This re-derives the two
that the close-out actually rests on:

1. THE STATLINE — run winrate and act-1 clear per archetype. If gate (1)
   suddenly passes under v6, the sprint was chasing a ghost and the
   close-out reopens.

2. PAYOFF REACH — how many of its OWN payoff cards the average fanfare deck
   holds. This is the compositional claim the null is built on (measured
   1.99 of ~18.4 under v5), and it is the one that should be independent of
   the run template. If the map rework moves it materially, then the old
   template was distorting draft reach and the diagnosis was an artefact.

A payoff is `draft._reads_fanfare`: printed output that scales with or
unlocks from held Fanfare. Deliberately NOT `core_complete`, which the
sprint established is an instrument bug -- it tests generation and floor
coverage, neither of which is a payoff, so it declares the archetype online
while it holds two payoffs in eighteen cards. That bug is reported here as
its own line rather than being used as a measure.

R14: diagnostics feeding a ruling. No acceptance targets in this file; the
registered bars live in the sprint log.

Usage: python -m tier05.exp_furina_ghostcheck [--runs N] [--route NAME]
"""

from __future__ import annotations

import collections
import statistics
import sys

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft, fanfare_telemetry, model

SEED = 11            # the sprint's registered seed
RUNS = 200
ARMS = ("fanfare", "salon", "spotlight")


def _decks(results: list) -> list[list]:
    return [[loader.peek_card(cid) for cid in r.deck_ids] for r in results]


def _arm(archetype: str, runs: int, route_name: str, jobs: int) -> dict:
    results = model.run_many("furina", archetype, archetype,
                             draft.assigned_policy, runs, SEED,
                             grant_relics=True, grant_potions=True,
                             jobs=jobs, route_name=route_name)
    decks = _decks(results)
    traces = [tr for r in results for _, tr in r.fanfare_traces]
    agg = fanfare_telemetry.aggregate(traces)
    payoffs = [sum(1 for c in d if draft._reads_fanfare(c)) for d in decks]
    return {
        "results": results,
        "decks": decks,
        "win": sum(r.won for r in results) / len(results),
        # acts_completed counts boss wins, so >= 1 IS the act-1 clear.
        "act1": sum(r.acts_completed >= 1 for r in results) / len(results),
        "payoffs": statistics.mean(payoffs),
        "decksize": statistics.mean(len(d) for d in decks),
        "online": sum(draft.core_complete(d, archetype) for d in decks)
                  / len(decks),
        "mean_at_read": agg.get("mean_at_read", 0.0),
        "read_at_cap": agg.get("read_at_cap", 0.0),
        "floors": fanfare_telemetry.per_run(
            agg, len(results)).get("floor_granted_per_run", 0.0),
        # Fights per run is a CONSTANT no longer: a route decides how many
        # fights a run takes. Printed so any per-combat figure quoted off this
        # sweep can be rescaled honestly instead of against a template.
        "fights": statistics.mean(len(r.fight_stats) for r in results),
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    runs, route_name, jobs = RUNS, "hunter", 0
    for flag, cast in (("--runs", int), ("--route", str), ("--jobs", int)):
        if flag in args:
            i = args.index(flag)
            value = cast(args[i + 1])
            del args[i:i + 2]
            if flag == "--runs":
                runs = value
            elif flag == "--route":
                route_name = value
            else:
                jobs = value

    print("=" * 78)
    # Read the stamp, never hard-code it. This script exists to catch a world
    # changing under a measurement, so a banner that names a version by hand
    # is the one line guaranteed to be wrong the next time it matters -- and
    # it was, one bump after it was written.
    print(f"FURINA GHOST CHECK under RUNTEMPLATE_VERSION "
          f"{C.RUNTEMPLATE_VERSION} — {runs} runs/arm, "
          f"seed {SEED}, route {route_name}")
    print("  Archive comparison (RUNTEMPLATE 5, seed 11): fanfare 1.3% win / "
          "44.0% act-1,")
    print("  payoff reach 1.99 per ~18.4-card deck. Gate (1): win >= 3% AND "
          "act-1 >= 50%.")
    print("=" * 78)
    print(f"\n  {'arm':>10} {'win':>7} {'act-1':>7} {'payoffs':>8} "
          f"{'deck':>6} {'reach':>7} {'online':>7} {'mean@read':>10} "
          f"{'floors/run':>11} {'fights':>7}")

    arms = {}
    for archetype in ARMS:
        a = _arm(archetype, runs, route_name, jobs)
        arms[archetype] = a
        gate = "  <-- GATE (1)" if (a["win"] >= 0.03
                                    and a["act1"] >= 0.50) else ""
        print(f"  {archetype:>10} {a['win']:>6.1%} {a['act1']:>6.1%} "
              f"{a['payoffs']:>8.2f} {a['decksize']:>6.1f} "
              f"{a['payoffs'] / a['decksize']:>6.1%} {a['online']:>6.1%} "
              f"{a['mean_at_read']:>10.1f} {a['floors']:>11.1f} "
              f"{a['fights']:>7.1f}{gate}")

    # The signature commons: the null's sharpest form is that the cards the
    # sprint spent two levers buffing are simply not in the deck.
    print("\n  fanfare-arm presence of the cards F-B1/F-B3 buffed:")
    decks = arms["fanfare"]["decks"]
    for cid in ("dramatic_entrance", "showstopper", "warmup_act",
                "standing_room_only", "high_tide", "flood_of_emotion"):
        held = sum(any(c.id.rstrip("+") == cid for c in d) for d in decks)
        print(f"    {cid:>22}  in {held / len(decks):>5.1%} of decks")

    # Top damage sources: under v5 the #1 in every deck was the starter basic.
    print("\n  fanfare-arm most-held cards (v5: the 4-damage starter basic "
          "out-damaged every payoff):")
    counts = collections.Counter(c.id.rstrip("+") for d in decks for c in d)
    for cid, n in counts.most_common(6):
        print(f"    {cid:>22}  {n / len(decks):>5.2f} copies/deck")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
