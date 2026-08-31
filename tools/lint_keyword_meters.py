"""Every face that names a METER must carry that meter's keyword tip, and
every face that names a RESOURCE must print it as a keyword.

WHY (run B6, R213 E1 / R215 D). The mod has two named meters and neither had
rules text on any face. R215 D found that Kokomi's Charge-gaining cards print
the word and nothing on screen says what it is; the blind seat then hit both
meters from the other side, unprompted -- "Gorou's free attack granting Charge
and Burst was not explained in its displayed rules text", and Burst
"accumulated alongside that plan, although I never saw how to spend it".
Kokomi slice 2 wrote the Charge definition and attached it to the SPENDERS
only; the Burst keyword did not exist at all. This lint is what keeps either
pass from having to happen a third time.

WHAT MAKES THIS A LINT RATHER THAN A TEST. The defect class is a word PRINTED
BY ONE SYSTEM AND EXPLAINED BY ANOTHER. The description builder puts the word
on the face; the tip attach rule puts the definition under it; nothing links
them, and a missing hover tip renders as NOTHING AT ALL -- there is no wrong
number to notice, no exception, no visual seam. Only a player can see it, and
only if they already know what they are missing. This is the join, run on every
push, over the files that actually ship.

ONE FILE, ONE ROW PER METER. It started as the Charge lint and grew its second
row the same week, which is the argument for a table rather than a second
file: the two meters have the same failure mode and the same evidence, and a
third meter should be a ROW here -- word, predicate, attach call, whose faces
may print it -- rather than a third near-copy of this reasoning. The rows
differ in exactly one property, REACH, and it is a data field rather than a
code path.

THE RULES ARE THE GENERATOR'S RULES, IMPORTED. `gen_klee_cards` decides what
"names Charge" and "names Burst" mean for codegen; this lint imports those
predicates rather than re-spelling them, so the generated faces and the
hand-written ones cannot end up held to two different definitions of a word.

BOTH DIRECTIONS.
  * A face whose printed description names a meter and whose class does not
    attach that meter's tip is the reported defect.
  * For a meter with a REACH -- Charge is Kokomi's alone -- a face outside that
    reach naming it is the same defect wearing the other sign: the word names
    her meter, so a card no Kokomi player can hold is printing a term the game
    cannot explain there. Zero of those ship today. Burst has NO reach: all
    three characters own a Burst meter and its tip is roster-wide, so that
    direction does not apply and the row says so with `owner=None`.

WHAT IT DOES NOT ASSERT. Not a tip's WORDING, not the accrual rates, not that
a definition is correct -- the tip classes build those from the constants and
the suite covers them. Not that a face SHOULD name a meter. The join only.

THE SECOND CHECK: GOLDING (`EB-258`)
------------------------------------
The tip half above answers "is the word explained". This half answers the
question one step earlier: "does the word LOOK like a term at all". A resource
printed in body text is a noun; the same resource in `[gold]` is a keyword the
reader knows to hover. Every resource on the roster's faces is gold-wrapped
except where somebody typed the sentence by hand and forgot -- and the forget
is invisible, because an un-golded word renders as perfectly ordinary prose.
Same failure shape as the tip join, which is why it is a second table in this
file rather than a seventh lint: one word, two surfaces that have to agree
about it.

It is here rather than in the METERS table because the two properties are
NOT co-extensive. `Energy` is a resource the whole roster prints and no tip
defines -- it is the base game's own, and a tip requirement on it would be
false. `Encore` and `Fanfare` are Furina's and have their own explanations.
So the rows are separate: `METERS` says "this word needs a definition
attached", `RESOURCE_WORDS` says "this word is a keyword wherever it is
printed", and a word can be in either, both, or neither.

`EB-258`'s provenance: *Undertow* shipped `Sly: Gain 1 Energy` un-golded while
`SaltLine` printed `[gold]Exhaust[/gold]` and `DriftwoodCharm` printed
`[gold]Charge[/gold]` beside it, and `gen_klee_cards.py` carried a comment
calling `swelling_overture` "the only un-golded resource keyword on a face" --
false by then in thirteen places. A comment is not a lock, which is the whole
argument for this half.

WHAT THE GOLDING HALF DOES NOT ASSERT. Not `Block`, and that is a deliberate
line rather than an oversight: Block is the base game's defensive stat, it is
un-golded on seventeen faces today, and whether it reads as a keyword at all
is a taste call on somebody else's roster -- filed, not fixed here. Not the
SENTENCE a resource sits in, not whether the face should name it, and not
markup outside a face (a hover tip is not a face).

Run: python tools/lint_keyword_meters.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from gen_klee_cards import (   # noqa: E402
    pascal, prints_burst_word, prints_charge_word)

CARD_ROOT = REPO / "klee-mod" / "KleeCode" / "Cards"

# Kokomi's own cards live in one directory, generated and hand-written alike.
KOKOMI_DIR = CARD_ROOT / "Kokomi"
PROTOTYPE_DIR = CARD_ROOT / "Prototype" / "Generated"

PROTOTYPE_SHEET = REPO / "docs" / "prototype-surface.yaml"
# Inazuma companions are the pool `Muster` draws from, so they are faces a
# Kokomi player holds even though they are emitted beside everyone else's.
POOL_SHEETS = (REPO / "docs" / "inazuma-companions.yaml",)


@dataclass(frozen=True)
class Meter:
    """One meter's join: the word a face prints, and the tip that defines it."""

    word: str
    prints: Callable[[str], bool]
    # The call the attach rule emits. Matched as a CALL, not as a bare name, so
    # a comment mentioning the method is not mistaken for the tip.
    attach: str
    # Whose faces may print the word. None = roster-wide, no reach check.
    owner: str | None


