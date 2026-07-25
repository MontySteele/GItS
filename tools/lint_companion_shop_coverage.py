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
     character, at each rarity the ladder can request, the WILDCARD pool must
     hold at least SHOP_COMPANION_SLOTS cards -- two slots draw without
     replacement, so a tier with one card can strand the second slot.
  2. DATA. Every character's HOME nation must supply the Uncommon floor, or
     slot 1 -- the targeted "buy your dream support" slot, and the whole
     reason the channel is priced as premium -- widens to wildcard on every
     single visit and the feature is cosmetic for that character.
  3. SOURCE (a tripwire, because there is no C# test project). The merchant
     patch must still contain all three fallback rungs. Deleting a rung is a
     one-line change that reintroduces the softlock and that nothing else in
     the repo would notice.

REPORTED BUT NOT FAILED: a home nation with no RARE companion. Fontaine ships
zero today, which is exactly the brittleness R59 cites when it rejects a
guaranteed-Rare slot 2, and the ladder handles it by widening the nation. It
is a roster fact worth seeing on every run of this lint, not a build break.

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
    ("base colorless last rung", r"ColorlessCardPool"),
]


def eligible(character: str, rarity: str, nation: str | None) -> list:
    pool = rewards.companion_pool()
    return [c for c in pool.get(rarity, [])
            if c.personal_pool in (None, character)
            and not c.guest_star
            and (nation is None or c.nation == nation)]


def main() -> int:
    findings: list[str] = []
    notes: list[str] = []
    slots = C.SHOP_COMPANION_SLOTS
    rarities = list(C.SHOP_COMPANION_RARITY_ODDS)

    for character in CHARACTERS:
        home = loader.character_nation(character)
        if home is None:
            findings.append(
                f"{character}: no home nation on the character sheet, so shop "
                "slot 1 can never be home-region")
            continue

        for rarity in rarities:
            wild = eligible(character, rarity, None)
            if len(wild) < slots:
                findings.append(
                    f"{character}: only {len(wild)} {rarity} companion(s) "
                    f"offerable at ANY nation, but the shop stocks {slots} "
                    "slots without replacement -- a slot can strand")

            home_tier = eligible(character, rarity, home)
            if home_tier:
                continue
            if rarity == "uncommon":
                findings.append(
                    f"{character}: {home} supplies no Uncommon companion, so "
                    "slot 1 widens to wildcard on EVERY visit -- the "
                    "home-region slot does not exist for this character")
            else:
                notes.append(
                    f"{character}: {home} designs no {rarity} companion; "
                    "slot 1 widens the nation when it rolls one (known, "
                    "handled by the ladder -- see R59)")

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

    for note in notes:
        print(f"note: {note}")
    for f in findings:
        print(f"FINDING: {f}")
    if findings:
        print(f"\ncompanion shop coverage: {len(findings)} finding(s)")
        return 1
    print(f"companion shop coverage OK: {len(CHARACTERS)} characters x "
          f"{len(rarities)} rarities x {C.SHOP_COMPANION_SLOTS} slots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
