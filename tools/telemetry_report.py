#!/usr/bin/env python3
"""The Balance telemetry report: per-fight medians by character, act and kind.

    python tools/telemetry_report.py --character Klee --character base5
    python tools/telemetry_report.py --character Klee --since 2026-10-02
    python tools/telemetry_report.py --character Klee --cards-merge-upgrades
    python tools/telemetry_report.py --character Varka --feed bot --json
    python tools/telemetry_report.py --reactions --character Klee
    python tools/telemetry_report.py --coop --reactions
    python tools/telemetry_report.py --offers --character Varka --element pyro
    python tools/telemetry_report.py --character Klee --character base5 \\
        --run-instance 20261007-2357 --baseline-run-instance 20261005-1055 \\
        --baseline-run-instance 20261005-113940

READ THIS BEFORE USING A FIELD.

  * `reactions_by_turn` is a RUNNING TOTAL since combat start, sampled when
    each turn opens (`PlayTelemetry.cs`, `OpenTurn`). Use its LAST entry (a
    lower bound: the last turn's reactions are never sampled) or
    `reactions_by_type`, never a sum of its entries -- a sum counts each
    reaction once per later turn.
  * Co-op rows before 2026-08-30 (EB-156, 3523aa2e) carry BOARD totals of
    reactions in every seat's row, not the seat's own.
  * A per-character window should start at a build or a `run_instance`
    (`--run-instance`), not a date: a date window picks up stopped attempts,
    off-seed runs and reruns on the same seed.
  * `run_instance` is `<session stamp>#<ordinal>`, the stamp being the
    second the game process first wrote telemetry. Two lanes started in the
    same second share it, so a run is (`run_id`, `run_instance`), never
    `run_instance` alone.

WHAT IT READS. The real game's per-fight records (`record: "fight"`), written
by `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` into the game profile's
`gits_telemetry/*.jsonl`: `%APPDATA%/SlayTheSpire2/gits_telemetry` (your own
play) and every seat lane's
`%LOCALAPPDATA%/gits-lanes/laneN/SlayTheSpire2/gits_telemetry`. The schema is
`understudy/README.md`, "Telemetry schema". `--dir` replaces both.

CO-OP LANE COPIES ARE DROPPED ON READ. The mod writes a row for EVERY seat of
a fight (`PlayTelemetry.OpenFight` loops `run.Players`), so a bot co-op run
played on two lanes lands each (fight, seat) row once in each lane's dir.
`load_fights` keeps the first copy of each two-seat row, keyed on
`fight_key` plus seat and character; solo rows are never merged.

WHAT IT PRINTS (the Balance bar, `docs/current/operations/stage-gate.md`):

  1. By group x act x kind (monster / elite / boss): fights, median damage a
     turn (`damage_dealt / turns`), median HP lost as % of max, median turns,
     median Block gained a turn, median peak Strength (the highest
     end-of-turn `strength_by_turn` reading in the fight), losses
     (`outcome: died`; written since 2026-10-05, when the mod began filing
     the fight a seat dies in).
  2. The comparison: each group's act-by-act NORMAL-fight damage a turn and
     HP lost as a ratio to the base five's (the bar is within about 15%).
     The baseline is always the base five under the same filters, or under
     `--baseline-since/--baseline-until` when given.
  3. Per card, for the first non-base5 group (or `--cards-for`): fights the
     card was played in, plays, damage credited (`damage_by_source`) and
     damage a play, by act -- so a scaling card can be read against a flat
     one across acts. `Strike+` is `Strike` upgraded; `--cards-merge-upgrades`
     groups by base name. Sources that are not cards (`(Bomb)`, `(Overload)`)
     are listed with no plays.

  4. With `--reactions`: what reactions are worth, per group -- reactions a
     turn by type (`reactions_by_type`), the amplifiers' bonus damage a turn
     (`amp_bonus_damage`) and reaction debuff stacks a turn
     (`debuffs_from_reactions`). POOLED, not medians: summed over the fights
     that carry the keys (`nR`; written since 2026-10-06), divided by their
     turns, because most fights hold a handful of reactions and a median of
     small counts reads 0. Credit is the dealing seat's.

CO-OP (`--coop`). Keeps only two-seat fights (`seats == 2`) instead of solo
ones. Every co-op lane writes a row for BOTH seats of the same fight, so rows
are de-duplicated on (run_id, run_instance, act, floor, fight_index,
encounter, kind, seat_index) before anything is counted; `run_instance` keeps
an abandoned attempt and its rerun on the same seed apart. The reaction section then groups by
TEAM -- the fight's characters, sorted, `Klee + Kokomi` -- with each member's
own line beneath it; a fight's turns are counted once for the team.

OLDER RECORDS LACK KEYS. `block_gained` arrived 2026-10-02 and the wider
damage credit the same day; a record missing a key is left out of that one
median and counted nowhere else as zero. The Block column's `nB` says how
many fights carried it; `strength_by_turn` arrived 2026-10-05.

Caveat carried from the paper: damage from a base character's Poison or orbs
is credited only when the engine names the seat's creature as the dealer, so
base damage a turn may read low.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

BASE5 = ("The Ironclad", "The Silent", "The Defect", "The Necrobinder",
         "The Regent")
BASE5_ALIAS = "base5"
KINDS = ("monster", "elite", "boss")
BAR = 0.15


# --------------------------------------------------------------- sources ---

def default_dirs() -> list[Path]:
    """The player's own profile and every lane's, those that exist."""
    out: list[Path] = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        out.append(Path(appdata) / "SlayTheSpire2" / "gits_telemetry")
    local = os.environ.get("LOCALAPPDATA")
    if local:
        for lane in sorted(glob.glob(os.path.join(local, "gits-lanes",
                                                  "lane*"))):
            out.append(Path(lane) / "SlayTheSpire2" / "gits_telemetry")
    return [d for d in out if d.is_dir()]


def load_fights(dirs: Iterable[Path], dedupe: bool = True) -> list[dict]:
    """Every `record: "fight"` row under the dirs. A bad line is skipped.
    With `dedupe` (the default) a two-seat row already read from another
    lane is dropped (`drop_lane_copies`)."""
    rows: list[dict] = []
    for d in dirs:
        for path in sorted(Path(d).glob("*.jsonl")):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("record") == "fight":
                    rows.append(row)
    return drop_lane_copies(rows) if dedupe else rows


def drop_lane_copies(rows: list[dict]) -> list[dict]:
    """Co-op: both lanes of a two-seat bot run write every seat's row, so
    each (fight, seat) arrives twice. Keep the first. Solo rows pass
    untouched: two solo lanes started in the same second on the same seed
    share every key here and are still two runs."""
    seen: set[tuple] = set()
    out = []
    for r in rows:
        if r.get("seats", 1) >= 2:
            k = (*fight_key(r), r.get("seat_index"),
                 str(r.get("character", "")))
            if k in seen:
                continue
            seen.add(k)
        out.append(r)
    return out


# --------------------------------------------------------------- filters ---

def parse_when(text: str | None) -> float | None:
    """ISO date or datetime -> unix seconds. A naive value is local time,
    which is what a person reading the clock means; `ts` is unix UTC."""
    if not text:
        return None
    when = dt.datetime.fromisoformat(text)
    return when.timestamp()


def canonical(name: str, seen: Iterable[str] = ()) -> str:
    """`ironclad` -> `The Ironclad`; `klee` -> `Klee`. Unknown names pass."""
    low = name.strip().lower()
    for known in (*BASE5, *seen):
        if low in (known.lower(), known.lower().removeprefix("the ")):
            return known
    return name.strip()


@dataclass
class Filters:
    since: float | None = None
    until: float | None = None
    run_ids: tuple[str, ...] = ()
    solo: bool = True
    feed: str = "all"
    coop: bool = False
    run_instances: tuple[str, ...] = ()

    def keep(self, row: dict) -> bool:
        ts = row.get("ts")
        if self.since is not None and (ts is None or ts < self.since):
            return False
        if self.until is not None and (ts is None or ts >= self.until):
            return False
        if self.run_ids and str(row.get("run_id", "")) not in self.run_ids:
            return False
        if self.run_instances and not str(row.get("run_instance", "")
                                          ).startswith(self.run_instances):
            return False
        if self.coop:
            if row.get("seats", 1) != 2:
                return False
        elif self.solo and row.get("seats", 1) != 1:
            return False
        if self.feed != "all" and row.get("feed", "human") != self.feed:
            return False
        return True


def group_rows(rows: list[dict], groups: list[str]) -> dict[str, list[dict]]:
    """Rows per group. `base5` pools the five; no groups = every character."""
    seen = sorted({str(r.get("character", "unknown")) for r in rows})
    if not groups:
        groups = seen
    out: dict[str, list[dict]] = {}
    for g in groups:
        if g.lower() == BASE5_ALIAS:
            members = set(BASE5)
            label = BASE5_ALIAS
        else:
            label = canonical(g, seen)
            members = {label}
        out[label] = [r for r in rows if r.get("character") in members]
    return out


# ----------------------------------------------------------------- stats ---

def _num(row: dict, key: str) -> float | None:
    v = row.get(key)
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def per_turn(row: dict, key: str) -> float | None:
    v, turns = _num(row, key), _num(row, "turns")
    if v is None or not turns or turns <= 0:
        return None
    return v / turns


def hp_lost_pct(row: dict) -> float | None:
    lost, top = _num(row, "hp_lost"), _num(row, "max_hp")
    if lost is None:
        start, end = _num(row, "hp_start"), _num(row, "hp_end")
        lost = start - end if start is not None and end is not None else None
    if lost is None or not top or top <= 0:
        return None
    return 100.0 * lost / top


def peak_strength(row: dict) -> float | None:
    """The highest end-of-turn Strength in the fight; None when the record
    has no `strength_by_turn` rows."""
    vals = [float(e[1]) for e in row.get("strength_by_turn") or []
            if isinstance(e, (list, tuple)) and len(e) >= 2
            and isinstance(e[1], (int, float)) and not isinstance(e[1], bool)]
    return max(vals) if vals else None


def _median(values: list[float | None]) -> float | None:
    vals = [v for v in values if v is not None]
    return statistics.median(vals) if vals else None


@dataclass
class Cell:
    group: str
    act: int
    kind: str
    fights: int
    dmg_turn: float | None
    hp_lost_pct: float | None
    turns: float | None
    block_turn: float | None
    n_block: int
    strength: float | None
    losses: int

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def cell(group: str, act: int, kind: str, rows: list[dict]) -> Cell:
    blocks = [per_turn(r, "block_gained") for r in rows]
    return Cell(group, act, kind, len(rows),
                _median([per_turn(r, "damage_dealt") for r in rows]),
                _median([hp_lost_pct(r) for r in rows]),
                _median([_num(r, "turns") for r in rows]),
                _median(blocks),
                sum(1 for b in blocks if b is not None),
                _median([peak_strength(r) for r in rows]),
                sum(1 for r in rows if r.get("outcome") == "died"))


def table(grouped: dict[str, list[dict]]) -> list[Cell]:
    out = []
    for g, rows in grouped.items():
        acts = sorted({r.get("act") for r in rows
                       if isinstance(r.get("act"), int)})
        for act in acts:
            for kind in KINDS:
                sub = [r for r in rows
                       if r.get("act") == act and r.get("kind") == kind]
                if sub:
                    out.append(cell(g, act, kind, sub))
    return out


def comparison(grouped: dict[str, list[dict]], baseline: list[dict]
               ) -> list[dict]:
    """Each group's normal-fight damage a turn and HP lost, act by act, as a
    ratio to the base five's."""
    out = []
    for g, rows in grouped.items():
        if g == BASE5_ALIAS:
            continue
        for act in (1, 2, 3):
            mine = [r for r in rows if r.get("act") == act
                    and r.get("kind") == "monster"]
            base = [r for r in baseline if r.get("act") == act
                    and r.get("kind") == "monster"]
            md = _median([per_turn(r, "damage_dealt") for r in mine])
            bd = _median([per_turn(r, "damage_dealt") for r in base])
            mh = _median([hp_lost_pct(r) for r in mine])
            bh = _median([hp_lost_pct(r) for r in base])
            dr = md / bd if md is not None and bd else None
            hr = mh / bh if mh is not None and bh else None
            out.append({
                "group": g, "act": act, "fights": len(mine),
                "base_fights": len(base),
                "dmg_turn": md, "base_dmg_turn": bd, "dmg_ratio": dr,
                "hp_lost_pct": mh, "base_hp_lost_pct": bh, "hp_ratio": hr,
                "within_bar": (dr is not None and hr is not None
                               and abs(dr - 1) <= BAR and abs(hr - 1) <= BAR),
            })
    return out


