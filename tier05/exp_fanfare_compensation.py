"""The Fanfare compensation battery — did reader density move the two numbers?

Registered in docs/archive/sprint-fanfare-compensation-2026-07-28.md. The parent
sprint (the Fanfare rework, a197294) shipped single-leg generation as ruled
and left two numbers outside a playable band. This battery exists to answer
whether this pass moved THEM, not whether some other number improved:

  REGISTERED BEFORE-NUMBERS, taken at a197294 in this world, this seed:
    fanfare arm winrate   0.5%   (roster floor is real_silent's 2.0%)
    fanfare arm act-1    44.7%
    salon arm winrate     7.7%   (real_ironclad's anchor, ruled acceptable)
    salon arm act-1      51.7%

Both leading numbers are the FANFARE arm's, and the salon rows are here as
the leak check rather than as a target: the pass put a reader on the STARTER,
which is in every Furina deck, so a compensation aimed at one archetype can
land on all three. If salon moves off its anchor, that row is why.

C3's fire-rate cell is the one the brief demanded by name. A reader that
fires under 10% is D4's mistake re-shipped -- Slip Backstage's old rider fired
3% and nobody knew for a year -- and the answer for a SLOPE reader is not the
conditional telemetry's, because a bonus_formula always evaluates. The
question is whether it PAID: read // step >= 1. That is per-card, so the
samples are kept per card and thresholded here.

STOP CONDITION, from the brief and binding on this sprint: if the fanfare arm
still sits below the 2.0% roster floor after this pass, REPORT AND STOP. A
second compensation round is a [USER] ruling, not a sprint judgment.

Usage: python -m tier05.exp_fanfare_compensation [c1|c2|c3|all] [--runs N]
"""

from __future__ import annotations

import sys

from tier05 import cells, expcli, fanfare_telemetry, rework_sim

# Every arm varies from the ratified cell. The PLAN differs between rows, so
# unlike the pilot-gap battery these rows are not each other's controls --
# they are three separate decks measured under one world.
BASE = cells.CANONICAL.but(name="fanfare-comp", character="furina")

# (label, archetype, pilot_override, what the row is for)
ARMS: tuple[tuple[str, str, str | None, str], ...] = (
    ("fanfare", "fanfare", None, "THE TARGET: 0.5% win / 44.7% act-1 before"),
    ("fanfare*", "fanfare", "salon_stoker",
     "the same deck under the stoker (standing rule: the stoker prices it)"),
    ("salon", "salon", None, "LEAK CHECK: 7.7% before, on the anchor"),
    ("salon*", "salon", "salon_stoker", "the stoker's salon row, 14.5% before"),
    ("spotlight", "spotlight", None, "LEAK CHECK: 2.8% before"),
)

# The readers this pass added or changed. Every one of them has to answer the
# fire-rate question, including the two that were already on the sheet -- a
# converted card is a new reader in every sense that matters here.
#
# STATIC BY CONSTRUCTION, not derived from the sheet: the step is per-card and
# the set is "what a pass changed", which no sheet field records. A new reader
# therefore joins BY HAND, and R135 (2026-08-08) is one -- lasting_impression
# got the commons-rate Block clause as its ruled body, and a reader nobody
# fire-rate-checks is exactly the D4 mistake this cell exists to prevent.
# These keys are BASE ids while the `fanfare_read` event carries the PLAYED
# card's id, so C3 folds sample ids through `rework_sim.base_id` -- an `<id>+`
# copy is the same reader and belongs in the same row. The step is the base
# card's: no upgrade delta on this sheet moves a reader's step.
NEW_READERS: tuple[tuple[str, int], ...] = (
    ("applause_line", 4),
    ("held_breath", 4),
    ("suffering_for_art", 4),
    ("hearts_swelling", 4),
    ("lasting_impression", 4),      # R135, 2026-08-08 (the ruled body)
)

_CACHE: list | None = None


def _arms(base: cells.Cell) -> list[tuple[str, str, cells.Cell, dict]]:
    global _CACHE
    if _CACHE is None:
        _CACHE = []
        for label, arch, pilot, note in ARMS:
            cell = base.but(name=f"fanfare-comp[{label}]", archetype=arch,
                            pilot_override=pilot)
            _CACHE.append((label, note, cell, cell.arm()))
    return _CACHE


def _fanfare_agg(results: list) -> dict:
    return fanfare_telemetry.aggregate(
        [tr for r in results for _, tr in r.fanfare_traces])


def _traces(results: list) -> list:
    return [tr for r in results for _, tr in r.fanfare_traces]


# ======================================================================
# C1 -- the two registered numbers
# ======================================================================

