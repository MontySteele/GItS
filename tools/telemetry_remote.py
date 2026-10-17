#!/usr/bin/env python3
"""Pull uploaded beta runs from the telemetry Worker's D1 database and summarise them.

    python tools/telemetry_remote.py                      # remote DB (needs `npx wrangler login`)
    python tools/telemetry_remote.py --local              # the local dev DB (`wrangler dev`)
    python tools/telemetry_remote.py --variant beta --since-days 14
    python tools/telemetry_remote.py --character CHARACTER.KLEEMOD-FURINA --top 15
    python tools/telemetry_remote.py --dump runs.jsonl    # raw records, one per line

The rows come from `npx wrangler d1 execute gits-telemetry [--remote|--local]
--json --command ...`, run in telemetry-worker/ so wrangler finds its config.
The summary: runs by character, win rate, floor reached, and per character the
most-picked and most-passed cards on card-reward floors (shops are left out of
the pick counts, because a shop "offers" its whole shelf). The record shape is
telemetry-worker/schema/run-v1.json. This is the uploaded-runs report; the
local Balance report over seat and play logs is tools/telemetry_report.py.
"""
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKER = ROOT / "telemetry-worker"
DATABASE = "gits-telemetry"
PAGE = 500


def _sql_str(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def build_where(variant: str | None, character: str | None,
                since_days: float | None, now: float | None = None) -> str:
    """The WHERE clause for the filters; values are quoted, never interpolated raw."""
    clauses = []
    if variant:
        clauses.append(f"variant = {_sql_str(variant)}")
    if character:
        clauses.append(f"character = {_sql_str(character)}")
    if since_days is not None:
        cutoff = int((now if now is not None else time.time()) - since_days * 86400)
        clauses.append(f"received_at >= {cutoff}")
    return (" WHERE " + " AND ".join(clauses)) if clauses else ""


def wrangler_query(sql: str, local: bool) -> list[dict]:
    """Run one SELECT through wrangler and return its result rows."""
    npx = shutil.which("npx")
    if npx is None:
        sys.exit("npx not found on PATH (install Node.js)")
    cmd = [npx, "wrangler", "d1", "execute", DATABASE,
           "--local" if local else "--remote", "--json", "--command", sql]
    proc = subprocess.run(cmd, cwd=WORKER, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        sys.exit(f"wrangler failed ({proc.returncode}):\n{proc.stderr or proc.stdout}")
    return parse_wrangler_json(proc.stdout)


def parse_wrangler_json(stdout: str) -> list[dict]:
    """`d1 execute --json` prints a list of statement results; collect their rows."""
    start = stdout.find("[")
    if start < 0:
        sys.exit(f"wrangler printed no JSON:\n{stdout}")
    data = json.loads(stdout[start:])
    rows: list[dict] = []
    for stmt in data if isinstance(data, list) else [data]:
        rows.extend(stmt.get("results") or [])
    return rows


def fetch_runs(where: str, local: bool) -> list[dict]:
    """Every matching record, paged so no single wrangler reply grows too large."""
    runs: list[dict] = []
    offset = 0
    while True:
        rows = wrangler_query(
            f"SELECT payload FROM runs{where} ORDER BY received_at, id "
            f"LIMIT {PAGE} OFFSET {offset}", local)
        runs.extend(json.loads(r["payload"]) for r in rows)
        if len(rows) < PAGE:
            return runs
        offset += PAGE


def summarise(runs: list[dict], top: int) -> dict:
    """Per character: runs, wins, win rate, floor reached, top picked and passed cards."""
    by_char: dict[str, list[dict]] = defaultdict(list)
    for run in runs:
        by_char[run["character"]].append(run)
    out: dict[str, dict] = {}
    for char, rs in sorted(by_char.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        offered: Counter[str] = Counter()
        picked: Counter[str] = Counter()
        screens = skips = 0
        for run in rs:
            for floor in run.get("floors", []):
                choice = floor.get("card_choice")
                if not choice or floor.get("type") == "shop":
                    continue
                screens += 1
                skips += not choice["picked"]
                offered.update(choice["offered"])
                picked.update(choice["picked"])
        passed = Counter({card: n - picked[card] for card, n in offered.items()})
        floors = [r["floor_reached"] for r in rs]
        wins = sum(bool(r["victory"]) for r in rs)
        out[char] = {
            "runs": len(rs),
            "wins": wins,
            "win_rate": wins / len(rs),
            "floor_median": statistics.median(floors),
            "floor_mean": statistics.fmean(floors),
            "ascension_max": max(r["ascension"] for r in rs),
            "card_screens": screens,
            "skip_rate": (skips / screens) if screens else 0.0,
            "top_picked": [(c, n, offered[c]) for c, n in picked.most_common(top)],
            "top_passed": [(c, n, offered[c]) for c, n in passed.most_common(top) if n > 0],
        }
    return out


def render(summary: dict, total: int) -> str:
    lines = [f"{total} runs"]
    if not summary:
        return lines[0]
    lines.append("")
    lines.append(f"{'character':<40} {'runs':>5} {'wins':>5} {'win%':>6} "
                 f"{'floor med':>9} {'floor avg':>9} {'skip%':>6}")
    for char, s in summary.items():
        lines.append(f"{char:<40} {s['runs']:>5} {s['wins']:>5} {s['win_rate']:>6.1%} "
                     f"{s['floor_median']:>9g} {s['floor_mean']:>9.1f} {s['skip_rate']:>6.1%}")
    for char, s in summary.items():
        lines.append("")
        lines.append(f"{char}: top picked (picked / offered)")
        lines.extend(f"  {c:<56} {n:>4} / {o:<4}" for c, n, o in s["top_picked"])
        lines.append(f"{char}: top passed (passed / offered)")
        lines.extend(f"  {c:<56} {n:>4} / {o:<4}" for c, n, o in s["top_passed"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--local", action="store_true",
                    help="read the local dev DB instead of the deployed one")
    ap.add_argument("--variant", choices=("beta", "public"))
    ap.add_argument("--character", help="a character id, e.g. CHARACTER.KLEEMOD-FURINA")
    ap.add_argument("--since-days", type=float, help="only runs received in the last N days")
    ap.add_argument("--top", type=int, default=10, help="cards per list (default 10)")
    ap.add_argument("--json", action="store_true", help="print the summary as JSON")
    ap.add_argument("--dump", type=Path, help="also write the raw records as JSON lines")
    args = ap.parse_args(argv)

    runs = fetch_runs(build_where(args.variant, args.character, args.since_days), args.local)
    if args.dump:
        with args.dump.open("w", encoding="utf-8", newline="\n") as fh:
            for run in runs:
                fh.write(json.dumps(run, sort_keys=True) + "\n")
    summary = summarise(runs, args.top)
    if args.json:
        print(json.dumps({"runs": len(runs), "characters": summary}, indent=1))
    else:
        print(render(summary, len(runs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