# ------------------------------------------------------------- reactions ---

REACTION_KEYS = ("reactions_by_type", "amp_bonus_damage",
                 "debuffs_from_reactions")


def fight_key(row: dict) -> tuple:
    """One fight, across the seats and lanes that wrote it. `run_instance`
    is in the key because `fight_index` restarts per instance: without it an
    abandoned attempt and its rerun on the same seed merge into one fight
    (the 2026-10-07 Klee + Varka and Ironclad + Silent runs did)."""
    return (str(row.get("run_id", "")), str(row.get("run_instance", "")),
            row.get("act"), row.get("floor"),
            row.get("fight_index"), str(row.get("encounter", "")),
            str(row.get("kind", "")))


def dedupe_seats(rows: list[dict]) -> list[dict]:
    """Co-op: each lane writes both seats' rows of one fight; keep one per
    (fight, seat). The first row read wins."""
    seen: set[tuple] = set()
    out = []
    for r in rows:
        k = (*fight_key(r), r.get("seat_index"))
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def _count_map(row: dict, key: str) -> dict[str, float]:
    v = row.get(key)
    if not isinstance(v, dict):
        return {}
    return {str(k): float(n) for k, n in v.items()
            if isinstance(n, (int, float)) and not isinstance(n, bool)}


def reaction_summary(group: str, fights: list[list[dict]]) -> dict:
    """Pooled per-turn reaction value over FIGHTS (each a list of the seat
    rows counted for this group). A fight counts toward the rates only when
    one of its rows carries `reactions_by_type`; its turns are the longest
    seat's, counted once."""
    totals: dict[str, dict[str, float]] = {k: {} for k in REACTION_KEYS}
    turns = 0.0
    carried = 0
    for seat_rows in fights:
        if not any(isinstance(r.get("reactions_by_type"), dict)
                   for r in seat_rows):
            continue
        carried += 1
        turns += max((_num(r, "turns") or 0.0) for r in seat_rows)
        for r in seat_rows:
            for key in REACTION_KEYS:
                for name, n in _count_map(r, key).items():
                    totals[key][name] = totals[key].get(name, 0.0) + n

    def rate(m: dict[str, float]) -> dict[str, float]:
        if turns <= 0:
            return {}
        return {k: m[k] / turns for k in sorted(m, key=lambda k: (-m[k], k))}

    def total(m: dict[str, float]) -> float | None:
        return sum(m.values()) / turns if turns > 0 else None

    return {"group": group, "fights": len(fights),
            "fights_with_keys": carried, "turns": turns,
            "reactions_turn": total(totals["reactions_by_type"]),
            "amp_bonus_turn": total(totals["amp_bonus_damage"]),
            "debuffs_turn": total(totals["debuffs_from_reactions"]),
            "reactions_by_type_turn": rate(totals["reactions_by_type"]),
            "amp_bonus_by_type_turn": rate(totals["amp_bonus_damage"]),
            "debuffs_by_type_turn": rate(totals["debuffs_from_reactions"]),
            "totals": {k: dict(sorted(v.items())) for k, v in totals.items()}}


