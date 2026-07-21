"""Every card class must belong to a card pool.

WHY (playtest crash 2026-07-21). MegaCrit's CardModel.Pool walks
ModelDb.AllCardPools looking for a pool whose AllCardIds contains the card, and
when nothing matches it probes MockCardPool -- whose GenerateAllCards calls
NeverEverCallThisOutsideOfTests_ClearOwner() and throws
InvalidOperationException("You monster!") in a shipped build.

Pool is read by NCard.Reload, i.e. whenever a card NODE is built. So a poolless
card does not fail when it is played -- it fails when it is drawn or previewed,
and it takes down the task that owned the draw. The two symptoms observed were
a companion reward whose take-button appeared dead (the throw escaped
SpecialCardReward.OnSelect after the card was already added) and a combat
softlock at turn start (the throw escaped CombatManager.SetupPlayerTurn).

Both cases were cards deliberately kept OUT of KleeCardPool -- companions
(the 4th reward slot is their only door), the kit Burst card, and token
statuses (created at play time). "Not rollable" is a legitimate design
position; "in no pool at all" is never legitimate.

THE POOL THAT COUNTS IS KleeCardPool. First fix attempt put those cards in a
second CardPoolModel, and this lint went green while the crash continued
unchanged in game: ModelDb.AllCardPools is AllCharacters.Select(c => c.CardPool)
plus a HARDCODED array of 7 shared pools, so a mod pool that is not a
character's CardPool is invisible to the Pool lookup. Membership therefore
means "reachable from KleeCardPool.GenerateAllCards" and nothing else --
KleeOffPoolCards is spliced in there, and KleeCardPool.FilterThroughEpochs is
what keeps those cards out of generation. A lint that checks source text can
confirm membership; it CANNOT confirm the engine sees the pool. That gap is why
the first fix shipped.

Usage: python tools/lint_pool_membership.py
Exit 1 with findings on stdout if any card class is unpooled.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CARD_DIRS = [
    REPO / "klee-mod" / "KleeCode" / "Cards",
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated",
]
# Files reachable from KleeCardPool.GenerateAllCards. KleeOffPoolCards is
# spliced into it; CompanionRoster.All is spliced into KleeOffPoolCards.
MEMBERSHIP_FILES = [
    REPO / "klee-mod" / "KleeCode" / "KleeCardPool.cs",
    REPO / "klee-mod" / "KleeCode" / "KleeOffPoolCards.cs",
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated" / "CompanionRoster.cs",
]

# `public sealed class Foo : CustomCardModel` / `: CustomCardModel, IElementalCard`
CLASS_RE = re.compile(
    r"^\s*public\s+sealed\s+class\s+(\w+)\s*:\s*CustomCardModel\b", re.M
)
# `ModelDb.Card<Foo>()`
MEMBER_RE = re.compile(r"ModelDb\.Card<(\w+)>\s*\(")


def main() -> int:
    findings: list[str] = []

    declared: dict[str, Path] = {}
    for directory in CARD_DIRS:
        if not directory.is_dir():
            findings.append(f"card directory missing: {directory}")
            continue
        for path in sorted(directory.glob("*.cs")):
            for name in CLASS_RE.findall(path.read_text(encoding="utf-8")):
                declared[name] = path

    if not declared:
        # A lint that silently passes because it found nothing is not a gate.
        print("FINDING: no CustomCardModel classes found -- the lint's class "
              "pattern or the source layout changed.")
        return 1

    pooled: set[str] = set()
    for path in MEMBERSHIP_FILES:
        if not path.is_file():
            findings.append(f"membership file missing: {path.relative_to(REPO)}")
            continue
        pooled.update(MEMBER_RE.findall(path.read_text(encoding="utf-8")))

    for name in sorted(declared):
        if name not in pooled:
            rel = declared[name].relative_to(REPO)
            findings.append(
                f"{rel}: {name} is in no card pool. CardModel.Pool falls "
                f"through to MockCardPool and throws 'You monster!' the first "
                f"time the card is drawn or previewed. Add it to KleeCardPool "
                f"(rollable) or KleeExtraCardPool (never rollable)."
            )

    for finding in findings:
        print(f"FINDING: {finding}")
    if findings:
        return 1
    print(f"pool membership: OK ({len(declared)} card classes, all pooled)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
