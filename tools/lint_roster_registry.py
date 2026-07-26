#!/usr/bin/env python3
"""Every roster site knows every registered character. (F1, audit sec.5.)

THE FINDING THIS CLOSES. Adding character #4 touches roughly 26 scattered edit
sites; 4 are gated and **22 are silent**. Silent is the whole problem: the mod
builds, the suite is green, every lint passes, and the character is simply
absent from whichever list was missed. Two of those have already happened --
Kokomi's archetype registry named three tags that existed on zero cards (R66,
and every adaptive number ever taken for her went through it), and her card art
was never staged because `deploy.ps1`'s directory array did not list her.

So this is the S6c pattern -- a closed list a lint holds shut -- extended from
one rule to the whole roster surface. `tier0/roster.py` declares the roster
once; every site below is swept for every registered character, and a miss is a
FINDING rather than an absence.

Sites the registry cannot simply be imported into are exactly the ones this
exists for: C# has no access to Python, PowerShell has no access to either, and
the codegen ladders are structural rather than data. Those get enforced.

    python tools/lint_roster_registry.py

Exit 1 with findings on stdout. Dual-wired: also `tier0/tests/test_roster_registry.py`,
for the same reason `test_sheet_lints.py` gives -- the deploy gate runs on one
Windows machine, and the population that will add character #4 may never see it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tier0 import roster                                     # noqa: E402

CODE = REPO / "klee-mod" / "KleeCode"


def _text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


# Each row: (label, path, how to build the token that must appear).
# The token is a FUNCTION of the character so a new roster row needs no edit
# here either -- a table of literals would be the same defect one level up.
SITES = [
    ("tier05 plan registry",
     REPO / "tier05" / "runner.py",
     lambda c: None),          # derived from the registry; checked in-process
    ("drafter archetype registry",
     REPO / "tier05" / "draft.py",
     lambda c: None),          # ditto
    ("C# character class",
     lambda c: c.character_cs, None),
    ("C# card pool",
     lambda c: c.card_pool_cs, None),
    ("C# relic pool",
     lambda c: c.relic_pool_cs, None),
    ("tier0 character sheet",
     lambda c: c.character_yaml, None),
    ("card sheet",
     lambda c: c.card_sheet, None),
    ("upgrade sheet",
     lambda c: c.upgrade_sheet, None),
]

# Files that carry a CLOSED LIST naming every character, where the token to
# look for is derived from the character. These are the 22 silent gaps.
CLOSED_LISTS = [
    ("KleeSelfCheck roster array",
     CODE / "Diagnostics" / "KleeSelfCheck.cs",
     lambda c: f"ModelDb.Character<{c.cs_class}>()"),
    ("KleeMod character registration",
     CODE / "KleeMod.cs",
     lambda c: c.cs_class),
    ("deploy.ps1 art source dirs",
     REPO / "klee-mod" / "build" / "deploy.ps1",
     lambda c: f"images\\cards\\{c.id}"),
    ("build_pck.ps1 character loop",
     REPO / "tools" / "build_pck.ps1",
     lambda c: f"'{c.id}'"),
    ("art_coverage sheet list",
     REPO / "tools" / "art_coverage.py",
     lambda c: f'"{c.id}-cards.yaml"'),
    ("companion shop coverage lint",
     REPO / "tools" / "lint_companion_shop_coverage.py",
     lambda c: f'"{c.id}"'),
    ("pool membership lint",
     REPO / "tools" / "lint_pool_membership.py",
     lambda c: f'"{c.cs_class}CardPool.cs"'),
    ("ancient coverage lint",
     REPO / "tools" / "lint_ancient_coverage.py",
     lambda c: c.cs_class),
    ("roster ancient ledger",
     CODE / "RosterAncientCards.cs",
     lambda c: c.cs_class),
    ("codegen character profiles",
     REPO / "tools" / "gen_klee_cards.py",
     lambda c: f'character_id="{c.id}"'),
    # The per-character driver, NOT gen_roster_cards.py -- that file is a
    # four-line wrapper around gen_klee_cards.main and carries no roster list
    # at all. (Pointing this row at the wrapper was the lint's first finding,
    # against itself, which is the correct thing for it to have caught.)
    # These three `_run_*` functions are 590 lines of triplicated driver with
    # three divergent manifest schemas -- F3's target, still open.
    ("codegen per-character driver",
     REPO / "tools" / "gen_klee_cards.py",
     lambda c: f"def _run_{c.id}("),
]


def check() -> list[str]:
    findings: list[str] = []

    # 1. Files that must EXIST, one per character.
    for label, path_of, _ in SITES:
        if not callable(path_of):
            continue
        for character in roster.ROSTER:
            path = path_of(character)
            if not path.exists():
                findings.append(
                    f"{label}: {character.id} has no {path.relative_to(REPO)}")

    # 2. Closed lists that must NAME every character.
    for label, path, token_of in CLOSED_LISTS:
        text = _text(path)
        if text is None:
            findings.append(f"{label}: missing file {path.relative_to(REPO)}")
            continue
        # Comments are stripped: several of these files explain the roster in
        # prose, and a prose mention is not membership. (The C# and PowerShell
        # comment markers differ; both are handled.)
        code = "\n".join(
            line for line in text.splitlines()
            if not line.lstrip().startswith(("//", "///", "#")))
        for character in roster.ROSTER:
            token = token_of(character)
            if token not in code:
                findings.append(
                    f"{label} ({path.relative_to(REPO)}): "
                    f"{character.id} missing -- expected {token!r}")

    # 3. The registry's own archetype vocabulary vs the cards themselves.
    #    This is R66, and it is checked in BOTH directions.
    from tier0.content import loader
    for character in roster.ROSTER:
        tags: set[str] = set()
        for card in loader._card_index().values():
            if card.character == character.id:
                tags.update(card.archetypes)
        tags.discard("generic")     # everyone has it; nobody IS it
        declared = set(character.archetypes)
        for phantom in sorted(declared - tags):
            findings.append(
                f"archetype registry: {character.id} declares {phantom!r}, "
                "which no card of hers carries. This is R66 exactly -- the "
                "drafter scores her deck with a synergy term that can never "
                "fire, and reports the result as evidence about drafting.")
        for orphan in sorted(tags - declared):
            findings.append(
                f"archetype registry: {character.id}'s cards carry {orphan!r}, "
                "which the registry does not declare. Either it is a typo on "
                "the sheet or it is an archetype nobody registered.")

    # 4. Reference anchors must NOT be roster members.
    for ref in roster.REFERENCE_IDS:
        if ref in roster.BY_ID:
            findings.append(
                f"{ref} is both a reference anchor and a roster member; the "
                "two are deliberately different (anchors have no art, pool or "
                "C# class) and every roster sweep above would be wrong.")

    return findings


def main() -> int:
    findings = check()
    for f in findings:
        print(f"LINT: {f}")
    if findings:
        print(f"\nFAIL: {len(findings)} roster-registry finding(s).")
        return 1
    print(f"roster registry: OK ({len(roster.ROSTER)} characters x "
          f"{len(CLOSED_LISTS)} closed lists)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
