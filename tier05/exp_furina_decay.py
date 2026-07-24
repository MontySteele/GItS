"""Fanfare decay sweep + the fanfare-archetype autopsy ("The Tide Turns").

Two questions, deliberately kept separate because they have different
answers:

A. DECAY SWEEP. The sprint plan picked FANFARE_DECAY_PER_TURN = 5 on the
   strength of a sweep whose source document never landed in this repo, so
   the number has no in-repo basis. User ruling 2026-07-24: re-derive it
   here before F-C's binding run. Direction (flat over proportional) is
   RATIFIED and not re-litigated -- what is re-derived is the MAGNITUDE.
   Cell 0 is the control: it is what the world looks like with the decay
   knob switched off, i.e. what decay actually bought.

B. FANFARE AUTOPSY. The fanfare plan sits at 0.0% winrate across F-A and
   F-B2 alike. This asks whether that is a resource problem the sprint can
   still fix or an archetype that is simply weak, by separating "the deck
   never assembles", "the deck assembles and still cannot kill", and "the
   deck kills but dies first".

R14: diagnostics feeding a ruling. No acceptance targets in this file --
the registered bars live in docs/furina-fanfare-sprint-log.md.

Usage: python -m tier05.exp_furina_decay [sweep|prop|frontload|autopsy] [--runs N]
"""

from __future__ import annotations

import statistics
import sys

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft, fanfare_telemetry, model

SEED = 11            # the sprint's registered seed (plan §5)
RUNS = 200
DECAY_CELLS = (0, 3, 5, 8, 12)
ARMS = (("fanfare", "fanfare"), ("salon", "salon"))


def _read(results: list) -> dict:
    traces = [tr for r in results for _, tr in r.fanfare_traces]
    return fanfare_telemetry.aggregate(traces)


def _act1_clear(results: list) -> float:
    """Fraction of runs that got past act 1. `acts_completed` counts boss
    wins, so >= 1 IS the act-1 clear."""
    return sum(r.acts_completed >= 1 for r in results) / len(results)


def _cell(archetype: str, pilot_id: str, runs: int) -> dict:
    results = model.run_many("furina", archetype, pilot_id,
                             draft.assigned_policy, runs, SEED,
                             grant_relics=True, grant_potions=True)
    agg = _read(results)
    pr = fanfare_telemetry.per_run(agg, len(results))
    return {
        "winrate": sum(r.won for r in results) / len(results),
        "act1": _act1_clear(results),
        "read_at_cap": agg.get("read_at_cap", 0.0),
        "mean_at_read": agg.get("mean_at_read", 0.0),
        "read_empty": agg.get("read_empty", 0.0),
        "floors_per_run": pr.get("floor_granted_per_run", 0.0),
        "results": results,
    }


def sweep(runs: int = RUNS) -> None:
    print("=" * 78)
    print(f"A. FANFARE DECAY SWEEP — {runs} realistic runs/cell, seed {SEED}")
    print(f"   shipping value: FANFARE_DECAY_PER_TURN = "
          f"{C.FANFARE_DECAY_PER_TURN} (flat). Cell 0 = knob OFF (control).")
    print("   Direction (flat over proportional) is RATIFIED; this re-derives")
    print("   the MAGNITUDE only. Gate (2) bar: read at-cap < 15%.")
    print("=" * 78)

    original = C.FANFARE_DECAY_PER_TURN
    try:
        for archetype, pilot_id in ARMS:
            print(f"\n  assigned {archetype}")
            print(f"  {'decay':>6} {'read@cap':>9} {'mean@read':>10} "
                  f"{'empty':>7} {'act-1':>7} {'win':>7}")
            for decay in DECAY_CELLS:
                # One variable per cell: the module attribute IS the knob
                # every read goes through (engine/ never hard-codes it).
                #
                # DO NOT add jobs>1 to the run_many call below. Worker
                # processes are SPAWNED on Windows, so they re-import
                # tier0.constants fresh and would silently run every cell at
                # the shipping default -- a sweep that reports five identical
                # rows and looks like a null result instead of a broken one.
                # A constants override and process parallelism do not mix
                # without shipping the override to the workers.
                C.FANFARE_DECAY_PER_TURN = decay
                c = _cell(archetype, pilot_id, runs)
                flag = "  <-- shipping" if decay == original else ""
                bar = "" if c["read_at_cap"] < 0.15 else "  !! GATE(2)"
                print(f"  {decay:>6} {c['read_at_cap']:>8.1%} "
                      f"{c['mean_at_read']:>10.1f} {c['read_empty']:>6.1%} "
                      f"{c['act1']:>6.1%} {c['winrate']:>6.1%}{flag}{bar}")
    finally:
        C.FANFARE_DECAY_PER_TURN = original


