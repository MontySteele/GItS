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
  * **costs** (EB-186, Klee slice 1 round 1; EB-211) — TWO halves since
    2026-08-30. The reader must not call a card free that the packet prints a
    cost for (`understudy/misreads.py`, the shipped check, unchanged and
    shared, so a battery pass means what a round's post-read check means) —
    **and** must carry a `price_ledger`: per play, the bank before, the price
    paid and the bank after, scored against the costs and the bank the PACKET
    prints. The second half is `EB-211`: with only the first, a form that
    never mentioned a price PASSED, and a 4-of-6 mark was satisfiable by
    SILENCE. **The six sealed `costs` items below were picked for the first
    half and are OWED a re-pick against the second — that is [USER]'s call
    and it is written up in `review/active/klee-sparks-2026-08-29.md`
    section 26, not taken here.**
  * **intent** (R213's fourth question) — the enemy's telegraph must be part
    of the decision. Scored with the `intent_insensitive` falsifier itself,
    for the same reason.

THE PASS MARK — R223 (2026-08-29), and it is [USER]'s, not this tool's. It
lives in the battery file's `threshold:` block, where it can be read beside
the boards it grades, and this module only applies it. [USER], answering the
pick list, verbatim: *"targets 6/6, others >= 4/6 works for me"* — so
**targets 6 of 6, costs 4 of 6, intent 4 of 6, and all three must hold.**
The mark is PER CATEGORY and there is no total: a seat cannot buy back the
blind spot that returned it (targets, `EB-203`) with the two categories it
still reads.

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
import re
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
    "the pass mark is R223 (2026-08-29) and is [USER]'s, carried in the "
    "battery file's threshold block: targets 6/6, costs 4/6, intent 4/6, all "
    "three holding. Per category, never a total")


class BatteryError(RuntimeError):
    """The battery file is not a battery."""


@dataclass
class Item:
    id: str
    category: str
    turn_id: str
    why: str = ""


@dataclass
class Threshold:
    """R223's pass mark: one required count per category, and no total."""

    per_category: dict[str, int]
    owner: str = ""

    def required(self, category: str) -> int:
        return self.per_category[category]


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


def load_threshold(path: Path | None = None) -> Threshold:
    """R223's pass mark, read from the same file as the boards it grades."""
    p = Path(path or BATTERY_FILE)
    blob = yaml.safe_load(p.read_text(encoding="utf-8"))
    raw = blob.get("threshold") if isinstance(blob, Mapping) else None
    if not isinstance(raw, Mapping):
        raise BatteryError(f"{p}: no 'threshold' block -- the pass mark is "
                           "R223's and a battery without one grades nothing")
    marks: dict[str, int] = {}
    for cat in CATEGORIES:
        if cat not in raw:
            raise BatteryError(f"{p}: the threshold names no mark for {cat!r}; "
                               "R223 is per category, so all of "
                               + ", ".join(CATEGORIES) + " are required")
        value = raw[cat]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise BatteryError(f"{p}: the {cat!r} mark is {value!r}; a mark is "
                               "a count of items, not a rate")
        marks[cat] = value
    for key in raw:
        if str(key) not in CATEGORIES and str(key) != "owner":
            raise BatteryError(f"{p}: the threshold names {key!r}, which is "
                               "not a category")
    return Threshold(per_category=marks, owner=str(raw.get("owner") or ""))


def unreachable_marks(items: Sequence[Item],
                      threshold: Threshold) -> list[str]:
    """Marks above what the battery can produce — R222 A's lesson as a check."""
    have = coverage(items)
    return [f"{cat} asks {threshold.required(cat)} of {have[cat]} item(s)"
            for cat in CATEGORIES if threshold.required(cat) > have[cat]]


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
    """Two halves: the "X is free" misread, and the PRICE LEDGER (`EB-211`).

    THE CATEGORY USED TO BE HALF A CHECK. It ran `free_card_misreads` over the
    reader's prose and PASSED on no hits, so a form that never mentioned a
    price passed `costs` and R223's mark of 4 of 6 was satisfiable by silence
    (`review/active/klee-sparks-2026-08-29.md` section 13.8, claim 3). Silence
    now FAILS: the reader states, per play and in the board's own printed
    numbers, the bank before, the price paid, and the bank after.

    WHAT IS CHECKED, AND ALL OF IT OFF THE PACKET. Nothing here opens a sheet;
    the question is whether the reading matches the page the reader was shown.

      * one ledger entry per play in `chosen_line`, in that order, naming the
        same printed titles;
      * `energy_price` equal to the `Cost:` the packet PRINTS for that card;
      * the first `energy_before` equal to the Energy the packet prints, and
        every later one equal to the previous `energy_after` -- the chain,
        which is what a bank IS;
      * `energy_after == energy_before - energy_price`, RELAXED to
        `>= energy_before - energy_price` for a card whose printed body says
        it gains or refunds Energy (`EB-238`'s Pounding Surprise class): a
        card that hands Energy back inside the turn is not a reader's
        arithmetic error, and a check that called it one would be exactly the
        false FAIL `misreads.py` refuses to ship;
      * the Spark half on the same rules where the packet PRINTS a Spark bank
        -- chain, never negative -- and required NULL where it does not. The
        packet prints a Spark price in a card's own prose rather than as a
        number of its own, so `spark_price` is not checked against a printed
        value; the bank it moves is.

    A ledger longer or shorter than the line, an entry out of order, a
    non-integer where an integer is required: each is a FAIL naming the play.
    """
    from understudy import misreads, staged_turn
    packet_path = turn_dir / "packet.md"
    if not packet_path.is_file():
        return False, "no packet.md for this item"
    packet = packet_path.read_text(encoding="utf-8")

    hits = misreads.free_card_misreads(
        packet, misreads.prose_of(dict(form), staged_turn.QUESTIONS))
    if hits:
        return False, "; ".join(hits)

    line = list(form.get("chosen_line") or [])
    if not line:
        return False, "the form names no cards played"
    ledger = form.get("price_ledger")
    if not isinstance(ledger, list) or not ledger:
        return False, ("the form carries no `price_ledger` -- it is silent on "
                       "every price, and silence is not a reading of the "
                       "board's costs (EB-211)")
    if len(ledger) != len(line):
        return False, (f"the ledger has {len(ledger)} entr(ies) for a line of "
                       f"{len(line)} play(s); one per play, in order")

    costs = misreads.printed_costs(packet)
    banks = misreads.printed_banks(packet)
    problems: list[str] = []
    prev_energy = banks.get("energy")
    spark_printed = banks.get("spark")
    prev_spark = spark_printed

    for i, (play, entry) in enumerate(zip(line, ledger), 1):
        title = str(play.get("card") or "")
        where = f"play {i} ({title})"
        if not isinstance(entry, Mapping):
            problems.append(f"{where}: the ledger entry is not an object")
            continue
        if (str(entry.get("card") or "").strip().casefold()
                != title.strip().casefold()):
            problems.append(
                f"{where}: the ledger names {entry.get('card')!r} here -- one "
                f"entry per play, in the line's own order")
            continue
        nums = {k: entry.get(k) for k in
                ("energy_before", "energy_price", "energy_after")}
        bad = [k for k, v in nums.items()
               if not isinstance(v, int) or isinstance(v, bool)]
        if bad:
            problems.append(f"{where}: {', '.join(sorted(bad))} must be a "
                            f"whole number of Energy")
            continue
        printed = next((v for k, v in costs.items()
                        if k.casefold() == title.strip().casefold()), None)
        if printed is not None and nums["energy_price"] != printed:
            problems.append(f"{where}: the ledger pays {nums['energy_price']}, "
                            f"the packet prints Cost: {printed}")
        if prev_energy is not None and nums["energy_before"] != prev_energy:
            problems.append(
                f"{where}: the bank enters at {nums['energy_before']} where "
                f"the board left it at {prev_energy}")
        spent = nums["energy_before"] - nums["energy_price"]
        # The relaxation is keyed to an ENERGY gain and nothing else. "Gain 5
        # Block" is most Skills in the game, and matching it would relax the
        # arithmetic on nearly every board -- which is the check not existing.
        body = misreads.printed_body(packet, title).casefold()
        gains = bool(re.search(r"(?:gain|regain)\s+\d*\s*energy|refund"
                               r"|energy back", body))
        if nums["energy_after"] < spent or (nums["energy_after"] != spent
                                            and not gains):
            problems.append(
                f"{where}: {nums['energy_before']} - {nums['energy_price']} "
                f"is {spent}, and the ledger leaves the bank at "
                f"{nums['energy_after']}")
        prev_energy = nums["energy_after"]

        sk = {k: entry.get(k) for k in
              ("spark_before", "spark_price", "spark_after")}
        if spark_printed is None:
            if any(v is not None for v in sk.values()):
                problems.append(f"{where}: the packet prints no Spark bank, "
                                f"so the Spark half of the entry is null")
            continue
        bad = [k for k, v in sk.items()
               if not isinstance(v, int) or isinstance(v, bool)]
        if bad:
            problems.append(f"{where}: the packet prints a Spark bank, so "
                            f"{', '.join(sorted(bad))} is a whole number")
            continue
        if prev_spark is not None and sk["spark_before"] != prev_spark:
            problems.append(
                f"{where}: Spark enters at {sk['spark_before']} where the "
                f"board left it at {prev_spark}")
        if sk["spark_after"] < 0 or sk["spark_price"] < 0:
            problems.append(f"{where}: a Spark bank does not go negative")
        prev_spark = sk["spark_after"]

    if problems:
        return False, "; ".join(problems)
    return True, (f"no card the packet prices was called free, and the ledger "
                  f"prices all {len(line)} play(s) against the printed costs "
                  f"and the printed bank")


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
                seat_id: str = "",
                threshold: Threshold | None = None) -> dict[str, Any]:
    """Score every item. `reader` returns the seat's form for one item.

    Injected rather than called: the locks run this against a fake seat, and a
    battery that could only be exercised with a 27B model on a loopback port
    would be a battery nobody runs in CI.

    `threshold` omitted means the shipped battery's mark (R223). Pass the one
    loaded beside a custom `--battery` file, so the boards and the mark that
    grades them always come from the same place.
    """
    threshold = threshold or load_threshold()
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

    per_category = {}
    for cat in CATEGORIES:
        passed = sum(1 for r in rows if r["category"] == cat and r["passed"])
        need = threshold.required(cat)
        per_category[cat] = {
            "items": sum(1 for r in rows if r["category"] == cat),
            "passed": passed,
            "required": need,
            "pass": passed >= need,
        }
    overall = all(v["pass"] for v in per_category.values())
    return {
        "seat": seat_id,
        "items": rows,
        "per_category": per_category,
        "total": {"items": len(rows),
                  "passed": sum(1 for r in rows if r["passed"]),
                  "pass": overall},
        "pass": overall,
        "threshold": dict(threshold.per_category),
        "threshold_owner": threshold.owner or THRESHOLD_NOTE,
        "threshold_note": THRESHOLD_NOTE,
        "thin_categories": thin_categories(items),
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def one_line(scorecard: Mapping[str, Any]) -> str:
    """The summary a person reads: the counts, and R223's verdict on them."""
    parts = [f"{cat} {v['passed']}/{v['items']}"
             f" (need {v['required']}) {'PASS' if v['pass'] else 'FAIL'}"
             for cat, v in scorecard["per_category"].items()]
    total = scorecard["total"]
    verdict = "PASS" if scorecard["pass"] else "FAIL"
    return (f"qualify: {verdict} -- {total['passed']}/{total['items']} items "
            f"({'; '.join(parts)}); pass mark R223, all three categories must "
            "hold")


def write_scorecard(scorecard: Mapping[str, Any],
                    out: Path | None = None) -> Path:
    path = Path(out or (REPO / "review" / "qa" / "qualify-scorecard.json"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scorecard, indent=1) + "\n", encoding="utf-8")
    return path
