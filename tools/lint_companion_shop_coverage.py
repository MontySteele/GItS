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

REPORTED BUT NOT FAILED: a home nation with no RARE companion. The ladder
handles it by widening the nation. It is a roster fact worth seeing on every
run of this lint, not a build break. (Fontaine shipped zero until R64 gave it
four on 2026-07-25 -- which is what made check 1 count cards the shop cannot
actually draw, and why `eligible` now models the banner.)

BANNER STATE IS PART OF THE POOL (R64). Every count below is the WORST CASE
over banner rolls, not the roster. While the banner was a no-op the two were
the same number; they no longer are, and the corner this lint exists to catch
-- a filter emptying a pool that looked full -- is now reachable through the
banner as well as through the nation filter.

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

# BOTH channels must gate 5-stars on the banner, and they must do it together.
# The standing ruling that kept the banner switched off named this exact
# condition -- "it goes live in both channels together, when a nation ships a
# 4th Rare" -- because a banner wired into one channel only means the reward
# slot and the shop disagree about which cards exist in a run, which no player
# could diagnose and no sim run can see (tier 0.5 models one seat).
#
# A source tripwire rather than a test, for the reason recorded throughout this
# file: there is no C# test project. It is a weak instrument and it is the
# strongest one available; deleting a filter is a one-line change that nothing
# else in the repo would notice.
#
# MATCHED ON THE CALL, NOT THE WORD. The first version of this check searched
# for "CompanionBanner" and passed against a file whose filter had been deleted,
# because both files also NAME the class in a comment. Verified by removing the
# call and watching the lint stay green -- the same inert-rule failure S9 hit in
# validate.ps1. A tripwire nobody has seen fire is a tripwire that does not
# exist.
BANNER_CALL = re.compile(r"CompanionBanner\.IsOffered\s*\(")
BANNER_CHANNELS = [
    ("reward slot", REPO / "klee-mod" / "KleeCode" / "CompanionSlot.cs"),
    ("shop channel", REPO / "klee-mod" / "KleeCode" / "CompanionPool.cs"),
]

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
    """Cards the shop could draw, WORST CASE over banner rolls.

    BANNER-AWARE SINCE R64 (2026-07-25). This used to return the full roster,
    which was exactly right while the Featured Banner was a no-op -- no nation
    designed more 5-stars than BANNER_FEATURED_SLOTS, so nothing was ever
    filtered. Fontaine's fourth Rare ended that: one Fontaine 5-star is now
    absent from any given run, and a lint that counts all four is counting
    cards the shop cannot draw.

    The thinning is applied PER NATION and only to 5-stars, mirroring
    rewards.roll_banner and _banner_filtered exactly: a nation contributes at
    most BANNER_FEATURED_SLOTS of them, and 4-stars are never gated. WHICH
    5-stars survive is seed-dependent and irrelevant here -- coverage is a
    counting question, and the count is the same for every roll.
    """
    pool = rewards.companion_pool()
    cards = [c for c in pool.get(rarity, [])
             if c.personal_pool in (None, character)
             and not c.guest_star
             and (nation is None or c.nation == nation)]

    kept = [c for c in cards if c.star != 5]
    by_nation: dict[str | None, list] = {}
    for c in cards:
        if c.star == 5:
            by_nation.setdefault(c.nation, []).append(c)
    for _nation, fives in by_nation.items():
        kept.extend(sorted(fives, key=lambda c: c.id)[:C.BANNER_FEATURED_SLOTS])
    return kept


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

    for label, path in BANNER_CHANNELS:
        if not path.exists():
            findings.append(f"missing {label} source: {path.relative_to(REPO)}")
        elif not BANNER_CALL.search(path.read_text(encoding="utf-8")):
            findings.append(
                f"{path.name}: the {label} no longer gates 5-stars on "
                "CompanionBanner. The banner is only correct if BOTH channels "
                "apply it -- one channel alone means the reward slot and the "
                "shop disagree about which cards exist in a run")

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