def team_label(seat_rows: list[dict]) -> str:
    return " + ".join(sorted(str(r.get("character", "unknown"))
                             for r in seat_rows))


def reactions(grouped: dict[str, list[dict]], kept: list[dict],
              coop: bool, groups: list[str]) -> list[dict]:
    """Solo: one summary per character group. Co-op: one per team (a team
    shows when it holds any named character; none named = every team), each
    followed by its members' own lines (`member` set)."""
    if not coop:
        return [reaction_summary(g, [[r] for r in rows])
                for g, rows in grouped.items()]
    fights: dict[tuple, list[dict]] = {}
    for r in kept:
        fights.setdefault(fight_key(r), []).append(r)
    seen = sorted({str(r.get("character", "unknown")) for r in kept})
    wanted: set[str] = set()
    for g in groups:
        wanted |= set(BASE5) if g.lower() == BASE5_ALIAS \
            else {canonical(g, seen)}
    teams: dict[str, list[list[dict]]] = {}
    for seat_rows in fights.values():
        if wanted and not wanted & {r.get("character") for r in seat_rows}:
            continue
        teams.setdefault(team_label(seat_rows), []).append(seat_rows)
    out = []
    for label in sorted(teams):
        team_fights = teams[label]
        out.append(reaction_summary(label, team_fights))
        members = sorted({str(r.get("character", "unknown"))
                          for f in team_fights for r in f})
        for m in members:
            line = reaction_summary(
                m, [[r] for f in team_fights for r in f
                    if r.get("character") == m])
            line["member"] = True
            line["team"] = label
            out.append(line)
    return out


