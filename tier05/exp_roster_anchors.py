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

import sys

from tier05 import cells

# R68: seed, runs, route and loadout come from the ratified cell rather than
# from local literals. They used to be `SEED = 11` / `RUNS = 600` here, which
# happened to agree with the ratified cell and with nothing else in the
# directory -- five different hand-rolled seeds were in play across twelve
# scripts, all of them looking equally authoritative at the call site.
BASE = cells.CANONICAL.but(name="roster-anchors")

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


def main(argv: list[str] | None = None) -> int:
    base, _ = cells.parse_overrides(
        list(sys.argv[1:] if argv is None else argv), BASE)

    # The stamp is read from the live world, never hard-coded -- the ghost
    # check mislabelled its own world exactly one bump after it was written,
    # which is the defect R68's mandatory stamp line exists to make
    # structurally impossible.
    cells.print_header(base, "ROSTER ANCHORS",
                       f"{len(ARMS)} arms across the roster")
    print("  Every row below comes from THIS run. Nothing is quoted across a "
          "version bump.")
    print(f"\n  {'character':>13} {'plan':>12} {'win':>7} {'act-1':>7} "
          f"{'acts':>6} {'deck':>6} {'fights':>7}")

    for character, archetype in ARMS:
        # One Cell per arm: same seed, same runs, same route, same loadout,
        # differing only in the two fields the table's first two columns
        # name. `arm()` is the consolidated reducer (R68) -- this script,
        # the ghost check and the free-draft cell each had their own copy.
        a = base.but(character=character, archetype=archetype).arm()
        print(f"  {character:>13} {archetype:>12} {a['win']:>6.1%} "
              f"{a['act1']:>6.1%} {a['acts']:>6.2f} {a['decksize']:>6.1f} "
              f"{a['fights']:>7.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