METERS = (
    Meter("Charge", prints_charge_word, "KokomiRiderTips.ForCharge(",
          owner="Kokomi"),
    Meter("Burst", prints_burst_word, "KleeCardTooltips.ForBurst(",
          owner=None),
)

# `EB-258`. The resources a face prints as KEYWORDS, longest first so
# "Burst Energy" is consumed before the bare "Energy" inside it.
RESOURCE_WORDS = (
    "Burst Energy",
    "Charge",
    "Encore",
    "Fanfare",
    "Sparks",
    "Spark",
    "Energy",
)

_STRING = re.compile(r'"((?:[^"\\]|\\.)*)"')

# A `[gold]...[/gold]` span. Non-greedy: the faces nest nothing, and a greedy
# read would swallow every word between the first open and the last close --
# which would make this half pass on exactly the faces it was written for.
_GOLD = re.compile(r"\[gold\](.*?)\[/gold\]")

# An interpolation token: `{Sparks:diff()}`, `{Cards:plural:|s}`,
# `{SpotlightSystem.FanfarePerCenterStagePlay}`. These carry VARIABLE NAMES
# that happen to spell resources, and the player never sees the name -- only
# the number it resolves to. Golding one would put markup inside a token.
_VAR = re.compile(r"\{[^{}]*\}")


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


def ungolded_resources(description: str) -> list[str]:
    """The resource words this face prints as plain prose, in order.

    Golded spans and interpolation tokens are blanked before the search, so a
    word inside either is invisible here -- that is what "already a keyword"
    and "not player-visible text" mean, spelled once.
    """
    chars = list(description)
    for span in _GOLD.finditer(description):
        for i in range(span.start(1), span.end(1)):
            chars[i] = "\0"
    for token in _VAR.finditer(description):
        for i in range(token.start(), token.end()):
            chars[i] = "\0"
    masked = "".join(chars)

    out: list[str] = []
    for word in RESOURCE_WORDS:
        for hit in re.finditer(r"\b" + re.escape(word) + r"\b", masked):
            out.append(word)
            # Consume it, so the "Energy" inside an un-golded "Burst Energy"
            # is reported once, under the longer name that is the real word.
            masked = masked[:hit.start()] + "\0" * len(word) + \
                masked[hit.end():]
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
        descriptions = _descriptions(text)
        rel = path.relative_to(root).as_posix()
        for meter in METERS:
            named = [d for d in descriptions if meter.prints(d)]
            if not named:
                continue
            # Reach is checked against Kokomi because she owns the only meter
            # that has a reach. A third meter scoped to somebody else needs
            # this to become a per-owner lookup; until then a second sheet
            # reader would be a second place for one set to be described
            # wrongly.
            if (meter.owner is not None
                    and not _is_kokomis(path, kokomi_dir, classes)):
                out.append(
                    f"{rel}: names {meter.word} on a face outside "
                    f"{meter.owner}'s reach, where nothing defines the word: "
                    f"{named[0]!r}")
            elif meter.attach not in text:
                out.append(
                    f"{rel}: names {meter.word} but does not attach "
                    f"{meter.attach.rstrip('(')} -- {named[0]!r}")
        # `EB-258`, the golding half. Per description rather than per file:
        # a card with an upgraded face can have the markup on one and not the
        # other, and the reader sees whichever one they hold.
        for description in descriptions:
            for word in ungolded_resources(description):
                out.append(
                    f"{rel}: prints {word} as plain text, not a "
                    f"[gold]{word}[/gold] keyword -- {description!r}")
    return out


def main() -> int:
    bad = findings()
    for line in bad:
        print(line)
    if bad:
        print(f"\n{len(bad)} face(s) name a meter without its keyword tip, "
              "or a resource without its markup.")
        return 1
    words = " and ".join(meter.word for meter in METERS)
    print(f"lint_keyword_meters: every face naming {words} carries the "
          f"keyword, and all {len(RESOURCE_WORDS)} resource words are golded "
          "wherever a face prints them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
