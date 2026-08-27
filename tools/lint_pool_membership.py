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

THE POOLS THAT COUNT are character-owned pools. ModelDb.AllCardPools is
AllCharacters.Select(c => c.CardPool) plus a hardcoded array of shared pools,
so an unattached helper pool is invisible. Membership therefore means
reachable from KleeCardPool, FurinaCardPool or KokomiCardPool. Their FilterThroughEpochs
overrides keep generated-only kit/token cards out of reward rolls.

Usage: python tools/lint_pool_membership.py
Exit 1 with findings on stdout if any card class is unpooled.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CARD_ROOT = REPO / "klee-mod" / "KleeCode" / "Cards"
# Files reachable from a visible character's GenerateAllCards. The generated
# roster classes are the sheet-owned membership ledgers.
MEMBERSHIP_FILES = [
    REPO / "klee-mod" / "KleeCode" / "KleeCardPool.cs",
    REPO / "klee-mod" / "KleeCode" / "KleeOffPoolCards.cs",
    REPO / "klee-mod" / "KleeCode" / "RosterAncientCards.cs",
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated" / "CompanionRoster.cs",
    REPO / "klee-mod" / "KleeCode" / "FurinaCardPool.cs",
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina" / "Generated"
    / "FurinaCardRoster.cs",
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina" / "Generated"
    / "GuestStarRoster.cs",
    REPO / "klee-mod" / "KleeCode" / "KokomiCardPool.cs",
    REPO / "klee-mod" / "KleeCode" / "Cards" / "Kokomi" / "Generated"
    / "KokomiCardRoster.cs",
]
# EB-150: the generated choose-one mode-face rosters, globbed rather than
# listed. They are per-character and the generator mints one the moment a sheet
# grows its first modal row, so a hand-maintained line here would be a line
# somebody has to remember on exactly the day they forgot the pool.
MEMBERSHIP_FILES += sorted(CARD_ROOT.rglob("*ModalOptions.cs"))

# `public sealed class Foo : CustomCardModel` / `: CustomCardModel, IElementalCard`
#
# ModalOptionCard IS A CustomCardModel, and EB-150 is why the alternation is
# here. The generated mode faces of a choose-one card derive from the shared
# `ModalOptionCard` base rather than naming `CustomCardModel` directly, so the
# original pattern could not see them: Deep Breath's two faces shipped in no
# pool at all, took `CardModel.Pool` through MockCardPool inside
# `NChooseACardSelectionScreen._Ready()`, and soft-locked the turn on the
# 2026-08-26 playtest. This lint's docstring had described that exact failure
# since 2026-07-21; only its regex had not kept up.
CLASS_RE = re.compile(
    r"^\s*public\s+sealed\s+class\s+(\w+)\s*:\s*"
    r"(?:CustomCardModel|ModalOptionCard)\b", re.M
)
# `ModelDb.Card<Foo>()`, or the namespace-qualified `ModelDb.Card<A.B.Foo>()`.
# The qualified form is legal C# and reads identically to the compiler; a
# pattern that only matched the bare name reported a correctly-pooled card as
# unpooled, which is the safe direction to fail but still a false alarm that
# invites someone to "fix" the pool instead of the lint.
MEMBER_RE = re.compile(r"ModelDb\.Card<(?:\w+\.)*(\w+)>\s*\(")


def main() -> int:
    findings: list[str] = []

    declared: dict[str, Path] = {}
    if not CARD_ROOT.is_dir():
        findings.append(f"card directory missing: {CARD_ROOT}")
    else:
        for path in sorted(CARD_ROOT.rglob("*.cs")):
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
                f"time the card is drawn or previewed. Add it to a visible "
                f"character pool (rollable or filtered as off-pool)."
            )

    for finding in findings:
        print(f"FINDING: {finding}")
    if findings:
        return 1
    print(f"pool membership: OK ({len(declared)} card classes, all pooled)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
