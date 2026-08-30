"""Grade `KLEESPARK-W3`'s slate off a finished blind-play session.

COMMITTED BEFORE THE RUN. Mechanical only. Every slot is computed from
artefacts the run wrote by itself -- the rendered observation pages
(`turn-*/prompt.md`), the tester's own per-turn reply (`turn-*/reply.json`),
and `transcript.jsonl` -- and nothing here reads a design judgement.
Guardrail-7 and R217 G ride on the output: these are counts about one capped
batch of fights, not a comparison and not evidence about balance.

    python review/qa/blindplay/kleespark-w3/grade.py <log_dir> [--json out]

The slate is `review/active/klee-sparks-2026-08-29.md` sec 18.4. `W1''`-`W5''`
are `W2`'s `W1'`-`W5'` at their published thresholds, on this deck; `W6''` is
new and is the only slot `KLEESPARK-S1` hands a number to.

  W1'' >= 3 combat turns where the bank affords TWO distinct priced titles at
       once and at least one of them is a NON-DAMAGE sink   (1-2 SPLIT, 0 MISS;
       UNREACHED only if the session saw zero combat pages)
  W2'' >= 1 successful play of a non-damage sink on a turn where a damage sink
       of price <= it was also affordable                   (0 MISS; UNREACHED
       if no page ever posed that pair)
  W3'' >= 1 `end turn` with an affordable sink in hand AND the recorded
       sentence names what the bank is being kept for       (0 MISS; UNREACHED
       if W1'' is MISS -- sec 14.4 condition 1)
  W4'' UNREACHED BY CONSTRUCTION (no redesigned price-3 rung was built).
       The one price-3 face in this deck is counted, ungraded.
  W5'' the attack share -- RECORDED, NOT GRADED.
  W6'' median PER-FIGHT PEAK printed Spark bank >= 2 -- a FLOOR relation
       against `S1`'s sim median of 5.0, never an equality (median 1 SPLIT,
       median 0 MISS; UNREACHED only if the session saw zero combat pages).

A FIGHT, for `W6''`, is a maximal run of CONSECUTIVE combat pages in turn
order. The blind feed has no fight id and the driver's records are prose, so
the page sequence is the only mechanical boundary there is; a fight the
tester left and came back to inside one combat does not exist, because
leaving a combat is leaving the fight.

AFFORDABLE, once, for the whole slate (sec 18.4, taken from sec 16.4
unchanged): printed Spark price <= the printed Spark bank AND printed Energy
cost <= the printed current Energy.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# The granted deck, sec 18.2. Printed name -> Spark price. The MAKERS carry no
# price and are not in either map: a maker is never an affordable "use" of the
# bank, and counting one as a sink would inflate `W1''` by construction.
DAMAGE_SINKS = {
    "Ka-pow!": 1,
}
NONDAMAGE_SINKS = {
    "Set It Off": 2,
    "Dig In": 2,
    "Powder Smoke": 2,
    "Rummage": 3,
}
PRICED = {**DAMAGE_SINKS, **NONDAMAGE_SINKS}
MAKERS = ("Powder Pop", "Skip and Hop", "Warm Glow", "Snap!", "Hot Hands",
          "All of My Treasures!", "Da-da-da!")
PRICE_3 = [n for n, p in PRICED.items() if p == 3]

# `W3'''`s hold vocabulary, sec 14.4 condition 2, IDENTICAL to `W2`'s grader.
# BOTH halves are required: the sentence must read as a deliberate keep AND
# must name a priced title or the bank itself, so a player who simply forgot
# the card in hand does not score as a player who held.
HOLD = re.compile(
    r"\b(hold|holding|held|save|saving|saved|keep|keeping|kept|"
    r"preserve|preserving|preserved|reserve|reserving|bank|banked|"
    r"store|storing|stockpile|accumulate|build up|"
    r"next turn|later|future|for now|instead of|rather than|"
    r"wait|waiting|until)\b", re.I)
BANK_WORD = re.compile(r"\bsparks?\b", re.I)

BANK = re.compile(r"^\s*-\s*Spark[:\s]\s*(\d+)", re.I | re.M)
ENERGY = re.compile(r"^\s*-\s*Energy[:\s]\s*(\d+)\s*/", re.I | re.M)
CARD = re.compile(r"^\s*-\s+\*\*(.+?)\*\*(?:\s+\(upgraded\))?"
                  r"(?:\s+—\s+(.*))?$", re.M)
COST = re.compile(r"\bcost\s+(\d+)", re.I)
COMBAT = re.compile(r"^#\s+Battle", re.I | re.M)


def _bare(title: str) -> str:
    """A printed title with `EB-177`'s repeat number taken back off."""
    return re.sub(r"\s*\(\d+\)\s*$", "", title).strip()


