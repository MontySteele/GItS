"""Fanfare decay sweep + the fanfare-archetype autopsy ("The Tide Turns").

Two questions, deliberately kept separate because they have different
answers:

A2. DECAY SWEEP (proportional). Re-derives the decay MAGNITUDE against the
   one shape the engine has. The original block A -- a flat-magnitude sweep
   over FANFARE_DECAY_PER_TURN, written when the plan had ruled flat over
   proportional -- was deleted by R67 (2026-07-26) along with its knob: the
   20% proportional ruling had made the flat branch unreachable, so every
   cell of it ran the same world. Its rows are struck.

B. FANFARE AUTOPSY. The fanfare plan sits at 0.0% winrate across F-A and
   F-B2 alike. This asks whether that is a resource problem the sprint can
   still fix or an archetype that is simply weak, by separating "the deck
   never assembles", "the deck assembles and still cannot kill", and "the
   deck kills but dies first".

R14: diagnostics feeding a ruling. No acceptance targets in this file --
the registered bars live in docs/archive/furina-fanfare-sprint-log.md.

Usage: python -m tier05.exp_furina_decay [prop|frontload|autopsy] [--runs N]
"""

from __future__ import annotations

import statistics
import sys

from tier0.content import loader
from tier05 import draft, expcli, fanfare_telemetry, model, sweeps

SEED = 11            # the sprint's registered seed (plan §5)
RUNS = 200
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


# Block A (the flat FANFARE_DECAY_PER_TURN magnitude sweep over
# DECAY_CELLS) was DELETED by R67, 2026-07-26, together with the knob it
# swept. The flat branch was reachable only when FANFARE_DECAY_FRACTION was
# 0, which the 20% proportional ruling made permanently false, so all five
# cells ran the identical world and the block's rows are STRUCK as
# instrument error -- NOT as a null result about decay magnitude. The block
# below (A2) swept a live knob and stands.


def prop(runs: int = RUNS) -> None:
    """A2. PROPORTIONAL decay sweep, 10% increments ([USER] 2026-07-24).

    Originally a direction re-open: it printed flat cells alongside the
    proportional ones, at the same seed and sample, so the two SHAPES were
    comparable rather than merely each internally consistent. That
    comparison is what carried the 20% ruling, and it is now a closed
    record -- R67 deleted the flat shape from the engine, so the flat cells
    are gone from here and the block is a pure magnitude sweep over the one
    surviving shape. The historical flat-vs-proportional table lives in the
    FANFARE_DECAY_FRACTION comment in tier0/constants.py.

    Runs through the R67 gated harness: a cell in which nothing ever reads
    the fraction fails loudly rather than printing a row.
    """
    print("=" * 78)
    print(f"A2. PROPORTIONAL DECAY SWEEP — {runs} realistic runs/cell, "
          f"seed {SEED}")
    print("    Fraction of the whole meter, clamped at the floor; always "
          "removes >= 1")
    print("    while above the floor. Gate (2) bar: read at-cap < 15%.")
    print("=" * 78)

    for archetype, pilot_id in ARMS:
        print(f"\n  assigned {archetype}")
        print(f"  {'decay':>8} {'read@cap':>9} {'mean@read':>10} "
              f"{'empty':>7} {'act-1':>7} {'win':>7}")
        # Serial only. DO NOT add jobs>1 to the run_many call inside _cell.
        # Worker processes are SPAWNED on Windows, so they re-import
        # tier0.constants fresh and would silently run every cell at the
        # stamped default -- a sweep that reports identical rows and looks
        # like a null result instead of a broken one. (The R67 gate does
        # not save you here: the parent process still reads the armed knob,
        # so the reads land while the WORK happens elsewhere at the
        # default.) A constants override and process parallelism do not mix
        # without shipping the override to the workers.
        for frac, c in sweeps.sweep(
                "FANFARE_DECAY_FRACTION", (0.1, 0.2, 0.3, 0.4, 0.5),
                lambda _: _cell(archetype, pilot_id, runs)):
            label = f"{int(frac * 100)}%"
            bar = "" if c["read_at_cap"] < 0.15 else "  !! GATE(2)"
            print(f"  {label:>8} {c['read_at_cap']:>8.1%} "
                  f"{c['mean_at_read']:>10.1f} {c['read_empty']:>6.1%} "
                  f"{c['act1']:>6.1%} {c['winrate']:>6.1%}{bar}")


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
    block = args[0] if args else "prop"
    if block == "sweep":
        # R67 deleted this block with FANFARE_DECAY_PER_TURN. Named
        # explicitly rather than falling through to "unknown block" so the
        # sprint docs that say `exp_furina_decay sweep` get an answer.
        print("block 'sweep' was DELETED by R67 (2026-07-26) with the dead "
              "FANFARE_DECAY_PER_TURN knob it swept; its rows are struck as "
              "instrument error. Use 'prop' for the live decay sweep.")
        return 2
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
    expcli.help_if_asked(__doc__)
    raise SystemExit(main())
