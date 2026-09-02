"""PER-CARD READ of a quarantined prototype arm, from the tier-0.5 sim.

WHAT IT IS. One instrument that runs the tier-0.5 runner under a prototype
arm's flag and reports, per card id, the four numbers a dead-card / automatic
-card read is made of: how often the drafter was OFFERED it, how often it PICKED
it when offered, how often the pilot PLAYED it once it reached hand, and the win
rate of runs that ended up carrying it against runs that did not.

WHAT IT IS NOT. Nothing here grades anything, and nothing it prints is quotable
as a statement about the design (R215 B: a prototype row's numbers are
instrument readings). The carried/not-carried split is CORRELATIONAL -- the
drafter picks a card because the run is already going a certain way, so a high
carried-winrate is as likely to be about the runs as about the card. The
register's paired reading (force the copy in on the same seeds) is a different
instrument and this is not it.

THE FLAG IS SET IN PROCESS, the way `tier0/tests/test_kokomi_overhaul.py`'s
`overhaul` fixture sets it: `C.<ARM>_OVERHAUL = True` plus a clear of the two
memoized caches whose answers move with it (`loader._card_prototype`,
`rewards.character_pool`). There is no environment switch and no CLI flag on
`tier05.runner`, so an in-process context manager is the only door; it restores
the previous value and re-clears on the way out, so an importing test leaves the
world where it found it.

ONE ARM DOES NOT RUN. `KLEE_OVERHAUL`'s eight ops
(`set_off`, `plant_bomb`, `grow_bombs`, `merge_bombs`, `remove_bomb_for_block`,
`damage_set_off_total`, `double_set_off`, `draw_per_set_off`) are registered in
`effects.OPS` as `_op_klee_overhaul_unbuilt`, which RAISES: that arm is C# first
and the sim was never brought up for it. So `--arm klee` reports the refusal by
name rather than a table, and `probe_arm_runnable` is what a caller asks first.

Usage:
    python tools/prototype_card_read.py --arm kokomi --runs 300 --seed 42
    python tools/prototype_card_read.py --arm kokomi --runs 300 --acts 1 --json out.json
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from collections import Counter

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft, model, rewards, run_metrics

#: The two quarantined kits this instrument knows how to open, and the seat,
#: assigned plan and pilot each one is measured on. The plan is the character's
#: registered default (`roster.ROSTER`), so nothing here invents a pairing
#: `tier05.runner.resolve_plan` would refuse.
ARMS: dict[str, dict[str, str]] = {
    "klee": {"flag": "KLEE_OVERHAUL", "character": "klee",
             "archetype": "demolition", "pilot": "demolition",
             "prefix": "proto_ko_"},
    "kokomi": {"flag": "KOKOMI_OVERHAUL", "character": "kokomi",
               "archetype": "priest", "pilot": "priest",
               "prefix": "proto_kk_"},
}


@contextlib.contextmanager
def arm_live(arm: str):
    """`C.<ARM>_OVERHAUL` True inside the block, restored on the way out.

    Both memoized doors are cleared going in AND coming out: `_card_prototype`
    answers a `proto_` id differently with the flag off, and
    `rewards.character_pool` answers the whole offerable pool differently, so a
    cache filled on one side of the flag is a wrong answer on the other.
    """
    flag = ARMS[arm]["flag"]
    previous = getattr(C, flag)
    loader._card_prototype.cache_clear()
    rewards.character_pool.cache_clear()
    setattr(C, flag, True)
    try:
        yield
    finally:
        setattr(C, flag, previous)
        loader._card_prototype.cache_clear()
        rewards.character_pool.cache_clear()


def probe_arm_runnable(arm: str, seed: int = 7) -> str | None:
    """None if the arm's own rows resolve in this engine, else the refusal.

    Asked by resolving every prototype row's body against a throwaway combat is
    more machinery than the question needs: the ops that refuse do so
    unconditionally, so reading `effects.OPS` for the arm's unbuilt marker
    answers it exactly and instantly.
    """
    from tier0.engine import effects
    unbuilt = sorted(
        op for op, fn in effects.OPS.items()
        if getattr(fn, "__name__", "") == "_op_klee_overhaul_unbuilt")
    if arm == "klee" and unbuilt:
        return ("the KLEE_OVERHAUL arm does not run in this engine: "
                f"{', '.join(unbuilt)} are registered as "
                "`_op_klee_overhaul_unbuilt`, which raises (C# first; the sim "
                "was not brought up for slice one)")
    return None


def base_id(card_id: str) -> str:
    """The printed row behind an instance id.

    A deck carries `feint`, `feint+`, `feint@sharp-2` and `feint@sharp-2+` as
    four keys; they are one CARD and the read is about the card. The upgrade
    mark is a trailing `+` and an enchantment is an `@suffix`, which is the
    spelling `loader` resolves and `test_eb109_suffix_appends.py` pins.
    """
    return card_id.rstrip("+").split("@", 1)[0]


def tally(arm: str, runs: int, seed: int, n_acts: int | None = None,
          jobs: int = 1, merge_upgrades: bool = True) -> dict:
    """Run the arm and return the per-card rows plus the run-level numbers."""
    spec = ARMS[arm]
    key = base_id if merge_upgrades else (lambda cid: cid)
    with arm_live(arm):
        results = model.run_many(
            spec["character"], spec["archetype"], spec["pilot"],
            draft.POLICIES["assigned"], runs, seed,
            grant_relics=True, grant_potions=True, n_acts=n_acts, jobs=jobs)
        summary = run_metrics.summarize_runs(results)

    offers, picks, offered_runs = Counter(), Counter(), Counter()
    draws, plays, dead = Counter(), Counter(), Counter()
    carried_n, carried_w, not_w = Counter(), Counter(), Counter()
    turns = fights = 0
    ids: set[str] = set()

    carried_sets = []
    for r in results:
        seen_offers: set[str] = set()
        for d in r.decisions:
            for card in d["offers"]:
                offers[key(card.id)] += 1
                seen_offers.add(key(card.id))
            if d["picked"]:
                picks[key(d["picked"])] += 1
        for cid in seen_offers:
            offered_runs[cid] += 1
        for fs in r.fight_stats:
            for src, dst in ((fs.card_draws, draws), (fs.card_plays, plays),
                             (fs.dead_in_hand, dead)):
                for cid, count in src.items():
                    dst[key(cid)] += count
            turns += fs.turns
            fights += 1
        held = {key(cid) for cid in r.deck_ids}
        carried_sets.append(held)
        ids |= held | seen_offers
        for cid in held:
            carried_n[cid] += 1
            carried_w[cid] += int(r.won)

    ids |= set(draws) | set(plays)
    for cid in ids:
        not_w[cid] = sum(1 for r, held in zip(results, carried_sets)
                         if cid not in held and r.won)

    rows = []
    for cid in sorted(ids):
        n_carried = carried_n[cid]
        n_not = len(results) - n_carried
        rows.append({
            "id": cid,
            "offers": offers[cid],
            "offered_runs": offered_runs[cid],
            "offered_rate": offered_runs[cid] / len(results),
            "picks": picks[cid],
            "pick_rate_when_offered": (picks[cid] / offers[cid]
                                       if offers[cid] else None),
            "draws": draws[cid],
            "plays": plays[cid],
            "play_rate_in_hand": (plays[cid] / draws[cid]
                                  if draws[cid] else None),
            "dead_in_hand": dead[cid],
            "carried_runs": n_carried,
            "winrate_carried": carried_w[cid] / n_carried if n_carried else None,
            "winrate_not_carried": not_w[cid] / n_not if n_not else None,
        })

    return {
        "arm": arm, "runs": len(results), "seed": seed, "n_acts": n_acts,
        "winrate": summary["winrate"],
        "act_funnel": summary["act_funnel"],
        "death_heatmap": summary["death_heatmap"],
        "fights": fights,
        "avg_fight_turns": turns / fights if fights else None,
        "rows": rows,
    }


def _fmt(value, spec: str = ".3f") -> str:
    return "--" if value is None else format(value, spec)


def print_report(out: dict, prefix_only: bool = False) -> None:
    spec = ARMS[out["arm"]]
    print(f"# {out['arm']} arm -- {out['runs']} runs, seed {out['seed']}, "
          f"acts {out['n_acts'] or 'all'}")
    print(f"run winrate {out['winrate']:.3f}   "
          f"avg fight length {_fmt(out['avg_fight_turns'], '.2f')} turns "
          f"over {out['fights']} fights")
    print("act | reached | cleared")
    for a in out["act_funnel"]:
        print(f"  {a['act']} | {a['reached_rate']:.3f} | {a['cleared_rate']:.3f}")
    print("\nid | offers | offered_rate | pick@offered | draws | play@hand | "
          "dead_in_hand | carried | wr_carried | wr_not")
    for row in out["rows"]:
        if prefix_only and not row["id"].startswith(spec["prefix"]):
            continue
        print(f"{row['id']} | {row['offers']} | {row['offered_rate']:.3f} | "
              f"{_fmt(row['pick_rate_when_offered'])} | {row['draws']} | "
              f"{_fmt(row['play_rate_in_hand'])} | {row['dead_in_hand']} | "
              f"{row['carried_runs']} | {_fmt(row['winrate_carried'])} | "
              f"{_fmt(row['winrate_not_carried'])}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", choices=sorted(ARMS), required=True)
    ap.add_argument("--runs", type=int, default=300)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--acts", type=int, default=None)
    ap.add_argument("--jobs", "-j", type=int, default=1)
    ap.add_argument("--json", default=None, help="also write the raw rows here")
    ap.add_argument("--prefix-only", action="store_true",
                    help="print only the arm's own proto_ rows")
    ap.add_argument("--split-upgrades", action="store_true",
                    help="keep `card+` and `card@enchant` as separate rows "
                         "instead of folding them into the printed card")
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    refusal = probe_arm_runnable(args.arm)
    if refusal:
        print(f"REFUSED: {refusal}")
        return 2

    out = tally(args.arm, args.runs, args.seed, n_acts=args.acts,
                jobs=args.jobs, merge_upgrades=not args.split_upgrades)
    print_report(out, prefix_only=args.prefix_only)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":                          # pragma: no cover
    raise SystemExit(main())