# ----------------------------------------------------------------- cards ---

def split_name(name: str) -> tuple[str, bool]:
    """`Strike++` -> (`Strike`, True); `Strike` -> (`Strike`, False)."""
    base = name.rstrip("+")
    return (base or name), base != name


def cards(rows: list[dict], merge_upgrades: bool = False) -> list[dict]:
    """Per card per act: fights played in, plays, damage credited, a play."""
    acc: dict[tuple[str, bool, int], dict[str, Any]] = {}

    def key(name: str, act: int) -> tuple[str, bool, int]:
        base, up = split_name(name)
        return (base, False if merge_upgrades else up, act)

    for i, r in enumerate(rows):
        act = r.get("act")
        if not isinstance(act, int):
            continue
        played: dict[str, int] = {}
        for entry in r.get("cards_played") or []:
            if isinstance(entry, (list, tuple)) and len(entry) >= 2:
                k = key(str(entry[1]), act)
                played[k] = played.get(k, 0) + 1
        for k, n in played.items():
            a = acc.setdefault(k, {"fights": 0, "plays": 0, "damage": 0})
            a["fights"] += 1
            a["plays"] += n
        dmg = r.get("damage_by_source") or {}
        if isinstance(dmg, dict):
            for src, amount in dmg.items():
                if not isinstance(amount, (int, float)):
                    continue
                k = key(str(src), act)
                a = acc.setdefault(k, {"fights": 0, "plays": 0, "damage": 0})
                a["damage"] += amount
    out = []
    for (name, up, act), a in acc.items():
        out.append({"card": name, "upgraded": up, "act": act,
                    "fights": a["fights"], "plays": a["plays"],
                    "damage": a["damage"],
                    "dmg_per_play": (a["damage"] / a["plays"]
                                     if a["plays"] else None)})
    total: dict[tuple[str, bool], float] = {}
    for c in out:
        total[(c["card"], c["upgraded"])] = total.get(
            (c["card"], c["upgraded"]), 0) + c["damage"]
    out.sort(key=lambda c: (-total[(c["card"], c["upgraded"])], c["card"],
                            c["upgraded"], c["act"]))
    return out


