"""The companion roster must be able to fill BOTH shop slots, always.

WHY (§4.7 shop channel, R59/R60/R61 -- sprint 2026-07-25). This is instance
TWO of the empty-draw class that `lint_ancient_coverage.py` was written for.
The shape is the same every time: some code asks a filtered pool for a card,
the filter empties the pool, and the draw dies somewhere with no "no card"
path. Dusty Tome was instance one and it softlocked act 2.

The shop's version: `MerchantCardEntry.Populate` ends in
`Rng.NextItem(items)` over a list filtered by rarity -- and, for slot 1, by
NATION as well. The merchant's slot layout is load-bearing UI with no empty
state, so a nation that cannot supply the requested rarity does not degrade,
it throws inside MerchantRoom's async continuation: black screen, run lost.
That is finding 24's exact failure mode.

Both implementations (the C# patch and tier05/shop.py) carry a fallback
ladder, so a thin corner is SURVIVABLE. This lint exists because surviving is
not the same as being right: every rung the ladder takes is a slot that
silently stopped honouring §4.7 -- a slot 1 that is not home-region, or a
rarity below the R59 floor. The player cannot see that; only this can.

CHECKS
  1. DATA (the sheets, where the defect actually lives). For every roster
     character, at each rarity, the WILDCARD pool must hold as many cards as
     there are slots whose ladder can draw that rarity -- the slots draw
     without replacement, so a thin tier can strand the second slot.
  2. DATA. Every character's HOME nation must supply the Uncommon floor, or
     slot 1 -- the targeted "buy your dream support" slot, and the whole
     reason the channel is priced as premium -- widens to wildcard on every
     single visit and the feature is cosmetic for that character.
  3. SOURCE (a tripwire, because there is no C# test project). The merchant
     patch must still contain all three fallback rungs. Deleting a rung is a
     one-line change that reintroduces the softlock and that nothing else in
     the repo would notice.

THE SLOTS' BANDS ([USER] 2026-10-18, legacy review pick 2): slot 1 is a fixed
home-nation Uncommon, slot 2 a fixed any-nation Rare that falls back to
Uncommon (`C.SHOP_COMPANION_SLOT_RARITIES`).

NO BANNER. The Featured Banner, which once thinned each nation's five-stars to
three per run, was scrapped everywhere on 2026-10-18 ([USER]: "Agreed on
(a)!"), so every count below is the roster itself.

Usage: python tools/lint_companion_shop_coverage.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tier0 import constants as C            # noqa: E402
from tier0.content import loader            # noqa: E402
from tier05 import rewards                  # noqa: E402

PATCH = (REPO / "klee-mod" / "KleeCode" / "Patches"
         / "MerchantCompanionSlots.cs")

# Characters that host the companion system. A new roster character means a
# new row here; the reference characters never see a companion at all.
CHARACTERS = ["klee", "furina", "kokomi"]

# The rungs the C# ladder must still have. Each is (label, regex) matched
# against the patch source.
REQUIRED_RUNGS = [
    ("widen the nation", r"Draw\(rarity,\s*null\)"),
    ("drop the rarity", r"Draw\(other,\s*null\)"),
    # LAST RUNG: OMIT THE SLOT ([USER] 2026-08-10). This used to look for
    # `ColorlessCardPool` -- the base-colorless fallback entry the mod built
    # when nothing was drawable. That rung is gone: the mod now returns before
    # constructing a MerchantCardEntry, matching tier05/shop.py, which has
    # always dropped the slot.
    #
    # MATCHED ON THE RETURN, NOT ON A WORD: the file still explains the old
    # rung in prose, and
    # a pattern that a comment can satisfy is a tripwire that cannot fire. The
    # regex below requires the `return;` that sits inside the empty-candidates
    # branch -- delete the branch and the match goes with it.
    ("omit the slot (last rung)", r'OMITTED[\s\S]{0,800}?"\);\s*return;'),
]

# The other half of the same ruling: the rung that was REMOVED must stay
# removed. A base-colorless fallback entry is the divergence [USER] closed on
# 2026-08-10 (the mod leaked a base card where the sim omits the slot), and
# re-adding it is the same one-line change in reverse. Matched on the CALL,
# so the file's prose account of the old rung does not satisfy it.
FORBIDDEN_RUNGS = [
    ("base colorless fallback entry (removed 2026-08-10)",
     r"ModelDb\s*\.?\s*CardPool<\s*ColorlessCardPool\s*>"),
]


def eligible(character: str, rarity: str, nation: str | None) -> list:
    """Cards the shop could draw for this character at this rarity."""
    pool = rewards.companion_pool()
    return [c for c in pool.get(rarity, [])
            if c.personal_pool in (None, character)
            and not c.guest_star
            and (nation is None or c.nation == nation)]


def main() -> int:
    findings: list[str] = []
    ladders = C.SHOP_COMPANION_SLOT_RARITIES
    # How many slots' ladders reach each rarity: both reach Uncommon, only
    # slot 1's roster-gap rung and slot 2 reach Rare.
    reach: dict[str, int] = {}
    for ladder in ladders:
        for rarity in ladder:
            reach[rarity] = reach.get(rarity, 0) + 1
    home_rarity = ladders[0][0]

    for character in CHARACTERS:
        home = loader.character_nation(character)
        if home is None:
            findings.append(
                f"{character}: no home nation on the character sheet, so shop "
                "slot 1 can never be home-region")
            continue

        for rarity, need in reach.items():
            wild = eligible(character, rarity, None)
            if len(wild) < need:
                findings.append(
                    f"{character}: only {len(wild)} {rarity} companion(s) "
                    f"offerable at ANY nation, but {need} shop slot(s) can "
                    "draw that band without replacement -- a slot can strand")

        if not eligible(character, home_rarity, home):
            findings.append(
                f"{character}: {home} supplies no {home_rarity} companion, so "
                "slot 1 widens to wildcard on EVERY visit -- the "
                "home-region slot does not exist for this character")

    if not PATCH.exists():
        findings.append(f"missing merchant patch: {PATCH.relative_to(REPO)}")
    else:
        src = PATCH.read_text(encoding="utf-8")
        for label, pattern in REQUIRED_RUNGS:
            if not re.search(pattern, src):
                findings.append(
                    f"{PATCH.name}: the '{label}' fallback rung is gone. "
                    "Every rung is what stands between a thin roster corner "
                    "and finding 24's black-screen softlock; restore it or "
                    "retire this check with a ruling, not a deletion")
        for label, pattern in FORBIDDEN_RUNGS:
            if re.search(pattern, src):
                findings.append(
                    f"{PATCH.name}: the '{label}' is back. It was removed by "
                    "ruling because it made the mod and tier05/shop.py two "
                    "different games on the same rung; re-adding it needs a "
                    "ruling of its own, and the sim would have to move too")

    for f in findings:
        print(f"FINDING: {f}")
    if findings:
        print(f"\ncompanion shop coverage: {len(findings)} finding(s)")
        return 1
    print(f"companion shop coverage OK: {len(CHARACTERS)} characters x "
          f"{len(reach)} wildcard rarities x {C.SHOP_COMPANION_SLOTS} slots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
