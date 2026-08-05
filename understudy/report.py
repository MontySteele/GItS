"""The morning report. Defects first, then outliers, then curves. No LLM.

    python -m understudy.report                 # the most recent soak
    python -m understudy.report 20260804-231500 # a named one

WHY DEFECTS COME FIRST, AND WHY THAT IS AN ORDERING DECISION
This report is read at 8am by someone deciding whether last night's build is
worth their evening. The brief's acceptance bar for P1 is "a broken build is
caught by the soak, not by [USER]'s evening" -- so the first thing on the page
is what broke, with the seed and the floor beside it. Aggregate curves are
below the fold on purpose: a page that opens with a winrate invites the reader
to read a winrate, and there is no winrate here that means anything.

WHAT EVERY NUMBER BELOW IS (Guardrail-7, restated where it will be read)
A bot-limited floor. policy_v1 is a heuristic; the seeds are read-back rather
than chosen (R95); a JSON-state agent cannot see the screen. The completion
rate is "how often this bot finished", not "how hard the game is", and the two
are not the same claim wearing different clothes.

Narrative reports written by a model are Phase 2. This is arithmetic and
sorting, so it runs on a fresh clone with no key and no network.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).resolve().parent / "logs" / "soak"

GUARDRAIL = (
    "Every number in this report is a BOT-LIMITED FLOOR (Guardrail-7). "
    "policy_v1 is a heuristic with declared reductions, the seeds are "
    "read-back rather than chosen (R95), and a JSON-state agent cannot see "
    "the screen. Nothing here is evidence about balance, difficulty, fun or "
    "legibility, and no figure below may be quoted against a floor or "
    "compared to another build's soak.")


def latest_stamp() -> str | None:
    stamps = sorted(p.name[len("soak-"):-len("-index.json")]
                    for p in LOG_DIR.glob("soak-*-index.json"))
    return stamps[-1] if stamps else None


def load(stamp: str) -> dict[str, Any]:
    p = LOG_DIR / f"soak-{stamp}-index.json"
    if not p.exists():
        raise SystemExit(f"no soak index at {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def read_run_log(stamp: str, run_index: int) -> list[dict]:
    p = LOG_DIR / f"soak-{stamp}-run{run_index:03d}.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _median(xs: list[float]) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def render(stamp: str | None = None) -> str:
    stamp = stamp or latest_stamp()
    if stamp is None:
        return "no soak logs found under " + str(LOG_DIR)
    idx = load(stamp)
    runs = idx.get("runs") or []
    fights: list[dict] = []
    defects: list[dict] = []
    forced: list[dict] = []
    for r in runs:
        for rec in read_run_log(stamp, r["run"]):
            kind = rec.get("record")
            if kind == "fight":
                rec["_run"] = r["run"]
                rec["_seed"] = r.get("seed")
                fights.append(rec)
            elif kind == "defect":
                defects.append(rec)
            elif kind == "forced_default":
                forced.append(rec)

    L: list[str] = []
    a = L.append
    a(f"# Understudy soak {stamp} -- morning report")
    a("")
    a(f"`{idx.get('policy')}` | character `{idx.get('character')}` | "
      f"{len(runs)} of {idx.get('requested_runs')} requested runs completed")
    a("")
    a("> " + GUARDRAIL.replace("\n", " "))
    a("")

    # ------------------------------------------------------------ defects
    a("## 1. Defects")
    a("")
    if idx.get("stopped_on"):
        a(f"**SOAK HALTED.** Two harness-side `{idx['stopped_on']}` failures "
          f"fired the stop-and-surface rule: that shape is the instrument "
          f"failing, not the build. Fix the harness before reading anything "
          f"below.")
        a("")
    if not defects:
        a("None. No crash, no soft-lock, no unhandled overlay, no stalled "
          "state across every run in this soak.")
    else:
        a(f"**{len(defects)}** filed. Each row is reproducible from its seed "
          f"and carries a state dump in the run log.")
        a("")
        a("| run | seed | kind | act/floor | screen | detail |")
        a("|---|---|---|---|---|---|")
        for d in defects:
            a(f"| {d.get('run')} | `{d.get('seed')}` | **{d.get('kind')}** | "
              f"{d.get('act')}/{d.get('floor')} | {d.get('state_type')} | "
              f"{str(d.get('detail'))[:160]} |")
    a("")
    if forced:
        by_screen: dict[str, int] = {}
        for f in forced:
            by_screen[str(f.get("state_type"))] = \
                by_screen.get(str(f.get("state_type")), 0) + 1
        a(f"**{len(forced)} forced defaults** -- screens policy_v1 declined "
          f"and the driver walked past to keep the run moving. These are not "
          f"defects, but every one is a decision nobody made: "
          + ", ".join(f"`{k}` x{v}" for k, v in sorted(by_screen.items())))
        a("")

    # ------------------------------------------------------------ outliers
    a("## 2. Runs, and the outliers among them")
    a("")
    a("| run | seed | outcome | act/floor | fights | actions | wall s |")
    a("|---|---|---|---|---|---|---|")
    for r in runs:
        a(f"| {r['run']} | `{r.get('seed')}` | {r.get('outcome')} | "
          f"{r.get('final_act')}/{r.get('final_floor')} | {r.get('fights')} | "
          f"{r.get('actions')} | {r.get('wall_s')} |")
    a("")
    depths = [r.get("final_floor") or 0 for r in runs]
    if depths and len(set(depths)) > 1:
        lo, hi = min(depths), max(depths)
        a(f"Depth spread: floor {lo} to floor {hi}, median "
          f"{_median([float(d) for d in depths]):.0f}. The shallowest and "
          f"deepest runs are the two worth opening by hand -- one shows what "
          f"kills this policy, the other how far it gets when nothing does.")
        a("")

    # ------------------------------------------------------------- curves
    a("## 3. Aggregate curves")
    a("")
    if not fights:
        a("No fight telemetry recorded.")
        a("")
        return "\n".join(L)

    a(f"{len(fights)} fights across {len(runs)} runs.")
    a("")
    a("### HP lost per fight, by floor")
    a("")
    by_floor: dict[int, list[dict]] = {}
    for f in fights:
        by_floor.setdefault(int(f.get("floor") or 0), []).append(f)
    a("| floor | fights | median HP lost | median turns | median incoming/turn |")
    a("|---|---|---|---|---|")
    for floor in sorted(by_floor):
        fs = by_floor[floor]
        inc = [i[1] for f in fs for i in (f.get("incoming_by_turn") or [])
               if isinstance(i, list) and len(i) > 1 and i[1]]
        a(f"| {floor} | {len(fs)} | "
          f"{_median([float(f.get('hp_lost') or 0) for f in fs]):.0f} | "
          f"{_median([float(f.get('turns') or 0) for f in fs]):.0f} | "
          f"{_median([float(x) for x in inc]):.0f} |")
    a("")

    a("### Damage by source (attributed to the play that caused it)")
    a("")
    src: dict[str, float] = {}
    plays: dict[str, int] = {}
    for f in fights:
        for k, v in (f.get("damage_by_source") or {}).items():
            src[k] = src.get(k, 0.0) + float(v)
        for entry in f.get("cards_played") or []:
            if isinstance(entry, list) and len(entry) > 1:
                plays[str(entry[1])] = plays.get(str(entry[1]), 0) + 1
    total = sum(src.values()) or 1.0
    a("| source | damage | share | plays | per play |")
    a("|---|---|---|---|---|")
    for k, v in sorted(src.items(), key=lambda kv: -kv[1])[:20]:
        n = plays.get(k, 0)
        a(f"| {k} | {v:.0f} | {100 * v / total:.1f}% | {n} | "
          f"{(v / n) if n else 0:.1f} |")
    a("")
    silent = sorted(k for k, n in plays.items() if k not in src and n >= 3)
    if silent:
        a(f"Played but never attributed damage ({len(silent)}): "
          + ", ".join(f"`{k}`" for k in silent[:25])
          + ". Expected for blocks, powers and draw -- read this list for the "
            "ATTACK that is missing from the table above.")
        a("")

    a("### Cards played per turn")
    a("")
    turns = sum(int(f.get("turns") or 0) for f in fights)
    cards = sum(int(f.get("n_cards_played") or 0) for f in fights)
    a(f"{cards} plays over {turns} recorded turns "
      f"= {cards / max(1, turns):.2f} per turn.")
    a("")
    a("---")
    a("")
    a("Instrument: `understudy/soak.py` (policy_v1, R93). Logs: "
      f"`understudy/logs/soak/soak-{stamp}-*.jsonl` (gitignored). Schema: "
      "`understudy/README.md`.")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    print(render(argv[0] if argv else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
