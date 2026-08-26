"""E2b (Neap Tide v2.1): isolating the accrual cuts inside the F batch.

PRE-AUTHORIZED, and it fired. Track E licensed E2b "only if E2 reads odd".
E2 read odd: on top of R73's own cut, the F batch took a further 3.4-6.0pp of
win rate and 12.7-19.4pp of act-1 clear, and act-1 Charge accrual fell
0.7-1.2 points of bank. Section 5 had held the accrual side fixed with G6 as
its ONE sanctioned exception, and the batch shipped two.

THE QUESTION. The F batch mixes two kinds of change:

    accrual   G6 (tactical_retreat loses its exhaust outlet)
              G8 (moonlit_offering loses exhaust_from 2 AND gain_charge 3)
    payout    R74 (Garment loses a 7-to-all splash)
              R77 (Surging Shoal 7 -> 6)
              R75 (Honor Guard loses its conscript)

Both shrink her. Only the first kind is a §5 exception, and P9 says to suspect
it before touching the multiplier again. So the arms revert the accrual cuts
and leave the payout cuts alone: whatever the arms do NOT recover is the
payout half's contribution.

WHAT THIS CANNOT DO, said plainly. The G8 arm restores moonlit_offering's old
effect line but does NOT re-add swift_currents to the pool -- re-adding a card
means pool membership, rarity tables and draft weights, which is a different
world rather than a reverted knob. So the G8 arm measures "the accrual moonlit
lost", not "the merge undone". The residual after both arms is therefore an
UPPER bound on the payout half, not an exact one.

jobs is forced to 1: the arms are made by mutating the loader's shared card
index, and a spawned worker re-reads the sheet from disk. E1 already paid for
this lesson.

Usage: python -m tier05.exp_neap_tide_e2b [--runs N] [--seed N]
"""

from __future__ import annotations

import copy
import sys
import time

from tier0.content import loader
from tier05 import cells, expcli, kurage_telemetry

PLANS = ("priest", "commander", "assist", "generic")

# The pre-G6 / pre-G8 effect lines, transcribed from the sheet at be0df49^.
PRE_G6_TACTICAL_RETREAT = [
    {"op": "exhaust_from", "amount": 1, "select": "chosen"},
    {"op": "draw", "amount": 1},
]
PRE_G8_MOONLIT_OFFERING = [
    {"op": "exhaust_from", "amount": 2, "select": "chosen"},
    {"op": "gain_charge", "amount": 3},
    {"op": "draw", "amount": 2},
]


def _patch(card_id: str, effects: list[dict]) -> None:
    """Swap one prototype's effects in the shared card index."""
    proto = loader._card_index()[card_id]
    proto.effects = copy.deepcopy(effects)


def _run(cell, reverts: dict[str, list[dict]]) -> dict:
    """One arm. Reverts applied for the duration, then undone."""
    index = loader._card_index()
    saved = {cid: copy.deepcopy(index[cid].effects) for cid in reverts}
    for cid, effects in reverts.items():
        _patch(cid, effects)
    try:
        arm = cell.arm()
    finally:
        for cid, effects in saved.items():
            _patch(cid, effects)
    arm["pulses"] = kurage_telemetry.by_act(
        [pair for r in arm["results"] for pair in r.kurage_traces])
    return arm


ARMS = (
    ("landed", {}),
    ("+G6 accrual", {"tactical_retreat": PRE_G6_TACTICAL_RETREAT}),
    ("+G8 accrual", {"moonlit_offering": PRE_G8_MOONLIT_OFFERING}),
    ("+both", {"tactical_retreat": PRE_G6_TACTICAL_RETREAT,
               "moonlit_offering": PRE_G8_MOONLIT_OFFERING}),
)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    base = cells.CANONICAL.but(character="kokomi", archetype="priest")
    base, rest = cells.parse_overrides(argv, base)
    if rest:
        raise SystemExit(f"unexpected argument(s): {' '.join(rest)}")
    base = base.but(jobs=1)          # the patch does not survive a spawn

    cells.print_header(
        base, "E2b -- isolating the F batch's accrual cuts",
        subject="kokomi, all four plans", varying=("archetype",))
    print("  Arms revert ACCRUAL only. R74/R75/R77 payout cuts stay in every")
    print("  arm, so the residual is the payout half (an upper bound -- the")
    print("  G8 arm restores moonlit's line but not swift_currents' slot).")

    t0 = time.perf_counter()
    table = {}
    for plan in PLANS:
        cell = base.but(archetype=plan)
        table[plan] = {label: _run(cell, reverts) for label, reverts in ARMS}

    print()
    print(f"{'plan':11} {'arm':13} {'win%':>6} {'act1%':>6} {'chg a1':>7}")
    print("-" * 50)
    for plan in PLANS:
        for label, _ in ARMS:
            a = table[plan][label]
            chg = a["pulses"].get(0, {}).get("mean_charge", float("nan"))
            print(f"{plan:11} {label:13} {a['win']*100:6.1f} "
                  f"{a['act1']*100:6.1f} {chg:7.1f}")
        landed = table[plan]["landed"]
        both = table[plan]["+both"]
        print(f"{'':11} {'accrual worth':13} "
              f"{(both['win']-landed['win'])*100:+6.1f} "
              f"{(both['act1']-landed['act1'])*100:+6.1f}")
        print()

    print(f"({base.runs} runs/arm, {len(PLANS)} plans, {len(ARMS)} arms "
          f"in {time.perf_counter() - t0:.1f}s)")
    print(f"  {base.stamp()}")
    return 0


if __name__ == "__main__":
    expcli.help_if_asked(__doc__)
    raise SystemExit(main())