# ---------------------------------------------------------------- render ---

def _f(v: float | None, digits: int = 1) -> str:
    return "--" if v is None else f"{v:.{digits}f}"


def _rates(m: dict[str, float]) -> str:
    return "  ".join(f"{k} {v:.2f}" for k, v in m.items()) or "--"


def render_reactions(rx: list[dict]) -> list[str]:
    lines = ["", "REACTIONS (pooled a turn: totals over the nR fights that "
             "carry the keys / their turns; the dealing seat's credit)",
             f"{'group':<30}{'n':>5}{'nR':>5}{'turns':>7}{'rx/t':>7}"
             f"{'amp+/t':>8}{'dbf/t':>7}"]
    for s in rx:
        member = bool(s.get("member"))
        name = ("  | " if member else "") + s["group"]
        lines.append(f"{name[:29]:<30}{s['fights']:>5}"
                     f"{s['fights_with_keys']:>5}{s['turns']:>7.0f}"
                     f"{_f(s['reactions_turn'], 2):>7}"
                     f"{_f(s['amp_bonus_turn'], 2):>8}"
                     f"{_f(s['debuffs_turn'], 2):>7}")
        pad = "      " if member else "    "
        lines.append(f"{pad}reactions/t: {_rates(s['reactions_by_type_turn'])}")
        lines.append(f"{pad}amp bonus/t: {_rates(s['amp_bonus_by_type_turn'])}")
        lines.append(f"{pad}debuffs/t:   {_rates(s['debuffs_by_type_turn'])}")
    return lines


