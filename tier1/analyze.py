"""Tier 1 soak analysis — read the GAME's own run history, no mod code.

The overnight queue assumed we would build a telemetry writer and pipe it
somewhere. We do not need one. `RunHistoryUtilities.CreateRunHistoryEntry`
already writes a complete plaintext JSON record per run
(`sts2.decompiled.cs:39421` -> `SaveManager.SaveRunHistory`), it writes it for
modded profiles too, and it records more than we would have thought to log:

    seed                   exact repro for any crash
    win / was_abandoned    outcome
    killed_by_encounter    where runs actually die
    players[].deck[]       every card, WITH `floor_added_to_deck`
    players[].relics[]     same
    map_point_history[]    per-floor path, choices, and stats
    build_id               pins the game version the data came from

`floor_added_to_deck` is the load-bearing field. It separates starters (floor 1)
from drafted cards, which is the same cut M6's `archetype_shares` makes with
rarity -- so this is an INDEPENDENT check on that exclusion rather than the same
assumption twice. If the two disagree about which cards were drafted, one of
them is wrong and we want to know.

SCOPE CAVEAT, and it is the important one. AutoSlay drives the base game's
heuristics. It knows nothing about bombs, sparks, or archetypes, so it does not
draft the way Tier 0.5's pilots draft. That makes this soak:

  GOOD for: crashes, soft locks, unreachable states, "does the run loop survive
            N runs", pool/rarity coverage, anything shaped like an assert.
  BAD  for: validating Tier 0.5's winrate or time-to-online predictions. Those
            assume archetype-committed drafting. A divergence here would be
            explained by the pilot, not the pool, and reading it as a pool
            finding is exactly the error M6 already made once with the starting
            deck.

So `--predict` is off by default and prints a banner when you ask for it.

Usage:
    python -m tier1.analyze                 # summarize the soak
    python -m tier1.analyze --crashes       # only runs that ended abnormally
    python -m tier1.analyze --predict       # vs Tier 0.5 (read the caveat)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

CHARACTER = "CHARACTER.KLEE"
CARD_PREFIX = "CARD.KLEEMOD-"

# The game writes under a `modded/` profile when any mod is loaded; an unmodded
# run of the same profile writes beside it. We only ever want the modded tree.
DEFAULT_ROOT = Path(os.environ.get("APPDATA", "")) / "SlayTheSpire2" / "steam"


def find_history_dirs(root: Path = DEFAULT_ROOT) -> list[Path]:
    """Every modded history dir under the Steam userdata tree.

    Globbed rather than hardcoded because the steamid and profile number vary
    per machine, and a soak box will not be this one.
    """
    return sorted(root.glob("*/modded/profile*/saves/history"))


def load_runs(dirs: list[Path], character: str = CHARACTER) -> list[dict]:
    runs = []
    for d in dirs:
        for f in sorted(d.glob("*.run"), key=lambda p: p.stat().st_mtime):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as e:
                print(f"  ! unreadable {f.name}: {e}", file=sys.stderr)
                continue
            players = data.get("players") or []
            if not any(p.get("character") == character for p in players):
                continue
            data["_file"] = f
            runs.append(data)
    return runs


def card_id(entry: dict) -> str:
    """`CARD.KLEEMOD-JUMPY_DUMPTY` -> `jumpy_dumpty`, matching the yaml sheet."""
    raw = entry.get("id", "")
    return raw[len(CARD_PREFIX):].lower() if raw.startswith(CARD_PREFIX) else raw


def klee_player(run: dict) -> dict:
    return next(p for p in run["players"] if p.get("character") == CHARACTER)


def drafted_cards(run: dict) -> list[dict]:
    """Cards acquired during the run. Floor 1 is the starting deck.

    Mirrors M6's basics exclusion by a different route -- see module docstring.
    """
    return [c for c in klee_player(run).get("deck", [])
            if c.get("floor_added_to_deck", 1) > 1]


def floors_reached(run: dict) -> int:
    return sum(len(act) for act in run.get("map_point_history", []))


def summarize(runs: list[dict]) -> dict:
    if not runs:
        return {}
    wins = sum(1 for r in runs if r.get("win"))
    abandoned = sum(1 for r in runs if r.get("was_abandoned"))
    decks = [len(klee_player(r).get("deck", [])) for r in runs]
    drafted = [len(drafted_cards(r)) for r in runs]
    floors = [floors_reached(r) for r in runs]
    return {
        "runs": len(runs),
        "wins": wins,
        "winrate": wins / len(runs),
        "abandoned": abandoned,
        "builds": Counter(r.get("build_id") for r in runs),
        "avg_deck": sum(decks) / len(decks),
        "avg_drafted": sum(drafted) / len(drafted),
        "median_floors": sorted(floors)[len(floors) // 2],
        "killed_by": Counter(r.get("killed_by_encounter") for r in runs
                             if not r.get("win")),
        "card_freq": Counter(card_id(c) for r in runs for c in drafted_cards(r)),
    }


def suspicious(runs: list[dict]) -> list[tuple[dict, str]]:
    """Runs that ended in a way worth a human look.

    A soft lock like finding 21 does NOT write a history entry at all -- the
    run never ends -- so its signature here is absence: the soak launched N
    runs and fewer than N records exist. That has to be checked against the
    launcher's count, which is why `--crashes` reports the total it found
    rather than only listing rows.
    """
    out = []
    for r in runs:
        if r.get("was_abandoned"):
            out.append((r, "abandoned mid-run (soak should not abandon)"))
        elif not r.get("win") and floors_reached(r) <= 1:
            out.append((r, "died on floor 1 -- possible boot/pool problem"))
        elif not r.get("win") and r.get("killed_by_encounter") in (None, "NONE.NONE"):
            out.append((r, "loss with no killer recorded"))
    return out


def print_report(s: dict, runs: list[dict]) -> None:
    if not s:
        print("No Klee runs found. Is the soak pointed at a modded profile?")
        return
    # ASCII only in printed output: the Windows console defaults to cp1252 and
    # mangles em dashes, which is noise in a log you will read at 3am.
    print(f"\n=== Tier 1 soak - {s['runs']} Klee runs ===")
    builds = ", ".join(f"{b} x{n}" for b, n in s["builds"].most_common())
    print(f"  build(s)       {builds}")
    print(f"  winrate        {s['winrate']:.1%}  ({s['wins']}/{s['runs']})")
    print(f"  abandoned      {s['abandoned']}")
    print(f"  median floors  {s['median_floors']}")
    print(f"  avg deck       {s['avg_deck']:.1f}  ({s['avg_drafted']:.1f} drafted)")

    if s["killed_by"]:
        print("\n  -- deaths by encounter --")
        for enc, n in s["killed_by"].most_common(8):
            print(f"    {n:>4}  {enc}")

    # Pool coverage is the check this soak is actually good at: a card that
    # never appears across many runs is either unreachable or unpickable, and
    # both are bugs we cannot see from inside Tier 0.
    print(f"\n  -- pool coverage: {len(s['card_freq'])} distinct cards drafted --")
    for cid, n in s["card_freq"].most_common(5):
        print(f"    {n:>4}  {cid}")
    if s["card_freq"]:
        print("    ...")
        for cid, n in s["card_freq"].most_common()[-3:]:
            print(f"    {n:>4}  {cid}")

    flagged = suspicious(runs)
    print(f"\n  -- {len(flagged)} run(s) worth a look --")
    for r, why in flagged[:10]:
        print(f"    seed {r.get('seed')}  {why}")
        print(f"      {r['_file'].name}")
    if not flagged:
        print("    none")
    print("\n  NOTE: a soft lock writes NO history entry (the run never ends).")
    print("  Compare this run count against how many the launcher started.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tier 1 soak analysis")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--crashes", action="store_true",
                    help="only list runs that ended abnormally")
    ap.add_argument("--predict", action="store_true",
                    help="compare against Tier 0.5 (read the scope caveat)")
    args = ap.parse_args(argv)

    dirs = find_history_dirs(args.root)
    if not dirs:
        print(f"No modded history dirs under {args.root}", file=sys.stderr)
        return 1
    for d in dirs:
        print(f"reading {d}")
    runs = load_runs(dirs)

    if args.crashes:
        flagged = suspicious(runs)
        print(f"\n{len(flagged)} suspicious of {len(runs)} Klee runs")
        for r, why in flagged:
            print(f"  seed {r.get('seed')}  {why}  ({r['_file'].name})")
        return 0

    print_report(summarize(runs), runs)

    if args.predict:
        print("\n" + "=" * 68)
        print("  Tier 0.5 comparison is NOT a validation of the sim.")
        print("  AutoSlay plays base-game heuristics and does not draft to an")
        print("  archetype. Any winrate or time-to-online gap is explained by")
        print("  the pilot before it is evidence about the pool. Treat this as")
        print("  a sanity check on ranges, not a verdict. See module docstring.")
        print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
