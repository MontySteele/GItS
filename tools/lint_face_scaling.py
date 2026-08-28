"""A card face states a scaling EXACTLY ONCE.

WHY (Kokomi slice 1 round 2, 2026-08-28, EB-164). Seventeen generated faces
printed a number that already carried its rider -- rendered through a
`Calculated*` var, the multiplier read before the card resolves -- and then
asserted the scaling AGAIN in a following sentence: "Deal 9 damage. Scales
with [gold]Charge[/gold]." A reader can only take the second sentence as "and
it will scale further", so the rider gets counted twice. Four of eleven blind
graders and the pair reviewer read *All Streams Flow to the Sea* as 13 where
the game deals 9; the phantom four manufactured a lethal line and seven
`intent_insensitive` refusals, three of them on SHIPPED control halves.
`understudy.staged_turn execute` settled it live: Seapunk 22 HP -> 1.

THE RULE THIS ENFORCES, one for the whole roster and stated in
`tools/gen_klee_cards.py`'s module docstring:

  (1) the scaler IS in the printed number -> the source is named in the
      number's own sentence as ", already including <source>", and NOTHING
      else on the face asserts that the card scales;
  (2) the scaler is NOT in the printed number (the count does not exist until
      the card resolves) -> the per-unit RATE is printed beside the number
      (R215 C), and again nothing asserts scaling separately.

WHAT MAKES THIS A LINT RATHER THAN A TEST. The number and the sentence are
produced by different limbs of the description builder -- the amount by a
`Calculated*` token chosen from the rider predicates, the sentence by an
independent append -- and neither knows what the other did. That is the same
join `lint_burst_legibility.py` guards, one class over, and it can only be
seen by reading the SHIPPED string. So this reads the committed C#, not a
fresh call to the builder, and it covers hand-written faces too: the defect
does not care who typed the string.

BOTH SIGNS. A folded number that also asserts scaling double-counts. A face
claiming "already including" with no calculated amount to include it IN is the
same defect wearing the other sign -- a promise that a flat number is not
flat.

WHAT IT DOES NOT ASSERT. Not the rate, not the source's spelling, not whether
a rider should have been rehomed at all. Only that the face says it once.

Run: python tools/lint_face_scaling.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CARD_ROOT = REPO / "klee-mod" / "KleeCode" / "Cards"

# The printed amount that already carries its rider. Every rehomed rider on
# every profile renders through one of these tokens.
CALC_RE = re.compile(r"\{Calculated\w+")

# The clause that states a fold, and the ONLY way a face may state one.
FOLD = "already including"

# Sentences that assert a scaling the number has already made. Each of these
# was live on a shipped face before EB-164; they are listed by their actual
# shipped text rather than by a loose "scales" search, so that a legitimate
# use of the word in flavour or in a Power's own body does not trip the lint.
ASSERTIONS = (
    "Scales with",
    "Bonus damage vs.",
)

# The shipped string, read out of the class's Localization block -- the same
# scrape lint_burst_legibility.py and tools/render_card_gallery.py do, and for
# the same reason: what a player sees is the committed file.
_DESC_RE = re.compile(r'\(\s*"description"\s*,\s*((?:\s*\+?\s*"(?:[^"\\]|\\.)*")+)')
_PIECE_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')


def shipped_descriptions() -> dict[str, str]:
    """class name -> the description string its Localization block ships.

    Concatenated string literals are joined, because two of the roster's
    hand-written faces are written that way and the defect straddled the
    concatenation on one of them (`let_the_people_rejoice`).
    """
    out: dict[str, str] = {}
    for path in sorted(CARD_ROOT.rglob("*.cs")):
        text = path.read_text(encoding="utf-8")
        match = _DESC_RE.search(text)
        if not match:
            continue
        for cls in re.findall(
                r"^\s*public\s+sealed\s+class\s+(\w+)\s*:", text, re.M):
            out.setdefault(cls, "".join(_PIECE_RE.findall(match.group(1))))
    return out


def findings(shipped: dict[str, str] | None = None) -> list[str]:
    """The join. `shipped` is injectable so the red half of this lint's test
    can force the defect on SYNTHETIC data rather than by writing a probe class
    into the live tree (test_sheet_lints.py's rule)."""
    shipped = shipped_descriptions() if shipped is None else shipped
    out: list[str] = []

    for cls, desc in sorted(shipped.items()):
        calculated = bool(CALC_RE.search(desc))
        folds = desc.count(FOLD)

        if calculated:
            for phrase in ASSERTIONS:
                if phrase in desc:
                    out.append(
                        f"DOUBLE-STATED SCALING: {cls} prints a calculated "
                        f"amount that already carries its rider AND says "
                        f"{phrase!r} beside it, so the rider reads as an "
                        f"addition on top of a number that already made it. "
                        f"This is EB-164 exactly. Fold the source into the "
                        f"number's own sentence as "
                        f"'..., {FOLD} <source>' and drop the assertion. "
                        f"Got {desc!r}")
        elif folds:
            out.append(
                f"PHANTOM FOLD: {cls} says {FOLD!r} but prints no calculated "
                f"amount for anything to be included IN, so the face claims a "
                f"flat number is not flat. Got {desc!r}")

        if folds > 1:
            out.append(
                f"SCALING STATED TWICE: {cls} carries {folds} {FOLD!r} "
                f"clauses; a face states its scaling once. Got {desc!r}")
    return out


def main() -> int:
    shipped = shipped_descriptions()
    bad = findings(shipped)
    for line in bad:
        print(f"FINDING: {line}")
    if bad:
        print(f"\n{len(bad)} finding(s).")
        return 1
    folded = sum(1 for desc in shipped.values() if FOLD in desc)
    print(f"face scaling OK: {folded} face(s) state a fold once and none "
          f"state one twice, of {len(shipped)} card class(es) read")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
