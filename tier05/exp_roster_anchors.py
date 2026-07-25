"""G-E2: same-world anchors for the roster under RUNTEMPLATE 7.

Furina's salon arm measured 18.5% in the v7 ghost check, and nobody could say
whether that is strong, because every Klee and ref-Ironclad number on record
was taken in an earlier world. RUNTEMPLATE 6 and 7 landed in one day, each bump
archives every prior measurement by house rule, and DRAFTER_VERSION has since
moved to 10 as well. A cross-character comparison across those bumps is not a
comparison.

So this re-runs the anchors in the SAME world, with the same seed, the same
route policy and the same grants as the ghost check, so that "salon is
dominant" becomes a statement with a denominator.

It deliberately re-prints Furina alongside them rather than quoting the ghost
check's numbers: DRAFTER_VERSION 10 (G-E1) changed the fanfare limb of
`core_complete`, so the v7 ghost-check fanfare row is itself archive now. Only
numbers produced by one invocation of this script belong in the same table.

This script MEASURES. It does not rule. The standing salon question -- trim,
or ratify as intentional -- is explicitly out of scope for this sprint and
waits on these numbers plus a [USER] ruling.

Usage: python -m tier05.exp_roster_anchors [--runs N] [--route NAME] [--jobs N]
"""

from __future__ import annotations

import statistics
import sys

from tier0 import constants as C
from tier05 import draft, model

SEED = 11            # the sprint's registered seed, as the ghost check uses
RUNS = 600

# (character, archetype). Klee's three plans plus the reference Ironclad's
# single generic plan, plus Furina's three, so every row in the printed table
# was produced by this run rather than quoted from an archived one.
ARMS: tuple[tuple[str, str], ...] = (
    ("klee", "demolition"),
    ("klee", "spark"),
    ("klee", "reaction"),
    ("ref_ironclad", "generic"),
    ("furina", "salon"),
    ("furina", "spotlight"),
    ("furina", "fanfare"),
)


def _arm(character: str, archetype: str, runs: int, route_name: str,
         jobs: int) -> dict:
    results = model.run_many(character, archetype, archetype,
                             draft.assigned_policy, runs, SEED,
                             grant_relics=True, grant_potions=True,
                             jobs=jobs, route_name=route_name)
    decks = [[c for c in r.deck_ids] for r in results]
    return {
        "win": sum(r.won for r in results) / len(results),
        # acts_completed counts boss wins, so >= 1 IS the act-1 clear.
        "act1": sum(r.acts_completed >= 1 for r in results) / len(results),
        "acts": statistics.mean(r.acts_completed for r in results),
        "decksize": statistics.mean(len(d) for d in decks),
        # Variable under RUNTEMPLATE 6+: a route decides how many fights a run
        # takes, and a deck that dies early simply gets fewer. Printed so any
        # per-combat rate quoted off this sweep can be rescaled honestly
        # rather than against a template constant that no longer exists.
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
    # Read the stamps, never hard-code them -- the ghost check mislabelled its
    # own world exactly one bump after it was written.
    print(f"ROSTER ANCHORS — RUNTEMPLATE {C.RUNTEMPLATE_VERSION}, "
          f"DRAFTER {C.DRAFTER_VERSION}, CONSTANTS {C.CONSTANTS_VERSION}")
    print(f"  {runs} runs/arm, seed {SEED}, route {route_name}, "
          f"relics + potions granted")
    print("  Every row below comes from THIS run. Nothing is quoted across a "
          "version bump.")
    print("=" * 78)
    print(f"\n  {'character':>13} {'plan':>12} {'win':>7} {'act-1':>7} "
          f"{'acts':>6} {'deck':>6} {'fights':>7}")

    for character, archetype in ARMS:
        a = _arm(character, archetype, runs, route_name, jobs)
        print(f"  {character:>13} {archetype:>12} {a['win']:>6.1%} "
              f"{a['act1']:>6.1%} {a['acts']:>6.2f} {a['decksize']:>6.1f} "
              f"{a['fights']:>7.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