def _hand(page: str) -> list[dict]:
    """Every card face the page prints under Your hand: title, kind, cost.

    Only the hand section is read: a reward screen prints faces too, and a
    card the tester cannot play is not a skipped sink.
    """
    head = re.search(r"^#+\s*Your hand.*$", page, re.I | re.M)
    if not head:
        return []
    rest = page[head.end():]
    nxt = re.search(r"^#+\s", rest, re.M)
    block = rest[:nxt.start()] if nxt else rest
    out = []
    for m in CARD.finditer(block):
        title = _bare(m.group(1))
        tail = (m.group(2) or "").lower()
        kind = ""
        for k in ("attack", "skill", "power", "status", "curse"):
            if k in tail:
                kind = k
                break
        cost = COST.search(tail)
        out.append({"title": title, "kind": kind,
                    "energy": int(cost.group(1)) if cost else None})
    return out


def _pages(log_dir: Path) -> list[dict]:
    """One row per answered turn, in order, with everything a slot needs."""
    rows = []
    for prompt in sorted(log_dir.glob("turn-*/prompt.md")):
        page = prompt.read_text(encoding="utf-8", errors="replace")
        reply_path = prompt.parent / "reply.json"
        reply = {}
        if reply_path.is_file():
            try:
                reply = json.loads(reply_path.read_text(encoding="utf-8"))
            except ValueError:
                reply = {}
        bank = BANK.search(page)
        energy = ENERGY.search(page)
        combat = bool(COMBAT.search(page))
        # AN ABSENT SPARK LINE ON A COMBAT PAGE IS A BANK OF ZERO, NOT AN
        # UNREAD ONE (`W1`'s and `W2`'s graders, same reason): the game prints
        # a power only while it is held, so a spent-out bank prints nothing.
        value = int(bank.group(1)) if bank else (0 if combat else None)
        rows.append({
            "turn": prompt.parent.name,
            "combat": combat,
            "bank": value,
            "energy": int(energy.group(1)) if energy else None,
            "hand": _hand(page),
            "command": str(reply.get("command") or "").strip(),
            "thinking": str(reply.get("thinking") or "").strip(),
        })
    return rows


def _affordable(row: dict) -> list[dict]:
    """The distinct priced titles in hand this page's bank and Energy pay for."""
    seen: dict[str, dict] = {}
    if row["bank"] is None:
        return []
    for card in row["hand"]:
        title = card["title"]
        if title not in PRICED or title in seen:
            continue
        price = PRICED[title]
        if price > row["bank"]:
            continue
        # Energy binds only where the page printed both numbers.
        if (card["energy"] is not None and row["energy"] is not None
                and card["energy"] > row["energy"]):
            continue
        seen[title] = {"title": title, "price": price,
                       "nondamage": title in NONDAMAGE_SINKS}
    return list(seen.values())


def w1(rows: list[dict]) -> dict:
    combat = [r for r in rows if r["combat"]]
    hits = []
    for r in combat:
        aff = _affordable(r)
        if len(aff) >= 2 and any(a["nondamage"] for a in aff):
            hits.append({"turn": r["turn"], "bank": r["bank"],
                         "energy": r["energy"],
                         "affordable": [a["title"] for a in aff]})
    n = len(hits)
    if not combat:
        grade = "UNREACHED"
    elif n >= 3:
        grade = "PREDICTED"
    elif n >= 1:
        grade = "SPLIT"
    else:
        grade = "MISS"
    return {"slot": "W1''", "value": n, "combat_pages": len(combat),
            "grade": grade, "hits": hits}


def w2(rows: list[dict]) -> dict:
    hits = []
    posed = []
    for r in rows:
        if not r["combat"]:
            continue
        aff = _affordable(r)
        nd = [a for a in aff if a["nondamage"]]
        dmg = [a for a in aff if not a["nondamage"]]
        if nd and dmg:
            posed.append(r["turn"])
        cmd = r["command"]
        m = re.match(r'^\s*play\s+"(.+?)"', cmd, re.I)
        if not m:
            continue
        played = _bare(m.group(1))
        if played not in NONDAMAGE_SINKS:
            continue
        rivals = [d["title"] for d in dmg
                  if d["price"] <= NONDAMAGE_SINKS[played]]
        if rivals:
            hits.append({"turn": r["turn"], "played": played,
                         "bank": r["bank"], "passed_over": rivals,
                         "thinking": r["thinking"]})
    n = len(hits)
    if not posed:
        grade = "UNREACHED"
    else:
        grade = "PREDICTED" if n >= 1 else "MISS"
    return {"slot": "W2''", "value": n, "grade": grade,
            "turns_that_posed_the_choice": posed, "hits": hits}