def c1(base: cells.Cell) -> None:
    print("=" * 78)
    print("C1. THE TWO REGISTERED NUMBERS — did the compensation move them?")
    print(f"    {base.stamp()}")
    print("    Rows are DIFFERENT DECKS, not each other's controls. The `*`")
    print("    rows are the stoker pilot and are labelled in every quote.")
    print("=" * 78)
    print(f"\n  {'arm':>10} {'win':>7} {'act-1':>7} {'acts':>6} {'deck':>6} "
          f"{'fights':>7}   what the row is for")
    for label, note, _cell, a in _arms(base):
        print(f"  {label:>10} {a['win']:>6.1%} {a['act1']:>6.1%} "
              f"{a['acts']:>6.2f} {a['decksize']:>6.1f} {a['fights']:>7.1f}   "
              f"{note}")

    fanfare = next(a for label, _n, _c, a in _arms(base) if label == "fanfare")
    print(f"\n  STOP CONDITION: the fanfare arm is at {fanfare['win']:.1%} "
          "against a 2.0% roster floor.")
    if fanfare["win"] < 0.02:
        print("    => STILL BELOW THE FLOOR. Report and stop: a second "
              "compensation round is a [USER] ruling, not a sprint judgment.")
    else:
        print("    => at or above the floor. The band question is [USER]'s, "
              "but the stop condition does not fire.")


# ======================================================================
# C2 -- where the meter comes from and whether it is being read
# ======================================================================

def c2(base: cells.Cell) -> None:
    print("\n" + "=" * 78)
    print("C2. THE METER — sources, and whether the deck reads it now")
    print(f"    {base.stamp()}")
    print("=" * 78)
    print(f"\n  {'arm':>10} {'reads/fight':>12} {'mean@read':>10} "
          f"{'@cap':>7} {'@floor':>7} {'empty':>7}")
    for label, _note, _cell, a in _arms(base):
        agg = _fanfare_agg(a["results"])
        if not agg:
            print(f"  {label:>10}   (no combats with a live meter)")
            continue
        per_fight = agg["reads"] / max(1, agg["combats"])
        print(f"  {label:>10} {per_fight:>12.2f} {agg['mean_at_read']:>10.1f} "
              f"{agg['read_at_cap']:>6.1%} {agg['read_at_floor']:>6.1%} "
              f"{agg['read_empty']:>6.1%}")

    print("\n  GENERATION BY SOURCE (share of requested; single-leg since the "
          "rework)")
    for label, _note, _cell, a in _arms(base):
        totals: dict[str, int] = {}
        for tr in _traces(a["results"]):
            for src, amount in tr.by_source.items():
                totals[src] = totals.get(src, 0) + amount
        grand = sum(totals.values())
        if not grand:
            continue
        shares = "  ".join(
            f"{src} {amount / grand:.1%}"
            for src, amount in sorted(totals.items(), key=lambda kv: -kv[1]))
        print(f"    {label:>10}  {shares}")


# ======================================================================
# C3 -- the fire-rate cell the brief demanded by name
# ======================================================================

def c3(base: cells.Cell) -> None:
    print("\n" + "=" * 78)
    print("C3. READER FIRE-RATES — every card this pass added or changed")
    print(f"    {base.stamp()}")
    print("    PAID = the slope returned at least 1 (read // step >= 1). A")
    print("    bonus_formula always evaluates, so 'did it run' is the wrong")
    print("    question; 'did it pay' is the one D4 should have asked.")
    print("    Under 10% paid is the brief's re-ship threshold.")
    print("=" * 78)
    for label, _note, _cell, a in _arms(base):
        by_card: dict[str, list[int]] = {}
        for tr in _traces(a["results"]):
            for cid, samples in tr.reads_by_card.items():
                by_card.setdefault(rework_sim.base_id(cid), []).extend(samples)
        rows = [(cid, step, by_card.get(cid, [])) for cid, step in NEW_READERS]
        rows = [r for r in rows if r[2]]
        if not rows:
            print(f"\n  {label:>10}  no new reader was ever played")
            continue
        print(f"\n  {label:>10}  {'card':<22} {'reads':>7} {'paid':>7} "
              f"{'mean':>6}")
        for cid, step, samples in rows:
            # max(0, v): the meter can sit below zero since the Hyperbeam,
            # and the readers clamp, so a buried meter pays nothing rather
            # than negative. The rate has to be computed the way the card
            # resolves or it would credit a debt as a payment.
            paid = sum(1 for v in samples if max(0, v) // step >= 1)
            mean = sum(max(0, v) for v in samples) / len(samples)
            flag = "  <-- UNDER 10%" if paid / len(samples) < 0.10 else ""
            print(f"  {'':>10}  {cid:<22} {len(samples):>7} "
                  f"{paid / len(samples):>6.1%} {mean:>6.1f}{flag}")


CELLS = {"c1": c1, "c2": c2, "c3": c3}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    which = "all"
    if argv and not argv[0].startswith("-"):
        which = argv.pop(0)
    runs = 600
    jobs = 0
    while argv:
        flag = argv.pop(0)
        if flag == "--runs":
            runs = int(argv.pop(0))
        elif flag == "--jobs":
            jobs = int(argv.pop(0))
        else:
            raise SystemExit(f"unknown flag {flag!r}")
    base = BASE.but(runs=runs, jobs=jobs)
    for name, fn in CELLS.items():
        if which in ("all", name):
            fn(base)
    return 0


if __name__ == "__main__":
    expcli.help_if_asked(__doc__)
    raise SystemExit(main())
