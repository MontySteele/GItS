"""F4 (Neap Tide addendum): does the Sly-lane bridge connect anything?

R14: report-only. No acceptance target lives here.

THE CLAIM UNDER TEST. Her Charge and Burst meters both pay on the EXHAUST verb
and only on it. The Sly lane makes DISCARDS. So the assist lane ran a churn
engine wired to nothing, and that -- not the pulse multiplier -- is why E1 read
0.5-2.0% assist win rate at EVERY value of the knob. F4 adds three rows to
connect it: `ebb_tide` converts hand cards into chosen exhausts, `salt_line`
rings a Sly bell straight into the exhaust pile, `undertow` reads the pile the
lane has been filling and pays energy back when it is discarded.

THE ARMS, paired seeds, one pool apart:

    landed   today's world, the three bridge rows in the pool
    pre-F4   the same world with all three rows REMOVED from the draft pool

Removal, not neutering: these cards did not exist before this pass, so the
honest counterfactual is a pool without them. Neutering their effects would
leave three dead rows diluting every draft screen and measure something nobody
shipped.

WHY THE POOL PATCH IS A REMOVAL FROM `_card_index`. The drafter, the reward
roller and the deck builder all read that index, so dropping the entries there
removes the cards from every surface at once -- which is what "the pool before
F4" means. jobs is forced to 1 for the same reason E1 and E2b force it: a
spawned worker re-imports the module from source and the patch vanishes,
silently producing two identical arms.

Usage: python -m tier05.exp_neap_tide_f4 [--runs N] [--seed N]
"""

from __future__ import annotations

import sys
import time

from tier0.content import loader
from tier05 import cells, draft, elite_blitz, rewards

# Every plan, not just assist. `salt_line` is [assist, generic], so the pool
# change reaches more than the lane it was written for, and "did it cost the
# other lanes anything" is part of the question rather than an assumption.
PLANS = ("priest", "commander", "assist", "generic")

F4_ROWS = ("ebb_tide", "salt_line", "undertow")


def _clear_downstream_caches() -> None:
    """Drop every memoised VIEW of the card index, and nothing upstream of it.

    NOT optional, and the first version of this script did not do it. The
    reward roller caches its rarity buckets, so the pre-F4 arm built them
    WITHOUT the three rows, the restore put the rows back into `_card_index`,
    and the landed arm rolled its rewards off the stale bucket anyway. Both
    arms then came out byte-identical -- the exact failure mode, and the exact
    tell, that E1's `jobs=0` mistake produced.

    What caught it was the DRAFT-RATE column reading 0.0% in an arm a direct
    measurement had already shown at ~12%. The win-rate delta alone was a
    clean +0.0 on all four plans, which would have read as "the bridge changes
    nothing" -- a publishable-looking wrong answer. Any A/B that patches
    content should print how often the patched content was actually seen.

    `loader` is deliberately NOT cleared: `_card_index` is an lru_cache whose
    dict this script MUTATES, so clearing it would rebuild from the sheet and
    silently undo the removal -- turning the pre-F4 arm into a second copy of
    the landed one.
    """
    for module in (rewards, draft):
        for name in dir(module):
            fn = getattr(module, name)
            if hasattr(fn, "cache_clear"):
                fn.cache_clear()


def _run(cell, drop: tuple[str, ...]) -> dict:
    """One arm, with `drop` removed from the shared card index."""
    index = loader._card_index()
    saved = {cid: index[cid] for cid in drop if cid in index}
    for cid in saved:
        del index[cid]
    _clear_downstream_caches()
    try:
        arm = cell.arm()
    finally:
        index.update(saved)
        _clear_downstream_caches()
    arm["elites"] = elite_blitz.aggregate(arm["results"])
    arm["drafted"] = {
        cid: sum(1 for r in arm["results"] if cid in r.deck_ids)
        for cid in F4_ROWS}
    return arm


ARMS = (("pre-F4", F4_ROWS), ("landed", ()))


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    base = cells.CANONICAL.but(character="kokomi", archetype="assist")
    base, rest = cells.parse_overrides(argv, base)
    if rest:
        raise SystemExit(f"unexpected argument(s): {' '.join(rest)}")
    base = base.but(jobs=1)          # the patch does not survive a spawn

    cells.print_header(
        base, "F4 -- the Sly-lane bridge, pool in vs pool out",
        subject="kokomi, all four plans", varying=("archetype",))
    print("  arms: pre-F4 (3 rows removed from the pool) vs landed.")
    print("  P7's pre-F4 baseline is the assist column of E1: 0.5-2.0% win at")
    print("  every pulse multiplier. R14: no target is asserted here.")

    t0 = time.perf_counter()
    table = {}
    for plan in PLANS:
        cell = base.but(archetype=plan)
        table[plan] = {label: _run(cell, drop) for label, drop in ARMS}

    print()
    print(f"{'plan':11} {'arm':8} {'win%':>6} {'act1%':>7} {'acts':>5} "
          f"{'deck':>5} {'a1 elite clear%':>16}")
    print("-" * 64)
    for plan in PLANS:
        for label, _ in ARMS:
            a = table[plan][label]
            act1 = a["elites"].get(0, {})
            print(f"{plan:11} {label:8} {a['win'] * 100:6.1f} "
                  f"{a['act1'] * 100:7.1f} {a['acts']:5.2f} "
                  f"{a['decksize']:5.1f} "
                  f"{act1.get('clear_rate', 0) * 100:16.1f}")
        d_win = (table[plan]["landed"]["win"]
                 - table[plan]["pre-F4"]["win"]) * 100
        d_act1 = (table[plan]["landed"]["act1"]
                  - table[plan]["pre-F4"]["act1"]) * 100
        print(f"{'':11} {'delta':8} {d_win:+6.1f} {d_act1:+7.1f}")
        print()

    # Draft rates are the load-bearing column here, not the win rate. If the
    # rows are not drafted, a null outcome says nothing about the DESIGN -- it
    # says the scorer never saw the cards, and the whole run is a measurement
    # of the drafter instead.
    print("Bridge rows, share of LANDED runs that drafted each")
    print("-" * 64)
    for plan in PLANS:
        runs = len(table[plan]["landed"]["results"])
        cells_txt = "   ".join(
            f"{cid} {n / runs * 100:.1f}%"
            for cid, n in table[plan]["landed"]["drafted"].items())
        print(f"{plan:11} {cells_txt}")

    print()
    print(f"({base.runs} runs/arm, {len(PLANS)} plans, {len(ARMS)} arms "
          f"in {time.perf_counter() - t0:.1f}s)")
    print(f"  {base.stamp()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
