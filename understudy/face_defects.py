"""EB-169: the funnel PREFLIGHT register -- cards with an OPEN defect that
changes what their face MEANS.

WHY THIS FILE EXISTS, IN ONE PARAGRAPH
--------------------------------------
Round 2 of the Kokomi slice staged *All Streams Flow to the Sea* on all eleven
boards while `EB-164` sat OPEN against exactly that face: the printed number
already folded Charge in, and a second sentence claimed the fold again, so a
reader who did the arithmetic honestly got 13 where the card deals 9. Four
blind graders and the pair reviewer all read it that way. Seven refusals were
manufactured out of a defect the repo already knew about and had written down.
Nothing in the funnel joined those two facts, because nothing was asked to.

This register is the join. It names the cards whose printed or runtime meaning
is currently WRONG, each with the backlog id that owns the defect, and the
funnel consults it BEFORE a game is launched. A packet that would have carried
a known-misleading face is refused as `open_face_defect` instead of being
graded, replayed, pair-read and then discovered at the end.

THE REGISTER IS EMPTY, AND THAT IS THE CORRECT STATE
-----------------------------------------------------
`EB-164` is CLOSED -- eighteen faces re-worded at the generator, no printed
number moved, and `tools/lint_face_scaling.py` on the ci lane refuses a face
that states a scaling twice. There is no other open face/runtime defect against
a card the funnel can stage, so `OPEN_FACE_DEFECTS` below holds nothing. An
empty register is not a dormant one: the refusal path is live, a red fixture
proves it bites, and `tools/lint_face_defects.py` proves every id in it is an
OPEN row in `docs/current/BACKLOG.md`.

THE CLOSING DISCIPLINE
-----------------------
An entry's `eb` MUST be an open row in BACKLOG. When the defect is fixed the
row leaves HEAD, and an entry pointing at a row that is gone is STALE -- the
lint fails, and the fix is to delete the entry in the same commit as the row.
Exactly the rot semantics `tools/lint_register_ids.py` puts on `OPEN_IDS`, and
for the same reason: a register nobody is forced to empty fills up with lies.

WHAT DOES *NOT* BELONG HERE
----------------------------
Not a balance worry, not a card somebody dislikes, not a face that is merely
terse. The bar is a DEFECT that changes what the face means to a reader who
has only the printed page -- a stated number that is not the number the game
pays, a keyword that does not do what it says, a mode that resolves as the
other mode. Anything else is a `QUEUE.md` call or a `BACKLOG.md` row, and
neither of those refuses a packet.

Nothing here rates a card. Guardrail-7 is unchanged.
"""

from __future__ import annotations

from typing import Any, Iterable

# ONE folder, and it is the one the rest of the funnel already uses. A second
# spelling of "is this the same card" is the way a register stops matching the
# thing it is supposed to refuse.
from understudy.scenario import card_key

# ---------------------------------------------------------------------------
# THE REGISTER.
#
# Keyed by CARD ID -- the sheet's own spelling, or the mod's `KLEEMOD-` one;
# `card_key` folds the difference. Each entry carries three things and no
# fourth:
#
#   `eb`      the backlog id that OWNS the defect. Must be an OPEN row in
#             docs/current/BACKLOG.md (lint_face_defects.py).
#   `titles`  the printed title(s) the defect reaches, as a blind reader sees
#             them. Both the id and every title are matched, because a packet
#             prints titles and a turn file names ids.
#   `defect`  ONE line, in the vocabulary of what the reader gets wrong.
#
# EMPTY BY DESIGN, 2026-08-28. The founding entry would have been:
#
#     "all_streams_flow": {
#         "eb": "EB-164",
#         "titles": ("All Streams Flow to the Sea",),
#         "defect": "the printed damage already folds Charge in and a second "
#                   "sentence claims the fold again, so an honest reader adds "
#                   "it twice and reads 13 where the card deals 9",
#     },
#
# and it is not here because `EB-164` is CLOSED. It is kept in this comment as
# the worked shape of an entry, not as a live row.
# ---------------------------------------------------------------------------

OPEN_FACE_DEFECTS: dict[str, dict[str, Any]] = {}

# The rule name a refusal is filed under, so a caller never spells it inline.
RULE = "open_face_defect"

WHY = ("a card in the hand has an OPEN defect against its printed or runtime "
       "meaning, so a blind grader would be reading a face the repo already "
       "knows is wrong")


def entries() -> dict[str, dict[str, Any]]:
    """The register, copied. Callers get data, never the module's own dict."""
    return {cid: dict(body) for cid, body in OPEN_FACE_DEFECTS.items()}


def _names(card_id: str, body: dict[str, Any]) -> list[str]:
    return [card_id] + [str(t) for t in (body.get("titles") or ())]


def hits(names: Iterable[str],
         register: dict[str, dict[str, Any]] | None = None
         ) -> list[dict[str, Any]]:
    """Every registered card that `names` mentions, in register order.

    `names` is whatever the caller has: a turn file's staged card ids, a
    packet's printed hand titles, a grader's `chosen_line`. Matching is by
    `card_key`, so an id, a loc key and a printed title all find the same row.
    """
    reg = OPEN_FACE_DEFECTS if register is None else register
    seen = {card_key(str(n)) for n in names}
    out: list[dict[str, Any]] = []
    for card_id, body in reg.items():
        matched = [n for n in _names(card_id, body) if card_key(n) in seen]
        if matched:
            out.append({"card": card_id, "eb": str(body.get("eb") or ""),
                        # WHAT THE BOARD SAID, and separately WHAT A READER
                        # SEES. The caller may have matched on an id; a
                        # refusal that printed only that leaves the human
                        # looking for a title that is not in the message.
                        "matched": matched[0],
                        "titles": [str(t) for t in (body.get("titles") or ())],
                        "defect": str(body.get("defect") or "")})
    return out


def refusal(found: list[dict[str, Any]]) -> str:
    """The refusal text: the rule, then one line per card naming its EB id.

    NAMES THE PRINTED TITLE, THE ID AND THE ROW, always. "This packet is
    unsafe" sends a reader to grep; "All Streams Flow to the Sea
    (all_streams_flow) -- EB-164" sends them to the row.
    """
    lines = [f"{RULE}: {WHY}"]
    for h in found:
        printed = " / ".join(h.get("titles") or []) or h["matched"]
        lines.append(f"  {printed} ({h['card']}, staged as {h['matched']}) "
                     f"-- {h['eb']}: {h['defect']}")
    lines.append("  Fix the defect and close its row, or stage a board that "
                 "does not hold the card. A graded packet may not carry one.")
    return "\n".join(lines)
