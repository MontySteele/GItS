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


def card_spark_prices(row: Mapping[str, Any]) -> list[int]:
    """Every Spark price ONE sheet row can charge, in the order it prints them.

    `EB-237`. R225's amended clause, in as many words: a Spark price sits at
    the card's TOP LEVEL **or** at the HEAD OF A `choose_one` MODE, and
    nothing nested and nothing conditional. This function reads both, and the
    mode half is why it exists.

    THE DEFECT IT REPAIRS. Until `EB-237` this read a top-level `spend_spark`
    and stopped there, so *Bag of Tricks* -- `proto_spark_mode_bombs`, the
    first row in the tree to price itself at a mode head, and the whole
    subject of `KLEESPARK-BT1` -- was INVISIBLE to `affordable_spark_uses`,
    `min_spark_price`, `spark_use_count` and every ceiling `--plan-only`
    printed. The round's own `slots.yaml` had to write every predicate about
    the OTHER cards in hand and say so at length. A check that cannot see the
    row under test is not a check on that round.

    HEAD, AND STRICTLY THE HEAD. A mode prices Sparks only when the FIRST
    effect of that mode is `spend_spark`; a `spend_spark` further down a
    mode's list is nested-or-conditional by construction and is not admitted,
    which is the half of R225's clause that keeps this from becoming a search
    for any spend anywhere in a row.
    """
    out: list[int] = []
    for eff in (row.get("effects") or []):
        if not isinstance(eff, Mapping):
            continue
        op = str(eff.get("op"))
        if op == "spend_spark":
            out.append(int(eff.get("amount", 0)))
        elif op == "choose_one":
            for mode in (eff.get("modes") or []):
                if not isinstance(mode, Mapping):
                    continue
                head = next(iter(mode.get("effects") or []), None)
                if (isinstance(head, Mapping)
                        and str(head.get("op")) == "spend_spark"):
                    out.append(int(head.get("amount", 0)))
    return out


def _spark_prices(turn: Any) -> list[int]:
    """What each card in the declared hand costs IN SPARKS, cheapest first.

    ONE PRICE PER CARD, and where a card prices more than one way to play it
    -- a `choose_one` with two priced modes -- the CHEAPEST is the one this
    list carries, because these facts count *uses the bank can reach* and the
    cheapest way in is the one that decides that. A card with no admitted
    price prices no Sparks and contributes nothing.
    """
    rows = sheet_rows_by_id()
    out: list[int] = []
    for card_id in getattr(getattr(turn, "board", None), "hand", None) or []:
        row = rows.get(str(card_id))
        if row is None:
            continue
        prices = card_spark_prices(row)
        if prices:
            out.append(min(prices))
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


# -------------------------------------------- EB-208: which slots COUNT ----
#
# THE CEILING IS TAKEN OFF THE DECLARED BOARD AND MUST STAY THAT WAY -- a
# ceiling taken off the live board would be taken after staging, which is too
# late to refuse a plan. What EB-208 adds is the OTHER end: once a board is
# staged, the slots whose predicate actually READS the enemy count are the
# only ones a wrong live count can invalidate, and they are named here so the
# preflight marks those and nothing else. A slot that never mentions
# `enemy_count` is unaffected by how many bodies rolled.

ENEMY_COUNT_FACT = "enemy_count"


def reads_fact(slot: Slot, fact: str) -> bool:
    """Does any clause of this slot's predicate name this fact?"""
    return any(str(clause.get(side)) == fact
               for clause in slot.predicate for side in ("left", "right"))


def slots_reading(slots: Sequence[Slot], fact: str) -> list[str]:
    return [s.id for s in slots if reads_fact(s, fact)]


def enemy_count_slots(directory: Path) -> list[str]:
    """The ids in this round's `slots.yaml` whose predicate counts enemies.

    `[]` where the round has no slot file, which is legal and common: a round
    with no machine-readable predicate has no slot this check can name, and
    guessing one from prose is the thing EB-202 exists to stop.
    """
    return slots_reading(load_slots(directory), ENEMY_COUNT_FACT)


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


