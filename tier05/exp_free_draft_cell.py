"""G-E3: ONE measurement cell — salon, plan-committed vs free-drafting.

THE QUESTION, and why the instrument had to be built before it could be asked.

The 2026-07-25 co-op playtest reported that the player "went for engine
pieces... rarely bothered" with Salon, while the sim calls salon the strongest
arm on the roster by a factor of two. Those two statements are not obviously
compatible, and the standing drafter cannot arbitrate between them, because it
is PLAN-COMMITTED: `assigned_policy` is handed an archetype and forces it
through every reward screen. A drafter that always takes the salon card
structurally cannot observe salon cards losing screens to neutral engine
pieces. The finding is invisible to the instrument by construction.

`adaptive_policy` is the non-committed counterpart and always has been -- pure
printed power plus synergy weighted by what the deck has already accumulated,
with no assigned label anywhere in it. What it was NOT, until POLICY_VERSION 2,
is able to see Furina: its archetype term began `if a not in ARCHETYPES:
continue`, and ARCHETYPES was hardcoded to Klee's three. Running it on Furina
before the fix would have measured a scorer blind to salon, spotlight and
fanfare alike, and the number would have looked like evidence about drafting.

THIS SCRIPT ENDS AT THE MEASUREMENT. What the number means for the card pool
belongs to the pool-sweep pass; the sprint that produced this file is
explicitly barred from responding to it.

NULL DISCIPLINE, registered in advance: the result is recorded whatever it
shows. If free-draft salon holds near plan-committed salon, the "sim artifact"
hypothesis is WEAKENED and the pool sweep opens knowing that.

Usage: python -m tier05.exp_free_draft_cell [--runs N] [--jobs N]
"""

from __future__ import annotations

import collections
import statistics
import sys

from tier0 import constants as C
from tier05 import draft, model

SEED = 11
RUNS = 600
ARM = ("furina", "salon")


def _cell(policy_name: str, runs: int, jobs: int) -> dict:
    character, archetype = ARM
    results = model.run_many(character, archetype, archetype,
                             draft.POLICIES[policy_name], runs, SEED,
                             grant_relics=True, grant_potions=True,
                             jobs=jobs, route_name="hunter")
    decks = [[c for c in r.deck_ids] for r in results]
    return {
        "results": results,
        "decks": decks,
        "win": sum(r.won for r in results) / len(results),
        "act1": sum(r.acts_completed >= 1 for r in results) / len(results),
        "decksize": statistics.mean(len(d) for d in decks),
        "fights": statistics.mean(len(r.fight_stats) for r in results),
    }


def _salon_density(decks: list[list[str]]) -> float:
    """Fraction of drafted cards carrying the salon tag.

    THE headline number. Winrate answers "is the plan good"; this answers the
    playtest's actual claim, which is about what gets PICKED. A free drafter
    that wins as often while holding half the salon cards is telling a very
    different story from one that simply loses.
    """
    from tier0.content import loader
    total = tagged = 0
    for deck in decks:
        for cid in deck:
            card = loader.peek_card(cid)
            if card.rarity == "basic":
                continue        # the starter was not drafted
            total += 1
            if "salon" in card.archetypes:
                tagged += 1
    return tagged / max(1, total)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    runs, jobs = RUNS, 0
    for flag in ("--runs", "--jobs"):
        if flag in args:
            i = args.index(flag)
            value = int(args[i + 1])
            del args[i:i + 2]
            if flag == "--runs":
                runs = value
            else:
                jobs = value

    print("=" * 78)
    print(f"FREE-DRAFT CELL — salon, RUNTEMPLATE {C.RUNTEMPLATE_VERSION}, "
          f"DRAFTER {C.DRAFTER_VERSION}, POLICY {draft.POLICY_VERSION}")
    print(f"  {runs} runs/arm, seed {SEED}, route hunter")
    print("  assigned = plan-committed (forces salon through every screen)")
    print("  adaptive = free-drafting (power + emergent synergy, no plan "
          "label)")
    print("=" * 78)
    print(f"\n  {'policy':>10} {'win':>7} {'act-1':>7} {'deck':>6} "
          f"{'fights':>7} {'salon share':>12}")

    cells = {}
    for policy_name in ("assigned", "adaptive"):
        cell = _cell(policy_name, runs, jobs)
        cells[policy_name] = cell
        share = _salon_density(cell["decks"])
        cell["share"] = share
        print(f"  {policy_name:>10} {cell['win']:>6.1%} {cell['act1']:>6.1%} "
              f"{cell['decksize']:>6.1f} {cell['fights']:>7.1f} "
              f"{share:>11.1%}")

    a, f = cells["assigned"], cells["adaptive"]
    print(f"\n  DELTA (free - committed): win {f['win'] - a['win']:+.1%}, "
          f"salon share {f['share'] - a['share']:+.1%}")

    # What the free drafter actually converged on, if anything. 'goodstuff' is
    # not a classifier failure -- it is the finding, and it is the shape the
    # playtest described.
    from tier0.content import loader
    shapes = collections.Counter(
        draft.dominant_archetype([loader.peek_card(cid) for cid in deck])
        for deck in f["decks"])
    print("\n  free-draft emergent shape:")
    for shape, n in shapes.most_common():
        print(f"    {shape:>12}  {n / len(f['decks']):>6.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