def render(cells: list[Cell], comp: list[dict], card_rows: list[dict],
           card_group: str | None, header: list[str], top: int,
           rx: list[dict] | None = None) -> str:
    lines = list(header)
    lines.append("")
    lines.append("BY GROUP x ACT x KIND (medians across fights)")
    lines.append(f"{'group':<16}{'act':>4} {'kind':<8}{'n':>5}{'dmg/t':>8}"
                 f"{'hp%':>7}{'turns':>7}{'blk/t':>7}{'nB':>5}{'str':>6}"
                 f"{'lost':>6}")
    for c in cells:
        lines.append(f"{c.group:<16}{c.act:>4} {c.kind:<8}{c.fights:>5}"
                     f"{_f(c.dmg_turn):>8}{_f(c.hp_lost_pct):>7}"
                     f"{_f(c.turns):>7}{_f(c.block_turn):>7}{c.n_block:>5}"
                     f"{_f(c.strength):>6}{c.losses:>6}")
    if comp:
        lines.append("")
        lines.append("COMPARISON: normal fights against the base five "
                     f"(bar: within {int(BAR * 100)}%)")
        lines.append(f"{'group':<16}{'act':>4}{'n':>5}{'base n':>8}"
                     f"{'dmg/t':>8}{'base':>7}{'ratio':>7}"
                     f"{'hp%':>7}{'base':>7}{'ratio':>7}  bar")
        for c in comp:
            bar = "--" if c["dmg_ratio"] is None or c["hp_ratio"] is None \
                else ("within" if c["within_bar"] else "OUTSIDE")
            lines.append(
                f"{c['group']:<16}{c['act']:>4}{c['fights']:>5}"
                f"{c['base_fights']:>8}{_f(c['dmg_turn']):>8}"
                f"{_f(c['base_dmg_turn']):>7}{_f(c['dmg_ratio'], 2):>7}"
                f"{_f(c['hp_lost_pct']):>7}{_f(c['base_hp_lost_pct']):>7}"
                f"{_f(c['hp_ratio'], 2):>7}  {bar}")
    if card_group is not None:
        lines.append("")
        names = []
        for c in card_rows:
            k = (c["card"], c["upgraded"])
            if k not in names:
                names.append(k)
        shown = set(names[:top]) if top else set(names)
        lines.append(f"PER CARD: {card_group} (by total damage credited; "
                     f"{len(shown)} of {len(names)} sources shown)")
        lines.append(f"{'card':<28}{'up':>3}{'act':>4}{'fights':>8}"
                     f"{'plays':>7}{'damage':>8}{'dmg/play':>10}")
        for c in card_rows:
            if (c["card"], c["upgraded"]) not in shown:
                continue
            lines.append(f"{c['card'][:27]:<28}{'+' if c['upgraded'] else '':>3}"
                         f"{c['act']:>4}{c['fights']:>8}{c['plays']:>7}"
                         f"{c['damage']:>8.0f}{_f(c['dmg_per_play']):>10}")
    if rx is not None:
        lines.extend(render_reactions(rx))
    return "\n".join(lines)