# ------------------------------------ EB-236: the resource-round check ------
#
# `KLEESPARK-BT1` REGISTERED A CLAIM ITS OWN BOARD DID NOT HOLD, and no check
# in this repo could see it. `t02`'s header reads, in as many words: *"the
# bank of 3 now buys EXACTLY ONE of two things -- the card's priced mode, or
# the whole of another card"*. In the SHIPPED world that sentence is false.
# Klee's starter relic *Pounding Surprise* pays +1 Spark for every Bomb that
# detonates, and the priced mode places three Bombs, so
#
#     Bag of Tricks, priced mode   bank 3 -> 0,  three Bombs on the target
#     any detonator or Attack      bombs pop,    +3 Sparks -> bank 3
#     Firework Finale              bank 3 -> 0,  18 damage
#
# buys BOTH, for 15 + 18. The round graded a decision the board never posed.
# R229 accepted the refund as an observed TEST CONDITION and put the arm under
# a pre-registered RETURN CONDITION; this is the check that stops a board from
# claiming an exclusivity it does not have, and it is the STRONG form GPT
# asked for: not "are the two prices greater than the bank" but "can ANY ORDER
# OF PLAY, counting every relic-triggered gain along the way, pay for both".
#
# TWO HALVES, AND THE SECOND IS THE ONE THAT REFUSED SEVEN OF EIGHT FORMS.
#
#   `both_buyable`      -- a board DECLARES an exclusive pair and some legal
#                          order pays for every member of it.
#   `no_forced_trade`   -- the whole hand is playable at once with the Energy
#                          the board gives, so the telegraph forces no trade
#                          and a reader answering question four honestly
#                          answers "no". All FOUR of `KLEESPARK-BT1`'s boards
#                          are this shape (one enemy, fixed telegraph, three
#                          Energy, at most two Energy-costed cards), and
#                          `intent_insensitive` refused seven of the eight
#                          forms they produced. §22.4 item 2 calls it a
#                          REGISTRATION defect and it is that round's RETURN.
#
# WHERE IT RUNS, AND WHY IT IS NOT A LINT.
# `local_tester round --plan-only`, beside `EB-202`'s reachability ceiling:
# before the one launch, on the committed boards, so a board that cannot ask
# its question costs a parse instead of a round. It is deliberately NOT a
# `tools/lint_*.py` in the CI lane. A lint sweeps every board in the tree,
# including `KLEESPARK-BT1`'s four -- which are the committed record of a run
# and graded round and stay exactly as registered (R101b). A check that turns
# CI red on a closed round's published boards is not a check, it is an erratum
# nobody can clear. The lint count is unchanged at 29.
#
# THE SIMPLIFICATIONS, STATED RATHER THAN LEFT TO BE FOUND. The rule this
# walks is the engine's (`tier0/engine/effects.py`'s `detonate_bombs` and
# `_detonate_bombs_on_hit`; the C# twin is `Powers/BombPower.cs` and
# `IBombDetonationListener`): a Bomb detonates when a `detonate` op resolves
# against its target, or when an ATTACK deals HP damage to it, and each
# detonated Bomb pays every `spark_on_detonation` listener one Spark.
#
#   1. ONE TURN, and no turn-start sweep. Bombs placed and not detonated in
#      the sequence simply sit; their next-turn payout is not counted, which
#      is the CONSERVATIVE direction -- it can only make a board look MORE
#      exclusive than it is, never less.
#   2. ONE ENEMY. Every Bomb is on the same body and every detonation takes
#      all of them. A multi-enemy board is out of this check's scope and is
#      refused rather than approximated.
#   3. AN ATTACK DETONATES WHEN ITS PRINTED DAMAGE EXCEEDS THE ENEMY'S
#      DECLARED BLOCK. Strength, Vulnerable, Weak, auras and multi-hit are not
#      modelled: this check counts the BANK, not damage, and a board that
#      needs any of those to answer its own question is a board whose claim is
#      not arithmetic.
#   4. ENERGY IS THE PRINTED COST, PAID ONCE PER CARD. A card printing an `X`
#      cost is refused rather than guessed at.
#   5. EVERY CARD IS PLAYED AT MOST ONCE and only from the declared hand: no
#      draw, no discard, no Exhaust-and-replay.
#
# None of the five can make a both-buyable sequence look exclusive. That is
# the direction a check like this has to err in.

RESOURCE_ROUND_KEY = "resource_round"
SPARK_ON_DETONATION = "spark_on_detonation"
_CHARACTER_SHEETS = Path("tier0") / "content" / "characters"


class BoardDesignError(RuntimeError):
    """A `resource_round:` block this check cannot read, or cannot walk."""


@dataclass(frozen=True)
class Use:
    """One WAY TO PLAY a card that the board's claim is about.

    `mode` is the 1-based index of a `choose_one` mode, or `None` for the
    card's top level. 1-based because a registration written by hand counts
    the modes the way the card prints them.
    """
    card: str
    mode: int | None = None

    def __str__(self) -> str:
        return self.card + (f" (mode {self.mode})" if self.mode else "")


@dataclass
class ResourceRound:
    """A board's own declaration of what its resource question is."""
    claim: str = ""
    exclusive: list[Use] = field(default_factory=list)
    relic_hooks: list[str] | None = None


