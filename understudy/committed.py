"""The archetype-committed DRAFT arm — R99/4b, behind a flag.

WHAT THIS IS. Track B could not grade R90/1b's Fanfare early-half prediction,
and the reason was the instrument rather than the sample: B2 measures cards,
and every deck the soak has ever recorded is a mixed deck (224 of 299 turn-1
plays were `generic`). A per-turn archetype total taken from a deck that
drafted little of that archetype cannot separate *this archetype produces too
little* from *this deck has little of it*, and the claim is about the first.

So this module is the controlled arm: a soak may DECLARE an archetype, and the
draft then takes that archetype's cards when they are on offer. Run N of those
and the resulting decks are decks somebody could point at and call Fanfare
decks — which is the precondition the grade was missing.

THE FOUR RULES IT IS WRITTEN UNDER, in the order that breaking them costs:

1. **The flag is the ONLY delta.** `commit=None` is baseline policy_v1, byte
   for byte, and `tier0/tests/test_understudy_committed.py` proves it by
   replaying every recorded Phase-0 state through both settings and comparing
   the logged decisions. R98's numbers stay comparable to a later baseline
   soak's because nothing about a baseline soak changed.
2. **It is a policy VARIANT, not a policy change.** One variable per
   measurement window: the pilot is untouched, the map arm is untouched, the
   rest arm is untouched, the combat ladder is untouched. Only card
   ACQUISITION moves, and only when an archetype was declared.
3. **It reads the design sheets, not the drafter.** `docs/*-cards.yaml`'s
   `archetypes` field is the same source `tools/track_b_curves.py` splits B2
   by, which is the point: the arm that builds the deck and the reader that
   grades it must agree on what a Fanfare card IS, or the grade is measuring
   the disagreement. No drafter price is read and no drafter code path is
   consulted for membership.
4. **The sim still scores.** Within the archetype the sim's own
   `score_offer` picks, and when the archetype is absent from an offer the
   sim's `assigned_policy` decides unchanged — including its right to skip.
   Commitment is a PRIORITY over the ordering, not a replacement for the
   valuation, so a divergence between this arm and baseline stays readable as
   "the commitment took this card" rather than as a second scorer's opinion.

WHAT IT IS NOT. It is not evidence about difficulty, a winrate, or a design
finding. Guardrail 7 applies to it exactly as it applies to every other number
this directory produces, and one notch harder: a committed arm is a bot-limited
floor measured under a constraint a person never plays under.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

REPO = Path(__file__).resolve().parent.parent
SHEETS = ("furina-cards.yaml", "klee-cards.yaml", "kokomi-cards.yaml")

# Declarable archetypes. `fanfare` and `salon` are the two the gate package
# names; `spotlight` is here because the sheets carry it and refusing a word
# the data already uses would be an arbitrary limit. `generic` is deliberately
# NOT declarable: committing to no archetype is what baseline already is.
COMMITTABLE = ("fanfare", "salon", "spotlight")

_TABLE: dict[str, tuple[str, ...]] | None = None


def archetype_table() -> dict[str, tuple[str, ...]]:
    """Card display NAME -> declared archetypes, off the design sheets.

    Cached per process: the sheets do not change under a running soak, and a
    per-offer YAML parse would put a file read on the decision path.
    """
    global _TABLE
    if _TABLE is not None:
        return _TABLE
    import yaml                                   # in the suite's dependencies

    out: dict[str, tuple[str, ...]] = {}
    for sheet in SHEETS:
        path = REPO / "docs" / sheet
        if not path.exists():
            continue
        rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        for row in rows:
            name = str(row.get("name") or "").strip()
            if not name:
                continue
            arch = tuple(str(a) for a in (row.get("archetypes") or ()))
            out[name] = arch
            out[name + "+"] = arch                # an upgrade is the same card
    _TABLE = out
    return out


def is_committed(card: Any, archetype: str,
                 table: dict[str, tuple[str, ...]] | None = None) -> bool:
    """Does this offer belong to the declared archetype?

    Membership is the sheet's `archetypes` list — the card's own declaration,
    not an inference from its text and not a drafter score. A card with no
    sheet row (every base-game and colorless card) belongs to nothing, which is
    correct: those are exactly the cards a committed deck is trying not to be
    made of.
    """
    if not archetype:
        return False
    table = table if table is not None else archetype_table()
    name = str(getattr(card, "name", "") or "").strip()
    return archetype in table.get(name, ())


def prefer(offers: Sequence[Any], archetype: str, score) -> Any | None:
    """The best offer of the declared archetype, or None if there is none.

    `score` is the sim's own scorer, passed in rather than imported so this
    module has no opinion about valuation at all — it orders what it is given
    and returns the winner. Ties break on the sim's score and then on offer
    order, which keeps the arm deterministic without consuming a policy roll:
    a commitment that needed randomness would be a second variable.
    """
    table = archetype_table()
    hits = [(i, c) for i, c in enumerate(offers)
            if is_committed(c, archetype, table)]
    if not hits:
        return None
    return max(hits, key=lambda pair: (score(pair[1]), -pair[0]))[1]


def normalise(declared: str | None) -> str | None:
    """`None` for "no commitment", a lowercase archetype otherwise.

    Raises on a word that is not declarable rather than silently running a
    baseline soak under a committed label — a mislabelled arm is worse than a
    refused one, because the label is what the whole measurement is read by.
    """
    if declared is None:
        return None
    word = str(declared).strip().lower()
    if not word:
        return None
    if word not in COMMITTABLE:
        raise ValueError(
            f"{word!r} is not a declarable archetype; "
            f"choose one of {', '.join(COMMITTABLE)}")
    return word
