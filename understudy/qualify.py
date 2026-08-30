"""M62 (5): THE REQUALIFICATION BATTERY — can this seat still read a board?

A local model is a FILE. It is swapped, requantised, re-served with different
flags, and none of those events announce themselves in a round's output: the
seat keeps answering, the forms keep parsing, and the reading quietly gets
worse. `KLEESPARK-R1` is what that looks like from the far end — 4 of 8
verdict agreement, five `intent_insensitive` refusals, one misread and two
lines the bridge could not play — discovered after a round of game time.

So the seat gets a fixed battery it can be run against BEFORE a round, on
boards that are already sealed. Three categories, each one a failure this
funnel has actually seen:

  * **targets** (EB-203) — a card whose printed effects aim at ONE enemy must
    carry a target, and a card that aims at nobody must not. Both directions,
    because "always name an enemy" passes the first half and is not literacy.
  * **costs** (EB-186, Klee slice 1 round 1) — the reader must not call a card
    free that the packet prints a cost for. `understudy/misreads.py` is the
    check, unchanged and shared, so a battery pass means the same thing a
    round's post-read check means.
  * **intent** (R213's fourth question) — the enemy's telegraph must be part
    of the decision. Scored with the `intent_insensitive` falsifier itself,
    for the same reason.

WHAT IT DOES NOT DECIDE. **There is no pass mark here.** The scorecard prints
per-category counts and the per-item reasons and stops; the threshold that
would qualify or disqualify a seat is `M62`'s and is [USER]'s to fix. A tool
that picked its own threshold would be answering the open question in the act
of instrumenting it.

WHERE THE BOARDS COME FROM. `understudy/battery/battery.yaml`, and every item
names a SEALED packet under `review/qa/` from a closed round — `kokomi-slice2`,
`klee-slice1-r3`, `klee-sparks-r1`. No new board is staged and no game is
launched: a requalification that cost a launch would be run rarely, which is
the opposite of what it is for. The packets are read-only here; nothing is
written into a closed turn directory (R101b), and a battery read lands in its
own output directory.

THE ONE ITEM SHAPE THE SEALED RECORD CANNOT GIVE US, STATED RATHER THAN
SMOOTHED. The intent category asks for *two packets identical except the
enemy intent*. No such pair exists in the record: every matched pair this
funnel has run differs in the ARM under test, not in the telegraph. So the
category is scored one packet at a time with the shipped `intent_insensitive`
detector, which is the same question asked of a single board. When a
telegraph-only pair is staged, the item shape widens; until then this is what
the sealed record can honestly support.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import yaml

REPO = Path(__file__).resolve().parents[1]
QA_DIR = REPO / "review" / "qa"
BATTERY_DIR = Path(__file__).resolve().parent / "battery"
BATTERY_FILE = BATTERY_DIR / "battery.yaml"

CATEGORIES: tuple[str, ...] = ("targets", "costs", "intent")

MIN_ITEMS_PER_CATEGORY = 6

THRESHOLD_NOTE = (
    "there is no pass mark in this file. The per-item and per-category counts "
    "are the output; the threshold that qualifies or disqualifies a seat is "
    "QUEUE M62 and is [USER]'s")


class BatteryError(RuntimeError):
    """The battery file is not a battery."""


@dataclass
class Item:
    id: str
    category: str
    turn_id: str
    why: str = ""


def load_battery(path: Path | None = None) -> list[Item]:
    p = Path(path or BATTERY_FILE)
    blob = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(blob, Mapping) or not isinstance(blob.get("items"), list):
        raise BatteryError(f"{p}: a battery is a mapping with an 'items' list")
    items: list[Item] = []
    for i, raw in enumerate(blob["items"]):
        if not isinstance(raw, Mapping):
            raise BatteryError(f"{p}: item {i} is a mapping")
        for key in ("id", "category", "turn_id"):
            if not raw.get(key):
                raise BatteryError(f"{p}: item {i} has no {key!r}")
        if str(raw["category"]) not in CATEGORIES:
            raise BatteryError(
                f"{p}: item {raw['id']!r} names category "
                f"{raw['category']!r}; one of: " + ", ".join(CATEGORIES))
        items.append(Item(id=str(raw["id"]), category=str(raw["category"]),
                          turn_id=str(raw["turn_id"]),
                          why=str(raw.get("why") or "")))
    return items


def coverage(items: Sequence[Item]) -> dict[str, int]:
    return {cat: sum(1 for i in items if i.category == cat)
            for cat in CATEGORIES}


def thin_categories(items: Sequence[Item]) -> list[str]:
    """Categories below the floor. The battery's own shape check."""
    return [cat for cat, n in coverage(items).items()
            if n < MIN_ITEMS_PER_CATEGORY]


# ------------------------------------------------------------- the scoring --

