"""Every visible roster character must ship >= 1 Ancient-rarity pool card.

WHY (act-2 softlock, playtest 2026-07-23). The Darv ancient event rolls the
Dusty Tome relic ~50% of the time, and vanilla DustyTome.SetupForPlayer draws
a random CardRarity.Ancient card from the character's pool via
GetUnlockedCards. For a character whose pool holds no Ancient cards the draw
is empty, NextItem(...).Id NREs inside Darv.GenerateInitialOptions, the event
never builds its buttons, and the run softlocks on room entry. BaseLib's
ITomeCard shim only rescues characters that mark cards with it; the repo-side
invariant is simpler and vanilla-shaped: keep >= 1 Ancient card VISIBLE in
every roster character's pool.

Safe because generation filters upstream: reward rolls, transforms and shop
inventory all exclude CardRarity.Ancient (decompiled CardFactory), so an
Ancient pool card is reachable through Dusty Tome only.

The curated surface is KleeCode/RosterAncientCards.cs (house pattern: when a
defect is structurally invisible to the compiler, give it a ledger and a
lint). Checks, per character in CHARACTERS:
  1. the ledger property exists and lists >= 1 ModelDb.Card<T>() reference;
  2. every referenced class is declared under Cards/ with CardRarity.Ancient
     in its base(...) constructor call;
  3. the character's pool file actually concats its ledger property -- a
     detached ledger is not a gate;
  4. no referenced class also appears in the character's off-pool filter
     (off-pool cards are stripped from GetUnlockedCards, which would remake
     the empty-draw crash with the ledger looking green);
  5. EB-284: every PROTOTYPE ARM pool concats the same ledger. An arm's
     FilterThroughEpochs RETURNS its own roster and never reaches the
     character pool above, so under its flag the arm roster IS
     GetUnlockedCards -- and both arms shipped without the Ancient tail,
     which is how [USER]'s Klee run ended at the act-two Darv door.

Adding a roster character means adding a ledger property AND a CHARACTERS
row here; a property the table does not know about is a FINDING, not a skip.

Usage: python tools/lint_ancient_coverage.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CODE = REPO / "klee-mod" / "KleeCode"
LEDGER = CODE / "RosterAncientCards.cs"
CARD_ROOT = CODE / "Cards"

# character -> (pool file that must concat the ledger, off-pool filter file).
# Furina's off-pool class lives inside her pool file; the off-pool check
# scans ModelDb.Card<T> references, which the pool concat does not use.
CHARACTERS = {
    "Klee": (CODE / "KleeCardPool.cs", CODE / "KleeOffPoolCards.cs"),
    "Furina": (CODE / "FurinaCardPool.cs", CODE / "FurinaCardPool.cs"),
    "Kokomi": (CODE / "KokomiCardPool.cs", CODE / "KokomiCardPool.cs"),
}

# EB-284. THE SAME GATE ON THE ARMS, BECAUSE THEY REPLACE THE POOL THE GATE
# ABOVE CHECKS.
#
# `KleeCardPool.FilterThroughEpochs` and its Kokomi twin RETURN the arm's
# roster and never reach `base.FilterThroughEpochs`, so under a prototype arm
# the pool file's concat above is not the set `GetUnlockedCards` yields --
# the arm roster is. Both arms shipped without the Ancient tail, Darv's Dusty
# Tome roll drew nothing, and [USER]'s Klee run ended at the act-two door with
# an NRE inside `Darv.GenerateInitialOptions`. Checked file-by-file rather
# than by following the seam, for the reason the whole lint exists: the
# compiler cannot see an empty draw, so the invariant needs a ledger and a
# text gate.
#
# An arm pool listed here must concat its character's ledger property. Adding
# an arm means adding a row; a `*OverhaulRoster.cs` this table does not know
# about is caught by the sweep below rather than skipped.
ARM_POOLS = {
    "Klee": CODE / "Powers" / "Prototype" / "KleeOverhaulRoster.cs",
    "Kokomi": CODE / "Powers" / "Prototype" / "KokomiOverhaulRoster.cs",
}
ARM_POOL_GLOB = "Powers/Prototype/*OverhaulRoster.cs"
# The one `*OverhaulRoster.cs` that is NOT a character reward pool: the
# companion overhaul replaces a NATION's Universal companion roster, which
# Dusty Tome never draws from, so it has no Ancient to owe.
ARM_POOL_EXEMPT = {"CompanionOverhaulRoster.cs"}

PROPERTY_RE = re.compile(
    r"public\s+static\s+IReadOnlyList<CardModel>\s+(\w+)\s*=>")
MEMBER_RE = re.compile(r"ModelDb\.Card<(\w+)>\s*\(")
CLASS_RE = re.compile(r"public\s+sealed\s+class\s+(\w+)\s*:")
ANCIENT_CTOR_RE = re.compile(r":\s*base\s*\([^;]*CardRarity\.Ancient", re.S)


def property_block(text: str, name: str) -> str | None:
    """The source slice of one ledger property, ended by the next property."""
    match = re.search(
        rf"IReadOnlyList<CardModel>\s+{name}\s*=>(.*?)(?:IReadOnlyList<CardModel>|\Z)",
        text, re.S)
    return match.group(1) if match else None


def main() -> int:
    findings: list[str] = []

    if not LEDGER.is_file():
        print(f"FINDING: ancient ledger missing: {LEDGER.relative_to(REPO)}")
        return 1
    ledger_text = LEDGER.read_text(encoding="utf-8")
    ledger_properties = set(PROPERTY_RE.findall(ledger_text))

    for stray in sorted(ledger_properties - set(CHARACTERS)):
        findings.append(
            f"ledger property '{stray}' has no CHARACTERS row in this lint; "
            f"a character the gate does not know about is ungated.")

    # Class -> declared-Ancient, from every card source file.
    ancient_classes: set[str] = set()
    declared_classes: set[str] = set()
    for path in sorted(CARD_ROOT.rglob("*.cs")):
        text = path.read_text(encoding="utf-8")
        names = CLASS_RE.findall(text)
        declared_classes.update(names)
        if ANCIENT_CTOR_RE.search(text):
            # One card class per file is the repo convention; the ctor match
            # is file-scoped, so enforce the convention when it matters.
            if len(names) == 1:
                ancient_classes.add(names[0])
            else:
                findings.append(
                    f"{path.relative_to(REPO)}: CardRarity.Ancient file "
                    f"declares {len(names)} classes; the lint needs exactly "
                    f"one card class per ancient file to attribute rarity.")

    for character, (pool_file, offpool_file) in CHARACTERS.items():
        if character not in ledger_properties:
            findings.append(
                f"{character}: no '{character}' property in "
                f"RosterAncientCards.cs -- Darv's Dusty Tome roll softlocks "
                f"this character at the ancient screen.")
            continue

        block = property_block(ledger_text, character)
        members = MEMBER_RE.findall(block or "")
        if not members:
            findings.append(
                f"{character}: RosterAncientCards.{character} lists no "
                f"cards -- the Dusty Tome draw is empty and Darv softlocks.")
            continue

        for name in members:
            if name not in declared_classes:
                findings.append(
                    f"{character}: ledger references {name} but no such "
                    f"card class exists under Cards/.")
            elif name not in ancient_classes:
                findings.append(
                    f"{character}: {name} is in the ancient ledger but its "
                    f"constructor is not CardRarity.Ancient -- Dusty Tome "
                    f"will not see it.")

        if not pool_file.is_file():
            findings.append(f"{character}: pool file missing: {pool_file}")
        elif f"RosterAncientCards.{character}" not in pool_file.read_text(
                encoding="utf-8"):
            findings.append(
                f"{character}: {pool_file.name} does not concat "
                f"RosterAncientCards.{character}; the ledger is detached "
                f"from the pool and the gate is decorative.")

        if offpool_file.is_file():
            offpool_members = set()
            offpool_text = offpool_file.read_text(encoding="utf-8")
            # Scan only the off-pool class body when it shares a file with
            # the pool (Furina): everything from 'class FurinaOffPoolCards'.
            marker = offpool_text.find("OffPoolCards")
            if marker != -1:
                offpool_members = set(
                    MEMBER_RE.findall(offpool_text[marker:]))
            for name in members:
                if name in offpool_members:
                    findings.append(
                        f"{character}: {name} is both in the ancient ledger "
                        f"and the off-pool filter; off-pool cards never "
                        f"reach GetUnlockedCards, so the Dusty Tome draw is "
                        f"empty again.")

    # EB-284: the arm pools, which REPLACE the pools checked above.
    seen_arm_files: set[str] = set()
    for character, arm_file in ARM_POOLS.items():
        seen_arm_files.add(arm_file.name)
        if not arm_file.is_file():
            findings.append(
                f"{character}: arm pool file missing: "
                f"{arm_file.relative_to(REPO)}")
            continue
        if f"RosterAncientCards.{character}" not in arm_file.read_text(
                encoding="utf-8"):
            findings.append(
                f"{character}: {arm_file.name} does not concat "
                f"RosterAncientCards.{character}; the arm REPLACES the "
                f"character's pool, so under its flag Dusty Tome draws from "
                f"this list and an empty Ancient draw softlocks Darv.")
    for path in sorted(CODE.glob(ARM_POOL_GLOB)):
        if path.name in seen_arm_files or path.name in ARM_POOL_EXEMPT:
            continue
        findings.append(
            f"{path.relative_to(REPO)} is an arm pool this lint has no row "
            f"for -- add it to ARM_POOLS (or to ARM_POOL_EXEMPT, with the "
            f"reason it draws no Ancient).")

    for finding in findings:
        print(f"FINDING: {finding}")
    if findings:
        return 1
    covered = ", ".join(
        f"{c}={len(MEMBER_RE.findall(property_block(ledger_text, c) or ''))}"
        for c in CHARACTERS)
    print(f"ancient coverage: OK ({covered}; "
          f"arm pools {', '.join(sorted(ARM_POOLS))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
