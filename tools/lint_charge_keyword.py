"""Every Kokomi face that names Charge must carry the Charge keyword tip.

WHY (run B6, R213 E1 / R215 D). Charge is a meter with no rules text on any
face. R215 D found that her Charge-gaining cards print the word and nothing on
screen says what it is; the blind seat then hit the same wall from the other
side, unprompted -- "Gorou's free attack granting Charge and Burst was not
explained in its displayed rules text". Kokomi slice 2 wrote the definition
(`KokomiRiderTips.ForCharge`) and attached it to the SPENDERS only, deferring
the gain faces to a wording-only pass. This lint is what keeps that pass from
having to happen a third time.

WHAT MAKES THIS A LINT RATHER THAN A TEST. The defect class is a word PRINTED
BY ONE SYSTEM AND EXPLAINED BY ANOTHER. The description builder puts the word
on the face; the tip attach rule puts the definition under it; nothing links
them, and a missing hover tip renders as NOTHING AT ALL -- there is no wrong
number to notice, no exception, no visual seam. Only a player can see it, and
only if they already know what they are missing. This is the join, run on every
push, over the files that actually ship.

THE RULE IS ONE RULE, IMPORTED. `gen_klee_cards.prints_charge_word` decides
what "names Charge" means for codegen; this lint imports it rather than
re-spelling it, so the generated faces and the hand-written ones cannot end up
held to two different definitions of the word.

BOTH DIRECTIONS.
  * A Kokomi face whose printed description names Charge and whose class does
    not attach `KokomiRiderTips.ForCharge` is the reported defect.
  * A face OUTSIDE Kokomi's reach whose description names Charge is the same
    defect wearing the other sign: the word names her meter, so a card no
    Kokomi player can hold is printing a term the game cannot explain there.
    Zero of those ship today.

WHAT IT DOES NOT ASSERT. Not the tip's WORDING, not the accrual rate, not that
the definition is correct -- `KokomiRiderTips` builds that from the constants
and the suite covers it. Not that a face SHOULD name Charge. The join only.

Run: python tools/lint_charge_keyword.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from gen_klee_cards import pascal, prints_charge_word   # noqa: E402

CARD_ROOT = REPO / "klee-mod" / "KleeCode" / "Cards"

# Kokomi's own cards live in one directory, generated and hand-written alike.
KOKOMI_DIR = CARD_ROOT / "Kokomi"
PROTOTYPE_DIR = CARD_ROOT / "Prototype" / "Generated"

PROTOTYPE_SHEET = REPO / "docs" / "prototype-surface.yaml"
# Inazuma companions are the pool `Muster` draws from, so they are faces a
# Kokomi player holds even though they are emitted beside everyone else's.
POOL_SHEETS = (REPO / "docs" / "inazuma-companions.yaml",)

# The call the attach rule emits. Matched as a call, not as a bare name, so a
# comment mentioning the method is not mistaken for the tip.
ATTACH = "KokomiRiderTips.ForCharge("

_STRING = re.compile(r'"((?:[^"\\]|\\.)*)"')


def _descriptions(text: str) -> list[str]:
    """Every description a card file ships, concatenation pieces joined.

    Generated files spell the row as one literal; the hand-written ones build
    it with `+` across several lines, and a single-literal scrape would read
    those as having no description at all -- which is exactly the direction
    that would make this lint quietly pass on the cards it was written for. So
    the argument is taken whole, by paren depth, and its literals joined.
    """
    out: list[str] = []
    for match in re.finditer(r'\(\s*"description"\s*,', text):
        depth = 1
        i = match.end()
        while i < len(text) and depth:
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
            i += 1
        out.append(" ".join(_STRING.findall(text[match.end():i - 1])))
    return out


def kokomi_classes() -> set[str]:
    """Class names that are Kokomi's, from the two sheets that say so."""
    names: set[str] = set()
    for row in yaml.safe_load(
            PROTOTYPE_SHEET.read_text(encoding="utf-8")) or []:
        if row.get("character") == "kokomi":
            names.add(pascal(row["id"]))
    for sheet in POOL_SHEETS:
        for row in yaml.safe_load(sheet.read_text(encoding="utf-8")) or []:
            names.add(pascal(row["id"]))
    return names


def _is_kokomis(path: Path, kokomi_dir: Path, classes: set[str]) -> bool:
    if kokomi_dir in path.parents:
        return True
    return path.stem in classes


def findings(root: Path = CARD_ROOT,
             classes: set[str] | None = None) -> list[str]:
    classes = kokomi_classes() if classes is None else classes
    kokomi_dir = root / "Kokomi"
    out: list[str] = []
    for path in sorted(root.rglob("*.cs")):
        text = path.read_text(encoding="utf-8")
        named = [d for d in _descriptions(text) if prints_charge_word(d)]
        if not named:
            continue
        rel = path.relative_to(root).as_posix()
        if not _is_kokomis(path, kokomi_dir, classes):
            out.append(
                f"{rel}: names Charge on a face outside Kokomi's reach, where "
                f"nothing defines the word: {named[0]!r}")
        elif ATTACH not in text:
            out.append(
                f"{rel}: names Charge but does not attach {ATTACH.rstrip('(')}"
                f" -- {named[0]!r}")
    return out


def main() -> int:
    bad = findings()
    for line in bad:
        print(line)
    if bad:
        print(f"\n{len(bad)} face(s) name Charge without the keyword tip.")
        return 1
    print("lint_charge_keyword: every face naming Charge carries the keyword.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