def prop(runs: int = RUNS) -> None:
    """A2. PROPORTIONAL decay sweep, 10% increments ([USER] 2026-07-24).

    The plan ruled flat over proportional on tooltip grounds, so this is a
    direction re-open, not a magnitude re-derivation. Flat cells are printed
    alongside at the same seed and sample so the two SHAPES are comparable
    rather than merely each internally consistent.
    """
    print("=" * 78)
    print(f"A2. PROPORTIONAL DECAY SWEEP — {runs} realistic runs/cell, "
          f"seed {SEED}")
    print("    Fraction of the whole meter, clamped at the floor; always "
          "removes >= 1")
    print("    while above the floor. Gate (2) bar: read at-cap < 15%.")
    print("=" * 78)

    frac0, flat0 = C.FANFARE_DECAY_FRACTION, C.FANFARE_DECAY_PER_TURN
    cells = ([("flat 3", 0.0, 3), ("flat 5", 0.0, 5)]
             + [(f"{int(f * 100)}%", f, 0) for f in
                (0.1, 0.2, 0.3, 0.4, 0.5)])
    try:
        for archetype, pilot_id in ARMS:
            print(f"\n  assigned {archetype}")
            print(f"  {'decay':>8} {'read@cap':>9} {'mean@read':>10} "
                  f"{'empty':>7} {'act-1':>7} {'win':>7}")
            for label, frac, flat in cells:
                # Serial only -- see the note in sweep().
                C.FANFARE_DECAY_FRACTION = frac
                if flat:
                    C.FANFARE_DECAY_PER_TURN = flat
                c = _cell(archetype, pilot_id, runs)
                bar = "" if c["read_at_cap"] < 0.15 else "  !! GATE(2)"
                print(f"  {label:>8} {c['read_at_cap']:>8.1%} "
                      f"{c['mean_at_read']:>10.1f} {c['read_empty']:>6.1%} "
                      f"{c['act1']:>6.1%} {c['winrate']:>6.1%}{bar}")
    finally:
        C.FANFARE_DECAY_FRACTION, C.FANFARE_DECAY_PER_TURN = frac0, flat0


# F-B3. The archetype's act-1 damage sources, which is the whole list: two
# attack commons and one damaging skill, plus the uncommon frontload payoff
# the plan names. Everything else the plan calls "act-1 commons" generates
# Encore or draws -- see the density note in the sprint log.
FRONTLOAD_CARDS = ("warmup_act", "dramatic_entrance", "standing_room_only",
                   "showstopper")


