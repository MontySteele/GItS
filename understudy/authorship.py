"""EB-190: WHO WROTE A PROTOTYPE ROW, and the one door that reads it.

R217 C fixes the roles at two families -- **Claude authors, GPT grades and
reviews** -- and OPERATIONS' "Doctrine seat protocol" records why: a seat that
writes a row and then grades it has graded its own work, and the outcome is
not evidence. Klee slice 1 is the case that made this mechanical rather than
procedural: the seat re-authored Rummage's text and picked Slow Burn's number,
and the same family then graded and pair-read both.

So every row on `docs/prototype-surface.yaml` records `authored_by:` as a list
of model FAMILIES, and this module is the ONE place that reads it.

WHAT THIS MODULE READS OFF THE SURFACE, AND NOTHING ELSE
--------------------------------------------------------
`id` and `authored_by`. Not `name`, not `effects`, not `cost`, not a rarity.
That narrowness is load-bearing rather than tidy: `understudy/seat.py` and
`understudy/blindplay.py` both import this, and both are pinned by
`tier0/tests/` as modules that may not reach a design sheet. A helper that
handed either of them a row's TEXT would be a leak wearing a governance name.
`rows_authorship()` returns families keyed by id and there is no second
accessor.

HOW A TURN RESOLVES TO ITS ROW
------------------------------
A staged turn's yaml under `understudy/turns/` names its cards twice -- once
in `staging:` as `give: {card: KLEEMOD-PROTO_...}`, and once in the tier0
mirror's `board.hand` as the bare row id. Both are read, and the union is the
answer, because a turn that grants a prototype it does not mirror (or the
reverse) is exactly the wiring mistake this should not silently pass. Shipped
cards produce no rows and pass by having nothing to check.

THE PACKET IS NOT THE ROUTE, on purpose: `review/qa/<turn>/packet.json` is
design-blind and prints TITLES, so it cannot name a row without becoming the
thing it is scrubbed to avoid being.

THE REFUSAL IS `check_independent`, GENERALISED, NOT A SECOND DOOR
------------------------------------------------------------------
`blindplay.check_independent` already refused the author family from the blind
seat. It moved here and grew one argument: the rows the run TOUCHES, with the
families each records. `blindplay` re-exports it, so there is one refusal,
asked two ways -- who is running, and what the row says about who wrote it.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

REPO = Path(__file__).resolve().parent.parent
SURFACE = REPO / "docs" / "prototype-surface.yaml"
TURN_DIR = REPO / "understudy" / "turns"

FIELD = "authored_by"
PROTOTYPE_ID_PREFIX = "proto_"           # tier0.content.loader's, un-imported

# Independence is by model FAMILY (R217 C). The slice's author is Claude, so a
# Claude seat is refused however fresh its context is -- "a fresh context on
# the same model does not satisfy it" is the ruling's own wording.
AUTHOR_FAMILY = "claude"
FAMILIES: tuple[str, ...] = ("claude", "gpt")
MODEL_FAMILIES: dict[str, tuple[str, ...]] = {
    "claude": ("claude", "anthropic", "opus", "sonnet", "haiku", "fable"),
    "gpt": ("gpt", "openai", "o1", "o3", "codex"),
}

_GIVE = re.compile(r"^KLEEMOD-(PROTO_[A-Z0-9_]+)$")


class IndependenceError(RuntimeError):
    """A seat may not answer for a row its own family wrote."""


# ------------------------------------------------------------- the surface --

def rows_authorship(sheet: Path | None = None) -> dict[str, list[str]]:
    """`{row id: [families]}` for the whole surface. The ONLY surface reader.

    A missing `authored_by` comes back as `[]` rather than raising: the
    REFUSAL for that belongs to `gen_prototype_cards` (which cannot emit the
    row) and to `tools/lint_prototype_authorship.py` (which says so by name).
    A reader that raised here would make an unrelated `seat grade` die with a
    schema error instead of the message the operator needs.
    """
    path = sheet or SURFACE
    if not path.exists():
        return {}
    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    out: dict[str, list[str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        rid = str(row.get("id") or "")
        if not rid:
            continue
        raw = row.get(FIELD)
        out[rid] = [str(f) for f in raw] if isinstance(raw, list) else []
    return out


def field_findings(row: Mapping[str, Any]) -> list[str]:
    """Why this row's `authored_by` is not valid, or an empty list.

    Shared by the generator (which refuses the row) and the lint (which
    reports every row at once), so the two cannot disagree about what a valid
    field is.
    """
    rid = str(row.get("id") or "<no id>")
    if FIELD not in row:
        return [f"{rid}: no `{FIELD}:`. Every prototype row records the model "
                f"FAMILIES that wrote it, from {list(FAMILIES)} (EB-190). "
                f"Claude authors; a family is added when a seat contributed "
                f"text, a number or a mode -- never for a clause name alone."]
    value = row.get(FIELD)
    if not isinstance(value, list) or not value:
        return [f"{rid}: `{FIELD}:` must be a non-empty LIST of families, "
                f"got {value!r}"]
    bad = [f for f in value if f not in FAMILIES]
    if bad:
        return [f"{rid}: `{FIELD}:` names unknown famil(ies) {bad}; the set "
                f"is closed at {list(FAMILIES)} -- there is no third family "
                f"and none is being added (R217 C)"]
    if len(set(value)) != len(value):
        return [f"{rid}: `{FIELD}:` repeats a family: {value!r}"]
    return []


def strip_field(row: Mapping[str, Any]) -> dict[str, Any]:
    """The row as the card schema sees it: provenance removed.

    `authored_by` is a fact about the ROW, not about the card, so it is taken
    off before `Card.from_dict` and before the emitter. That is what makes the
    field provably unable to move generated output.
    """
    return {k: v for k, v in row.items() if k != FIELD}


# ------------------------------------------------------------ turn -> rows --

def _rows_in_blob(blob: Mapping[str, Any]) -> list[str]:
    found: set[str] = set()
    for card in ((blob.get("board") or {}).get("hand") or []):
        if isinstance(card, str) and card.startswith(PROTOTYPE_ID_PREFIX):
            found.add(card)
    for step in (blob.get("staging") or []):
        give = step.get("give") if isinstance(step, dict) else None
        if not isinstance(give, dict):
            continue
        m = _GIVE.match(str(give.get("card") or "").strip().upper())
        if m:
            found.add(m.group(1).lower())
    return sorted(found)


def turn_index(directory: Path | None = None) -> dict[str, list[str]]:
    """`{turn id: [prototype row ids]}` for every staged turn, read ONCE.

    Same walk `staged_turn.all_turns` does, and `fixtures/` is excluded for
    the same reason: it holds grader FORMS, not turns. Parsed with
    `yaml.safe_load` rather than through `staged_turn`, because importing that
    module would drag the tier0 sheet loaders into the blind seat.

    Built as a whole-directory index rather than a per-id search because both
    callers ask about many ids -- the lint sweeps every record, and a review
    prompt names a round's worth of turns -- and a per-id walk would re-read
    the tree once per token.
    """
    d = directory or TURN_DIR
    index: dict[str, list[str]] = {}
    if not d.is_dir():
        return index
    for path in sorted(d.rglob("*.yaml")):
        if "fixtures" in path.relative_to(d).parts:
            continue
        try:
            blob = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:                                # noqa: PERF203
            continue
        if not isinstance(blob, dict):
            continue
        turn_id = str(blob.get("id") or "")
        if turn_id:
            index[turn_id] = _rows_in_blob(blob)
    return index


def rows_in_turn(turn_id: str, directory: Path | None = None) -> list[str]:
    """Every prototype row id the turn carries, from BOTH of its declarations.

    Returns `[]` for a turn with no file and for a turn holding only shipped
    cards -- the second is the ordinary case and is not an error.
    """
    return turn_index(directory).get(turn_id, [])


def rows_named_in(text: str, directory: Path | None = None) -> list[str]:
    """Prototype rows a piece of prose names, by row id or by turn id.

    This is how `seat review` resolves a pair-review prompt: those prompts
    name the TURNS they cover (the ids are opaque on purpose, which is why the
    turn files are consulted rather than the prose read for card names), and
    an author-visible prompt may also name a row outright.
    """
    found: set[str] = set(re.findall(r"\bproto_[a-z0-9_]+\b", text or ""))
    words = set(re.findall(r"\b[a-z0-9]+(?:-[a-z0-9]+)+\b", text or ""))
    if words:
        for turn_id, rows in turn_index(directory).items():
            if turn_id in words:
                found.update(rows)
    return sorted(found)


# ------------------------------------------------------------ the refusal --

def model_family(model: str) -> str:
    low = str(model or "").casefold()
    for family, markers in MODEL_FAMILIES.items():
        if any(m in low for m in markers):
            return family
    return ""


def conflicts(model: str, row_ids: Iterable[str],
              sheet: Path | None = None) -> list[str]:
    """One line per row this model's family is recorded as having written."""
    family = model_family(model)
    if not family:
        return []
    known = rows_authorship(sheet)
    out: list[str] = []
    for rid in sorted(set(row_ids)):
        families = known.get(rid) or []
        if family in families:
            out.append(f"{rid}: authored_by {list(families)} includes the "
                       f"seat's own family {family!r}")
    return out


def check_independent(model: str, author: str = AUTHOR_FAMILY, *,
                      rows: Iterable[str] = (),
                      sheet: Path | None = None) -> None:
    """Refuse a tester/grader that is not independent of what it is judging.

    Two questions, one door (R217 C, EB-190):

      * WHO IS RUNNING -- the author family may not be the tester. This is the
        original check and its wording is unchanged.
      * WHAT THE ROW RECORDS -- a row whose `authored_by` names the running
        model's family may not be graded or reviewed by it, whichever family
        that is.
    """
    family = model_family(model)
    if not family:
        raise IndependenceError(
            f"cannot tell which model family {model!r} belongs to, and an "
            f"independence rule that cannot name the family is not a check")
    if family == author:
        raise IndependenceError(
            f"{model!r} is in the {family!r} family, which authored this "
            f"slice. Independence is by model FAMILY, not by fresh context "
            f"(R217 C): the tester must be the Codex seat.")
    hits = conflicts(model, rows, sheet)
    if hits:
        raise IndependenceError(
            f"{model!r} is in the {family!r} family, which is recorded as an "
            f"AUTHOR of the row(s) under it -- a seat may not answer for its "
            f"own family's work (R217 C, EB-190): " + "; ".join(hits))
