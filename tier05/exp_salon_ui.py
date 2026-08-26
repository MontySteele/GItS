"""Salon UI sprint — measurement battery (Tracks 3 and 4, 2026-07-28).

Registered in docs/archive/sprint-salon-ui-2026-07-28.md. Both cells are MEASURE
ONLY: they ship an instrument and a baseline, and the levers they inform
(D8's Encore economy, D4's re-authoring of the Slip Backstage condition) are
[USER] red-pen and out of scope.

T3. Encore saturation baseline. The playtest read is that Encore refills
    faster than the stage drains it and trends toward a passively-full free
    block bar. Reported per assigned archetype and PER ACT, because "trends
    toward full" is a claim about late acts -- the stage is largest there,
    so the upkeep bill is largest there too, and a run-level average hides
    exactly the turn where the bill should have started to bite.

T4. Slip Backstage rider fire-rate. `graceful_retreat` reads
    hp_lost_this_turn on a BLOCK card, and block resolves before the enemy
    swings. The whole conditional table is printed alongside it, ascending
    by fire rate, so the card is read in the company of its peers rather
    than against an unstated expectation.

R14: diagnostics feeding a ruling. No acceptance targets in this file.

Usage: python -m tier05.exp_salon_ui [t3|t4|all] [--runs N]
"""

from __future__ import annotations

import sys

from tier0 import constants as C
from tier05 import conditional_telemetry, draft, encore_telemetry, model
from tier05 import expcli

SEED = 20260728
RUNS = 200

# Salon is the primary arm -- it is the only one that fields a stage large
# enough for the upkeep bill to matter. Fanfare and generic are context: if
# the bar saturates for a deck with no members at all, the finding is about
# Encore GENERATION and not about the stage draining it, which is a
# different lever than the one D8 is written against.
CONFIGS = (
    ("salon", "salon"),
    ("fanfare", "fanfare"),
    ("generic", "generic"),
)

WATCHED_CARD = "graceful_retreat"


def _by_act(results: list, attr: str) -> dict[int, list]:
    out: dict[int, list] = {}
    for res in results:
        for act_i, tr in getattr(res, attr):
            out.setdefault(act_i, []).append(tr)
    return out


def _run(archetype: str, pilot_id: str, runs: int) -> list:
    return model.run_many(
        "furina", archetype, pilot_id, draft.assigned_policy,
        runs, SEED, grant_relics=True, grant_potions=True)


def t3(runs: int = RUNS) -> None:
    print("=" * 78)
    print(f"T3. Encore saturation baseline — {runs} realistic runs/arm, "
          f"seed {SEED}")
    print(f"    constants: SALON_TICK_ENCORE_COST "
          f"{C.SALON_TICK_ENCORE_COST}, SALON_MEMBER_SLOTS "
          f"{C.SALON_MEMBER_SLOTS}, SALON_DRY_DAMAGE_MULT "
          f"{C.SALON_DRY_DAMAGE_MULT}")
    print("    dry = upkeep arrives under ONE member's cost; full = arrives "
          "holding the WHOLE stage's bill;")
    print("    surplus = held minus that bill (positive means the bar is "
          "running ahead of the stage).")
    print("=" * 78)

    for archetype, pilot_id in CONFIGS:
        results = _run(archetype, pilot_id, runs)
        wr = sum(r.won for r in results) / len(results)
        every = [tr for r in results for _, tr in r.encore_traces]
        agg = encore_telemetry.aggregate(every)
        print(f"\n  assigned {archetype} (pilot {pilot_id}) "
              f"— run winrate {wr:.1%}")
        print(encore_telemetry.format_row("all acts", agg))
        for act_i, traces in sorted(_by_act(results, "encore_traces").items()):
            print(encore_telemetry.format_row(
                f"act {act_i + 1}", encore_telemetry.aggregate(traces)))


def t4(runs: int = RUNS) -> None:
    print("=" * 78)
    print(f"T4. Conditional rider fire-rates — {runs} realistic runs/arm, "
          f"seed {SEED}")
    print("    Denominator is EVALUATIONS, not plays: a card that repeats "
          "itself evaluates twice in one play,")
    print("    and 'how often does the rider pay' is a question about "
          "evaluations.")
    print("=" * 78)

    for archetype, pilot_id in CONFIGS:
        results = _run(archetype, pilot_id, runs)
        every = [tr for r in results for _, tr in r.conditional_traces]
        agg = conditional_telemetry.aggregate(every)
        print(f"\n  assigned {archetype} (pilot {pilot_id})")
        watched = conditional_telemetry.format_rows(agg, WATCHED_CARD)
        if watched:
            print("  WATCHED (D4):")
            for row in watched:
                print(row)
        else:
            print(f"  WATCHED (D4): {WATCHED_CARD} never drafted/played — "
                  "no evaluations, no fire rate. This is a real result, not "
                  "a zero.")
        print("  whole table, ascending by fire rate:")
        for row in conditional_telemetry.format_rows(agg):
            print(row)


def main(argv: list[str]) -> None:
    cell = argv[1] if len(argv) > 1 else "all"
    runs = RUNS
    if "--runs" in argv:
        runs = int(argv[argv.index("--runs") + 1])
    if cell in ("t3", "all"):
        t3(runs)
    if cell in ("t4", "all"):
        t4(runs)


if __name__ == "__main__":
    expcli.help_if_asked(__doc__)
    main(sys.argv)
