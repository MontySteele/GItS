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

# E3 (audit sec.5): this instrument predates the roster and could not see
# Furina or Kokomi runs at all -- `CHARACTER.KLEE` was a module constant and
# `klee_player()` was in its name. A soak box running the shipped mod produces
# runs for three characters; the analyser silently discarded two thirds of
# them and reported the remainder as "the soak".
#
# The card prefix is MOD-wide, not character-wide: every card this mod ships
# carries `CARD.KLEEMOD-` whoever owns it, because it is BaseLib's mod-id
# prefix. It stays a single constant on purpose -- making it per-character
# would invent a distinction the game does not have.
CARD_PREFIX = "CARD.KLEEMOD-"

# Character id in the run history -> the name this repo uses everywhere else.
# A curated map because the two vocabularies are genuinely different (the game
# upper-cases and namespaces; the sim uses the sheet name), and because a
# fourth character must be ADDED here rather than silently missing.
ROSTER = {
    "CHARACTER.KLEE": "klee",
    "CHARACTER.FURINA": "furina",
    "CHARACTER.KOKOMI": "kokomi",
}
DEFAULT_CHARACTER = "CHARACTER.KLEE"
CHARACTER = DEFAULT_CHARACTER      # back-compat for callers that imported it

# The game writes under a `modded/` profile when any mod is loaded; an unmodded
# run of the same profile writes beside it. We only ever want the modded tree.
DEFAULT_ROOT = Path(os.environ.get("APPDATA", "")) / "SlayTheSpire2" / "steam"


def find_history_dirs(root: Path = DEFAULT_ROOT) -> list[Path]:
    """Every modded history dir under the Steam userdata tree.

    Globbed rather than hardcoded because the steamid and profile number vary
    per machine, and a soak box will not be this one.
    """
    return sorted(root.glob("*/modded/profile*/saves/history"))


def load_runs(dirs: list[Path],
              character: str | None = DEFAULT_CHARACTER) -> list[dict]:
    """Runs featuring `character`, or -- with `character=None` -- every run
    featuring ANY roster character. The None case is what makes a mixed soak
    readable instead of silently Klee-only."""
    runs = []
    for d in dirs:
        for f in sorted(d.glob("*.run"), key=lambda p: p.stat().st_mtime):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as e:
                print(f"  ! unreadable {f.name}: {e}", file=sys.stderr)
                continue
            players = data.get("players") or []
            wanted = ROSTER if character is None else {character}
            if not any(p.get("character") in wanted for p in players):
                continue
            data["_file"] = f
            runs.append(data)
    return runs


def card_id(entry: dict) -> str:
    """`CARD.KLEEMOD-JUMPY_DUMPTY` -> `jumpy_dumpty`, matching the yaml sheet."""
    raw = entry.get("id", "")
    return raw[len(CARD_PREFIX):].lower() if raw.startswith(CARD_PREFIX) else raw


def roster_player(run: dict, character: str | None = None) -> dict:
    """The roster seat in this run.

    With `character` given, that seat specifically. Without, the first seat
    belonging to ANY roster character -- which is what makes a co-op run
    readable at all: a Klee/Kokomi lobby has two roster seats and the old
    Klee-only lookup would raise StopIteration on a Furina/Kokomi one.
    """
    wanted = ROSTER if character is None else {character}
    return next(p for p in run["players"] if p.get("character") in wanted)


def roster_seats(run: dict) -> list[dict]:
    """EVERY roster seat, so a co-op run is not counted as one player."""
    return [p for p in run["players"] if p.get("character") in ROSTER]


def drafted_cards(run: dict) -> list[dict]:
    """Cards acquired during the run. Floor 1 is the starting deck.

    Mirrors M6's basics exclusion by a different route -- see module docstring.
    """
    return [c for c in roster_player(run).get("deck", [])
            if c.get("floor_added_to_deck", 1) > 1]


def floors_reached(run: dict) -> int:
    return sum(len(act) for act in run.get("map_point_history", []))


def summarize(runs: list[dict]) -> dict:
    if not runs:
        return {}
    wins = sum(1 for r in runs if r.get("win"))
    abandoned = sum(1 for r in runs if r.get("was_abandoned"))
    decks = [len(roster_player(r).get("deck", [])) for r in runs]
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


def print_report(s: dict, runs: list[dict], label: str = "roster") -> None:
    if not s:
        print(f"No {label} runs found. Is the soak pointed at a modded profile?")
        return
    # ASCII only in printed output: the Windows console defaults to cp1252 and
    # mangles em dashes, which is noise in a log you will read at 3am.
    print(f"\n=== Tier 1 soak - {s['runs']} {label} runs ===")
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
    # E3. Default is the WHOLE roster, not Klee. The old default was Klee by
    # construction rather than by choice, and it made "the soak" mean "the
    # third of the soak this tool happened to look at".
    ap.add_argument("--character", default="all",
                    choices=["all", *sorted(ROSTER.values())],
                    help="restrict to one character (default: all)")
    args = ap.parse_args(argv)

    by_name = {v: k for k, v in ROSTER.items()}
    character = None if args.character == "all" else by_name[args.character]

    dirs = find_history_dirs(args.root)
    if not dirs:
        print(f"No modded history dirs under {args.root}", file=sys.stderr)
        return 1
    for d in dirs:
        print(f"reading {d}")
    runs = load_runs(dirs, character)
    label = "roster" if args.character == "all" else args.character

    # Which characters the soak ACTUALLY contains, printed every run. A soak
    # that turns out to be 90% one character is a finding about the soak, and
    # the Klee-only tool could not have told you -- it discarded the rest
    # silently and reported what was left as "the soak".
    seats = Counter(p.get("character") for r in runs for p in roster_seats(r))
    if seats:
        mix = ", ".join(f"{ROSTER.get(k, k)} {v}"
                        for k, v in sorted(seats.items()))
        print(f"roster seats: {mix}")

    if args.crashes:
        flagged = suspicious(runs)
        print(f"\n{len(flagged)} suspicious of {len(runs)} {label} runs")
        for r, why in flagged:
            print(f"  seed {r.get('seed')}  {why}  ({r['_file'].name})")
        return 0

    print_report(summarize(runs), runs, label)

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