def parse_resource_round(raw: Any, where: str = "") -> "ResourceRound | None":
    """The `resource_round:` block of a turn file. `None` where none is.

    ABSENT IS LEGAL: every board committed before this row existed carries no
    block, and only the `no_forced_trade` half is checked on those. A board
    that makes an EXCLUSIVITY CLAIM has to say so HERE, because a claim that
    lives only in a header comment is exactly what `KLEESPARK-BT1` shipped.
    """
    if raw is None:
        return None
    if not isinstance(raw, Mapping):
        raise BoardDesignError(f"{where}: {RESOURCE_ROUND_KEY!r} is a mapping")
    uses: list[Use] = []
    for i, entry in enumerate(raw.get("exclusive") or []):
        if not isinstance(entry, Mapping) or not entry.get("card"):
            raise BoardDesignError(
                f"{where}: exclusive[{i}] is a mapping with a 'card' -- the "
                f"sheet id -- and an optional 1-based 'mode'")
        mode = entry.get("mode")
        uses.append(Use(card=str(entry["card"]),
                        mode=int(mode) if mode is not None else None))
    if len(uses) == 1:
        raise BoardDesignError(
            f"{where}: an exclusive pair is TWO OR MORE uses. One use is not "
            f"a claim about anything")
    hooks = raw.get("relic_hooks")
    return ResourceRound(
        claim=str(raw.get("claim") or ""),
        exclusive=uses,
        relic_hooks=None if hooks is None else [str(h) for h in hooks])


# ---------------------------------------------------------------- the walk --

def _variants(row: Mapping[str, Any]
              ) -> list[tuple[int | None, list[Mapping[str, Any]]]]:
    """The ways one card can be played: `(mode, effects in printed order)`.

    A `choose_one` becomes one variant per mode, with the card's other
    effects kept in place around it, which is how the game resolves one.
    """
    effects = [e for e in (row.get("effects") or []) if isinstance(e, Mapping)]
    modal = next((e for e in effects if str(e.get("op")) == "choose_one"), None)
    if modal is None:
        return [(None, effects)]
    out: list[tuple[int | None, list[Mapping[str, Any]]]] = []
    for i, mode in enumerate(modal.get("modes") or [], 1):
        if not isinstance(mode, Mapping):
            continue
        expanded: list[Mapping[str, Any]] = []
        for eff in effects:
            if eff is modal:
                expanded += [m for m in (mode.get("effects") or [])
                             if isinstance(m, Mapping)]
            else:
                expanded.append(eff)
        out.append((i, expanded))
    return out


def _energy_cost(row: Mapping[str, Any], card_id: str) -> int:
    cost = row.get("cost")
    try:
        return int(cost)
    except (TypeError, ValueError):
        raise BoardDesignError(
            f"{card_id} prints cost {cost!r}; this check pays the PRINTED "
            f"Energy cost once per card and does not guess at an X") from None


def _character_relic_hooks(character: str,
                           repo: Path | None = None) -> list[str]:
    """The starter relic's hooks off the character sheet, or `[]`.

    `tier0/content/characters/klee.yaml` carries
    `relic_hooks: [spark_on_detonation]`, with *Pounding Surprise* named in
    the comment beside it. READ rather than declared per board, so a board
    cannot forget the relic every run of that character starts with -- which
    is the omission `KLEESPARK-BT1` is the record of.
    """
    path = (repo or resource_order.REPO) / _CHARACTER_SHEETS / f"{character}.yaml"
    if not path.is_file():
        return []
    blob = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [str(h) for h in (blob.get("relic_hooks") or [])]


@dataclass
class _Walk:
    bank: int
    energy: int
    bombs: int
    block: int
    refunds: bool


def _resolve(state: _Walk, effects: Sequence[Mapping[str, Any]],
             is_attack: bool) -> "_Walk | None":
    """Resolve one play. `None` where its Spark price cannot be paid."""
    bank, bombs = state.bank, state.bombs
    for eff in effects:
        op = str(eff.get("op"))
        amount = int(eff.get("amount", 0) or 0)
        if op == "spend_spark":
            if bank < amount:
                return None
            bank -= amount
        elif op == "gain_spark":
            bank += amount
        elif op == "place_bomb":
            bombs += amount
        elif op == "detonate":
            bank += bombs if state.refunds else 0
            bombs = 0
        elif op == "damage" and is_attack and bombs and amount > state.block:
            # `_detonate_bombs_on_hit`: an Attack that gets HP damage through
            # pops the target's Bombs, and every one pays the relic.
            bank += bombs if state.refunds else 0
            bombs = 0
    return _Walk(bank=bank, energy=state.energy, bombs=bombs,
                 block=state.block, refunds=state.refunds)


def _enemy_block(enemy: Any) -> int:
    if isinstance(enemy, Mapping):
        return int(enemy.get("block", 0) or 0)
    return int(getattr(enemy, "block", 0) or 0)