def frontload(runs: int = RUNS) -> None:
    """F-B3, registered as its own cell (plan §4): a NUMBERS pass on the
    fanfare plan's act-1 damage, swept one variable at a time.

    Deliberately not folded into F-B1: "the archetype needed frontload all
    along" is a finding worth isolating, and mixing the two would make
    either result uninterpretable.

    The variable is a flat +N to printed damage on FRONTLOAD_CARDS. If the
    sweep cannot reach gate (1) at any N a numbers pass could justify, that
    is itself the finding -- it would mean the deficit is structural
    (attack DENSITY) rather than per-card magnitude, and no amount of
    bumping two commons reaches it.
    """
    print("=" * 78)
    print(f"F-B3. FRONTLOAD NUMBERS SWEEP — {runs} realistic runs/cell, "
          f"seed {SEED}")
    print(f"      +N printed damage on: {', '.join(FRONTLOAD_CARDS)}")
    print("      Gate (1): run winrate >= 3% AND act-1 clear >= 50%.")
    print("=" * 78)
    print(f"\n  {'+dmg':>5} {'act-1':>7} {'win':>7} {'DPT':>6} "
          f"{'death node':>11} {'mean@read':>10}")

    for bump in (0, 1, 2, 3, 4, 6):
        # Rebuild from the sheet, THEN mutate the shared index entries. Order
        # matters: reset_caches() drops _card_prototype, which is derived from
        # _card_index, so mutating after the reset is what the memoized
        # upgraded forms are built from. Mutating first would be undone.
        loader.reset_caches()
        index = loader._card_index()
        for cid in FRONTLOAD_CARDS:
            for fx in index[cid].effects:
                if fx.get("op") == "damage" and fx.get("target") != "self":
                    fx["amount"] += bump
        c = _cell("fanfare", "fanfare", runs)
        results = c["results"]
        fights = [fs for r in results for fs in r.fight_stats]
        dpt = statistics.mean(fs.total_damage_dealt / max(1, fs.turns)
                              for fs in fights)
        deaths = [r.death_node for r in results if r.death_node is not None]
        node = statistics.median(deaths) if deaths else float("nan")
        gate = "  <-- GATE (1)" if (c["winrate"] >= 0.03
                                    and c["act1"] >= 0.50) else ""
        print(f"  {bump:>5} {c['act1']:>6.1%} {c['winrate']:>6.1%} "
              f"{dpt:>6.1f} {node:>11.0f} {c['mean_at_read']:>10.1f}{gate}")
    loader.reset_caches()      # leave the index as the sheet has it


def autopsy(runs: int = RUNS) -> None:
    """Why is the fanfare plan at 0%? Three candidate causes, separated."""
    print("=" * 78)
    print(f"B. FANFARE AUTOPSY — {runs} realistic runs/arm, seed {SEED}")
    print("=" * 78)

    for archetype, pilot_id in (("fanfare", "fanfare"), ("salon", "salon"),
                                ("spotlight", "spotlight")):
        c = _cell(archetype, pilot_id, runs)
        results = c["results"]
        deaths = [r.death_node for r in results if r.death_node is not None]
        online = [r.time_to_online for r in results
                  if r.time_to_online is not None]
        fights = [fs for r in results for fs in r.fight_stats]
        dpt = [fs.total_damage_dealt / max(1, fs.turns) for fs in fights]
        won_fights = sum(fs.won for fs in fights) / max(1, len(fights))

        print(f"\n  {archetype}: win {c['winrate']:.1%}   "
              f"act-1 clear {c['act1']:.1%}")
        print(f"    assembly    core online in {len(online)}/{len(results)} "
              f"runs"
              + (f", median fight {statistics.median(online):.0f}"
                 if online else " — NEVER"))
        print(f"    lethality   {statistics.mean(dpt):5.1f} damage/turn "
              f"(median {statistics.median(dpt):.1f}), "
              f"fight winrate {won_fights:.1%}")
        print(f"    survival    died in {len(deaths)}/{len(results)} runs"
              + (f", median node {statistics.median(deaths):.0f}"
                 if deaths else ""))
        print(f"    meter       mean@read {c['mean_at_read']:.1f}, "
              f"empty reads {c['read_empty']:.1%}, "
              f"floors {c['floors_per_run']:.1f}/run")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    runs = RUNS
    if "--runs" in args:
        i = args.index("--runs")
        runs = int(args[i + 1])
        del args[i:i + 2]
    block = args[0] if args else "sweep"
    if block == "sweep":
        sweep(runs)
    elif block == "prop":
        prop(runs)
    elif block == "frontload":
        frontload(runs)
    elif block == "autopsy":
        autopsy(runs)
    else:
        print(f"unknown block: {block}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
