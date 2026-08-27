"""Every card that GRANTS Burst Energy must print that it does.

WHY (playtest 2026-08-26, EB-152). [USER]: "Klee's cards that give Burst
energy are labelled, but Kokomi's are not." That was true and it was one
predicate: the generator's Burst reading was gated to rows on Klee's sheet
while `combat.play_card` and `KleeElementalHooks.AfterCardPlayed` paid the same
BURST_PER_SKILL_TAG to every character carrying a Burst meter. Thirteen of
Furina's faces and one of Kokomi's collected a real number that nothing on the
card said out loud.

WHAT MAKES THIS A LINT RATHER THAN A TEST. The defect class is a number that is
PAID BY ONE SYSTEM AND PRINTED BY ANOTHER, and the two systems key off
different things -- the payer off the `skill_tag` tag through the
`ISkillTagCard` marker, the printer off a string the description builder
assembles. Nothing links them, so they can drift in silence and only a player
can see it. This is the join, run on every push.

BOTH DIRECTIONS. A tagged card that does not print the reading is the defect
[USER] reported. An untagged card that DOES print it is the same defect wearing
the other sign -- a face promising 5 Burst Energy that no hook will ever pay --
and it is the one a careless edit to the description builder would introduce.

WHAT IT DOES NOT ASSERT. Not the AMOUNT of the meter, not the tag's
membership, not the `Elemental Skill` keyword badge (that rides
`CanonicalKeywords` and its own loc rows, and a card can legitimately carry the
badge). The reading only.

Run: python tools/lint_burst_legibility.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from gen_klee_cards import BURST_PER_SKILL_TAG, pascal   # noqa: E402

CARD_ROOT = REPO / "klee-mod" / "KleeCode" / "Cards"
SHEETS = (
    REPO / "docs" / "klee-cards.yaml",
    REPO / "docs" / "furina-cards.yaml",
    REPO / "docs" / "kokomi-cards.yaml",
    REPO / "docs" / "mondstadt-companions.yaml",
    REPO / "docs" / "fontaine-companions.yaml",
    REPO / "docs" / "inazuma-companions.yaml",
)

# The reading, exactly as `build_description` appends it. Built from the shared
# constant rather than spelled here: a lint that hard-codes the number it is
# guarding is a second place for that number to be wrong.
READING = f"[gold]Burst[/gold] +{BURST_PER_SKILL_TAG}."

# The shipped string, read out of the generated class's Localization block --
# the same scrape `tools/render_card_gallery.py` does, and for its reason: what
# a player sees is the committed file, not a fresh call to the builder.
_DESC_RE = re.compile(r'\(\s*"description"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\)')


def shipped_descriptions() -> dict[str, str]:
    """class name -> the description string its Localization block ships."""
    out: dict[str, str] = {}
    for path in sorted(CARD_ROOT.rglob("*.cs")):
        text = path.read_text(encoding="utf-8")
        for cls in re.findall(
                r"^\s*public\s+sealed\s+class\s+(\w+)\s*:", text, re.M):
            # One class per generated card file, and the roster/option files
            # carry no description at all -- so the first match in the file is
            # this class's, and a file with none simply does not appear.
            match = _DESC_RE.search(text)
            if match:
                out.setdefault(cls, match.group(1))
    return out


def tagged_ids() -> dict[str, Path]:
    """Every sheet row carrying `skill_tag`, by id, with the sheet it is on."""
    out: dict[str, Path] = {}
    for sheet in SHEETS:
        for row in yaml.safe_load(sheet.read_text(encoding="utf-8")) or []:
            if "skill_tag" in (row.get("tags") or ()):
                out[row["id"]] = sheet
    return out


def findings(tagged: dict[str, Path] | None = None,
             shipped: dict[str, str] | None = None) -> list[str]:
    """The join. Both arguments are injectable so the red half of this lint's
    test can force the defect on SYNTHETIC data rather than by writing a probe
    card into the live tree (test_sheet_lints.py's rule, learned the hard way
    when an orphaned probe file produced a phantom CI failure)."""
    tagged = tagged_ids() if tagged is None else tagged
    shipped = shipped_descriptions() if shipped is None else shipped
    out: list[str] = []

    tagged_classes = {pascal(card_id): (card_id, sheet)
                      for card_id, sheet in tagged.items()}

    for cls, (card_id, sheet) in sorted(tagged_classes.items()):
        desc = shipped.get(cls)
        if desc is None:
            continue        # blocked row: no class ships, nothing to print on
        if READING not in desc:
            out.append(
                f"SILENT BURST: {card_id!r} ({sheet.name}) carries `skill_tag`, "
                f"so playing it pays {BURST_PER_SKILL_TAG} Burst Energy -- and "
                f"{cls}'s face never says so. Expected {READING!r} in the "
                f"description; got {desc!r}. This is EB-152's defect exactly: "
                f"a number one system pays and another forgets to print.")

    for cls, desc in sorted(shipped.items()):
        if READING in desc and cls not in tagged_classes:
            out.append(
                f"PHANTOM BURST: {cls} prints {READING!r} but its sheet row "
                f"carries no `skill_tag`, so no hook will ever pay it. The "
                f"face is promising Burst Energy the card does not grant.")
    return out


def main() -> int:
    tagged = tagged_ids()
    shipped = shipped_descriptions()
    bad = findings(tagged, shipped)
    for line in bad:
        print(f"FINDING: {line}")
    if bad:
        print(f"\n{len(bad)} finding(s).")
        return 1
    printed = sum(1 for cls in map(pascal, tagged)
                  if READING in shipped.get(cls, ""))
    print(f"burst legibility OK: {printed} skill_tag card(s) print the "
          f"reading, of {len(tagged)} tagged sheet row(s) and "
          f"{len(shipped)} card class(es) read")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