# ------------------------------------------------------------------ main ---

def build(args: argparse.Namespace, rows: list[dict]) -> dict:
    coop = bool(getattr(args, "coop", False))
    instances = tuple(getattr(args, "run_instance", None) or ())
    base_instances = tuple(getattr(args, "baseline_run_instance", None)
                           or ()) or instances
    filt = Filters(parse_when(args.since), parse_when(args.until),
                   tuple(args.run_id or ()), args.solo, args.feed, coop,
                   instances)
    kept = [r for r in rows if filt.keep(r)]
    if coop:
        kept = dedupe_seats(kept)
    grouped = group_rows(kept, list(args.character or []))
    base_filt = Filters(parse_when(args.baseline_since or args.since),
                        parse_when(args.baseline_until or args.until),
                        tuple(args.run_id or ()), args.solo, args.feed, coop,
                        base_instances)
    baseline = [r for r in rows if base_filt.keep(r)
                and r.get("character") in BASE5]
    if coop:
        baseline = dedupe_seats(baseline)
    cells = table(grouped)
    comp = comparison(grouped, baseline)
    if args.cards_for:
        card_group, card_src = next(iter(
            group_rows(kept, [args.cards_for]).items()))
    else:
        card_group = next((g for g in grouped if g != BASE5_ALIAS), None)
        card_src = grouped.get(card_group, []) if card_group else []
    card_rows = cards(card_src, args.cards_merge_upgrades) \
        if card_group is not None else []
    rx = reactions(grouped, kept, coop, list(args.character or [])) \
        if getattr(args, "reactions", False) else None
    out = {"filters": {"since": args.since, "until": args.until,
                        "baseline_since": args.baseline_since or args.since,
                        "baseline_until": args.baseline_until or args.until,
                        "run_id": list(args.run_id or ()),
                        "run_instance": list(instances),
                        "baseline_run_instance": list(base_instances),
                        "solo": args.solo,
                        "coop": coop, "feed": args.feed},
            "records_read": len(rows), "records_kept": len(kept),
            "groups": {g: len(v) for g, v in grouped.items()},
            "table": [c.as_dict() for c in cells],
            "comparison": comp,
            "cards_for": card_group,
            "cards": card_rows,
            "_cells": cells}
    if rx is not None:
        out["reactions"] = rx
    return out


def field_notes() -> str:
    """The docstring's READ THIS block, which --help prints as its epilog."""
    doc = __doc__ or ""
    start = doc.find("READ THIS BEFORE USING A FIELD.")
    end = doc.find("WHAT IT READS.")
    return doc[start:end].rstrip() if 0 <= start < end else ""


