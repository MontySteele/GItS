"""Grade `KLEESPARK-W1`'s four slots off a finished blind-play session.

Mechanical only. Every slot is computed from artefacts the run wrote by
itself -- the rendered observation pages (`turn-*/prompt.md`), the tester's own
per-turn reply (`turn-*/reply.json`), and `transcript.jsonl` -- and nothing
here reads a judgement or a design claim. Guardrail-7 and R217 G ride on the
output: these are counts about one fight, not a comparison and not evidence
about balance.

    python review/qa/klee-sparks-wholefight-1/grade.py <log_dir> [--json out]

The slate is `review/active/klee-sparks-2026-08-29.md` sec 12.3:

  W1  a named Spark trade-off on >= 3 combat turns   (1-2 SPLIT, 0 MISS)
  W2  Sparks spent / Sparks generated >= 0.5         (0.25-0.5 SPLIT, < MISS)
  W3  >= 1 affordable sink deliberately skipped      (0 MISS, no SPLIT)
  W4  >= 70% of successful plays are Attacks         (50-70 SPLIT, < MISS)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# The granted ladder, sec 12.2. Printed name -> Spark price.
PRICED = {
    "Ka-pow!": 1,
    "Fwoosh!": 1,
    "Tinder Toss": 1,
    "Bang Bang!": 2,
    "Firework Finale": 3,
}
GENERATOR = "Powder Pop"

# W1's hold vocabulary. A trade-off is NAMED when the tester's own sentence
# either weighs two priced rows against each other or says out loud that it is
# keeping the bank for something. Both halves are required to mention a priced
# row: a sentence about saving energy is not a sentence about Sparks.
HOLD = re.compile(
    r"\b(hold|holding|held|save|saving|saved|keep|keeping|bank|banked|"
    r"later|next turn|preserve|preserving|reserve|wait|store|storing|"
    r"instead of|rather than|trade|trade-?off|afford|cannot afford|"
    r"can't afford|too expensive|not enough spark)\b", re.I)

BANK = re.compile(r"^\s*-\s*Spark[:\s]\s*(\d+)", re.I | re.M)
CARD = re.compile(r"^\s*-\s+\*\*(.+?)\*\*(?:\s+\(upgraded\))?"
                  r"(?:\s+—\s+(.*))?$", re.M)
COMBAT = re.compile(r"^#\s+Battle", re.I | re.M)


def _pages(log_dir: Path) -> list[dict]:
    """One row per answered turn, in order, with everything a slot needs."""
    rows = []
    for prompt in sorted(log_dir.glob("turn-*/prompt.md")):
        turn = prompt.parent.name
        page = prompt.read_text(encoding="utf-8", errors="replace")
        reply_path = prompt.parent / "reply.json"
        reply = {}
        if reply_path.is_file():
            try:
                reply = json.loads(reply_path.read_text(encoding="utf-8"))
            except ValueError:
                reply = {}
        bank = BANK.search(page)
        hand = _hand(page)
        combat = bool(COMBAT.search(page))
        # AN ABSENT SPARK LINE ON A COMBAT PAGE IS A BANK OF ZERO, NOT AN
        # UNREAD ONE. The game prints a power only while it is held, so a
        # spent-out bank prints nothing at all -- seen on this run's very
        # first combat page. Reading that as "unread" would drop every
        # return-to-zero out of W2's deltas, which is exactly the movement
        # the slot is about.
        value = int(bank.group(1)) if bank else (0 if combat else None)
        rows.append({
            "turn": turn,
            "combat": combat or bank is not None,
            "bank": value,
            "hand": hand,
            "command": str(reply.get("command") or "").strip(),
            "thinking": str(reply.get("thinking") or "").strip(),
        })
    return rows


def _hand(page: str) -> list[tuple[str, str]]:
    """`(title, kind)` for every card face the page prints under Your hand.

    The render prints a face as `- **Title** — cost N, kind`. Only the hand
    section is read: a reward screen prints faces too and a card the tester
    cannot play is not a skipped sink.
    """
    head = re.search(r"^#+\s*Your hand.*$", page, re.I | re.M)
    if not head:
        return []
    rest = page[head.end():]
    nxt = re.search(r"^#+\s", rest, re.M)
    block = rest[:nxt.start()] if nxt else rest
    out = []
    for m in CARD.finditer(block):
        title = m.group(1).strip()
        tail = (m.group(2) or "").lower()
        kind = ""
        for k in ("attack", "skill", "power", "status", "curse"):
            if k in tail:
                kind = k
                break
        out.append((title, kind))
    return out


def _kind_index(rows: list[dict]) -> dict[str, str]:
    """Printed title -> the kind the page printed for it, anywhere it appeared."""
    idx: dict[str, str] = {}
    for r in rows:
        for title, kind in r["hand"]:
            if kind and title not in idx:
                idx[title] = kind
    return idx


def _bare(title: str) -> str:
    """A printed title with `EB-177`'s repeat number taken back off."""
    return re.sub(r"\s*\(\d+\)\s*$", "", title).strip()


