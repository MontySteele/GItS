"""EB-202: A SLOT THAT ASKED FOR MORE BOARDS THAN THE SET COULD PRODUCE.

`KLEESPARK-R1`'s `P1` predicted YES on **at least 4 of 8** graded turns, where
YES meant *a visible spend-versus-hold choice: two Spark uses competing, both
affordable, in one hand*. Only THREE of the eight boards could pose that
question at all -- `t07`'s bank of 4 pays Firework Finale (3) AND Fwoosh! (1)
together, so it is not a competition; `t01` and `t08` sit at bank 0; `t04` and
`t05` hold one Spark use each. **A ceiling of three against a threshold of
four means no reading of that round could have met the slot**, so the MISS
established nothing about the cards -- it established that the board set could
not ask. The mismatch was invisible until the pair read, weeks of game time
later.

`MANIFEST.md` counted four, and its count was TRUE: "two or more Spark uses in
hand that the bank can each individually afford" is a different predicate from
"two Spark uses COMPETING". Two true sentences, one number, and prose is where
they were allowed to look like the same sentence. So the repair is to make the
predicate MACHINE-READABLE, and to compute the ceiling before the round is
accepted rather than after it is graded.

THE SMALLEST SCHEMA THAT SAYS IT
---------------------------------
One file per round, `slots.yaml`, beside the turn files it is about:

    slots:
      - id: P1
        threshold: 4
        question: "..."            # optional prose, never read by the check
        predicate:
          - {left: spark_bank, op: ">=", right: min_spark_price}
          - {left: spark_bank, op: "<",  right: affordable_spark_price_sum}

A predicate is a LIST OF CLAUSES and a board qualifies when ALL of them hold
-- a conjunction and nothing else. There is no `or`, no `not`, no nesting, and
that is the point: a predicate language rich enough to express anything is a
second program nobody reviews, and the one slot this row exists for is a
conjunction of two comparisons. When a round needs a disjunction it will need
a ruling about what the slot means first, and the schema can grow then.

Each side of a clause is either an INTEGER or the name of a FACT -- a named
reading of one board, from the table below. A fact that a board cannot answer
(the hand prices no Spark use, so there is no cheapest one) is UNDEFINED, and
a clause with an undefined side is FALSE: a board that cannot be asked the
question does not qualify for the slot, which is exactly what `t04` and `t05`
are.

WHAT IT REFUSES, AND WHEN. `local_tester round --plan-only` and
`staged_turn check` compute each slot's CEILING -- how many of the round's
boards qualify -- and refuse the plan when a ceiling is below the slot's
threshold, naming the number. It runs where the preflights run: before the one
launch, on the committed boards, so an unreachable threshold costs a parse
instead of a round.

WHAT IT IS NOT. It is not a grade and it does not predict one. A board that
qualifies is a board that CAN pose the slot's question; whether a grader saw
the choice is what the round is for, and `P1` is graded on what a grader sees
on the page. The ceiling is an upper bound on the count and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import yaml

from understudy import resource_order

SLOT_FILE = "slots.yaml"

OPS: dict[str, Callable[[int, int], bool]] = {
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    "<": lambda a, b: a < b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}

# The wire and the sheets spell the Spark bank both ways; a board declares
# whichever its author wrote. Listed rather than guessed at read time.
_SPARK_KEYS = ("sparks", "spark")
_CHARGE_KEYS = ("charge", "charges")


class SlotError(RuntimeError):
    """A `slots.yaml` that cannot be used: a bad op, an unknown fact."""


class Unreachable(RuntimeError):
    """A slot's threshold is above what its board set can produce."""


# ------------------------------------------------------------- the facts ---
#
# Every fact is a reading of ONE board's declared half -- the `board:` mapping
# of the turn file, which is committed with the board and is what the round
# pre-registered. The LIVE board can differ (the encounter is generated) and
# the round's own manifest says so; a reachability ceiling taken off the live
# boards would be taken after they were staged, which is too late to refuse a
# plan.

def _resource(turn: Any, keys: Sequence[str]) -> int | None:
    res = getattr(getattr(turn, "board", None), "resources", None) or {}
    for key in keys:
        if key in res:
            return int(res[key])
    return None


