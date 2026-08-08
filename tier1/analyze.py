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

PER-FIGHT GRANULARITY (EB-18). The run history above is the run's OUTCOME: one
record per run, and a fight inside it is invisible. The mod's own human feed
(`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs`) writes one JSON-lines record
per seat per FIGHT into `%APPDATA%/SlayTheSpire2/gits_telemetry/*.jsonl`, and
since EB-18 those records carry `run_id` -- the run's string seed, which is the
same token the run history writes as `seed`. That is the join, and it is why
this file can now read both granularities without a second instrument. A seed is
not a run, though -- replaying one is a supported arm -- so the fight side also
carries `run_instance`, and GROUPING is on the pair while the JOIN stays on the
seed.

Everything about the fight stream is OPTIONAL and ADDITIVE here. A machine with
no fight logs, or logs written before EB-18, analyses exactly as it did before:
the run report is unchanged, missing keys read as absent rather than as zero,
and a half-written last line (the crash that JSON-lines exists to survive) is
skipped rather than fatal.

Usage:
    python -m tier1.analyze                 # summarize the soak
    python -m tier1.analyze --crashes       # only runs that ended abnormally
    python -m tier1.analyze --predict       # vs Tier 0.5 (read the caveat)
    python -m tier1.analyze --fights        # the per-fight stream only
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

# The human feed's directory, fixed by `PlayTelemetry.Root()`: the game's own
# profile root, deliberately OUTSIDE the mod directory (deploy.ps1 deletes and
# re-copies `mods/klee`, which would destroy the log exactly when it holds the
# newest data). Kept as its own constant rather than derived from DEFAULT_ROOT
# because the two trees are siblings by coincidence, not by rule.
DEFAULT_FIGHT_ROOT = Path(os.environ.get("APPDATA", "")) / "SlayTheSpire2" \
    / "gits_telemetry"


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


# --------------------------------------------------------------- fights ----
#
# EB-18. Everything below reads the mod's per-fight JSON-lines stream. It is a
# SECOND source with a different failure mode from the run history, and the two
# are only ever joined on `run_id`; nothing here infers a fight from a run or a
# run from a fight. `run_instance` never crosses the join -- it only separates
# fight groups the seed alone cannot tell apart.

def find_fight_logs(root: Path = DEFAULT_FIGHT_ROOT) -> list[Path]:
    """Every per-fight log under `root`, oldest first.

    `play-*.jsonl` is what the mod names its files; the glob is wider than that
    on purpose, because a log copied off a soak box under another name is still
    the same records and refusing to read it would be a naming rule pretending
    to be a schema rule.
    """
    if not root.is_dir():
        return []
    return sorted(root.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)


def load_fights(root: Path = DEFAULT_FIGHT_ROOT) -> list[dict]:
    """Fight records from every log under `root`.

    TOLERANT BY CONSTRUCTION, which is the whole reason the stream is
    JSON-lines: a crashed or killed game leaves a half-written final line, and
    one bad line must cost one fight rather than the file. Anything that is not
    a `record: "fight"` object is skipped in silence -- a future record type is
    not an error here.
    """
    fights = []
    for f in find_fight_logs(root):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError as e:
            print(f"  ! unreadable {f.name}: {e}", file=sys.stderr)
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue            # truncated tail, or a line from a crash
            if not isinstance(rec, dict) or rec.get("record") != "fight":
                continue
            rec["_file"] = f
            fights.append(rec)
    return fights


def run_key(fight: dict) -> tuple[str, str]:
    """The identity of the RUN a fight belongs to: `(run_id, run_instance)`.

    A SEED IS NOT A RUN. `run_id` is the run's string seed -- the token the
    game's own history writes, and the only thing that joins the two sources --
    but replaying a seed is a first-class arm (P1.5 / R104), so one session can
    hold two DIFFERENT runs that carry the same `run_id`. `run_instance` is the
    mod's per-`RunState` token (`<session stamp>#<ordinal>`), which is what
    makes the pair unique where the seed alone is not.

    BACKWARD COMPATIBLE BY CONSTRUCTION. A record written before the token
    existed carries `""` and so groups exactly as it used to: one group per
    seed, ambiguous under a replayed seed, and reported as such rather than
    silently repaired.
    """
    return (fight.get("run_id", ""), fight.get("run_instance", ""))


