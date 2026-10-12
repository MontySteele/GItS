"""KOKOMI GROWTH POWERS (2026-10-10): what survives the re-founding.

Brief `review/active/kokomi-growth-powers-2026-10-10.md`, ruled ("Agreed on
both"). THE RE-FOUNDING (2026-10-12) retired the Casket, so Flood Tide is cut,
Grand Design is a new card under the old name, and Brine Sting is an Attack;
those tests left with them (the re-founding's own tests cover the new rows).
What stays: The General's Banner is still out, and the pool's shape. NOTHING
MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import collections

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.tests.test_kokomi_plan import overhaul  # noqa: F401


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def test_the_generals_banner_stays_out_and_the_pool_is_78(overhaul):
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == len(set(ids)) == 78
    for gone in ("proto_kk_the_generals_banner", "proto_kk_flood_tide"):
        assert gone not in ids
        assert gone not in {c.id for c in loader.prototype_cards()}
    rarity = collections.Counter(_row(cid).rarity for cid in ids)
    assert rarity == {"common": 21, "uncommon": 36, "rare": 21}


def test_kurage_canopy_prints_2_and_3(overhaul):
    # Ceremonial Garment left this pin in the Kokomi card pass (2026-10-11):
    # 1 [2] per stack (`test_kokomi_casket_pass.test_the_moved_numbers`).
    assert _row("proto_kk_kurage_canopy").effects[0]["amount"] == 2
    assert _up("proto_kk_kurage_canopy").effects[0]["amount"] == 3