def _spark_prices(turn: Any) -> list[int]:
    """What each card in the declared hand costs IN SPARKS, cheapest first.

    Off the sheet's own top-level `spend_spark` op, which is where the price
    has to live for the playability gate to see it (the rule authored at
    `powder_charge` and enforced through Klee slice 1). A card with no such op
    prices no Sparks and contributes nothing.
    """
    rows = sheet_rows_by_id()
    out: list[int] = []
    for card_id in getattr(getattr(turn, "board", None), "hand", None) or []:
        row = rows.get(str(card_id))
        if row is None:
            continue
        for eff in (row.get("effects") or []):
            if isinstance(eff, Mapping) and str(eff.get("op")) == "spend_spark":
                out.append(int(eff.get("amount", 0)))
                break
    return sorted(out)


def _affordable(turn: Any) -> list[int]:
    bank = _resource(turn, _SPARK_KEYS)
    if bank is None:
        return []
    return [p for p in _spark_prices(turn) if p <= bank]


def _min_spark_price(turn: Any) -> int | None:
    prices = _spark_prices(turn)
    return min(prices) if prices else None


def _affordable_sum(turn: Any) -> int | None:
    prices = _affordable(turn)
    return sum(prices) if prices else None


FACTS: dict[str, Callable[[Any], int | None]] = {
    "spark_bank": lambda t: _resource(t, _SPARK_KEYS),
    "charge_bank": lambda t: _resource(t, _CHARGE_KEYS),
    "energy": lambda t: int(getattr(t.board, "energy", 0)),
    "hp": lambda t: int(getattr(t.board, "hp", 0)),
    "block": lambda t: int(getattr(t.board, "block", 0)),
    "hand_size": lambda t: len(getattr(t.board, "hand", []) or []),
    "enemy_count": lambda t: len(getattr(t.board, "enemies", []) or []),
    "spark_use_count": lambda t: len(_spark_prices(t)),
    "affordable_spark_uses": lambda t: len(_affordable(t)),
    "min_spark_price": _min_spark_price,
    "affordable_spark_price_sum": _affordable_sum,
}


