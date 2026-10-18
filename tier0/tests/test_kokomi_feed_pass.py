"""THE FEED PASS (2026-09-29): five 0-cost Plan-only Commons, eight now-and-Plan
Commons to Uncommon, Coral Bulwark a plain Block card, Exposed Flank cut.

[USER], after an act-1 death: "some Plan cards need to go to 0 cost so
there's some way to draft lower-impact feed for the Plan mechanism. Let's not
make too many 'do a thing now AND get a plan going' cards - those should be
higher rarity at least."

THE RE-FOUNDING (2026-10-12) took the five feed rows apart: Nip and Current
Read are cut, and Bubble Ward, Jellyfish Drift and Brine Sting are now-cards
that hand her Wards and Stings (their tests are the re-founding's). What stays
here is the pass's other half.

The sim half. NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    carry_out, kokomi_state, overhaul, plan_card)

MOVED = ("proto_kk_ambush", "proto_kk_read_the_field",
         "proto_kk_riptide", "proto_kk_pincer",
         "proto_kk_surging_shoal")


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def test_a_zero_plan_block_is_nothing_even_with_dexterity(overhaul):
    """Current Read's unprinted clause (the row is cut since 2026-10-12;
    the rule stays): a 0 flat Block must not become a Dexterity-sized Block
    the face never printed."""
    st = kokomi_state(enemies=[make_enemy(hp=100)])
    st.player.powers["dexterity"] = 2
    st.player.block = 0
    carry_out(st, [{"op": "block", "amount": 0}])
    assert st.player.block == 0
    carry_out(st, [{"op": "block", "amount": 2}])
    assert st.player.block == 4


def test_coral_bulwark_blocks_eight_and_writes_no_plan(overhaul):
    row = _row("proto_kk_coral_bulwark")
    assert row.rarity == "common"
    assert row.effects == [{"op": "block", "amount": 8}]
    assert not row.plan
    assert _up("proto_kk_coral_bulwark").effects == [
        {"op": "block", "amount": 11}]


@pytest.mark.parametrize("cid", MOVED)
def test_the_now_and_plan_commons_are_uncommon(overhaul, cid):
    assert _row(cid).rarity == "uncommon"


def test_the_offer_is_78_without_exposed_flank(overhaul):
    # Forty-eight at the feed pass; expansion batch one (2026-09-29) appended
    # 22 rows after the feed and cut The Clouds Like Waves Rippling; the
    # payoff pass (2026-10-01) appended two more and cut Second Thoughts;
    # pool completion (2026-10-01) appended eight; the status batch
    # (2026-10-01) cut seven (All Streams after the feed) and appended seven;
    # the growth Powers (2026-10-10) appended Flood Tide; the re-founding
    # (2026-10-12) cut Nip and Current Read with 22 others.
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 79  # Kokomi v3 (2026-10-18): Unbroken Tide
    for cut in ("proto_kk_nip", "proto_kk_current_read"):
        assert cut not in ids
    assert "proto_kk_exposed_flank" not in ids
    assert "proto_kk_exposed_flank" not in {
        c.id for c in loader.prototype_cards()}
