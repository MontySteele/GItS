"""KOKOMI GROWTH POWERS (2026-10-10): what survives the re-founding.

Brief `review/active/kokomi-growth-powers-2026-10-10.md` (archived), ruled ("Agreed on
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
    assert len(ids) == len(set(ids)) == 79  # Kokomi v3 (2026-10-18): Unbroken Tide
    for gone in ("proto_kk_the_generals_banner", "proto_kk_flood_tide"):
        assert gone not in ids
        assert gone not in {c.id for c in loader.prototype_cards()}
    rarity = collections.Counter(_row(cid).rarity for cid in ids)
    # The Kokomi level pass (2026-10-12): Change of Plans C -> U, 20 / 38 / 20.
    assert rarity == {"common": 20, "uncommon": 39, "rare": 20}


def test_kurage_canopy_installs_one_ward_power_and_its_plus(overhaul):
    # Kokomi round 3 A-list (2026-10-13): a Ward per carry-out (was 3 [4]
    # Block); the upgraded card installs the Plus power (Ward+).
    assert _row("proto_kk_kurage_canopy").effects[0]["amount"] == 1
    assert _up("proto_kk_kurage_canopy").effects[0]["power"] == (
        "kk_kurage_canopy_plus")
