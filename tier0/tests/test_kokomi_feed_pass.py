"""THE FEED PASS (2026-09-29): five 0-cost Plan-only Commons, eight now-and-Plan
Commons to Uncommon, Coral Bulwark a plain Block card, Exposed Flank cut.

[USER], after an act-1 death: "some Plan cards need to go to 0 cost so
there's some way to draft lower-impact feed for the Plan mechanism. Let's not
make too many 'do a thing now AND get a plan going' cards - those should be
higher rarity at least."

The sim half. The C# twin is `KleeTests/Prototype/KokomiFeedPassTests.cs`.
NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

import pytest

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    carry_out, kokomi_state, overhaul, plan_card)

FEED = ("proto_kk_bubble_ward", "proto_kk_nip", "proto_kk_jellyfish_drift",
        "proto_kk_current_read", "proto_kk_brine_sting")

MOVED = ("proto_kk_ambush", "proto_kk_read_the_field",
         "proto_kk_stolen_chapter", "proto_kk_riptide", "proto_kk_pincer",
         "proto_kk_feigned_retreat", "proto_kk_signal_arrow",
         "proto_kk_surging_shoal")


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


@pytest.mark.parametrize("cid", FEED)
def test_each_feed_row_is_a_zero_cost_plan_only_common(overhaul, cid):
    row = _row(cid)
    assert (row.cost, row.type, row.rarity) == (0, "skill", "common")
    assert row.effects == []
    assert row.plan and kokomi_plan.plan_shape_reason(row.plan) is None


@pytest.mark.parametrize("cid,base,upgraded", [
    ("proto_kk_bubble_ward",
     [{"op": "block", "amount": 4}], [{"op": "block", "amount": 6}]),
    ("proto_kk_nip",
     [{"op": "damage", "amount": 5, "target": "front_enemy"}],
     [{"op": "damage", "amount": 7, "target": "front_enemy"}]),
    ("proto_kk_jellyfish_drift",
     [{"op": "damage", "amount": 2, "target": "all_enemies"}],
     [{"op": "damage", "amount": 3, "target": "all_enemies"}]),
    ("proto_kk_current_read",
     [{"op": "draw", "amount": 1}, {"op": "block", "amount": 0}],
     [{"op": "draw", "amount": 1}, {"op": "block", "amount": 2}]),
    ("proto_kk_brine_sting",
     [{"op": "apply_power", "power": "weak", "amount": 1,
       "target": "front_enemy"}],
     [{"op": "apply_power", "power": "weak", "amount": 2,
       "target": "front_enemy"}]),
])
def test_the_feed_rows_print_the_ruled_numbers(overhaul, cid, base, upgraded):
    assert _row(cid).plan == base
    assert _up(cid).plan == upgraded


def test_a_zero_plan_block_is_nothing_even_with_dexterity(overhaul):
    """Current Read's unprinted clause: no key adds a Plan clause, so the
    upgrade's "Gain 2 Block" is written at 0, and a 0 flat Block must not
    become a Dexterity-sized Block the face never printed."""
    st = kokomi_state(enemies=[make_enemy(hp=100)])
    st.player.powers["dexterity"] = 2
    st.player.block = 0
    carry_out(st, [{"op": "block", "amount": 0}])
    assert st.player.block == 0
    carry_out(st, [{"op": "block", "amount": 2}])
    assert st.player.block == 4


def test_nip_and_drift_land_on_the_morning(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=40), make_enemy(hp=40)])
    kokomi_plan.schedule(st, _row("proto_kk_nip"))
    kokomi_plan.schedule(st, _row("proto_kk_jellyfish_drift"))
    kokomi_plan.resolve_all(st)
    assert [e.hp for e in st.enemies] == [40 - 5 - 2, 40 - 2]


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


def test_the_offer_holds_the_feed_after_the_casket_rows(overhaul):
    # Forty-eight at the feed pass; expansion batch one (2026-09-29) appended
    # 22 rows after the feed and cut The Clouds Like Waves Rippling; the
    # payoff pass (2026-10-01) appended two more and cut Second Thoughts;
    # pool completion (2026-10-01) appended eight.
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 78
    assert ids[-37:-32] == FEED
    assert "proto_kk_exposed_flank" not in ids
    assert "proto_kk_exposed_flank" not in {
        c.id for c in loader.prototype_cards()}