def w3(rows: list[dict], w1_grade: str) -> dict:
    bare = []
    named = []
    for r in rows:
        if r["command"].lower() != "end turn" or not r["combat"]:
            continue
        aff = _affordable(r)
        if not aff:
            continue
        entry = {"turn": r["turn"], "bank": r["bank"],
                 "affordable": [a["title"] for a in aff],
                 "thinking": r["thinking"]}
        bare.append(entry)
        text = r["thinking"]
        titles = [t for t in PRICED if t.lower() in text.lower()]
        if HOLD.search(text) and (titles or BANK_WORD.search(text)):
            entry = dict(entry, named=titles)
            named.append(entry)
    n = len(named)
    if w1_grade == "MISS":
        grade = "UNREACHED"
    else:
        grade = "PREDICTED" if n >= 1 else "MISS"
    return {"slot": "W3''", "value": n, "grade": grade,
            "bare_detector": len(bare), "bare_hits": bare, "hits": named}


def _plays(log_dir: Path, rows: list[dict]) -> list[dict]:
    idx: dict[str, str] = {}
    for r in rows:
        for card in r["hand"]:
            if card["kind"] and card["title"] not in idx:
                idx[card["title"]] = card["kind"]
    out = []
    transcript = log_dir / "transcript.jsonl"
    if not transcript.is_file():
        return out
    for line in transcript.read_text(encoding="utf-8",
                                     errors="replace").splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("kind") != "command" or not rec.get("ok"):
            continue
        if rec.get("verb") != "play":
            continue
        blob = rec.get("printed")
        raw = (blob.get("card") if isinstance(blob, dict) else blob) or ""
        title = _bare(str(raw))
        out.append({"title": title, "kind": idx.get(title, "")})
    return out


def w4(plays: list[dict]) -> dict:
    """UNREACHED BY CONSTRUCTION. The count is recorded, never graded."""
    bought = [p["title"] for p in plays if p["title"] in PRICE_3]
    return {"slot": "W4''", "grade": "UNREACHED",
            "why": "no redesigned price-3 rung was built (sec 14.4 cond 4; "
                   "R224 took option (5) migrate-only, Powder Keg unbuilt)",
            "price_3_faces_in_deck": PRICE_3,
            "price_3_plays_recorded_not_graded": bought}


def w5(plays: list[dict]) -> dict:
    """RECORDED, NOT GRADED (sec 14.4's fourth item)."""
    total = len(plays)
    attacks = sum(1 for p in plays if p["kind"] == "attack")
    unknown = [p["title"] for p in plays if not p["kind"]]
    return {"slot": "W5''", "grade": "NOT GRADED", "plays": total,
            "attacks": attacks,
            "pct": (attacks / total * 100) if total else None,
            "unknown_kind": unknown, "played": plays}


def _fights(rows: list[dict]) -> list[list[dict]]:
    """Maximal runs of CONSECUTIVE combat pages, in turn order."""
    out: list[list[dict]] = []
    current: list[dict] = []
    for r in rows:
        if r["combat"]:
            current.append(r)
        elif current:
            out.append(current)
            current = []
    if current:
        out.append(current)
    return out


def w6(rows: list[dict]) -> dict:
    """`S1`'s median per-fight peak bank, re-asked live as a FLOOR of 2."""
    fights = _fights(rows)
    peaks = [max(r["bank"] or 0 for r in f) for f in fights]
    if not peaks:
        return {"slot": "W6''", "grade": "UNREACHED", "fights": 0,
                "peaks": [], "median": None,
                "why": "the session recorded zero combat pages"}
    median = statistics.median(peaks)
    if median >= 2:
        grade = "PREDICTED"
    elif median >= 1:
        grade = "SPLIT"
    else:
        grade = "MISS"
    return {"slot": "W6''", "grade": grade, "fights": len(peaks),
            "peaks": peaks, "median": median,
            "pages_per_fight": [len(f) for f in fights],
            "sim_comparator_not_a_threshold": 5.0}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("log_dir")
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)
    log_dir = Path(args.log_dir)
    rows = _pages(log_dir)
    plays = _plays(log_dir, rows)
    s1 = w1(rows)
    out = {
        "log_dir": str(log_dir),
        "turns": len(rows),
        "combat_turns": sum(1 for r in rows if r["combat"]),
        "W1''": s1,
        "W2''": w2(rows),
        "W3''": w3(rows, s1["grade"]),
        "W4''": w4(plays),
        "W5''": w5(plays),
        "W6''": w6(rows),
    }
    for slot in ("W1''", "W2''", "W3''", "W4''", "W5''", "W6''"):
        s = out[slot]
        print(f"{slot}: {s['grade']}  " + json.dumps(
            {k: v for k, v in s.items()
             if k in ("value", "combat_pages", "bare_detector", "plays",
                      "attacks", "pct", "price_3_plays_recorded_not_graded",
                      "fights", "peaks", "median")}))
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=1, default=str)
                                   + "\n", encoding="utf-8")
        print(f"json: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