def w1(rows: list[dict]) -> dict:
    hits = []
    for r in rows:
        if not r["combat"] or not r["thinking"]:
            continue
        text = r["thinking"]
        named = [n for n in PRICED if n.lower() in text.lower()]
        if not named:
            continue
        if len(named) >= 2 or HOLD.search(text):
            hits.append({"turn": r["turn"], "named": named,
                         "thinking": text})
    n = len(hits)
    grade = "PREDICTED" if n >= 3 else ("SPLIT" if n >= 1 else "MISS")
    return {"slot": "W1", "value": n, "grade": grade, "hits": hits}


def w2(rows: list[dict]) -> dict:
    banks = [(r["turn"], r["bank"]) for r in rows if r["bank"] is not None]
    gen = spent = 0
    deltas = []
    for (t0, a), (t1, b) in zip(banks, banks[1:]):
        d = b - a
        if d:
            deltas.append({"from": t0, "to": t1, "delta": d})
        if d > 0:
            gen += d
        else:
            spent += -d
    ratio = (spent / gen) if gen else None
    if ratio is None:
        grade = "MISS"
    elif ratio >= 0.5:
        grade = "PREDICTED"
    elif ratio >= 0.25:
        grade = "SPLIT"
    else:
        grade = "MISS"
    return {"slot": "W2", "generated": gen, "spent": spent,
            "ratio": ratio, "grade": grade, "banks": banks,
            "deltas": deltas}


def w3(rows: list[dict]) -> dict:
    hits = []
    for r in rows:
        if r["command"].lower() != "end turn" or r["bank"] is None:
            continue
        afford = [(_bare(t), PRICED[_bare(t)]) for t, _ in r["hand"]
                  if _bare(t) in PRICED and PRICED[_bare(t)] <= r["bank"]]
        if afford:
            hits.append({"turn": r["turn"], "bank": r["bank"],
                         "affordable": afford, "thinking": r["thinking"]})
    n = len(hits)
    return {"slot": "W3", "value": n,
            "grade": "PREDICTED" if n >= 1 else "MISS", "hits": hits}


def w4(rows: list[dict], transcript: Path) -> dict:
    idx = _kind_index(rows)
    plays = []
    if transcript.is_file():
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
            raw = (blob.get("card") if isinstance(blob, dict)
                   else blob) or ""
            printed = _bare(str(raw))
            plays.append({"title": printed,
                          "kind": idx.get(printed, "")
                          or idx.get(_bare(printed), "")})
    total = len(plays)
    attacks = sum(1 for p in plays if p["kind"] == "attack")
    unknown = [p["title"] for p in plays if not p["kind"]]
    pct = (attacks / total * 100) if total else None
    if pct is None:
        grade = "MISS"
    elif pct >= 70:
        grade = "PREDICTED"
    elif pct >= 50:
        grade = "SPLIT"
    else:
        grade = "MISS"
    return {"slot": "W4", "plays": total, "attacks": attacks,
            "pct": pct, "grade": grade, "unknown_kind": unknown,
            "played": plays}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("log_dir")
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)
    log_dir = Path(args.log_dir)
    rows = _pages(log_dir)
    out = {
        "log_dir": str(log_dir),
        "turns": len(rows),
        "combat_turns": sum(1 for r in rows if r["combat"]),
        "W1": w1(rows),
        "W2": w2(rows),
        "W3": w3(rows),
        "W4": w4(rows, log_dir / "transcript.jsonl"),
    }
    for slot in ("W1", "W2", "W3", "W4"):
        s = out[slot]
        print(f"{slot}: {s['grade']}  " + json.dumps(
            {k: v for k, v in s.items()
             if k in ("value", "ratio", "generated", "spent", "plays",
                      "attacks", "pct")}))
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=1, default=str)
                                   + "\n", encoding="utf-8")
        print(f"json: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