def main(argv: list[str] | None = None) -> int:
    # `--offers` is the card-offer report (`tools/offer_report.py`): the
    # bridge's log of what seats were offered and took, not fight records.
    argv = sys.argv[1:] if argv is None else list(argv)
    if "--offers" in argv:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import offer_report
        return offer_report.main([a for a in argv if a != "--offers"])
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=field_notes())
    ap.add_argument("--character", action="append",
                    help="a group: a display name (Klee, The Ironclad, "
                    "ironclad) or base5 for the five pooled; repeatable; "
                    "none = every character")
    ap.add_argument("--since", help="ISO date/datetime, local time, on ts")
    ap.add_argument("--until", help="ISO date/datetime, exclusive")
    ap.add_argument("--baseline-since", help="the base-five window, if not "
                    "--since")
    ap.add_argument("--baseline-until", help="the base-five window, if not "
                    "--until")
    ap.add_argument("--run-id", "--seed", action="append", dest="run_id",
                    help="keep one run seed (the record's run_id); repeatable")
    ap.add_argument("--run-instance", action="append",
                    help="keep rows whose run_instance starts with this "
                    "(a whole token like 20261005-113940#0, or a prefix like "
                    "20261005-1055); repeatable. Grades against named runs "
                    "instead of a clock window")
    ap.add_argument("--baseline-run-instance", action="append",
                    help="the base five's run instances, if not "
                    "--run-instance; prefix match, repeatable")
    ap.add_argument("--solo", action=argparse.BooleanOptionalAction,
                    default=True, help="single-player fights only (default)")
    ap.add_argument("--coop", action="store_true",
                    help="two-seat fights only (overrides --solo), one row "
                    "per seat per fight across lanes")
    ap.add_argument("--reactions", action="store_true",
                    help="add the reaction section: reactions, amplifier "
                    "bonus damage and reaction debuffs a turn, by type "
                    "(by team under --coop)")
    ap.add_argument("--feed", choices=("bot", "human", "all"), default="all")
    ap.add_argument("--cards-for", help="the group whose cards are listed "
                    "(default: the first non-base5 group)")
    ap.add_argument("--cards-merge-upgrades", action="store_true",
                    help="group Strike and Strike+ under Strike")
    ap.add_argument("--top", type=int, default=40,
                    help="card sources shown, by total damage (0 = all)")
    ap.add_argument("--dir", action="append", type=Path,
                    help="read this telemetry dir instead of the defaults; "
                    "repeatable")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--offers", action="store_true",
                    help="the card-offer report instead: what seats were "
                    "offered and took (tools/offer_report.py --help)")
    args = ap.parse_args(argv)

    try:  # card titles carry characters a cp1252 console cannot encode
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    dirs = args.dir or default_dirs()
    rows = load_fights(dirs)
    out = build(args, rows)
    cells = out.pop("_cells")
    if args.json:
        out["dirs"] = [str(d) for d in dirs]
        print(json.dumps(out, indent=1))
        return 0
    header = [f"telemetry_report: {out['records_kept']} of "
              f"{out['records_read']} fight records kept from {len(dirs)} "
              f"dir(s); solo={args.solo and not args.coop} "
              f"coop={args.coop} feed={args.feed} "
              f"since={args.since or '-'} until={args.until or '-'}"
              + (f" seeds={','.join(args.run_id)}" if args.run_id else "")
              + (f" run_instance={','.join(args.run_instance)}"
                 if args.run_instance else "")
              + (f" baseline_run_instance="
                 f"{','.join(args.baseline_run_instance)}"
                 if args.baseline_run_instance else ""),
              "note: reactions_by_turn is a running total (use its last "
              "entry or reactions_by_type, never a sum); co-op rows before "
              "2026-08-30 (EB-156) carry board totals per seat",
              "groups: " + ", ".join(f"{g} {n}" for g, n in
                                     out["groups"].items())]
    print(render(cells, out["comparison"], out["cards"], out["cards_for"],
                 header, args.top, out.get("reactions")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
