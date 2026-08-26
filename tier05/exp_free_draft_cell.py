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
import sys

from tier05 import cells, draft, expcli

# R68: this experiment WAS the ratified cell -- 600 runs, seed 11, hunter,
# furina/salon, realistic loadout -- expressed as local literals that
# happened to agree with it. Now it says so, and its stamp proves it.
BASE = cells.CANONICAL.but(name="free-draft-g-e3")


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
    base, _ = cells.parse_overrides(
        list(sys.argv[1:] if argv is None else argv), BASE)

    cells.print_header(base, "FREE-DRAFT CELL",
                       "furina/salon, assigned vs adaptive",
                       varying=("policy",))
    print("  assigned = plan-committed (forces salon through every screen)")
    print("  adaptive = free-drafting (power + emergent synergy, no plan "
          "label)")
    print(f"\n  {'policy':>10} {'win':>7} {'act-1':>7} {'deck':>6} "
          f"{'fights':>7} {'salon share':>12}")

    # `arms`, not `cells` -- the local name used to shadow the module this
    # script now gets its configuration from.
    arms = {}
    for policy_name in ("assigned", "adaptive"):
        arm = base.but(policy=policy_name).arm()
        arms[policy_name] = arm
        share = _salon_density(arm["decks"])
        arm["share"] = share
        print(f"  {policy_name:>10} {arm['win']:>6.1%} {arm['act1']:>6.1%} "
              f"{arm['decksize']:>6.1f} {arm['fights']:>7.1f} "
              f"{share:>11.1%}")

    a, f = arms["assigned"], arms["adaptive"]
    print(f"\n  DELTA (free - committed): win {f['win'] - a['win']:+.1%}, "
          f"salon share {f['share'] - a['share']:+.1%}")
    # The confound, printed with the number rather than filed next to it.
    # Audit §2.5: `_static_power` prices 33 of 37 power names at exactly 0.0
    # -- 58.3% of Furina's draftable cards, and 88.9% of the spotlight-tagged
    # ones. The adaptive arm is the one that leans on that scorer, so its
    # winrate is measured through a pricer that is blind to most of the pool
    # it is choosing from, and the delta above is NOT a clean read on
    # free-drafting. Repricing is EPOCH 2 (DRAFTER 11), deferred by [USER] to
    # a design session and deliberately not waited on here.
    # ASCII only in printed strings: a cp1252 console is the Windows default
    # and a section sign here would mojibake the caveat.
    print("  ^ CONFOUNDED, do not cite clean: the adaptive arm scores through"
          "\n    _static_power, which prices 58.3% of Furina's draftable "
          "cards at 0.0"
          "\n    (audit 2.5). Reprice = DRAFTER 11 = EPOCH 2, not yet ruled.")

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
    expcli.help_if_asked(__doc__)
    raise SystemExit(main())
