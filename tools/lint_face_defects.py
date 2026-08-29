"""EB-169: the funnel's open-face-defect register may not go stale.

WHAT IT GUARDS. `understudy/face_defects.OPEN_FACE_DEFECTS` names cards whose
printed or runtime meaning is currently WRONG, and the funnel refuses to stage
or grade a board holding one. Every entry cites the `BACKLOG.md` row that owns
the defect. This lint joins the two: an entry whose EB id is not an OPEN row in
`docs/current/BACKLOG.md` is STALE, and stale means the defect was fixed, the
row left HEAD (house norm: closed items leave HEAD) and nobody deleted the
entry beside it.

WHY THAT DIRECTION IS THE DANGEROUS ONE. A register that over-refuses looks
like a working register: every packet naming the card is refused, the refusal
names a card that is fine, and the only symptom is a slice that cannot stage
the board it needs. The failure is silent and it argues for itself. So the
closing discipline is mechanical rather than remembered -- exactly the rot
semantics `tools/lint_register_ids.py` puts on `OPEN_IDS`.

WHAT IT DOES NOT ASSERT. Not that a defect is real, not that the card is
misprinted today, not that the register is COMPLETE -- no tool can know what
nobody has written down. The register is curated by hand and this checks its
one mechanical property.

An EMPTY register passes, and says so. That is the shipped state: `EB-164`,
the defect the register was built for, is closed.

Run: python tools/lint_face_defects.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from understudy import face_defects   # noqa: E402

BACKLOG = REPO / "docs" / "current" / "BACKLOG.md"

# A register row: a leading pipe, then the id in backticks. The same shape
# `lint_register_ids` reads, kept narrow on purpose -- a prose MENTION of an id
# is not a row, and a register whose ids resolve against prose would keep an
# entry alive on the strength of a sentence in somebody's rationale.
ROW = re.compile(r"^\|\s*`([A-Z][A-Z0-9]*-?\d+)`\s*\|")


def open_rows(path: Path = BACKLOG) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return {m.group(1) for line in text.splitlines()
            if (m := ROW.match(line))}


def findings(register: dict | None = None,
             rows: set[str] | None = None) -> list[str]:
    reg = face_defects.OPEN_FACE_DEFECTS if register is None else register
    have = open_rows() if rows is None else rows
    out: list[str] = []
    for card_id, body in reg.items():
        eb = str(body.get("eb") or "")
        if not eb:
            out.append(f"{card_id}: the entry cites no backlog id. Every "
                       f"entry names the row that OWNS the defect")
            continue
        if eb not in have:
            out.append(
                f"{card_id}: cites {eb}, which is not an open row in "
                f"{BACKLOG.relative_to(REPO).as_posix()}. Either the defect "
                f"was fixed and the row left HEAD -- in which case delete "
                f"this entry, that is the closing discipline -- or the id is "
                f"a typo")
        if not str(body.get("defect") or "").strip():
            out.append(f"{card_id}: the entry states no defect. One line, in "
                       f"the vocabulary of what a blind reader gets wrong")
        if not (body.get("titles") or ()):
            out.append(f"{card_id}: the entry names no printed title, so a "
                       f"packet -- which prints titles, not ids -- cannot be "
                       f"matched against it")
    return out


def main() -> int:
    bad = findings()
    for line in bad:
        print(f"FINDING: {line}")
    if bad:
        print(f"\n{len(bad)} finding(s).")
        return 1
    n = len(face_defects.OPEN_FACE_DEFECTS)
    if not n:
        print("face-defect register OK: EMPTY, which is the correct state -- "
              "no card the funnel can stage has an open printed/runtime "
              "defect. The refusal path is live either way "
              "(understudy/face_defects.py).")
    else:
        print(f"face-defect register OK: {n} entr(ies), every cited backlog "
              f"row still open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
