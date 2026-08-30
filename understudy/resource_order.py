"""THE ORDER FLAG: a line that spends a resource a later play still reads.

WHY THIS EXISTS, AND WHOSE CONDITION IT IS. The Codex seat's 2026-08-29
confirmation advanced the local model into the TESTER chair for staged
single-turn reads, and attached four conditions. This module is the fourth:
*"require review of any reading whose ordered line changes a resource before a
later resource-dependent play."* The seat found the case itself, on
`kokomi-slice2-t06`: the local reading played Twin Tides' *Spend 6 Charge*
mode and THEN All Streams Flow to the Sea, whose damage reads Charge -- and
carried the pre-spend damage number through the spend. That is not a bad
preference; it is a misread of the board, and it is exactly the shape that
reads as a competent line until someone does the arithmetic.

WHAT IT IS NOT. It is not a verdict, it is not a MISREAD claim, and it does
not say the line is wrong: two plays can legitimately sit in that order (the
spend may be the point). It says one thing -- **a human-grade seat should read
this one** -- and the funnel routes the turn to the Codex seat regardless of
the spot-check rate. A flag that tried to decide would be a grader, and this
family is not one.

WHERE THE FACTS COME FROM, AND WHY NOT THE PACKET
-------------------------------------------------
The card SHEETS, through the effect ops -- `spend_charge`, `spend_spark`,
`salon_rotate`, `crash_fanfare` on the spending side; `bonus_formula`,
`requires` and a `conditional`'s `if:` on the reading side. The packet's
printed prose says "already including Charge", which is true and is not
machine-readable; the op is. This module therefore READS A DESIGN SHEET and
must never be imported by anything that builds a blind prompt --
`understudy/local_tester.py` imports it LAZILY, after the read has already
happened, for that reason, and `tier0/tests/test_local_tester.py` pins it.

THE MODE REFINEMENT, WHICH IS THE DIFFERENCE BETWEEN A FLAG AND A NUISANCE
--------------------------------------------------------------------------
`Twin Tides` is a *Choose one*: one mode spends Charge and one does not. The
form records the chosen mode's PRINTED text in `choose:`, so when a play names
a mode only that mode's effects count. A choose-one play with no `choose:`
recorded falls back to the UNION of its modes -- flagging a turn nobody can
resolve is the safe direction here, because the cost of a flag is one seat
read and the cost of a miss is an unreviewed misread.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

REPO = Path(__file__).resolve().parents[1]

# Every sheet that can print a face a staged turn may put in a hand. Declared
# rather than globbed: `*-upgrades.yaml` rows are DELTAS with no printed title
# of their own, and a glob would silently start reading them the day one grows
# an `effects:` key.
SHEETS: tuple[str, ...] = (
    "docs/klee-cards.yaml",
    "docs/furina-cards.yaml",
    "docs/kokomi-cards.yaml",
    "docs/mondstadt-companions.yaml",
    "docs/fontaine-companions.yaml",
    "docs/inazuma-companions.yaml",
    "docs/prototype-surface.yaml",
)

# The meters a line can spend out from under a later play. Each maps to the
# tokens that name it inside an op name or a formula string. `burst` is here
# because `requires: burst_energy_full` is a READ of it and `burst_energy` is
# how a face spends it.
RESOURCES: dict[str, tuple[str, ...]] = {
    "charge": ("charge",),
    "spark": ("spark", "sparks"),
    "encore": ("encore",),
    "fanfare": ("fanfare",),
    "salon": ("salon", "salon_member", "salon_members"),
    "burst": ("burst", "burst_energy"),
}

# An op that CHANGES the meter -- the seat's own word, which is wider than
# "spends": rotating the salon does not shorten the line but it does move what
# the next read sees. `spend_*` is the family; the four below change without
# saying `spend`, and each is listed BY NAME so a new op cannot join the set
# by accident. `burst_energy` is deliberately absent: it GAINS (`Gain 10 Burst
# Energy`), and a gain before a read is the good order, not the flagged one.
SPEND_PREFIX = "spend_"
NAMED_SPEND_OPS: dict[str, str] = {
    "salon_rotate": "salon",
    "salon_bow": "salon",
    "salon_perform": "salon",
    "crash_fanfare": "fanfare",
}

# Where a READ hides. A value under one of these keys is scanned for a
# resource token; nothing else in the effect is.
READ_KEYS: tuple[str, ...] = (
    "bonus_formula", "requires", "if", "condition", "predicate",
    "threshold", "when", "unless",
)

_TAG = re.compile(r"\[/?[a-z_]+\]")
_PUNCT = re.compile(r"[^a-z0-9 ]+")


class SheetError(RuntimeError):
    """A sheet on `SHEETS` could not be read."""


# ------------------------------------------------------------- the index --

def _rows(path: Path) -> list[dict[str, Any]]:
    blob = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(blob, dict):
        blob = blob.get("cards") or blob.get("rows") or []
    return [r for r in (blob or []) if isinstance(r, dict)]


def card_index(repo: Path | None = None) -> dict[str, dict[str, Any]]:
    """`{normalised printed title: row}` across every sheet a hand can name.

    A title that two sheets print keeps the FIRST row read, in `SHEETS` order,
    and the collision is not an error here: `tools/lint_unique_names.py` owns
    that question and a second opinion from this module would just be a second
    place to fix it.
    """
    root = repo or REPO
    out: dict[str, dict[str, Any]] = {}
    for rel in SHEETS:
        path = root / rel
        if not path.is_file():
            continue
        try:
            rows = _rows(path)
        except yaml.YAMLError as exc:                         # noqa: PERF203
            raise SheetError(f"{rel}: {exc}") from exc
        for row in rows:
            key = normalise(row.get("name"))
            if key and key not in out:
                out[key] = row
    return out


def normalise(text: Any) -> str:
    """A printed title or mode label, comparable across a form and a sheet.

    Markup tags come off first (`Spend 6 [gold]Charge[/gold]` is one phrase to
    a reader and three tokens to a parser), then punctuation, then whitespace.
    """
    low = str(text or "").casefold()
    low = _TAG.sub(" ", low)
    low = low.replace("’", "'").replace("'", "")
    return " ".join(_PUNCT.sub(" ", low).split())


# ------------------------------------------------------- reading the ops --

def _walk(effects: Any) -> list[Mapping[str, Any]]:
    """Every effect dict under a row, including branches and modes."""
    out: list[Mapping[str, Any]] = []
    if isinstance(effects, Mapping):
        out.append(effects)
        for key in ("then", "else", "effects"):
            out += _walk(effects.get(key))
        for mode in (effects.get("modes") or []):
            out += _walk(mode)
    elif isinstance(effects, (list, tuple)):
        for item in effects:
            out += _walk(item)
    return out


def _resource_in(text: Any) -> list[str]:
    low = str(text or "").casefold()
    return [name for name, tokens in RESOURCES.items()
            if any(re.search(rf"(?<![a-z]){t}(?![a-z])", low) for t in tokens)]


def spends(effects: Any) -> set[str]:
    """Resources these effects take DOWN."""
    found: set[str] = set()
    for eff in _walk(effects):
        op = str(eff.get("op") or "").casefold()
        if not op:
            continue
        if op in NAMED_SPEND_OPS:
            found.add(NAMED_SPEND_OPS[op])
        elif op.startswith(SPEND_PREFIX):
            found.update(_resource_in(op[len(SPEND_PREFIX):]))
    return found


def reads(effects: Any) -> set[str]:
    """Resources these effects LOOK AT -- a slope, a gate or a threshold."""
    found: set[str] = set()
    for eff in _walk(effects):
        for key in READ_KEYS:
            if key in eff:
                found.update(_resource_in(eff.get(key)))
    return found


def _selected(row: Mapping[str, Any], choose: Any) -> Any:
    """The effects that actually resolve, given the form's recorded mode.

    A row with no `choose_one` returns its effects unchanged. A `choose_one`
    whose recorded `choose:` matches a mode label returns THAT mode; one with
    no recorded choice, or a choice that matches nothing, returns the whole
    row -- the conservative union, because a turn whose mode cannot be
    resolved is a turn a person should look at.
    """
    effects = row.get("effects")
    label = normalise(choose)
    if not label:
        return effects
    for eff in _walk(effects):
        if str(eff.get("op") or "") != "choose_one":
            continue
        for mode in (eff.get("modes") or []):
            if not isinstance(mode, Mapping):
                continue
            mode_label = normalise(mode.get("label"))
            if mode_label and (mode_label == label
                               or mode_label in label
                               or label in mode_label):
                return mode.get("effects")
    return effects


def selected_effects(row: Mapping[str, Any], choose: Any = None) -> Any:
    """`_selected` under a public name, for the other sheet readers.

    `understudy/targeting.py` (EB-203) has to resolve a *Choose one* exactly
    the way this module does -- one aimed mode, one that is not, which is
    `EB-184` from the other side -- and two implementations of "which mode did
    the form record" is two places for the answer to drift.
    """
    return _selected(row, choose)


# ----------------------------------------------------------- the finding --

def findings(chosen_line: Sequence[Mapping[str, Any]], *,
             index: Mapping[str, Mapping[str, Any]] | None = None,
             repo: Path | None = None) -> list[dict[str, Any]]:
    """One entry per (spend, later read) pair in this ordered line.

    Empty means the line spends nothing a later play reads, which is the
    ordinary case. A card whose printed title is on no sheet contributes
    nothing and is reported by `unresolved()` instead -- a flag raised because
    a title could not be found would name the harness, not the reading.
    """
    cards = index if index is not None else card_index(repo)
    resolved: list[tuple[str, set[str], set[str]]] = []
    for play in chosen_line or []:
        title = str(play.get("card") or "")
        row = cards.get(normalise(title))
        if row is None:
            resolved.append((title, set(), set()))
            continue
        effects = _selected(row, play.get("choose"))
        resolved.append((title, spends(effects), reads(row.get("effects"))))

    out: list[dict[str, Any]] = []
    for i, (title, spent, _) in enumerate(resolved):
        for resource in sorted(spent):
            for later, (other, _s, read) in enumerate(resolved[i + 1:], i + 1):
                if resource in read:
                    out.append({
                        "resource": resource,
                        "spent_by": title,
                        "spent_at": i,
                        "read_by": other,
                        "read_at": later,
                        "why": (f"{title!r} spends {resource} at position "
                                f"{i + 1} and {other!r} at position "
                                f"{later + 1} reads {resource}; the second "
                                f"play's printed number is the PRE-spend one "
                                f"and a reading that carries it through is "
                                f"the misread the seat named"),
                    })
    return out


def unresolved(chosen_line: Sequence[Mapping[str, Any]], *,
               index: Mapping[str, Mapping[str, Any]] | None = None,
               repo: Path | None = None) -> list[str]:
    """Printed titles in the line that no sheet prints. Disclosed, not fatal."""
    cards = index if index is not None else card_index(repo)
    return [str(p.get("card") or "") for p in (chosen_line or [])
            if normalise(p.get("card")) not in cards]


def summary(chosen_line: Sequence[Mapping[str, Any]], *,
            index: Mapping[str, Mapping[str, Any]] | None = None,
            repo: Path | None = None) -> dict[str, Any]:
    """The whole check as one blob, for a tester record to carry verbatim."""
    cards = index if index is not None else card_index(repo)
    hits = findings(chosen_line, index=cards)
    return {
        "flagged": bool(hits),
        "findings": hits,
        "unresolved_titles": unresolved(chosen_line, index=cards),
        "rule": ("a card whose printed text SPENDS or converts a meter may "
                 "not precede a card whose printed text READS that meter "
                 "without a seat reading the turn"),
    }


def resources_named(text: str) -> list[str]:
    """Public shim over the token table, for a caller writing prose."""
    return _resource_in(text)