def score_targets(form: Mapping[str, Any], turn_dir: Path) -> tuple[bool, str]:
    """Both directions: an aimed card carries a target, and nothing else does."""
    from understudy import resource_order, targeting
    index = resource_order.card_index()
    line = list(form.get("chosen_line") or [])
    if not line:
        return False, "the form names no cards played"
    missing = targeting.findings(line, index=index)
    extra = []
    for i, play in enumerate(line, 1):
        title = str(play.get("card") or "")
        row = index.get(resource_order.normalise(title))
        if row is None:
            continue
        if targeting.needs_target(row, play.get("choose")):
            continue
        if str(play.get("target") or "").strip():
            extra.append(f"play {i} ({title}) aims at nobody and named "
                         f"{play['target']!r}")
    if missing:
        return False, "; ".join(h["why"].split(" -- ")[0] for h in missing)
    if extra:
        return False, "; ".join(extra)
    return True, (f"every one of {len(line)} play(s) carried a target exactly "
                  f"when its printed effects need one")


def score_costs(form: Mapping[str, Any], turn_dir: Path) -> tuple[bool, str]:
    """`misreads.free_card_misreads`, the shipped check, on the reader's prose."""
    from understudy import misreads, staged_turn
    packet = turn_dir / "packet.md"
    if not packet.is_file():
        return False, "no packet.md for this item"
    hits = misreads.free_card_misreads(
        packet.read_text(encoding="utf-8"),
        misreads.prose_of(dict(form), staged_turn.QUESTIONS))
    if hits:
        return False, "; ".join(hits)
    return True, "no card the packet prices was called free"


def score_intent(form: Mapping[str, Any], turn_dir: Path) -> tuple[bool, str]:
    """The `intent_insensitive` falsifier itself, on one board."""
    from understudy import staged_turn
    if (form.get("q4_changed") is False
            or staged_turn.is_negative(form.get("q4_different_intent"))):
        return False, ("intent_insensitive: a different enemy intent would "
                       "not have changed the line")
    return True, "the telegraph is part of the decision"


SCORERS: dict[str, Callable[[Mapping[str, Any], Path], tuple[bool, str]]] = {
    "targets": score_targets,
    "costs": score_costs,
    "intent": score_intent,
}


# -------------------------------------------------------------- the runner --

def run_battery(items: Sequence[Item], *,
                reader: Callable[[Item], Mapping[str, Any] | None],
                qa_dir: Path | None = None,
                seat_id: str = "") -> dict[str, Any]:
    """Score every item. `reader` returns the seat's form for one item.

    Injected rather than called: the locks run this against a fake seat, and a
    battery that could only be exercised with a 27B model on a loopback port
    would be a battery nobody runs in CI.
    """
    base = qa_dir or QA_DIR
    rows: list[dict[str, Any]] = []
    for item in items:
        turn_dir = base / item.turn_id
        try:
            form = reader(item)
        except Exception as exc:                              # noqa: BLE001
            rows.append({"item": item.id, "category": item.category,
                         "turn_id": item.turn_id, "passed": False,
                         "why": f"the seat raised {type(exc).__name__}: {exc}"})
            continue
        if not form:
            rows.append({"item": item.id, "category": item.category,
                         "turn_id": item.turn_id, "passed": False,
                         "why": ("the seat filed no form -- a refusal is a "
                                 "failed item, never a skipped one")})
            continue
        ok, why = SCORERS[item.category](form, turn_dir)
        rows.append({"item": item.id, "category": item.category,
                     "turn_id": item.turn_id, "passed": bool(ok), "why": why})

    per_category = {
        cat: {"items": sum(1 for r in rows if r["category"] == cat),
              "passed": sum(1 for r in rows
                            if r["category"] == cat and r["passed"])}
        for cat in CATEGORIES}
    return {
        "seat": seat_id,
        "items": rows,
        "per_category": per_category,
        "total": {"items": len(rows),
                  "passed": sum(1 for r in rows if r["passed"])},
        "threshold": None,
        "threshold_owner": THRESHOLD_NOTE,
        "thin_categories": thin_categories(items),
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def one_line(scorecard: Mapping[str, Any]) -> str:
    """The summary a person reads. Counts only; it grades nothing."""
    parts = [f"{cat} {v['passed']}/{v['items']}"
             for cat, v in scorecard["per_category"].items()]
    total = scorecard["total"]
    return (f"qualify: {total['passed']}/{total['items']} items "
            f"({', '.join(parts)}) -- no pass mark here; the threshold is M62")


def write_scorecard(scorecard: Mapping[str, Any],
                    out: Path | None = None) -> Path:
    path = Path(out or (REPO / "review" / "qa" / "qualify-scorecard.json"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scorecard, indent=1) + "\n", encoding="utf-8")
    return path
