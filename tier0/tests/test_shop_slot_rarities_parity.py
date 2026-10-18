"""The shop's two companion slots stock the same bands in both engines.

[USER] 2026-10-18, legacy review pick 2 ("Agreed on all 6 legacy picks"):
slot 1 is a fixed home-nation Uncommon, slot 2 a fixed any-nation Rare that
falls back to Uncommon. The ladders are arrays, which `lint_constant_parity`
does not compare, so this reads them off the C# source.
"""

from __future__ import annotations

import random
import re
from pathlib import Path

from tier0 import constants as C
from tier05 import shop

PATCH = (Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode"
         / "Patches" / "MerchantCompanionSlots.cs")


def _cs_ladder(name: str) -> tuple[str, ...]:
    src = PATCH.read_text(encoding="utf-8")
    m = re.search(rf"{name}\s*=\s*\{{([^}}]*)\}}", src)
    assert m, f"{name} not found in {PATCH.name}"
    return tuple(r.strip().removeprefix("CardRarity.").lower()
                 for r in m.group(1).split(",") if r.strip())


def test_slot_ladders_match_the_mod():
    assert C.SHOP_COMPANION_SLOT_RARITIES == (
        _cs_ladder("SlotOneRarities"), _cs_ladder("SlotTwoRarities"))


def test_the_base_shape():
    assert C.SHOP_COMPANION_SLOT_RARITIES[0][0] == "uncommon"
    assert C.SHOP_COMPANION_SLOT_RARITIES[1] == ("rare", "uncommon")


def test_no_rarity_roll_is_left_in_the_patch():
    src = PATCH.read_text(encoding="utf-8")
    assert "Shops.NextFloat" not in src


def test_sim_slots_are_fixed_uncommon_then_rare():
    for character in ("klee", "furina", "kokomi"):
        for seed in range(40):
            offers = shop.companion_shop_offer(random.Random(seed), character)
            assert [c.rarity for c, _ in offers] == ["uncommon", "rare"], (
                character, seed)
            assert [p for _, p in offers] == [
                C.SHOP_COMPANION_PRICE["uncommon"],
                C.SHOP_COMPANION_PRICE["rare"]]