def _sheet_rows_by_id(root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for rel in resource_order.SHEETS:
        path = root / rel
        if not path.is_file():
            continue
        for row in resource_order._rows(path):
            key = str(row.get("id") or "")
            if key and key not in out:
                out[key] = row
    return out


_ROWS_CACHE: dict[str, dict[str, dict[str, Any]]] = {}


def sheet_rows_by_id(repo: Path | None = None) -> dict[str, dict[str, Any]]:
    """`{sheet id: row}`. Keyed by ID because a `board.hand` names ids.

    `resource_order.card_index` is keyed by PRINTED TITLE, which is what a
    grader's form speaks; a turn file's mirrored hand speaks sheet ids, and
    the two vocabularies are deliberately different everywhere else in this
    funnel.
    """
    root = repo or resource_order.REPO
    key = str(root)
    if key not in _ROWS_CACHE:
        _ROWS_CACHE[key] = _sheet_rows_by_id(root)
    return _ROWS_CACHE[key]


# ------------------------------------------------------------- the schema --

@dataclass
class Slot:
    id: str
    threshold: int
    predicate: list[dict[str, Any]] = field(default_factory=list)
    question: str = ""

    def qualifies(self, turn: Any) -> bool:
        """Does this board qualify -- every clause true, on defined facts?"""
        for clause in self.predicate:
            left = _side(clause["left"], turn)
            right = _side(clause["right"], turn)
            if left is None or right is None:
                return False
            if not OPS[clause["op"]](left, right):
                return False
        return bool(self.predicate)


def _side(spec: Any, turn: Any) -> int | None:
    if isinstance(spec, bool):
        raise SlotError("a clause side is an integer or a fact name, not a "
                        "boolean")
    if isinstance(spec, int):
        return spec
    return FACTS[str(spec)](turn)


def parse_slots(blob: Any, where: str = SLOT_FILE) -> list[Slot]:
    """The `slots.yaml` mapping as a list of `Slot`. Refuses, never coerces."""
    if not isinstance(blob, Mapping) or not isinstance(blob.get("slots"), list):
        raise SlotError(f"{where}: the file is a mapping with a 'slots' list")
    out: list[Slot] = []
    for i, raw in enumerate(blob["slots"]):
        if not isinstance(raw, Mapping) or not raw.get("id"):
            raise SlotError(f"{where}: slot {i} needs an 'id'")
        sid = str(raw["id"])
        try:
            threshold = int(raw["threshold"])
        except (KeyError, TypeError, ValueError):
            raise SlotError(
                f"{where}: slot {sid!r} needs an integer 'threshold' -- the "
                f"count of boards the registration asks for. A slot with no "
                f"threshold is not a COUNTING slot and does not belong in "
                f"this file") from None
        clauses = raw.get("predicate")
        if not isinstance(clauses, list) or not clauses:
            raise SlotError(
                f"{where}: slot {sid!r} needs a non-empty 'predicate' -- the "
                f"machine-readable half is the whole row (EB-202). Prose is "
                f"what let a threshold of four ride on a ceiling of three")
        parsed = []
        for j, clause in enumerate(clauses):
            if not isinstance(clause, Mapping):
                raise SlotError(f"{where}: {sid} clause {j} is a mapping")
            for key in ("left", "op", "right"):
                if key not in clause:
                    raise SlotError(f"{where}: {sid} clause {j} has no {key!r}")
            if str(clause["op"]) not in OPS:
                raise SlotError(
                    f"{where}: {sid} clause {j}: {clause['op']!r} is not a "
                    f"comparison. One of: " + ", ".join(sorted(OPS)))
            for side in ("left", "right"):
                spec = clause[side]
                if isinstance(spec, int) and not isinstance(spec, bool):
                    continue
                if str(spec) not in FACTS:
                    raise SlotError(
                        f"{where}: {sid} clause {j}: {spec!r} is neither an "
                        f"integer nor a fact this check can read. One of: "
                        + ", ".join(sorted(FACTS)))
            parsed.append({"left": clause["left"], "op": str(clause["op"]),
                           "right": clause["right"]})
        out.append(Slot(id=sid, threshold=threshold, predicate=parsed,
                        question=str(raw.get("question") or "")))
    return out


def load_slots(directory: Path) -> list[Slot]:
    """The `slots.yaml` beside a round's turn files, or `[]` where none is.

    ABSENT IS LEGAL, and deliberately so: every round committed before this
    row existed carries no slot file, and a check that refused those would
    refuse the whole history to catch one defect.
    """
    path = Path(directory) / SLOT_FILE
    if not path.is_file():
        return []
    try:
        blob = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SlotError(f"{path}: {exc}") from exc
    return parse_slots(blob, where=str(path))


# ------------------------------------------------------- the reachability --

def ceiling(slot: Slot, turns: Sequence[Any]) -> dict[str, Any]:
    """How many of these boards CAN pose this slot's question."""
    qualifying = [t.id for t in turns if slot.qualifies(t)]
    return {"slot": slot.id, "threshold": slot.threshold,
            "ceiling": len(qualifying), "boards": len(turns),
            "qualifying": qualifying,
            "reachable": len(qualifying) >= slot.threshold}


def reachability(slots: Sequence[Slot],
                 turns: Sequence[Any]) -> list[dict[str, Any]]:
    return [ceiling(slot, turns) for slot in slots]


def refusals(report: Sequence[Mapping[str, Any]]) -> list[str]:
    """One sentence per unreachable slot, NAMING THE NUMBER."""
    out = []
    for row in report:
        if row["reachable"]:
            continue
        out.append(
            f"{row['slot']}: threshold {row['threshold']} is above this board "
            f"set's ceiling of {row['ceiling']} -- only "
            f"{row['ceiling']} of {row['boards']} board(s) can pose the "
            f"question at all"
            + (f" ({', '.join(row['qualifying'])})" if row["qualifying"]
               else "")
            + ". No reading of this round could meet the slot, so a MISS "
              "would say nothing about the cards (EB-202)")
    return out


def check_round(turns: Sequence[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Every slot file the round's turn files sit beside, over those boards.

    A round is a DIRECTORY of turn files, so the slot file is found from the
    boards rather than named on the command line: a plan that named its own
    slot file could name a different one than the round it staged.
    """
    by_dir: dict[Path, list[Any]] = {}
    for turn in turns:
        path = getattr(turn, "path", None)
        if path is None:
            continue
        by_dir.setdefault(Path(path).parent, []).append(turn)
    report: list[dict[str, Any]] = []
    bad: list[str] = []
    for directory in sorted(by_dir):
        slots = load_slots(directory)
        if not slots:
            continue
        rows = reachability(slots, by_dir[directory])
        report += rows
        bad += refusals(rows)
    return report, bad
