#!/usr/bin/env python3
"""Card offers a seat saw and what it took, per character and per card.

    python tools/offer_report.py --character Varka
    python tools/offer_report.py --character Varka --element pyro
    python tools/offer_report.py --character Varka --element cryo --rarity rare
    python tools/offer_report.py --character Varka --card "Deep Freeze"
    python tools/offer_report.py --character Varka --embark 20261008 --json
    python tools/telemetry_report.py --offers --character Varka   # the same

WHAT IT READS. `understudy/logs/offers/card-offers-lane<N>.jsonl`, written by
`understudy/offer_log.py` whenever `blindplay act` answers a card reward, a
shop, an out-of-fight card chooser or a bundle (`--dir` replaces the folder).
A seat run from another checkout writes that checkout's folder: pass both.

WHAT AN OFFER IS. Rows are folded before counting, so a reward opened,
skipped, reopened and taken is one offer, taken:

  * a card reward, event chooser or bundle is one offer per (lane, embark,
    seed, act, floor, screen, cards shown); taken if any row took a card.
  * a shop is one offer per (lane, embark, seed, act, floor): every card
    shelf seen on any row, bought if any row bought it.
  * `card_reward_unopened` (a reward screen left with its card reward never
    opened) counts once per floor that has no opened card reward. Its cards
    were never on the wire, so it is a count, not a card.

WHAT IT PRINTS. Per character: offers by screen (taken, skipped, unopened),
then per card: times offered, times taken, take rate, and the split by card
reward / shop / event. A card is its name without `+`; `up` is how many of the
offers were already upgraded. The sheet columns (owner, rarity, elements) come
from `docs/prototype-surface.yaml`, joined on the wire id
(`KLEEMOD-PROTO_X` is row `proto_x`) or the name; a base-game card has none.

THE FILTERS ASK THE PICK'S QUESTION. `--element`, `--tag`, `--rarity`,
`--type`, `--card` narrow the card table; with any of them set and a single
`--character`, the sheet rows of that character that match and were NEVER
offered are listed under the table. That list is the "never offered" half of
the Varka question; the table is the "offered and passed" half. Elements are
the sheet's `element:` field where it has one (companions), else every element
the row's effects or description name (`[gold]Pyro[/gold]`). `--tag` matches
`tags`, `role_c`, `type`, `rarity` and `personal_pool`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import yaml

REPO = Path(__file__).resolve().parents[1]
DEFAULT_DIR = REPO / "understudy" / "logs" / "offers"
SHEET = REPO / "docs" / "prototype-surface.yaml"
ELEMENTS = ("pyro", "hydro", "electro", "cryo", "anemo", "geo", "dendro")
_WIRE_ID = re.compile(r"^KLEEMOD-(PROTO_[A-Z0-9_]+)$")
SCREEN_GROUP = {"card_reward": "reward", "shop": "shop", "choose": "event",
                "simple_select": "event", "bundle": "event"}


# ---------------------------------------------------------------- sources --

def load_rows(dirs: Iterable[Path]) -> list[dict]:
    rows: list[dict] = []
    for d in dirs:
        files = [d] if d.is_file() else sorted(d.glob("card-offers-*.jsonl"))
        for path in files:
            for line in path.read_text(encoding="utf-8").splitlines():
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("screen"):
                    rows.append(row)
    return rows


def _elements_named(row: dict) -> list[str]:
    explicit = str(row.get("element") or "").lower()
    if explicit in ELEMENTS:
        return [explicit]
    text = json.dumps(row.get("effects") or []).lower() + " " + \
        str(row.get("description") or "").lower()
    return [e for e in ELEMENTS if re.search(rf"\b{e}\b", text)]


def load_sheet(path: Path = SHEET) -> dict[str, dict]:
    """`{key: facts}` keyed by row id AND by name, for the join."""
    try:
        rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    except OSError:
        return {}
    out: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict) or not row.get("id"):
            continue
        tags = [str(t).lower() for t in row.get("tags") or []]
        tags += [str(row[k]).lower() for k in ("role_c", "type", "rarity",
                                               "personal_pool") if row.get(k)]
        facts = {"id": str(row["id"]), "name": str(row.get("name") or ""),
                 "owner": str(row.get("character") or "").lower(),
                 "rarity": str(row.get("rarity") or "").lower(),
                 "type": str(row.get("type") or "").lower(),
                 "elements": _elements_named(row), "tags": tags}
        out[facts["id"]] = facts
        out.setdefault(facts["name"], facts)
    return out


def sheet_facts(sheet: dict[str, dict], card: dict) -> dict | None:
    m = _WIRE_ID.match(str(card.get("id") or "").strip().upper())
    if m and m.group(1).lower() in sheet:
        return sheet[m.group(1).lower()]
    return sheet.get(str(card.get("name") or ""))


# ---------------------------------------------------------------- folding --

def _run(row: dict) -> tuple:
    return (row.get("lane"), row.get("embark"), row.get("seed"),
            row.get("act"), row.get("floor"))


def _shown(card: dict) -> tuple:
    return (card.get("name"), bool(card.get("upgraded")),
            card.get("bundle"))


def fold(rows: list[dict]) -> list[dict]:
    """One dict per offer: `character, screen, cards, taken, outcome`."""
    offers: dict[tuple, dict] = {}
    opened_floors: set[tuple] = set()
    unopened: dict[tuple, dict] = {}
    for row in rows:
        screen = row.get("screen")
        run = _run(row)
        if screen == "card_reward_unopened":
            unopened.setdefault(run, row)
            continue
        if screen == "card_reward":
            opened_floors.add(run)
        cards = [c for c in row.get("offered") or [] if isinstance(c, dict)]
        if screen == "shop":
            key = run + ("shop",)
        else:
            key = run + (screen, tuple(sorted(map(str, map(_shown, cards)))))
        held = offers.setdefault(key, {
            "character": row.get("character") or "", "screen": screen,
            "room": row.get("room") or "", "cards": {}, "taken": {},
            "outcome": ""})
        for c in cards:
            held["cards"].setdefault(_shown(c), c)
        for c in row.get("taken") or []:
            if isinstance(c, dict):
                held["taken"][_shown(c)] = c
    out = list(offers.values())
    for o in out:
        if o["taken"]:
            o["outcome"] = "bought" if o["screen"] == "shop" else "taken"
        else:
            o["outcome"] = "passed" if o["screen"] == "shop" else "skipped"
    for run, row in unopened.items():
        if run not in opened_floors:
            out.append({"character": row.get("character") or "",
                        "screen": "card_reward_unopened",
                        "room": row.get("room") or "", "cards": {},
                        "taken": {}, "outcome": "unopened"})
    return out


# ------------------------------------------------------------- the tables --

def screen_counts(offers: list[dict]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for o in offers:
        out[o["screen"]]["offers"] += 1
        out[o["screen"]][o["outcome"] or "unknown"] += 1
    return {k: dict(v) for k, v in out.items()}


def card_table(offers: list[dict], sheet: dict[str, dict]) -> list[dict]:
    cards: dict[str, dict] = {}
    for o in offers:
        group = SCREEN_GROUP.get(o["screen"])
        if group is None:
            continue
        taken_names = {k[0] for k in o["taken"]}
        for key, c in o["cards"].items():
            name = str(c.get("name") or "")
            row = cards.get(name)
            if row is None:
                facts = sheet_facts(sheet, c) or {}
                row = cards[name] = {
                    "card": name, "offered": 0, "taken": 0, "upgraded": 0,
                    "owner": facts.get("owner", ""),
                    "rarity": facts.get("rarity") or c.get("rarity") or "",
                    "type": facts.get("type", ""),
                    "elements": facts.get("elements", []),
                    "tags": facts.get("tags", []), "sheet_id": facts.get("id"),
                    "by": {g: [0, 0] for g in ("reward", "shop", "event")}}
            row["offered"] += 1
            row["upgraded"] += int(bool(c.get("upgraded")))
            row["by"][group][0] += 1
            if name in taken_names:
                row["taken"] += 1
                row["by"][group][1] += 1
                taken_names.discard(name)
    for row in cards.values():
        row["rate"] = row["taken"] / row["offered"] if row["offered"] else None
    return sorted(cards.values(), key=lambda r: (-r["offered"], r["card"]))


def _matches(facts: dict, args: argparse.Namespace) -> bool:
    if args.element and not set(e.lower() for e in args.element) & set(
            facts.get("elements") or []):
        return False
    if args.rarity and (facts.get("rarity") or "") not in {
            r.lower() for r in args.rarity}:
        return False
    if args.type and (facts.get("type") or "") not in {
            t.lower() for t in args.type}:
        return False
    if args.tag and not {t.lower() for t in args.tag} & set(
            facts.get("tags") or []):
        return False
    if args.card and (facts.get("card") or facts.get("name")) not in args.card:
        return False
    return True


def _filtered(args: argparse.Namespace) -> bool:
    return bool(args.element or args.rarity or args.type or args.tag
                or args.card)


def never_offered(table: list[dict], sheet: dict[str, dict], owner: str,
                  args: argparse.Namespace) -> list[dict]:
    seen = {r["card"] for r in table}
    rows = {f["id"]: f for f in sheet.values()}.values()
    return sorted(({"card": f["name"], "rarity": f["rarity"],
                    "elements": f["elements"]} for f in rows
                   if f["owner"] == owner and f["rarity"] != "basic"
                   and f["name"] not in seen
                   and _matches(dict(f, card=f["name"]), args)),
                  key=lambda r: r["card"])


def build(args: argparse.Namespace, rows: list[dict],
          sheet: dict[str, dict]) -> dict:
    since = dt.datetime.fromisoformat(args.since) if args.since else None
    keep = []
    for row in rows:
        if args.embark and not any(str(row.get("embark") or "").startswith(e)
                                   for e in args.embark):
            continue
        if since and dt.datetime.fromisoformat(
                str(row.get("ts") or "1970-01-01")) < since:
            continue
        keep.append(row)
    offers = fold(keep)
    wanted = {c.lower() for c in args.character or []}
    out: dict[str, Any] = {"characters": []}
    for who in sorted({o["character"] for o in offers}):
        if wanted and who.lower() not in wanted:
            continue
        mine = [o for o in offers if o["character"] == who]
        table = [r for r in card_table(mine, sheet) if _matches(r, args)]
        entry = {"character": who, "screens": screen_counts(mine),
                 "cards": table}
        if _filtered(args) and len(wanted) == 1:
            entry["never_offered"] = never_offered(
                table, sheet, who.lower().split()[-1], args)
        out["characters"].append(entry)
    return out


def _rate(v: float | None) -> str:
    return "-" if v is None else f"{v:.0%}"


def render(report: dict, top: int) -> str:
    lines: list[str] = []
    for entry in report["characters"]:
        lines.append(f"== {entry['character']}")
        for screen, n in sorted(entry["screens"].items()):
            rest = ", ".join(f"{k} {v}" for k, v in sorted(n.items())
                             if k != "offers")
            lines.append(f"  {screen}: {n['offers']} offers ({rest})")
        lines.append(f"  {'card':32} {'offered':>7} {'taken':>5} {'rate':>5}"
                     f"  {'reward':>7} {'shop':>7} {'event':>7}  {'up':>3}"
                     f"  owner/rarity/elements")
        for r in entry["cards"][:top]:
            by = "  ".join(f"{a:>3}/{b:<3}" for a, b in
                           (r["by"][g] for g in ("reward", "shop", "event")))
            facts = "/".join(x for x in (r["owner"], r["rarity"],
                                         ",".join(r["elements"])) if x)
            lines.append(f"  {r['card'][:32]:32} {r['offered']:>7} "
                         f"{r['taken']:>5} {_rate(r['rate']):>5}  {by}  "
                         f"{r['upgraded']:>3}  {facts}")
        if len(entry["cards"]) > top:
            lines.append(f"  ... {len(entry['cards']) - top} more (--top)")
        if "never_offered" in entry:
            names = [f"{r['card']} ({r['rarity']})"
                     for r in entry["never_offered"]]
            lines.append(f"  never offered, matching the filter "
                         f"({len(names)}): " + (", ".join(names) or "none"))
        lines.append("")
    return "\n".join(lines) if lines else "no offers in the log"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--character", action="append",
                    help="the seat's character (repeatable)")
    ap.add_argument("--element", action="append",
                    help="cards naming this element (repeatable)")
    ap.add_argument("--rarity", action="append")
    ap.add_argument("--type", action="append", help="attack, skill, power")
    ap.add_argument("--tag", action="append",
                    help="tags / role_c / type / rarity / personal_pool")
    ap.add_argument("--card", action="append", help="exact card name")
    ap.add_argument("--embark", action="append",
                    help="embark stamp prefix (repeatable)")
    ap.add_argument("--since", help="ISO date/datetime, local time, on ts")
    ap.add_argument("--dir", action="append", type=Path,
                    help=f"log folder or file (default {DEFAULT_DIR})")
    ap.add_argument("--sheet", type=Path, default=SHEET)
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    rows = load_rows(args.dir or [DEFAULT_DIR])
    report = build(args, rows, load_sheet(args.sheet))
    if args.json:
        print(json.dumps(report, indent=1))
    else:
        print(render(report, args.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