def buying_orders(turn: Any, spec: ResourceRound,
                  repo: Path | None = None) -> list[list[str]]:
    """Every order of play that pays for EVERY use the board calls exclusive.

    An EMPTY list is the passing answer: no order buys both, so the claim the
    board registered is a claim its own arithmetic holds.
    """
    rows = sheet_rows_by_id(repo)
    board = getattr(turn, "board", None)
    hand = [str(c) for c in (getattr(board, "hand", None) or [])]
    enemies = list(getattr(board, "enemies", None) or [])
    if len(enemies) != 1:
        raise BoardDesignError(
            f"{getattr(turn, 'id', '?')}: this check walks ONE body. A board "
            f"with {len(enemies)} enem(ies) is refused rather than "
            f"approximated")
    hooks = (spec.relic_hooks if spec.relic_hooks is not None
             else _character_relic_hooks(str(getattr(board, "character", "")),
                                         repo))
    start = _Walk(
        bank=int((getattr(board, "resources", None) or {}).get("sparks", 0)),
        energy=int(getattr(board, "energy", 0)),
        bombs=0,
        block=_enemy_block(enemies[0]),
        refunds=SPARK_ON_DETONATION in hooks)
    wanted = set(spec.exclusive)
    if not wanted:
        return []
    missing = sorted({u.card for u in wanted} - set(hand))
    if missing:
        raise BoardDesignError(
            f"{getattr(turn, 'id', '?')}: the exclusive pair names "
            f"{', '.join(missing)}, which is not in the declared hand")

    found: list[list[str]] = []

    def walk(state: _Walk, left: list[int], paid: frozenset,
             order: list[str]) -> None:
        if wanted <= paid:
            found.append(list(order))
            return
        for pos, idx in enumerate(left):
            card_id = hand[idx]
            row = rows.get(card_id)
            if row is None:
                continue
            cost = _energy_cost(row, card_id)
            if cost > state.energy:
                continue
            is_attack = str(row.get("type")) == "attack"
            for mode, effects in _variants(row):
                after = _resolve(state, effects, is_attack)
                if after is None:
                    continue
                after.energy = state.energy - cost
                use = Use(card=card_id, mode=mode)
                walk(after, left[:pos] + left[pos + 1:],
                     paid | ({use} if use in wanted else frozenset()),
                     order + [str(use)])

    walk(start, list(range(len(hand))), frozenset(), [])
    return found


def hand_is_wholly_playable(turn: Any, repo: Path | None = None) -> bool:
    """Does the Energy pay for EVERY card in the declared hand at once?

    The `no_forced_trade` reading, and it is exactly the construction §22.4
    item 2 names: three Energy against a hand of at most two Energy-costed
    cards, so the telegraph never forces a choice and question four is
    honestly answered "no".
    """
    rows = sheet_rows_by_id(repo)
    total = 0
    for card_id in (getattr(getattr(turn, "board", None), "hand", None) or []):
        row = rows.get(str(card_id))
        if row is None:
            continue
        total += _energy_cost(row, str(card_id))
    return total <= int(getattr(getattr(turn, "board", None), "energy", 0))


def board_design_findings(turn: Any, repo: Path | None = None) -> list[str]:
    """Every reason this board cannot ask the resource question it registers."""
    spec = getattr(turn, "resource_round", None)
    out: list[str] = []
    if hand_is_wholly_playable(turn, repo):
        out.append(
            f"{turn.id}: no_forced_trade -- the Energy on this board pays for "
            f"the WHOLE declared hand at once, so the telegraph forces no "
            f"trade and a reader answering question four honestly answers "
            f"'no'. Seven of eight forms in the first Bag of Tricks round "
            f"were refused intent_insensitive on exactly this construction; a "
            f"resource round needs one line the board cannot buy")
    if spec is None or not spec.exclusive:
        return out
    orders = buying_orders(turn, spec, repo)
    if orders:
        out.append(
            f"{turn.id}: both_buyable -- this board declares "
            + " and ".join(str(u) for u in spec.exclusive)
            + " mutually exclusive"
            + (f" ({spec.claim})" if spec.claim else "")
            + f", and {len(orders)} order(s) of play pay for every one of "
              f"them, counting relic-triggered Spark gains. The first is: "
            + " -> ".join(orders[0])
            + ". A board whose exclusive pair is not exclusive grades a "
              "decision it never posed (EB-236)")
    return out


def check_board_design(turns: Sequence[Any],
                       repo: Path | None = None) -> list[str]:
    """`board_design_findings` over a whole planned round, in board order."""
    out: list[str] = []
    for turn in turns:
        out += board_design_findings(turn, repo)
    return out