def fights_by_run(fights: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """Fights grouped by the run they belong to, in fight order.

    A record with no `run_id` (every record written before EB-18) groups under
    an empty id and is reported as UNLINKED rather than merged into a run -- an
    empty id is one absent join key per record, not one shared run.
    """
    out: dict[tuple[str, str], list[dict]] = {}
    for f in fights:
        out.setdefault(run_key(f), []).append(f)
    for rows in out.values():
        rows.sort(key=lambda r: (r.get("fight_index", 0), r.get("ts", 0)))
    return out


def summarize_fights(fights: list[dict]) -> dict:
    if not fights:
        return {}
    by_run = fights_by_run(fights)
    linked = {k: v for k, v in by_run.items() if k[0]}
    # `corpse_detonations` is ABSENT on a pre-EB-18 record and 0 on a fight
    # that had none. The two are different facts and the denominator says so:
    # a rate over records that never carried the key would be a reading about
    # the log format.
    scored = [f for f in fights if "corpse_detonations" in f]
    return {
        "fights": len(fights),
        "runs": len(linked),
        "unlinked": sum(len(v) for k, v in by_run.items() if not k[0]),
        # Linked fights that predate `run_instance`. They group by seed alone,
        # so two runs of one seed among them are ONE group here and there is no
        # way to tell from the record that they were two -- a caveat on the
        # count, printed beside it rather than quietly folded into it.
        "seed_only": sum(len(v) for k, v in by_run.items()
                         if k[0] and not k[1]),
        "outcomes": Counter(f.get("outcome", "unknown") for f in fights),
        "encounters": Counter(f.get("encounter") or "(unrecorded)"
                              for f in fights),
        "characters": Counter(f.get("character", "unknown") for f in fights),
        "feeds": Counter(f"{f.get('feed', 'unknown')}/{f.get('source', 'unknown')}"
                         for f in fights),
        "coop_fights": sum(1 for f in fights if (f.get("seats") or 1) > 1),
        "hp_lost": sum(f.get("hp_lost", 0) for f in fights),
        "turns": sum(f.get("turns", 0) for f in fights),
        "detonation_fights": len(scored),
        "detonations": sum(f.get("detonations", 0) for f in scored),
        "corpse_detonations": sum(f.get("corpse_detonations", 0) for f in scored),
        "fights_with_corpse": sum(1 for f in scored
                                  if f.get("corpse_detonations", 0) > 0),
    }


def join_fights_to_runs(runs: list[dict], fights: list[dict]) -> dict:
    """How much of the fight stream belongs to runs this analysis loaded.

    Reported rather than enforced. A fight whose run is not in the history is
    ordinarily a run still in progress (the history entry is written when the
    run ENDS), which is exactly the case per-fight telemetry exists to make
    visible -- so it is a count, never a warning.

    THE JOIN IS STILL THE SEED, and only the seed: `run_instance` is the mod's
    own token and the run history has never heard of it. It splits the fight
    side into the runs it really was; both halves of a replayed seed then match
    that seed's history entries, which is correct -- the history holds two
    entries for two runs of one seed too.
    """
    seeds = {r.get("seed") for r in runs if r.get("seed")}
    by_run = fights_by_run(fights)
    matched = {k: v for k, v in by_run.items() if k[0] and k[0] in seeds}
    return {
        "runs_with_fights": len(matched),
        "fights_matched": sum(len(v) for v in matched.values()),
        "fights_unmatched": len(fights) - sum(len(v) for v in matched.values()),
    }


def print_fight_report(s: dict, join: dict | None = None) -> None:
    if not s:
        return
    print(f"\n=== per-fight stream - {s['fights']} fight records ===")
    print(f"  runs (id+instance) {s['runs']}"
          + (f"   [{s['unlinked']} unlinked - pre-EB-18 records]"
             if s["unlinked"] else ""))
    if s.get("seed_only"):
        print(f"  {s['seed_only']} fight row(s) predate `run_instance` and group "
              "by seed alone;")
        print("    two runs of one seed among them read as one run.")
    feeds = ", ".join(f"{k} x{n}" for k, n in s["feeds"].most_common())
    print(f"  feed/source        {feeds}")
    chars = ", ".join(f"{k} {n}" for k, n in s["characters"].most_common())
    print(f"  seats recorded     {chars}")
    print(f"  co-op fight rows   {s['coop_fights']}")
    outcomes = ", ".join(f"{k} {n}" for k, n in s["outcomes"].most_common())
    print(f"  outcomes           {outcomes}")
    print(f"  turns / hp lost    {s['turns']} / {s['hp_lost']}")

    print("\n  -- most-fought encounters --")
    for enc, n in s["encounters"].most_common(8):
        print(f"    {n:>4}  {enc}")

    # THE COUNT EB-18 EXISTS FOR. A detonation that resolved on an
    # already-dead body -- probe (e) / Q11's question, answered from ordinary
    # play instead of a scripted two-arm run. Reported, never graded.
    print(f"\n  -- bombs, over {s['detonation_fights']} fight(s) carrying the counters --")
    if s["detonation_fights"]:
        print(f"    detonations          {s['detonations']}")
        print(f"    corpse detonations   {s['corpse_detonations']}"
              f"  (in {s['fights_with_corpse']} fight(s))")
        print("    NOTE: >0 is a fact. 0 is not proof of absence -- a corpse")
        print("    detonation from the blow that ended the fight can land")
        print("    after the record is written (PlayTelemetry.FlushAll).")
    else:
        print("    no record carries them (logs predate EB-18)")

    if join:
        print("\n  -- joined to run history --")
        print(f"    runs with fights   {join['runs_with_fights']}")
        print(f"    fights matched     {join['fights_matched']}")
        print(f"    fights unmatched   {join['fights_unmatched']}"
              "   (a run still in progress writes no history entry)")


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
    # EB-18. `--fights` is the fight stream ALONE, which is the mode a machine
    # that has played but not finished a run needs: the run history is empty
    # until a run ends, and refusing to report without it would hide the
    # granularity this option exists to add.
    ap.add_argument("--fights", action="store_true",
                    help="report the per-fight stream only (no run history)")
    ap.add_argument("--fights-root", type=Path, default=DEFAULT_FIGHT_ROOT,
                    help="where the mod's per-fight jsonl logs live")
    # E3. Default is the WHOLE roster, not Klee. The old default was Klee by
    # construction rather than by choice, and it made "the soak" mean "the
    # third of the soak this tool happened to look at".
    ap.add_argument("--character", default="all",
                    choices=["all", *sorted(ROSTER.values())],
                    help="restrict to one character (default: all)")
    args = ap.parse_args(argv)

    by_name = {v: k for k, v in ROSTER.items()}
    character = None if args.character == "all" else by_name[args.character]

    fights = load_fights(args.fights_root)
    if args.fights:
        if not fights:
            print(f"No per-fight records under {args.fights_root}. The mod "
                  "writes them from normal play; a machine that has not "
                  "played the deployed build has none.", file=sys.stderr)
            return 1
        print(f"reading {args.fights_root}")
        print_fight_report(summarize_fights(fights))
        return 0

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

    # Additive: a machine with no fight logs prints exactly what it printed
    # before EB-18.
    if fights:
        print_fight_report(summarize_fights(fights),
                           join_fights_to_runs(runs, fights))

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
